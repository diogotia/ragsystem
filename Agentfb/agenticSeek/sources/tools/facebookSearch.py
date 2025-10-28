import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from sources.browser import Browser
from sources.utility import animate_thinking

if __name__ == "__main__":
    from tools import Tools
else:
    from sources.tools.tools import Tools


class FacebookSearch(Tools):
    def __init__(self, browser=None, email=None, password=None):
        super().__init__()
        self.tag = "facebook_search"
        self.browser = browser
        self.email = email or os.getenv("FACEBOOK_EMAIL")
        self.password = password or os.getenv("FACEBOOK_PASSWORD")
        self.logger = logging.getLogger(__name__)  # Correct placement
        self.delay = 2
        self.depth = 3
        self.logged_in = True  # ➔ Track if login was successful

    def login_to_facebook(self):
        try:
            animate_thinking(f"Logging into Facebook...", color="status")
            self.browser.go_to("https://www.facebook.com/login")
            self.logger.info("Facebook login page opened.")

            # Step 1: Wait and type email
            email_input = WebDriverWait(self.browser.driver, 20).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            self.logger.info("Email field found.")
            time.sleep(1)
            email_input.click()
            email_input.clear()
            email_input.send_keys("electroautocar@gmail.com")
            self.logger.info("Email typed.")

            # Step 2: Now wait for password field AFTER typing email
            password_input = WebDriverWait(self.browser.driver, 20).until(
                EC.presence_of_element_located((By.ID, "pass"))
            )
            self.logger.info("Password field found.")
            time.sleep(1)
            password_input.click()
            password_input.clear()
            password_input.send_keys("qaz@qaz123")
            self.logger.info("Password typed.")

            # Step 3: Wait for login button
            login_button = WebDriverWait(self.browser.driver, 20).until(
                EC.element_to_be_clickable((By.NAME, "login"))
            )
            self.logger.info("Login button found.")
            time.sleep(1)
            login_button.click()
            self.logger.info("Clicked login button.")

            # Step 4: Wait for redirect
            WebDriverWait(self.browser.driver, 20).until(
                lambda driver: "home.php" in driver.current_url or "checkpoint" in driver.current_url
            )

            current_url = self.browser.get_current_url()
            if "checkpoint" in current_url:
                self.logger.error("Checkpoint detected! Facebook wants verification.")
                animate_thinking(f"Checkpoint detected! Cannot proceed.", color="error")
                return False

            if "home.php" in current_url:
                self.logger.info("Successfully logged into Facebook.")
                animate_thinking(f"Successfully logged in!", color="success")
                self.logged_in = True
                return True

            self.logger.error("Unknown page after login.")
            return False

        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            animate_thinking(f"Error logging in: {str(e)}", color="error")
            return False

    def search_posts(self, query):
        """Search for posts matching the query."""
        try:
            search_url = f"https://www.facebook.com/search/posts/?q={query}"
            self.browser.go_to(search_url)
            time.sleep(self.delay)

            for _ in range(self.depth):
                self.browser.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(self.delay)

            posts = self.browser.driver.find_elements(By.CSS_SELECTOR, "[role='article']")
            results = []

            for post in posts:
                try:
                    text_elem = post.find_element(By.CSS_SELECTOR, "[data-ad-preview='message']")
                    author_elem = post.find_element(By.CSS_SELECTOR, "h3 a")
                    link_elem = post.find_element(By.CSS_SELECTOR, "a[href*='/posts/']")

                    text = text_elem.text if text_elem else "No text available"
                    author = author_elem.text if author_elem else "Unknown author"
                    link = link_elem.get_attribute("href") if link_elem else None

                    if text and author:
                        results.append({
                            "author": author,
                            "text": text,
                            "link": link
                        })
                except Exception:
                    continue

            return results

        except Exception as e:
            print(f"Search failed: {str(e)}")
            return []

    def execute(self, blocks: list, safety: bool = False) -> str:
        """Executes a search."""
        if not self.browser:
            return "Error: Browser instance not provided"

        if not blocks:
            return "Error: No search query provided"

        query = blocks[0].strip()
        if not query:
            return "Error: Empty search query"

        if not self.login_to_facebook():
            return "Error: Facebook login failed"

        results = self.search_posts(query)

        if not results:
            return "No results found"

        formatted_results = []
        for result in results:
            formatted_result = f"Author: {result['author']}\nPost: {result['text']}"
            if result['link']:
                formatted_result += f"\nLink: {result['link']}"
            formatted_results.append(formatted_result)

        return "\n\n".join(formatted_results)

    def execution_failure_check(self, output: str) -> bool:
        """Check if execution failed."""
        return output.startswith("Error") or output == "No results found"

    def interpreter_feedback(self, output: str) -> str:
        """Provide feedback about the search results."""
        if self.execution_failure_check(output):
            return f"Facebook search failed: {output}"
        return f"Facebook search results:\n{output}"