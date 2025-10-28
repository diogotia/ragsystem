from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import chromedriver_autoinstaller
import time
import os
import shutil
import tempfile
import sys
import logging

class Browser:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    def __init__(self, headless=False, anticaptcha_install=False):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Browser...")
        try:
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--v=1")  # Enable verbose logging for debugging

            # Headless mode configuration
            if headless:
                chrome_options.add_argument("--headless=new")  # Correct argument for newer Chrome versions

            # Dynamically determine Chrome binary path
            chrome_binary_path = self.get_chrome_path()
            if not chrome_binary_path:
                raise FileNotFoundError("Chrome binary not found. Please install Google Chrome.")
            chrome_options.binary_location = chrome_binary_path
            self.logger.info(f"Using Chrome binary: {chrome_binary_path}")

            # Use a unique user data dir only once
            self.user_data_dir = tempfile.mkdtemp()
            self.logger.info(f"Using user data directory: {self.user_data_dir}")


            chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")
            self.logger.info(f"Using user data directory: {self.user_data_dir}")

            # Ensure chromedriver is installed
            chromedriver_path = chromedriver_autoinstaller.install()
            if not chromedriver_path:
                raise FileNotFoundError("ChromeDriver not found. Please install it or add it to your PATH.")
            self.logger.info(f"Using ChromeDriver: {chromedriver_path}")

            # Initialize the browser
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Browser initialized successfully")

        except Exception as e:
            raise Exception(f"Failed to initialize browser: {str(e)}")

    @staticmethod
    def get_chrome_path():
        """Determine the path to the Chrome binary based on the operating system."""
        if sys.platform.startswith("win"):
            paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google\\Chrome\\Application\\chrome.exe"),
            ]
        elif sys.platform.startswith("darwin"):  # macOS
            paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta",
            ]
        else:  # Linux
            paths = [
                "/opt/google/chrome/google-chrome",  # Actual Chrome binary location
                "/usr/bin/google-chrome",  # Symlink
                "/etc/alternatives/google-chrome",  # Alternative symlink
                "/snap/bin/chromium",  # Snap-installed Chromium
            ]

        for path in paths:
            if os.path.exists(path) and os.access(path, os.X_OK):  # Check if executable
                logging.info(f"Found Chrome binary at: {path}")
                return path
        logging.error("Chrome binary not found. Checked the following paths:")
        for path in paths:
            logging.error(f"- {path}")
        return None

    def facebook_login(self, email, password):
        try:
            self.logger.info("Logging into Facebook...")
            self.go_to("https://www.facebook.com/login")

            email_input = self.driver.find_element(By.ID, "email")
            password_input = self.driver.find_element(By.ID, "pass")

            email_input.send_keys(email)
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)

            time.sleep(5)  # Let it load after login
            self.logger.info("Facebook login successful.")
            return True
        except Exception as e:
            self.logger.error(f"Facebook login failed: {e}")
            return False

    def go_to(self, url):
        """Navigate to a specified URL."""
        try:
            self.driver.get(url)
            time.sleep(1)
            self.logger.info(f"Navigated to: {url}")
            return True
        except Exception as e:
            self.logger.error(f"Error navigating to {url}: {str(e)}")
            return False

    def is_sentence(self, text):
        """Check if the text qualifies as a meaningful sentence or contains important error codes."""
        text = text.strip()

        error_codes = ["404", "403", "500", "502", "503"]
        if any(code in text for code in error_codes):
            return True
        words = re.findall(r'\w+', text, re.UNICODE)
        word_count = len(words)
        has_punctuation = any(text.endswith(p) for p in ['.', '，', ',', '!', '?', '。', '！', '？', '।', '۔'])
        is_long_enough = word_count > 5
        return (word_count >= 5 and (has_punctuation or is_long_enough))


    def click_element(self, xpath):
        """Click an element specified by xpath."""
        try:
            element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            time.sleep(2)  # Wait for action to complete
            return True
        except TimeoutException:
            self.logger.error(f"Element not found or not clickable: {xpath}")
            return False

    def get_current_url(self):
        """Get the current URL of the page."""
        return self.driver.current_url

    def get_page_title(self):
        """Get the title of the current page."""
        return self.driver.title

    def scroll_bottom(self):
        """Scroll to the bottom of the page."""
        try:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(1)  # Wait for scroll to complete
            return True
        except Exception as e:
            self.logger.error(f"Error scrolling: {str(e)}")
            return False

    def screenshot(self, filename):
        """Take a screenshot of the current page."""
        try:
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved as {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return False

    def get_navigable(self):
        """Get all navigable links on the current page."""
        try:
            links = []
            elements = self.driver.find_elements(By.TAG_NAME, "a")

            for element in elements:
                href = element.get_attribute("href")
                if href and href.startswith(("http", "https")):
                    links.append({
                        "url": href,
                        "text": element.text.strip(),
                        "is_displayed": element.is_displayed()
                    })

            self.logger.info(f"Found {len(links)} navigable links")
            return [self.clean_url(link['url']) for link in links if (link['is_displayed'] == True and self.is_link_valid(link['url']))]
        except Exception as e:
            self.logger.error(f"Error getting navigable links: {str(e)}")
            return []

    def get_text(self) -> str:
        """
        Извлекает весь текст со страницы, игнорируя скрипты и стили
        """
        try:
            # Ждем загрузки контента (можно настроить время ожидания)
            time.sleep(2)

            # Извлекаем текст из тега <body>, игнорируя скрипты и стили
            body = self.driver.find_element(By.TAG_NAME, 'body')
            return body.text
        except Exception as e:
            self.logger.error(f"Ошибка при извлечении текста со страницы: {e}")
            return ""

    def close(self):
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
        except Exception as e:
            self.logger.error(f"Error while closing browser: {e}")
        finally:
            # Clean up the temporary user data directory
            if hasattr(self, 'user_data_dir') and os.path.exists(self.user_data_dir):
                shutil.rmtree(self.user_data_dir)
                self.logger.info(f"Deleted user data directory: {self.user_data_dir}")
                self.logger.info("Browser closed")



    def __del__(self):
        self.close()

class FacebookSearch:
    def __init__(self, browser, email, password):
        self.browser = browser
        self.email = email
        self.password = password

    def execute(self, query):
        """
        Search inside Facebook groups using the provided query
        Example: 'кровельщик германия'
        """
        if not self.browser.facebook_login(self.email, self.password):
            return "Login failed."

        search_url = f"https://www.facebook.com/groups/search?q={query}"
        self.browser.go_to(search_url)
        time.sleep(5)  # wait for FB to load

        # Optionally scroll for more posts
        for _ in range(3):
            self.browser.scroll_bottom()
            time.sleep(2)

        content = self.browser.get_text()
        return content

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    browser = Browser(headless=False)
    try:
        browser.go_to("https://github.com/Fosowl/agenticSeek")
        text = browser.get_text()
        print("Page Text in Markdown:")
        print(text)
        links = browser.get_navigable()
        print("\nNavigable Links:", links)
    finally:
        browser.close()