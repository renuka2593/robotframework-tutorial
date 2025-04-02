"""
Configuration Manager for Robot Framework
"""
import os
from pathlib import Path
from dotenv import load_dotenv


class ConfigManager:
    """
    Manages configuration settings for the automation framework.
    Loads configuration from environment variables and .env file.
    """

    def __init__(self):
        """Initialize the ConfigManager."""
        # Load .env file if it exists
        env_path = Path(os.path.join(os.getcwd(), '.env'))
        load_dotenv(dotenv_path=env_path)

    def get_env_var(self, var_name, default_value=None):
        """
        Get an environment variable.

        Args:
            var_name (str): Name of the environment variable
            default_value: Value to return if variable doesn't exist

        Returns:
            The value of the environment variable or the default value
        """
        return os.environ.get(var_name, default_value)

    def get_browser_config(self):
        """
        Get browser configuration settings.

        Returns:
            dict: Browser configuration settings
        """
        return {
            'browser': self.get_env_var('BROWSER', 'chrome'),
            'headless': self.get_env_var('HEADLESS', 'False').lower() == 'true',
            'implicit_wait': int(self.get_env_var('IMPLICIT_WAIT', '5')),
            'default_timeout': int(self.get_env_var('DEFAULT_TIMEOUT', '10'))
        }

    def get_credentials(self, app_name=None):
        """
        Get credentials for a specific application.

        Args:
            app_name (str, optional): Name of the application

        Returns:
            dict: Username and password for the specified application
        """
        if app_name:
            username_var = f'{app_name.upper()}_USERNAME'
            password_var = f'{app_name.upper()}_PASSWORD'
        else:
            username_var = 'TEST_USERNAME'
            password_var = 'TEST_PASSWORD'

        return {
            'username': self.get_env_var(username_var, ''),
            'password': self.get_env_var(password_var, '')
        }

    def get_url(self, url_name=None):
        """
        Get a URL for a specific application.

        Args:
            url_name (str, optional): Name of the application URL

        Returns:
            str: URL for the specified application
        """
        if url_name:
            return self.get_env_var(f'{url_name.upper()}_URL', '')
        return self.get_env_var('WEB_URL', 'https://www.example.com') 