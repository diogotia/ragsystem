import re
import time
import os

from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent
from sources.tools.searxSearch import searxSearch
from sources.tools.facebookSearch import FacebookSearch
from sources.browser import Browser
from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FacebookSearchAgent(Agent):
    def __init__(self, model, name, prompt_path, provider):
        super().__init__(model, name, prompt_path, provider)
        self.browser = Browser()

        fb_email = os.getenv("FACEBOOK_EMAIL")
        fb_password = os.getenv("FACEBOOK_PASSWORD")

        self.tools = {
            "web_search": searxSearch(),
            "facebook_search": FacebookSearch(self.browser, fb_email, fb_password)
        }

        self.role = "facebook search, web search, social media"
        self.search_history = []
        self.navigable_links = []
        self.notes = []
        self.date = self.get_today_date()

    def process(self, user_prompt, speech_module):
        complete = False
        animate_thinking(f"Searching...", color="status")

        if "facebook" in user_prompt.lower():
            search_result_raw = self.tools["facebook_search"].execute([user_prompt], False)
            search_result = self.parse_facebook_results(search_result_raw)
        else:
            self.memory.push('user', self.search_prompt(user_prompt))
            ai_prompt, _ = self.llm_request()
            search_result_raw = self.tools["web_search"].execute([ai_prompt], False)
            search_result = self.jsonify_search_results(search_result_raw)[:5]

        prompt = self.make_newsearch_prompt(user_prompt, search_result)
        unvisited = [None]

        while not complete:
            answer, reasoning = self.llm_decide(prompt)
            self.save_notes(answer)

            if "REQUEST_EXIT" in answer:
                complete = True
                break

            links = self.extract_links(answer)
            if len(unvisited) == 0:
                break

            if len(links) == 0 or "GO_BACK" in answer:
                unvisited = self.select_unvisited(search_result)
                prompt = self.make_newsearch_prompt(user_prompt, unvisited)
                pretty_print(f"Going back to results. Still {len(unvisited)}", color="warning")
                links = []
                continue

            animate_thinking(f"Navigating to {links[0]}", color="status")
            speech_module.speak(f"Navigating to {links[0]}")
            self.browser.go_to(links[0])
            self.search_history.append(links[0])
            page_text = self.browser.get_text()
            self.navigable_links = self.browser.get_navigable()
            prompt = self.make_navigation_prompt(user_prompt, page_text)

        self.browser.close()
        prompt = self.conclude_prompt(user_prompt)
        self.memory.push('user', prompt)
        answer, reasoning = self.llm_request()
        pretty_print(answer, color="output")
        return answer, reasoning

    def parse_facebook_results(self, raw_text):
        results = []
        elements = self.browser.driver.find_elements(By.CSS_SELECTOR, "div.x1yztbdb")
        for el in elements:
            try:
                results.append({
                    "title": el.find_element(By.CSS_SELECTOR, "span.x193iq5w").text,
                    "price": el.find_element(By.CSS_SELECTOR, "span.x19c4wfv").text,
                    "link": el.find_element(By.TAG_NAME, "a").get_attribute("href"),
                    "date": el.find_element(By.CSS_SELECTOR, "span.x1p4m5qa").text
                })
            except:
                continue
        return results

    def format_facebook_results(self, fb_results):
        formatted_results = []
        if isinstance(fb_results, str):
            if fb_results.startswith("Error") or fb_results == "No results found":
                return []
            results = fb_results.split("\n\n")
            for result in results:
                result_dict = {"title": "", "snippet": "", "link": ""}
                lines = result.split("\n")
                for line in lines:
                    if line.startswith("Author:"):
                        result_dict["title"] = line.replace("Author:", "").strip()
                    elif line.startswith("Post:"):
                        result_dict["snippet"] = line.replace("Post:", "").strip()
                    elif line.startswith("Link:"):
                        result_dict["link"] = line.replace("Link:", "").strip()
                if result_dict["title"] or result_dict["snippet"]:
                    formatted_results.append(result_dict)
        return formatted_results

    def get_today_date(self):
        date_time = date.today()
        return date_time.strftime("%B %d, %Y")

    def extract_links(self, search_result):
        pattern = r'(https?://\S+|www\.\S+)'
        matches = re.findall(pattern, search_result)
        trailing_punct = ".,!?;:"
        cleaned_links = [link.rstrip(trailing_punct) for link in matches]
        return self.clean_links(cleaned_links)

    def clean_links(self, links):
        links_clean = []
        for link in links:
            link = link.strip()
            if link[-1] == '.':
                links_clean.append(link[:-1])
            else:
                links_clean.append(link)
        return links_clean

    def get_unvisited_links(self):
        return "\n".join([f"[{i}] {link}" for i, link in enumerate(self.navigable_links) if link not in self.search_history])

    def make_newsearch_prompt(self, user_prompt, search_result):
        search_choice = self.stringify_search_results(search_result)
        return f"""
        Based on the search result:
        {search_choice}
        Your goal is to find accurate and complete information to satisfy the user's request.
        User request: {user_prompt}
        To proceed, choose a relevant link from the search results. Announce your choice by saying: "I want to navigate to <link>"
        Do not explain your choice.
        """

    def make_navigation_prompt(self, user_prompt, page_text):
        remaining_links = self.get_unvisited_links()
        return f"""
        You are a web browser.
        You are currently on this webpage:
        {page_text}

        You can navigate to these navigation links:
        {remaining_links}

        Your task:
        1. Decide if the current page answers the user's query: {user_prompt}
          - If it does, take notes of the useful information, write down source, link or reference, then move to a new page.
          - If it does and you are 100% certain that it provide a definitive answer, say REQUEST_EXIT
          - If it doesn't, say: Error: This page does not answer the user's query then go back or navigate to another link.
        2. Navigate by either:
          - Navigate to a navigation link (write the full URL).
          - If no link seems helpful, say: GO_BACK.

        Recap:
        - Useful -> Note: [Finding].
        - Not useful -> Error: [Reason].
        """

    def llm_decide(self, prompt):
        animate_thinking("Thinking...", color="status")
        self.memory.push('user', prompt)
        answer, reasoning = self.llm_request()
        pretty_print("-" * 100)
        pretty_print(answer, color="output")
        pretty_print("-" * 100)
        return answer, reasoning

    def select_unvisited(self, search_result):
        results_unvisited = []
        for res in search_result:
            if res["link"] not in self.search_history:
                results_unvisited.append(res)
        return results_unvisited

    def jsonify_search_results(self, results_string):
        result_blocks = results_string.split("\n\n")
        parsed_results = []
        for block in result_blocks:
            if not block.strip():
                continue
            lines = block.split("\n")
            result_dict = {}
            for line in lines:
                if line.startswith("Title:"):
                    result_dict["title"] = line.replace("Title:", "").strip()
                elif line.startswith("Snippet:"):
                    result_dict["snippet"] = line.replace("Snippet:", "").strip()
                elif line.startswith("Link:"):
                    result_dict["link"] = line.replace("Link:", "").strip()
            if result_dict:
                parsed_results.append(result_dict)
        return parsed_results

    def stringify_search_results(self, results_arr):
        return '\n\n'.join([f"Link: {res['link']}" for res in results_arr])

    def save_notes(self, text):
        lines = text.split('\n')
        for line in lines:
            if "note" in line.lower():
                self.notes.append(line)

    def conclude_prompt(self, user_query):
        annotated_notes = [f"{i + 1}: {note.lower().replace('note:', '')}" for i, note in enumerate(self.notes)]
        search_note = '\n'.join(annotated_notes)
        print("AI research notes:\n", search_note)
        return f"""
        Following a human request:
        {user_query}
        A web AI made the following finding across different pages:
        {search_note}

        Summarize the finding, and provide a conclusion that answers the request.
        """

    def search_prompt(self, user_prompt):
        return f"""
        Current date: {self.date}
        Make an efficient search engine query to help users with their request:
        {user_prompt}
        Do not explain, do not write anything besides the search query.
        """
