import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from utils.locators.dynamic_locator import DynamicLocator


class TestLocators(unittest.TestCase):
    def test_xpath_locator(self):
        base_xpath = "//div[@id='{id}']/span[text()='{text}']"
        result = DynamicLocator.create_xpath(base_xpath, id="user", text="Profile")
        expected = "//div[@id='user']/span[text()='Profile']"
        self.assertEqual(result, expected)
        
    def test_css_locator(self):
        base_css = "div#{id} > .{class_name}"
        result = DynamicLocator.create_css(base_css, id="main", class_name="profile")
        expected = "div#main > .profile"
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main() 