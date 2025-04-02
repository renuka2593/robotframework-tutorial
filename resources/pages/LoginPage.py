"""
Login Page Object for Robot Framework UI tests.
"""
from robot.api.deco import keyword
from resources.pages.BasePage import BasePage


class LoginPage(BasePage):
    """
    Page Object for a login page.
    Handles login functionality and verification.
    """

    def __init__(self):
        """Initialize the Login Page Object."""
        super().__init__("LoginPage")

    def _init_selectors(self):
        """Initialize login page selectors."""
        self.selectors = {
            'username_field': 'id:user-name',
            'password_field': 'id:password',
            'login_button': 'id:login-button',
            'error_message': 'xpath://h3[@data-test="error"]',
            'logo': 'css:.login_logo',
            'user_row': 'xpath://div[@class="user-row" and @data-username="{username}"]'
        }

    @keyword
    def verify_page_loaded(self):
        """
        Verify that the login page is loaded.

        Example:
            | Verify Page Loaded |
        """
        selenium = self._get_selenium_library()
        selenium.wait_until_element_is_visible(self.selectors['username_field'])
        selenium.wait_until_element_is_visible(self.selectors['password_field'])
        selenium.wait_until_element_is_visible(self.selectors['login_button'])
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
        self.input_text_on_page(self.selectors['username_field'], username)
        self.input_text_on_page(self.selectors['password_field'], password)
        self.click_element_on_page(self.selectors['login_button'])

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
        error_elem = self.selectors['error_message']
        self.element_should_be_visible(error_elem)
        
        actual_message = self.get_element_text(error_elem)
        if expected_message not in actual_message:
            raise AssertionError(f"Expected error message '{expected_message}' not found in '{actual_message}'")
        
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
        actual_title = self.get_page_title()
        if actual_title != expected_title:
            raise AssertionError(f"Expected title '{expected_title}' but got '{actual_title}'")
        
        return True

    @keyword
    def get_user_row_locator(self, username):
        """
        Get a dynamic locator for a user row with the specified username.

        Args:
            username (str): Username value for the locator

        Returns:
            str: Locator for the user row

        Example:
            | ${locator} = | Get User Row Locator | standard_user |
        """
        locator_lib = self._get_locator_library()
        return locator_lib.create_xpath_locator(self.selectors['user_row'].split(':', 1)[1], username=username) 