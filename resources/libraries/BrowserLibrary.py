"""
Robot Framework library for browser management and common web interactions.
"""
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
import sys
import os

# Add parent directory to sys.path to import from utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from resources.libraries.config_manager import ConfigManager


class BrowserLibrary:
    """
    Library for browser management and common web interactions.
    Extends SeleniumLibrary with custom functionality and configuration.
    """

    def __init__(self):
        """Initialize the BrowserLibrary."""
        self.config_manager = ConfigManager()
        self.selenium_lib = None
        self.browser_config = self.config_manager.get_browser_config()
        
    def _get_selenium_library(self):
        """Get the SeleniumLibrary instance from Robot Framework."""
        if self.selenium_lib is None:
            self.selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
        return self.selenium_lib

    @keyword
    def init_browser(self, url=None, browser=None, headless=None):
        """
        Initialize browser with configurable settings.

        Args:
            url (str, optional): URL to navigate to
            browser (str, optional): Browser to use (chrome, firefox, etc.)
            headless (bool, optional): Whether to run in headless mode

        Example:
            | Init Browser | url=${WEB_URL} | browser=chrome | headless=${TRUE} |
        """
        selenium = self._get_selenium_library()
        
        browser = browser or self.browser_config['browser']
        headless = headless if headless is not None else self.browser_config['headless']
        url = url or self.config_manager.get_url()
        
        # Configure browser options
        options = []
        if headless:
            if browser.lower() == 'chrome':
                options.append('headless=True')
                options.append('disable-gpu=True')
            elif browser.lower() == 'firefox':
                options.append('-headless')
        
        # Configure timeouts
        implicit_wait = self.browser_config['implicit_wait']
        default_timeout = self.browser_config['default_timeout']
        
        # Open browser
        selenium.set_selenium_implicit_wait(implicit_wait)
        selenium.set_selenium_timeout(default_timeout)
        selenium.open_browser(url, browser, options=options)
        selenium.maximize_browser_window()
        
        return selenium

    @keyword
    def navigate_to(self, url, verify_page=True):
        """
        Navigate to a URL and optionally verify the page.

        Args:
            url (str): URL to navigate to
            verify_page (bool, optional): Whether to verify the page after navigation

        Example:
            | Navigate To | ${LOGIN_URL} | verify_page=${TRUE} |
        """
        selenium = self._get_selenium_library()
        selenium.go_to(url)
        
        if verify_page:
            selenium.wait_until_page_contains_element('tag:body')

    @keyword
    def take_screenshot_with_name(self, name):
        """
        Take a screenshot with a custom name.

        Args:
            name (str): Name for the screenshot file

        Example:
            | Take Screenshot With Name | login-page |
        """
        selenium = self._get_selenium_library()
        timestamp = BuiltIn().get_time(format='%Y%m%d-%H%M%S')
        filename = f"{name}_{timestamp}"
        selenium.capture_page_screenshot(f"{filename}.png")
        return filename

    @keyword
    def wait_and_click(self, locator, timeout=None):
        """
        Wait for an element to be clickable and then click it.

        Args:
            locator (str): Locator for the element
            timeout (str, optional): Timeout for the wait

        Example:
            | Wait And Click | id:submit-button | timeout=10s |
        """
        selenium = self._get_selenium_library()
        timeout = timeout or f"{self.browser_config['default_timeout']}s"
        
        selenium.wait_until_element_is_visible(locator, timeout)
        selenium.wait_until_element_is_enabled(locator, timeout)
        selenium.click_element(locator)

    @keyword
    def wait_and_input_text(self, locator, text, timeout=None, clear=True):
        """
        Wait for an element to be visible and then input text.

        Args:
            locator (str): Locator for the element
            text (str): Text to input
            timeout (str, optional): Timeout for the wait
            clear (bool, optional): Whether to clear the field before inputting

        Example:
            | Wait And Input Text | id:username | john.doe@example.com | timeout=5s | clear=${TRUE} |
        """
        selenium = self._get_selenium_library()
        timeout = timeout or f"{self.browser_config['default_timeout']}s"
        
        selenium.wait_until_element_is_visible(locator, timeout)
        
        if clear:
            selenium.clear_element_text(locator)
            
        selenium.input_text(locator, text)

    @keyword
    def scroll_to_element(self, locator):
        """
        Scroll to an element.

        Args:
            locator (str): Locator for the element

        Example:
            | Scroll To Element | id:footer |
        """
        selenium = self._get_selenium_library()
        selenium.wait_until_element_is_visible(locator)
        selenium.scroll_element_into_view(locator)

    @keyword
    def is_element_present(self, locator, timeout=None):
        """
        Check if an element is present on the page.

        Args:
            locator (str): Locator for the element
            timeout (str, optional): Timeout for the wait

        Returns:
            bool: True if element is present, False otherwise

        Example:
            | ${present} = | Is Element Present | id:error-message | timeout=2s |
        """
        selenium = self._get_selenium_library()
        timeout = timeout or f"{self.browser_config['default_timeout']}s"
        
        try:
            selenium.wait_until_element_is_visible(locator, timeout)
            return True
        except:
            return False 