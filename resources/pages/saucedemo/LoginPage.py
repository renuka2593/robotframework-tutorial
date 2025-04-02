"""
Login Page Object for SauceDemo tests.
"""
from robot.api.deco import keyword
from resources.pages.saucedemo.BasePage import BasePage


class LoginPage(BasePage):
    """
    Page Object for SauceDemo login page.
    Handles login functionality and verification.
    """

    def __init__(self):
        """Initialize the login page object."""
        super().__init__()
        
        # Define selectors
        self.selectors = {
            'username_field': 'id=user-name',
            'password_field': 'id=password',
            'login_button': 'id=login-button',
            'error_message': 'css=h3[data-test="error"]',
            'login_logo': 'css=.login_logo',
            'login_credentials': 'id=login_credentials',
            'login_password': 'css=.login_password'
        }

    @keyword
    def navigate_to_login_page(self, url):
        """
        Navigate to the login page.

        Args:
            url (str): URL of the login page
        """
        browser = self._get_browser_library()
        browser.go_to(url)
        self.element_should_be_visible(self.selectors['login_logo'])
        self.logger.info(f"Navigated to login page: {url}")

    @keyword
    def verify_login_page_loaded(self):
        """
        Verify that the login page is loaded properly.
        """
        # Verify key elements are visible
        for element in ['username_field', 'password_field', 'login_button']:
            self.element_should_be_visible(self.selectors[element])
        
        # Verify page title
        self.verify_page_title("Swag Labs")
        self.logger.info("Login page loaded successfully")
        return True

    @keyword
    def login_with_credentials(self, username, password):
        """
        Log in with the provided credentials.

        Args:
            username (str): Username
            password (str): Password
        """
        browser = self._get_browser_library()
        
        # Enter credentials
        browser.fill_text(self.selectors['username_field'], username)
        browser.fill_secret(self.selectors['password_field'], password)
        
        # Click login button
        browser.click(self.selectors['login_button'])
        self.logger.info(f"Attempted login with username: {username}")

    @keyword
    def login_as_user(self, user_dict):
        """
        Log in using a user dictionary containing username and password.

        Args:
            user_dict (dict): Dictionary with username and password keys
        """
        self.login_with_credentials(user_dict['username'], user_dict['password'])

    @keyword
    def verify_login_error(self, expected_error):
        """
        Verify that login failed with the expected error message.

        Args:
            expected_error (str): Expected error message
        """
        self.element_should_be_visible(self.selectors['error_message'])
        self.element_should_contain_text(self.selectors['error_message'], expected_error)
        self.logger.info(f"Verified login error: {expected_error}")
        return True

    @keyword
    def get_available_credentials(self):
        """
        Get the list of available credentials shown on the login page.

        Returns:
            list: List of available usernames
        """
        browser = self._get_browser_library()
        credentials_text = browser.get_text(self.selectors['login_credentials'])
        
        # Extract usernames from the credentials text
        lines = credentials_text.split('\n')
        usernames = [line.strip() for line in lines[1:] if line.strip()]
        
        self.logger.info(f"Available usernames: {usernames}")
        return usernames

    @keyword
    def get_password_from_page(self):
        """
        Get the password shown on the login page.

        Returns:
            str: Password
        """
        browser = self._get_browser_library()
        password_text = browser.get_text(self.selectors['login_password'])
        
        # Extract password from the text
        lines = password_text.split('\n')
        password = lines[1].strip() if len(lines) > 1 else None
        
        return password 