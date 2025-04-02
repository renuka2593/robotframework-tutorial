"""
Robot Framework library for dynamic locator generation.
"""
from robot.api.deco import keyword
import sys
import os

# Add parent directory to sys.path to import from utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from utils.locators.dynamic_locator import DynamicLocator, LocatorRepository


class LocatorLibrary:
    """
    Robot Framework library for dynamic locator generation.
    Provides keywords for creating and managing locators dynamically.
    """

    def __init__(self):
        """Initialize the LocatorLibrary."""
        self.repository = LocatorRepository()
        self.locator_generator = DynamicLocator()

    @keyword
    def add_locator_to_repository(self, name, strategy, template):
        """
        Add a locator to the repository.

        Args:
            name (str): Name of the locator
            strategy (str): Locator strategy (xpath, css, id, etc.)
            template (str): Locator template with placeholders

        Example:
            | Add Locator To Repository | login_button | id | login-button |
        """
        self.repository.add_locator(name, strategy, template)

    @keyword
    def get_locator_from_repository(self, name, **kwargs):
        """
        Get a locator from the repository with placeholders replaced.

        Args:
            name (str): Name of the locator
            **kwargs: Key-value pairs for placeholder replacement

        Returns:
            str: Complete locator string in Robot Framework format

        Example:
            | ${locator} = | Get Locator From Repository | user_row | user_id=${user_id} |
        """
        return self.repository.get_locator(name, **kwargs)

    @keyword
    def create_xpath_locator(self, base_xpath, **kwargs):
        """
        Create a dynamic XPath locator.

        Args:
            base_xpath (str): Base XPath locator with placeholders
            **kwargs: Key-value pairs for placeholder replacement

        Returns:
            str: The XPath locator with placeholders replaced

        Example:
            | ${locator} = | Create XPath Locator | //div[@id='{id}']/span[text()='{text}'] | id=user-info | text=Profile |
        """
        xpath = self.locator_generator.create_xpath(base_xpath, **kwargs)
        return f"xpath:{xpath}"

    @keyword
    def create_css_locator(self, base_css, **kwargs):
        """
        Create a dynamic CSS selector.

        Args:
            base_css (str): Base CSS selector with placeholders
            **kwargs: Key-value pairs for placeholder replacement

        Returns:
            str: The CSS selector with placeholders replaced

        Example:
            | ${locator} = | Create CSS Locator | div#{id} > .{class} | id=main | class=profile |
        """
        css = self.locator_generator.create_css(base_css, **kwargs)
        return f"css:{css}"

    @keyword
    def generate_dynamic_locator(self, strategy, locator_template, **kwargs):
        """
        Generate a locator with specific strategy and template.

        Args:
            strategy (str): Locator strategy (xpath, css, id, etc.)
            locator_template (str): Template with placeholders
            **kwargs: Key-value pairs for placeholder replacement

        Returns:
            str: Complete locator string in Robot Framework format

        Example:
            | ${locator} = | Generate Dynamic Locator | xpath | //button[@name='{name}'] | name=submit |
        """
        return self.locator_generator.generate_locator(strategy, locator_template, **kwargs)

    @keyword
    def combine_locators(self, strategy, *locator_parts):
        """
        Combine multiple locator parts into a single locator.

        Args:
            strategy (str): Locator strategy (xpath, css)
            *locator_parts: Variable number of locator parts to combine

        Returns:
            str: Combined locator string in Robot Framework format

        Example:
            | ${locator} = | Combine Locators | xpath | //button[@id='submit'] | //input[@type='submit'] |
        """
        return self.locator_generator.combine_locators(strategy, *locator_parts) 