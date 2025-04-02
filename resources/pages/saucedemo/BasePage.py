"""
Base Page Object for SauceDemo tests.
All SauceDemo page objects should inherit from this class.
"""
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
import logging


class BasePage:
    """
    Base Page Object for SauceDemo application.
    Provides common functionality for all page objects.
    """

    def __init__(self):
        """Initialize the base page."""
        self.logger = logging.getLogger(__name__)
        
    def _get_browser_library(self):
        """Get the Browser library instance."""
        return BuiltIn().get_library_instance('Browser')

    @keyword
    def get_page_title(self):
        """
        Get the title of the current page.

        Returns:
            str: Page title
        """
        browser = self._get_browser_library()
        return browser.get_title()

    @keyword
    def verify_page_title(self, expected_title):
        """
        Verify that the current page has the expected title.

        Args:
            expected_title (str): Expected title of the page
        """
        actual_title = self.get_page_title()
        BuiltIn().should_be_equal(actual_title, expected_title)
        self.logger.info(f"Verified page title: {actual_title}")

    @keyword
    def wait_for_element(self, selector, state="visible", timeout="10s"):
        """
        Wait for an element to reach the expected state.

        Args:
            selector (str): Element selector
            state (str): Expected state (visible, hidden, enabled, disabled, stable)
            timeout (str): Timeout for the wait operation
        """
        browser = self._get_browser_library()
        browser.wait_for_elements_state(selector, state, timeout=timeout)

    @keyword
    def element_should_be_visible(self, selector, timeout="10s"):
        """
        Verify that an element is visible.

        Args:
            selector (str): Element selector
            timeout (str): Timeout for the wait operation
        """
        self.wait_for_element(selector, "visible", timeout)

    @keyword
    def element_should_contain_text(self, selector, expected_text, timeout="10s"):
        """
        Verify that an element contains the expected text.

        Args:
            selector (str): Element selector
            expected_text (str): Expected text to be contained in the element
            timeout (str): Timeout for the wait operation
        """
        self.wait_for_element(selector, "visible", timeout)
        browser = self._get_browser_library()
        actual_text = browser.get_text(selector)
        BuiltIn().should_contain(actual_text, expected_text)
        
    @keyword
    def take_screenshot_with_name(self, name=None):
        """
        Take a screenshot with an optional name.

        Args:
            name (str, optional): Name for the screenshot
            
        Returns:
            str: Path to the screenshot
        """
        browser = self._get_browser_library()
        return browser.take_screenshot(filename=name) 