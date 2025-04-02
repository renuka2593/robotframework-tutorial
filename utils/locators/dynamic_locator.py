"""
Dynamic Locator Generator for Robot Framework
"""
import re


class DynamicLocator:
    """
    Utility class for dynamically generating and manipulating locators.
    Supports various locator strategies including CSS, XPath, and more.
    """

    @staticmethod
    def create_xpath(base_xpath, **kwargs):
        """
        Create a dynamic XPath locator by replacing placeholders with values.

        Args:
            base_xpath (str): Base XPath locator with placeholders
            **kwargs: Key-value pairs for placeholder replacement

        Returns:
            str: The XPath locator with placeholders replaced
        """
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            base_xpath = base_xpath.replace(placeholder, str(value))
        return base_xpath

    @staticmethod
    def create_css(base_css, **kwargs):
        """
        Create a dynamic CSS selector by replacing placeholders with values.

        Args:
            base_css (str): Base CSS selector with placeholders
            **kwargs: Key-value pairs for placeholder replacement

        Returns:
            str: The CSS selector with placeholders replaced
        """
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            base_css = base_css.replace(placeholder, str(value))
        return base_css

    @staticmethod
    def generate_locator(strategy, locator_template, **kwargs):
        """
        Generate a locator with specific strategy and template.

        Args:
            strategy (str): Locator strategy (xpath, css, id, etc.)
            locator_template (str): Template with placeholders
            **kwargs: Key-value pairs for placeholder replacement

        Returns:
            str: Complete locator string in Robot Framework format
        """
        if strategy.lower() == 'xpath':
            locator = DynamicLocator.create_xpath(locator_template, **kwargs)
            return f"xpath:{locator}"
        elif strategy.lower() == 'css':
            locator = DynamicLocator.create_css(locator_template, **kwargs)
            return f"css:{locator}"
        else:
            # For other strategies like id, name, class, etc.
            for key, value in kwargs.items():
                placeholder = f"{{{key}}}"
                locator_template = locator_template.replace(placeholder, str(value))
            return f"{strategy}:{locator_template}"

    @staticmethod
    def combine_locators(strategy, *locator_parts):
        """
        Combine multiple locator parts into a single locator.
        Useful for complex element identification.

        Args:
            strategy (str): Locator strategy (xpath, css, id, etc.)
            *locator_parts: Variable number of locator parts to combine

        Returns:
            str: Combined locator string in Robot Framework format
        """
        if strategy.lower() == 'xpath':
            combined = ' | '.join(f'({part})' for part in locator_parts if part)
            return f"xpath:{combined}"
        elif strategy.lower() == 'css':
            combined = ', '.join(part for part in locator_parts if part)
            return f"css:{combined}"
        else:
            raise ValueError(f"Strategy '{strategy}' does not support combining locators")


class LocatorRepository:
    """
    Repository for storing and managing locators.
    Enables central management of locators for Page Objects.
    """

    def __init__(self):
        """Initialize the locator repository."""
        self.locators = {}

    def add_locator(self, name, strategy, template):
        """
        Add a locator to the repository.

        Args:
            name (str): Name of the locator
            strategy (str): Locator strategy (xpath, css, id, etc.)
            template (str): Locator template with placeholders

        Returns:
            None
        """
        self.locators[name] = {'strategy': strategy, 'template': template}

    def get_locator(self, name, **kwargs):
        """
        Get a locator from the repository with placeholders replaced.

        Args:
            name (str): Name of the locator
            **kwargs: Key-value pairs for placeholder replacement

        Returns:
            str: Complete locator string in Robot Framework format
        """
        if name not in self.locators:
            raise KeyError(f"Locator '{name}' not found in repository")

        locator_info = self.locators[name]
        return DynamicLocator.generate_locator(
            locator_info['strategy'],
            locator_info['template'],
            **kwargs
        ) 