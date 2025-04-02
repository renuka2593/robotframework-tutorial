"""
Robot Framework library for desktop application testing.
Integrates WhiteLibrary and PyWinAuto for Windows desktop automation.
"""
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
import sys
import os
import time

# Add parent directory to sys.path to import from utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from resources.libraries.config_manager import ConfigManager


class DesktopLibrary:
    """
    Library for desktop application testing.
    Provides keywords for automating desktop applications.
    """

    def __init__(self):
        """Initialize the DesktopLibrary."""
        self.config_manager = ConfigManager()
        self.white_lib = None
        self.timeout = int(self.config_manager.get_env_var('DEFAULT_TIMEOUT', '10'))
        
    def _get_white_library(self):
        """Get the WhiteLibrary instance from Robot Framework."""
        if self.white_lib is None:
            self.white_lib = BuiltIn().get_library_instance('WhiteLibrary')
        return self.white_lib

    @keyword
    def launch_application(self, app_path, arguments=None):
        """
        Launch a desktop application.

        Args:
            app_path (str): Path to the application executable
            arguments (str, optional): Command-line arguments for the application

        Example:
            | Launch Application | C:\\Program Files\\App\\app.exe | --debug |
        """
        white = self._get_white_library()
        white.launch_application(app_path, arguments)
        
        # Wait for application to be ready
        time.sleep(1)

    @keyword
    def attach_application_by_name(self, app_name, timeout=None):
        """
        Attach to a running application by its name.

        Args:
            app_name (str): Name of the application
            timeout (int, optional): Timeout for the operation

        Example:
            | Attach Application By Name | Notepad | timeout=5 |
        """
        white = self._get_white_library()
        timeout = timeout or self.timeout
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                white.attach_window(app_name)
                return True
            except:
                time.sleep(0.5)
                
        raise TimeoutError(f"Failed to attach to application '{app_name}' within {timeout} seconds")

    @keyword
    def attach_window_by_title(self, title, timeout=None):
        """
        Attach to a window by its title.

        Args:
            title (str): Title of the window
            timeout (int, optional): Timeout for the operation

        Example:
            | Attach Window By Title | Untitled - Notepad | timeout=5 |
        """
        white = self._get_white_library()
        timeout = timeout or self.timeout
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                white.attach_window(title)
                return True
            except:
                time.sleep(0.5)
                
        raise TimeoutError(f"Failed to attach to window '{title}' within {timeout} seconds")

    @keyword
    def click_desktop_element(self, locator, search_strategy='AutomationId'):
        """
        Click an element in a desktop application.

        Args:
            locator (str): Locator for the element
            search_strategy (str, optional): Strategy for finding the element

        Example:
            | Click Desktop Element | okButton | search_strategy=AutomationId |
        """
        white = self._get_white_library()
        white.click_button(locator, search_strategy)

    @keyword
    def input_text_to_desktop_element(self, locator, text, search_strategy='AutomationId'):
        """
        Input text to an element in a desktop application.

        Args:
            locator (str): Locator for the element
            text (str): Text to input
            search_strategy (str, optional): Strategy for finding the element

        Example:
            | Input Text To Desktop Element | nameTextBox | John Doe | search_strategy=AutomationId |
        """
        white = self._get_white_library()
        white.input_text(locator, text, search_strategy)

    @keyword
    def verify_element_exists(self, locator, search_strategy='AutomationId', timeout=None):
        """
        Verify that an element exists in a desktop application.

        Args:
            locator (str): Locator for the element
            search_strategy (str, optional): Strategy for finding the element
            timeout (int, optional): Timeout for the verification

        Returns:
            bool: True if element exists, False otherwise

        Example:
            | ${exists} = | Verify Element Exists | errorMessage | search_strategy=Name | timeout=3 |
        """
        white = self._get_white_library()
        timeout = timeout or self.timeout
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                white.verify_button(locator, search_strategy)
                return True
            except:
                try:
                    white.verify_label(locator, search_strategy)
                    return True
                except:
                    try:
                        white.verify_text_box(locator, search_strategy)
                        return True
                    except:
                        time.sleep(0.5)
                        
        return False

    @keyword
    def take_desktop_screenshot(self, name=None):
        """
        Take a screenshot of the desktop application.

        Args:
            name (str, optional): Name for the screenshot file

        Example:
            | Take Desktop Screenshot | login-screen |
        """
        white = self._get_white_library()
        if name is None:
            timestamp = BuiltIn().get_time(format='%Y%m%d-%H%M%S')
            name = f"desktop_{timestamp}"
            
        file_path = os.path.join(os.path.abspath('reports'), f"{name}.png")
        white.take_screenshot(file_path)
        return file_path

    @keyword
    def select_from_combobox(self, locator, value, search_strategy='AutomationId'):
        """
        Select a value from a combobox in a desktop application.

        Args:
            locator (str): Locator for the combobox
            value (str): Value to select
            search_strategy (str, optional): Strategy for finding the combobox

        Example:
            | Select From Combobox | countrySelect | United States | search_strategy=Name |
        """
        white = self._get_white_library()
        white.select_combobox_value(locator, value, search_strategy)

    @keyword
    def close_desktop_application(self):
        """
        Close the desktop application.

        Example:
            | Close Desktop Application |
        """
        white = self._get_white_library()
        white.close_application() 