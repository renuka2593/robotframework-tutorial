"""
Login Page Object for Browser Library UI tests.
"""
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn


class BrowserLoginPage:
    """
    Page Object for a login page using Browser library.
    Handles login functionality and verification.
    """

    def __init__(self):
        """Initialize the Browser Login Page Object."""
        self.selectors = {
            'username_field': 'id=user-name',
            'password_field': 'id=password',
            'login_button': 'id=login-button',
            'error_message': 'css=h3[data-test="error"]',
            'logo': 'css=.login_logo',
            'inventory_container': 'css=.inventory_container',
            'inventory_items': 'css=.inventory_item'
        }

    def _get_browser_library(self):
        """Get the Browser library instance."""
        return BuiltIn().get_library_instance('Browser')

    @keyword
    def verify_page_loaded(self):
        """
        Verify that the login page is loaded.

        Example:
            | Verify Page Loaded |
        """
        browser = self._get_browser_library()
        browser.wait_for_elements_state(self.selectors['username_field'], 'visible')
        browser.wait_for_elements_state(self.selectors['password_field'], 'visible')
        browser.wait_for_elements_state(self.selectors['login_button'], 'visible')
        return True

    @keyword
    def login(self, username, password):
        """
        Login with the provided credentials.

        Args:
            username (str): Username
            password (str): Password

        Example:
            | Login | standard_user | secret_sauce |
        """
        browser = self._get_browser_library()
        browser.type_text(self.selectors['username_field'], username)
        browser.type_secret(self.selectors['password_field'], password)
        browser.click(self.selectors['login_button'])

    @keyword
    def login_should_fail_with_message(self, username, password, expected_message):
        """
        Verify that login fails with the expected error message.

        Args:
            username (str): Username
            password (str): Password
            expected_message (str): Expected error message

        Example:
            | Login Should Fail With Message | locked_out_user | secret_sauce | Sorry, this user has been locked out |
        """
        self.login(username, password)
        browser = self._get_browser_library()
        browser.wait_for_elements_state(self.selectors['error_message'], 'visible')
        
        actual_message = browser.get_text(self.selectors['error_message'])
        BuiltIn().should_contain(actual_message, expected_message)
        return True

    @keyword
    def verify_login_page_title(self, expected_title):
        """
        Verify that the login page has the expected title.

        Args:
            expected_title (str): Expected page title

        Example:
            | Verify Login Page Title | Swag Labs |
        """
        browser = self._get_browser_library()
        actual_title = browser.get_title()
        BuiltIn().should_be_equal(actual_title, expected_title)
        return True

    @keyword
    def verify_successful_login(self):
        """
        Verify that login was successful by checking for inventory container.

        Example:
            | Verify Successful Login |
        """
        browser = self._get_browser_library()
        browser.wait_for_elements_state(self.selectors['inventory_container'], 'visible')
        return True

    @keyword
    def get_inventory_item_count(self):
        """
        Get the count of inventory items on the page.

        Returns:
            int: Count of inventory items

        Example:
            | ${count} = | Get Inventory Item Count |
        """
        browser = self._get_browser_library()
        return browser.get_element_count(self.selectors['inventory_items'])

    @keyword
    def take_element_screenshot(self, selector, filename):
        """
        Take a screenshot of a specific element.

        Args:
            selector (str): Element selector
            filename (str): Path to save the screenshot

        Example:
            | Take Element Screenshot | css=.login_logo | ${EXECDIR}/logo.png |
        """
        browser = self._get_browser_library()
        browser.take_screenshot(selector=selector, filename=filename)
        return filename 