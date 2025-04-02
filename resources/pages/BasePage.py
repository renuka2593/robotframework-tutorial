"""
Base Page Object class for Robot Framework UI tests.
All page objects should inherit from this class.
"""
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn


class BasePage:
    """
    Base Page Object class for the framework.
    Provides common functionality for all page objects.
    """

    def __init__(self, page_name=None):
        """
        Initialize the base page object.

        Args:
            page_name (str, optional): Name of the page for reporting purposes
        """
        self.page_name = page_name or self.__class__.__name__
        self.selectors = {}
        self._init_selectors()

    def _init_selectors(self):
        """
        Initialize page selectors.
        Override this method in subclasses to define page-specific selectors.
        """
        pass

    def _get_selenium_library(self):
        """Get the SeleniumLibrary instance from Robot Framework."""
        return BuiltIn().get_library_instance('SeleniumLibrary')

    def _get_browser_library(self):
        """Get the BrowserLibrary instance from Robot Framework."""
        return BuiltIn().get_library_instance('BrowserLibrary')

    def _get_locator_library(self):
        """Get the LocatorLibrary instance from Robot Framework."""
        return BuiltIn().get_library_instance('LocatorLibrary')

    @keyword
    def verify_page_loaded(self):
        """
        Verify that the page is loaded.
        Override this method in subclasses to define page-specific verification logic.

        Example:
            | Verify Page Loaded |
        """
        raise NotImplementedError("Subclasses must implement verify_page_loaded()")

    @keyword
    def get_page_title(self):
        """
        Get the title of the current page.

        Returns:
            str: Page title

        Example:
            | ${title} = | Get Page Title |
        """
        selenium = self._get_selenium_library()
        return selenium.get_title()

    @keyword
    def take_page_screenshot(self):
        """
        Take a screenshot of the current page.

        Returns:
            str: Path to the screenshot file

        Example:
            | ${screenshot} = | Take Page Screenshot |
        """
        browser = self._get_browser_library()
        return browser.take_screenshot_with_name(self.page_name)

    @keyword
    def wait_for_element(self, locator, timeout=None):
        """
        Wait for an element to be visible on the page.

        Args:
            locator (str): Element locator
            timeout (str, optional): Timeout for the wait

        Example:
            | Wait For Element | id:submit-button | timeout=10s |
        """
        selenium = self._get_selenium_library()
        selenium.wait_until_element_is_visible(locator, timeout)

    @keyword
    def click_element_on_page(self, locator):
        """
        Click an element on the page.

        Args:
            locator (str): Element locator

        Example:
            | Click Element On Page | id:submit-button |
        """
        browser = self._get_browser_library()
        browser.wait_and_click(locator)

    @keyword
    def input_text_on_page(self, locator, text, clear=True):
        """
        Input text to an element on the page.

        Args:
            locator (str): Element locator
            text (str): Text to input
            clear (bool, optional): Whether to clear the field before inputting

        Example:
            | Input Text On Page | id:username | john.doe@example.com | clear=${TRUE} |
        """
        browser = self._get_browser_library()
        browser.wait_and_input_text(locator, text, clear=clear)

    @keyword
    def get_element_text(self, locator):
        """
        Get the text of an element on the page.

        Args:
            locator (str): Element locator

        Returns:
            str: Element text

        Example:
            | ${text} = | Get Element Text | id:message |
        """
        selenium = self._get_selenium_library()
        return selenium.get_text(locator)

    @keyword
    def element_should_be_visible(self, locator, timeout=None):
        """
        Verify that an element is visible on the page.

        Args:
            locator (str): Element locator
            timeout (str, optional): Timeout for the verification

        Example:
            | Element Should Be Visible | id:success-message | timeout=5s |
        """
        selenium = self._get_selenium_library()
        selenium.wait_until_element_is_visible(locator, timeout)

    @keyword
    def element_should_not_be_visible(self, locator, timeout='5s'):
        """
        Verify that an element is not visible on the page.

        Args:
            locator (str): Element locator
            timeout (str, optional): Timeout for the verification

        Example:
            | Element Should Not Be Visible | id:error-message | timeout=3s |
        """
        selenium = self._get_selenium_library()
        selenium.wait_until_element_is_not_visible(locator, timeout)

    @keyword
    def get_dynamic_locator(self, base_locator, **kwargs):
        """
        Get a dynamic locator with placeholders replaced by values.

        Args:
            base_locator (str): Base locator with placeholders
            **kwargs: Key-value pairs for placeholder replacement

        Returns:
            str: Complete locator with placeholders replaced

        Example:
            | ${locator} = | Get Dynamic Locator | xpath://div[@id='user-{id}'] | id=12345 |
        """
        locator_lib = self._get_locator_library()
        strategy = base_locator.split(':', 1)[0] if ':' in base_locator else 'xpath'
        template = base_locator.split(':', 1)[1] if ':' in base_locator else base_locator
        
        return locator_lib.generate_dynamic_locator(strategy, template, **kwargs) 