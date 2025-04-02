"""
Notepad Page Object for Robot Framework desktop UI tests.
"""
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn


class NotepadPage:
    """
    Page Object for Windows Notepad application.
    Handles Notepad-specific interactions and verifications.
    """

    def __init__(self):
        """Initialize the Notepad Page Object."""
        self.selectors = {
            'text_area': 'Name:Text Editor',
            'save_button': 'Name:Save',
            'dont_save_button': 'Name:Don\'t Save',
            'file_menu': 'Name:File',
            'save_as_menu_item': 'Name:Save As...',
            'open_menu_item': 'Name:Open...',
            'file_name_input': 'Name:File name:',
            'save_dialog_save_button': 'Name:Save',
            'open_dialog_open_button': 'Name:Open'
        }

    def _get_desktop_library(self):
        """Get the DesktopLibrary instance from Robot Framework."""
        return BuiltIn().get_library_instance('DesktopLibrary')

    def _get_white_library(self):
        """Get the WhiteLibrary instance from Robot Framework."""
        return BuiltIn().get_library_instance('WhiteLibrary')

    @keyword
    def launch_notepad(self):
        """
        Launch Notepad application.

        Example:
            | Launch Notepad |
        """
        desktop = self._get_desktop_library()
        desktop.launch_application('notepad.exe')
        return True

    @keyword
    def verify_notepad_opened(self):
        """
        Verify that Notepad has been opened.

        Example:
            | Verify Notepad Opened |
        """
        desktop = self._get_desktop_library()
        desktop.attach_window_by_title('Untitled - Notepad')
        desktop.verify_element_exists(self.selectors['text_area'])
        return True

    @keyword
    def type_text(self, text):
        """
        Type text into Notepad.

        Args:
            text (str): Text to type

        Example:
            | Type Text | Hello, World! |
        """
        desktop = self._get_desktop_library()
        desktop.input_text_to_desktop_element(self.selectors['text_area'], text, 'Name')
        return True

    @keyword
    def get_text(self):
        """
        Get text from Notepad.

        Returns:
            str: Text from Notepad

        Example:
            | ${text} = | Get Text |
        """
        white = self._get_white_library()
        return white.get_text(self.selectors['text_area'], 'Name')

    @keyword
    def save_file(self, file_path):
        """
        Save the Notepad file to the specified path.

        Args:
            file_path (str): Path to save the file

        Example:
            | Save File | C:\\Temp\\test.txt |
        """
        white = self._get_white_library()
        desktop = self._get_desktop_library()
        
        # Click File menu
        white.click_menu_button(self.selectors['file_menu'])
        
        # Click Save As menu item
        white.click_menu_item(self.selectors['save_as_menu_item'])
        
        # Input file path
        desktop.input_text_to_desktop_element(self.selectors['file_name_input'], file_path, 'Name')
        
        # Click Save button
        desktop.click_desktop_element(self.selectors['save_dialog_save_button'], 'Name')
        
        return True

    @keyword
    def open_file(self, file_path):
        """
        Open a file in Notepad.

        Args:
            file_path (str): Path of the file to open

        Example:
            | Open File | C:\\Temp\\test.txt |
        """
        white = self._get_white_library()
        desktop = self._get_desktop_library()
        
        # Click File menu
        white.click_menu_button(self.selectors['file_menu'])
        
        # Click Open menu item
        white.click_menu_item(self.selectors['open_menu_item'])
        
        # Input file path
        desktop.input_text_to_desktop_element(self.selectors['file_name_input'], file_path, 'Name')
        
        # Click Open button
        desktop.click_desktop_element(self.selectors['open_dialog_open_button'], 'Name')
        
        return True

    @keyword
    def close_notepad(self, save=False):
        """
        Close Notepad.

        Args:
            save (bool, optional): Whether to save changes before closing

        Example:
            | Close Notepad | save=${FALSE} |
        """
        white = self._get_white_library()
        desktop = self._get_desktop_library()
        
        # Send Alt+F4 to close Notepad
        white.send_keys('{Alt}', '{F4}')
        
        # Handle save dialog if it appears
        if desktop.verify_element_exists(self.selectors['save_button'], 'Name', timeout=2):
            if save:
                desktop.click_desktop_element(self.selectors['save_button'], 'Name')
                desktop.click_desktop_element(self.selectors['save_dialog_save_button'], 'Name')
            else:
                desktop.click_desktop_element(self.selectors['dont_save_button'], 'Name')
        
        return True

    @keyword
    def take_notepad_screenshot(self, name="notepad"):
        """
        Take a screenshot of Notepad.

        Args:
            name (str, optional): Name for the screenshot

        Returns:
            str: Path to the screenshot file

        Example:
            | ${screenshot} = | Take Notepad Screenshot | notepad-test |
        """
        desktop = self._get_desktop_library()
        return desktop.take_desktop_screenshot(name) 