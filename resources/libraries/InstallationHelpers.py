#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Robot Framework library for handling Windows application installations.
Provides functions for both pywinauto and FlaUI automation.
"""

import os
import sys
import time
import logging
import subprocess
from typing import Optional, Dict, Any, Tuple, List, Union
from robot.api.deco import keyword

# pywinauto imports
import pywinauto
from pywinauto import Application, Desktop
from pywinauto.application import ProcessNotFoundError
from pywinauto.timings import TimeoutError
from pywinauto.findwindows import ElementNotFoundError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class InstallationHelpers:
    """
    Library for handling Windows application installations using PyWinAuto and FlaUI.
    Provides keywords for installing and uninstalling Windows applications.
    """
    
    # Constants
    RETRY_INTERVAL = 1  # Time between retries (in seconds)
    MAX_RETRIES = 5  # Maximum number of retries for operations
    
    def __init__(self, default_timeout=60):
        """
        Initialize the InstallationHelpers library.
        
        Args:
            default_timeout (int): Default timeout for operations in seconds
        """
        self.default_timeout = default_timeout
    
    class InstallerError(Exception):
        """Base exception for installer errors."""
        pass

    class TimeoutInstallerError(InstallerError):
        """Exception raised when an operation times out."""
        pass

    class InstallationFailedError(InstallerError):
        """Exception raised when installation fails."""
        pass
    
    @keyword
    def is_process_running(self, process_name: str) -> bool:
        """
        Check if a process is running by name.
        
        Args:
            process_name (str): Name of the process to check (e.g., 'setup.exe')
            
        Returns:
            bool: True if the process is running, False otherwise
            
        Example:
            | ${running}= | Is Process Running | notepad.exe |
            | Run Keyword If | ${running} | Log | Notepad is running |
        """
        try:
            # Use pywinauto to check if the process is running
            Application().connect(path=process_name, timeout=1)
            return True
        except (ProcessNotFoundError, TimeoutError):
            return False
    
    @keyword
    def get_installer_type(self, installer_path: str) -> str:
        """
        Determine the type of installer based on file extension.
        
        Args:
            installer_path (str): Path to the installer file
            
        Returns:
            str: Type of installer ('msi', 'exe', 'appx', or 'unknown')
            
        Example:
            | ${type}= | Get Installer Type | C:\\setup.exe |
            | Run Keyword If | '${type}' == 'exe' | Log | This is an EXE installer |
        """
        ext = os.path.splitext(installer_path)[1].lower()
        if ext == '.msi':
            return 'msi'
        elif ext == '.exe':
            return 'exe'
        elif ext == '.appx' or ext == '.msix':
            return 'appx'
        else:
            return 'unknown'
    
    @keyword
    def wait_for_window(self, title_regex: str, timeout: Optional[int] = None) -> pywinauto.WindowSpecification:
        """
        Wait for a window to appear based on title regex.
        
        Args:
            title_regex (str): Regular expression for the window title
            timeout (int, optional): Maximum time to wait in seconds
            
        Returns:
            pywinauto.WindowSpecification: Window specification object
            
        Raises:
            TimeoutInstallerError: If the window doesn't appear within the timeout
            
        Example:
            | ${window}= | Wait For Window | Installation Complete | timeout=30 |
            | Log | Found window with title: ${window.window_text()} |
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        desktop = Desktop(backend='uia')
        
        while time.time() - start_time < timeout:
            try:
                window = desktop.window(title_re=title_regex)
                if window.exists():
                    return window
            except ElementNotFoundError:
                pass
            time.sleep(self.RETRY_INTERVAL)
        
        raise self.TimeoutInstallerError(f"Window with title matching '{title_regex}' did not appear within {timeout} seconds")
    
    def _run_installer(self, installer_path: str, arguments: Optional[str] = None, 
                      timeout: Optional[int] = None, wait_for_completion: bool = True) -> subprocess.Popen:
        """
        Run an installer process.
        
        Args:
            installer_path (str): Path to the installer file
            arguments (str, optional): Command-line arguments for the installer
            timeout (int, optional): Maximum time to wait for installer to complete
            wait_for_completion (bool): Whether to wait for the installer to complete
            
        Returns:
            subprocess.Popen: Process object
            
        Raises:
            FileNotFoundError: If the installer file doesn't exist
            InstallationFailedError: If installation fails
        """
        timeout = timeout or self.default_timeout
        
        if not os.path.exists(installer_path):
            raise FileNotFoundError(f"Installer not found: {installer_path}")
        
        logger.info(f"Starting installer: {installer_path}")
        
        cmd = [installer_path]
        if arguments:
            cmd.extend(arguments.split())
        
        # Start the installer process
        try:
            process = subprocess.Popen(cmd, shell=True)
            
            if wait_for_completion:
                logger.info(f"Waiting for installer to complete (timeout: {timeout}s)")
                start_time = time.time()
                
                while process.poll() is None:
                    if time.time() - start_time > timeout:
                        process.kill()
                        raise self.TimeoutInstallerError(f"Installation timed out after {timeout} seconds")
                    time.sleep(self.RETRY_INTERVAL)
                
                exit_code = process.returncode
                logger.info(f"Installer completed with exit code: {exit_code}")
                
                if exit_code != 0:
                    raise self.InstallationFailedError(f"Installation failed with exit code: {exit_code}")
            
            return process
        
        except Exception as e:
            logger.error(f"Error during installation: {str(e)}")
            raise self.InstallationFailedError(f"Installation failed: {str(e)}")
    
    def _handle_next_button(self, app: pywinauto.Application, 
                           button_names: List[str] = ['Next', 'Next >', '&Next', '&Next >', 'Continue', '&Continue'],
                           timeout: Optional[int] = None) -> bool:
        """
        Find and click the Next button in an installer dialog.
        
        Args:
            app (pywinauto.Application): Application instance
            button_names (List[str]): Possible names for the Next button
            timeout (int, optional): Maximum time to wait for the button
            
        Returns:
            bool: True if button was found and clicked, False otherwise
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Try to find the main window
                main_window = app.top_window()
                
                # Look for buttons with names in the provided list
                for button_name in button_names:
                    try:
                        button = main_window.child_window(title=button_name, control_type="Button")
                        if button.exists():
                            logger.info(f"Clicking button: {button_name}")
                            button.click()
                            return True
                    except (ElementNotFoundError, RuntimeError):
                        continue
            except Exception as e:
                logger.debug(f"Error finding Next button: {str(e)}")
            
            time.sleep(self.RETRY_INTERVAL)
        
        return False
    
    def _handle_license_agreement(self, app: pywinauto.Application,
                                 accept_button_names: List[str] = ['I &Agree', 'I &accept', 'Accept', '&Accept', 'Yes'],
                                 timeout: Optional[int] = None) -> bool:
        """
        Handle license agreement by accepting it.
        
        Args:
            app (pywinauto.Application): Application instance
            accept_button_names (List[str]): Possible names for the accept button
            timeout (int, optional): Maximum time to wait for the button
            
        Returns:
            bool: True if license was accepted, False otherwise
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                main_window = app.top_window()
                
                # First try to find and check any checkbox
                try:
                    checkbox = main_window.child_window(control_type="CheckBox")
                    if checkbox.exists() and not checkbox.is_checked():
                        logger.info("Checking license agreement checkbox")
                        checkbox.check()
                except (ElementNotFoundError, RuntimeError):
                    pass
                
                # Then look for accept button
                for button_name in accept_button_names:
                    try:
                        button = main_window.child_window(title=button_name, control_type="Button")
                        if button.exists():
                            logger.info(f"Clicking license agreement button: {button_name}")
                            button.click()
                            return True
                    except (ElementNotFoundError, RuntimeError):
                        continue
            except Exception as e:
                logger.debug(f"Error handling license agreement: {str(e)}")
            
            time.sleep(self.RETRY_INTERVAL)
        
        return False
    
    def _handle_install_location(self, app: pywinauto.Application,
                                install_path: Optional[str] = None,
                                timeout: Optional[int] = None) -> bool:
        """
        Handle installation location dialog.
        
        Args:
            app (pywinauto.Application): Application instance
            install_path (str, optional): Custom installation path
            timeout (int, optional): Maximum time to wait
            
        Returns:
            bool: True if successful, False otherwise
        """
        timeout = timeout or self.default_timeout
        
        if not install_path:
            # If no custom path, just click Next
            return self._handle_next_button(app, timeout=timeout)
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                main_window = app.top_window()
                
                # Look for edit control where path can be entered
                edit = main_window.child_window(control_type="Edit")
                if edit.exists():
                    logger.info(f"Setting installation path: {install_path}")
                    edit.set_text(install_path)
                    
                    # Click Next after setting the path
                    return self._handle_next_button(app, timeout=timeout)
            except Exception as e:
                logger.debug(f"Error handling install location: {str(e)}")
            
            time.sleep(self.RETRY_INTERVAL)
        
        return False
    
    def _handle_finish_button(self, app: pywinauto.Application,
                             button_names: List[str] = ['Finish', '&Finish', 'Close', '&Close', 'Done', '&Done'],
                             timeout: Optional[int] = None) -> bool:
        """
        Find and click the Finish button in an installer dialog.
        
        Args:
            app (pywinauto.Application): Application instance
            button_names (List[str]): Possible names for the Finish button
            timeout (int, optional): Maximum time to wait for the button
            
        Returns:
            bool: True if button was found and clicked, False otherwise
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                main_window = app.top_window()
                
                # Try to uncheck "Launch application" checkbox if present
                try:
                    launch_checkbox = main_window.child_window(title_re='.*[Ll]aunch.*', control_type="CheckBox")
                    if launch_checkbox.exists() and launch_checkbox.is_checked():
                        logger.info("Unchecking 'Launch application' checkbox")
                        launch_checkbox.uncheck()
                except (ElementNotFoundError, RuntimeError):
                    pass
                
                # Look for finish button
                for button_name in button_names:
                    try:
                        button = main_window.child_window(title=button_name, control_type="Button")
                        if button.exists():
                            logger.info(f"Clicking finish button: {button_name}")
                            button.click()
                            return True
                    except (ElementNotFoundError, RuntimeError):
                        continue
            except Exception as e:
                logger.debug(f"Error finding Finish button: {str(e)}")
            
            time.sleep(self.RETRY_INTERVAL)
        
        return False
    
    @keyword
    def run_silent_installation(self, installer_path: str, silent_args: Optional[str] = None, 
                               timeout: Optional[int] = None) -> int:
        """
        Run a silent installation.
        
        Args:
            installer_path (str): Path to the installer
            silent_args (str, optional): Silent installation arguments
            timeout (int, optional): Maximum time to wait for installation
            
        Returns:
            int: Exit code
            
        Raises:
            InstallationFailedError: If installation fails
            
        Example:
            | ${result}= | Run Silent Installation | C:\\setup.exe | /S /v/qn | timeout=120 |
            | Should Be Equal As Integers | ${result} | 0 | Installation failed |
        """
        timeout = timeout or self.default_timeout
        installer_type = self.get_installer_type(installer_path)
        
        if silent_args is None:
            # Default silent arguments based on installer type
            if installer_type == 'msi':
                silent_args = '/quiet /norestart'
            elif installer_type == 'exe':
                silent_args = '/S /v/qn'  # Common for many installers, but not universal
            elif installer_type == 'appx':
                silent_args = ''
        
        logger.info(f"Running silent installation: {installer_path} {silent_args}")
        
        cmd = [installer_path]
        if silent_args:
            cmd.extend(silent_args.split())
        
        try:
            process = subprocess.Popen(cmd, shell=True)
            
            logger.info(f"Waiting for silent installation to complete (timeout: {timeout}s)")
            start_time = time.time()
            
            while process.poll() is None:
                if time.time() - start_time > timeout:
                    process.kill()
                    raise self.TimeoutInstallerError(f"Silent installation timed out after {timeout} seconds")
                time.sleep(self.RETRY_INTERVAL)
            
            exit_code = process.returncode
            logger.info(f"Silent installation completed with exit code: {exit_code}")
            
            if exit_code != 0:
                raise self.InstallationFailedError(f"Silent installation failed with exit code: {exit_code}")
            
            return exit_code
        
        except Exception as e:
            logger.error(f"Error during silent installation: {str(e)}")
            raise self.InstallationFailedError(f"Silent installation failed: {str(e)}")
    
    @keyword
    def install_application(self, installer_path: str, silent: bool = False, silent_args: Optional[str] = None,
                           custom_install_path: Optional[str] = None, timeout: Optional[int] = None,
                           handle_reboot: bool = False) -> bool:
        """
        Install an application using PyWinAuto.
        
        Args:
            installer_path (str): Path to the installer
            silent (bool): Whether to perform a silent installation
            silent_args (str, optional): Arguments for silent installation
            custom_install_path (str, optional): Custom installation path
            timeout (int, optional): Maximum time to wait for installation
            handle_reboot (bool): Whether to handle system reboot if required
            
        Returns:
            bool: True if installation succeeded
            
        Raises:
            InstallationFailedError: If installation fails
            
        Example:
            | ${result}= | Install Application | C:\\setup.exe | silent=${TRUE} |
            | Should Be True | ${result} | Installation failed |
        """
        timeout = timeout or self.default_timeout
        
        if not os.path.exists(installer_path):
            raise FileNotFoundError(f"Installer not found: {installer_path}")
        
        # Run silent installation if requested
        if silent:
            exit_code = self.run_silent_installation(installer_path, silent_args, timeout)
            return exit_code == 0
        
        # Interactive installation
        installer_process = self._run_installer(installer_path, wait_for_completion=False)
        
        try:
            # Wait for installer to initialize
            time.sleep(2)
            
            # Connect to the application
            app = Application(backend='uia').connect(process=installer_process.pid)
            
            # Handle common installer dialogs
            steps_completed = 0
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                main_window = app.top_window()
                window_title = main_window.window_text()
                
                logger.info(f"Current window: {window_title}")
                
                # Handle license agreement
                if self._handle_license_agreement(app):
                    steps_completed += 1
                    time.sleep(1)
                    continue
                
                # Handle install location
                if self._handle_install_location(app, custom_install_path):
                    steps_completed += 1
                    time.sleep(1)
                    continue
                
                # Handle next button
                if self._handle_next_button(app):
                    steps_completed += 1
                    time.sleep(1)
                    continue
                
                # Handle finish button
                if self._handle_finish_button(app):
                    logger.info("Installation completed successfully")
                    return True
                
                # Check if installation is still running
                if installer_process.poll() is not None:
                    exit_code = installer_process.returncode
                    if exit_code == 0:
                        logger.info("Installation process completed successfully")
                        return True
                    else:
                        raise self.InstallationFailedError(f"Installation failed with exit code: {exit_code}")
                
                time.sleep(self.RETRY_INTERVAL)
            
            # If we get here, timeout occurred
            if installer_process.poll() is None:
                installer_process.kill()
            raise self.TimeoutInstallerError(f"Installation timed out after {timeout} seconds")
        
        except Exception as e:
            logger.error(f"Error during installation: {str(e)}")
            # Try to terminate the installer process if it's still running
            if installer_process.poll() is None:
                installer_process.kill()
            raise self.InstallationFailedError(f"Installation failed: {str(e)}")
    
    @keyword
    def uninstall_application(self, app_name: str, uninstaller_path: Optional[str] = None,
                             silent: bool = False, timeout: Optional[int] = None) -> bool:
        """
        Uninstall an application using PyWinAuto.
        
        Args:
            app_name (str): Name of the application to uninstall
            uninstaller_path (str, optional): Path to the uninstaller executable
            silent (bool): Whether to perform a silent uninstallation
            timeout (int, optional): Maximum time to wait for uninstallation
            
        Returns:
            bool: True if uninstallation succeeded
            
        Raises:
            InstallationFailedError: If uninstallation fails
            
        Example:
            | ${result}= | Uninstall Application | My Application | silent=${TRUE} |
            | Should Be True | ${result} | Uninstallation failed |
        """
        timeout = timeout or self.default_timeout
        logger.info(f"Uninstalling application: {app_name}")
        
        # If uninstaller path is provided, use it directly
        if uninstaller_path and os.path.exists(uninstaller_path):
            return self.install_application(
                uninstaller_path,
                silent=silent,
                timeout=timeout
            )
        
        # Otherwise, try to uninstall through Control Panel
        try:
            # Open Control Panel > Programs and Features
            subprocess.run('control appwiz.cpl', shell=True)
            time.sleep(2)
            
            # Connect to Programs and Features window
            app = Application(backend='uia').connect(title='Programs and Features')
            programs_window = app.window(title='Programs and Features')
            
            # Find the application in the list
            programs_list = programs_window.child_window(control_type="List")
            app_item = None
            
            for item in programs_list.items():
                if app_name.lower() in item.texts()[0].lower():
                    app_item = item
                    break
            
            if not app_item:
                logger.error(f"Application '{app_name}' not found in Programs and Features")
                return False
            
            # Select the application and click Uninstall
            app_item.select()
            uninstall_button = programs_window.child_window(title='Uninstall', control_type="Button")
            uninstall_button.click()
            
            # Handle confirm dialog if it appears
            try:
                confirm_dialog = app.window(title_re='.*[Cc]onfirm.*')
                if confirm_dialog.exists():
                    yes_button = confirm_dialog.child_window(title='Yes', control_type="Button")
                    yes_button.click()
            except ElementNotFoundError:
                pass
            
            # Handle the uninstaller
            start_time = time.time()
            uninstall_app = None
            
            # Try to connect to the uninstaller application
            while time.time() - start_time < timeout:
                try:
                    # Look for windows with title containing 'uninstall' or the app name
                    desktop = Desktop(backend='uia')
                    windows = desktop.windows()
                    
                    for window in windows:
                        window_title = window.window_text().lower()
                        if ('uninstall' in window_title or app_name.lower() in window_title) and window.is_visible():
                            uninstall_app = Application(backend='uia').connect(handle=window.handle)
                            break
                    
                    if uninstall_app:
                        break
                except Exception:
                    pass
                
                time.sleep(self.RETRY_INTERVAL)
            
            if not uninstall_app:
                logger.warning("Could not find uninstaller window")
                return False
            
            # Handle uninstaller dialogs (similar to installer)
            while time.time() - start_time < timeout:
                try:
                    main_window = uninstall_app.top_window()
                    
                    # Try various buttons
                    if self._handle_next_button(uninstall_app) or \
                       self._handle_finish_button(uninstall_app):
                        time.sleep(1)
                        continue
                    
                    # Check if uninstallation is complete
                    if not main_window.exists() or not main_window.is_visible():
                        logger.info("Uninstallation completed successfully")
                        return True
                except Exception:
                    # Window might have closed
                    if not any(w for w in Desktop(backend='uia').windows() if app_name.lower() in w.window_text().lower()):
                        logger.info("No more uninstaller windows found, uninstallation likely completed")
                        return True
                
                time.sleep(self.RETRY_INTERVAL)
            
            raise self.TimeoutInstallerError(f"Uninstallation timed out after {timeout} seconds")
        
        except Exception as e:
            logger.error(f"Error during uninstallation: {str(e)}")
            raise self.InstallationFailedError(f"Uninstallation failed: {str(e)}")
        finally:
            # Try to close Programs and Features window if it's still open
            try:
                Desktop(backend='uia').window(title='Programs and Features').close()
            except Exception:
                pass
    
    @keyword
    def install_msi_application(self, msi_path: str, properties: str = "", timeout: Optional[int] = None) -> int:
        """
        Install an MSI application silently.
        
        Args:
            msi_path (str): Path to the MSI file
            properties (str): MSI properties to set during installation
            timeout (int, optional): Maximum time to wait for installation
            
        Returns:
            int: Exit code
            
        Example:
            | ${result}= | Install MSI Application | C:\\app.msi | INSTALLDIR="C:\\MyApp" ACCEPT_EULA=1 |
            | Should Be Equal As Integers | ${result} | 0 | MSI installation failed |
        """
        timeout = timeout or self.default_timeout
        
        # Validate MSI path
        if not os.path.exists(msi_path):
            raise FileNotFoundError(f"MSI file not found: {msi_path}")
        
        # Build silent arguments
        silent_args = '/quiet /norestart'
        
        # Add custom properties if provided
        if properties:
            silent_args = f"{silent_args} {properties}"
        
        # Call the silent installation function
        return self.run_silent_installation(msi_path, silent_args, timeout)
    
    @keyword
    def install_exe_application(self, exe_path: str, silent: bool = True, silent_args: Optional[str] = None,
                              custom_install_path: Optional[str] = None, timeout: Optional[int] = None) -> bool:
        """
        Install an EXE application.
        
        Args:
            exe_path (str): Path to the EXE file
            silent (bool): Whether to perform a silent installation
            silent_args (str, optional): Arguments for silent installation
            custom_install_path (str, optional): Custom installation path
            timeout (int, optional): Maximum time to wait for installation
            
        Returns:
            bool: True if installation succeeded
            
        Example:
            | ${result}= | Install EXE Application | C:\\setup.exe | silent=${TRUE} | silent_args=/S |
            | Should Be True | ${result} | EXE installation failed |
        """
        timeout = timeout or self.default_timeout
        
        # Validate EXE path
        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"EXE file not found: {exe_path}")
        
        # Default silent args for common installers if not provided and installation is silent
        if silent and silent_args is None:
            installer_type = self.get_installer_type(exe_path)
            if installer_type == 'exe':
                silent_args = '/S'  # NSIS installers
        
        # Call the installation function
        return self.install_application(exe_path, silent, silent_args, custom_install_path, timeout) 