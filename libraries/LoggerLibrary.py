#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Robot Framework library for enhanced logging, assertions and screenshots.
"""

import os
import time
import base64
from datetime import datetime
from robot.api import logger
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

class LoggerLibrary:
    """
    Library providing enhanced logging with assertion capabilities for Robot Framework.
    Can embed screenshots in logs and handle various assertion types.
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    
    def __init__(self, screenshot_directory=None, capture_screenshot_on_fail=True):
        """
        Initialize the LoggerLibrary.
        
        Arguments:
            screenshot_directory: Directory to save screenshots (defaults to ${OUTPUT_DIR}/screenshots)
            capture_screenshot_on_fail: Whether to capture a screenshot on assertion failures
        """
        self._builtin = BuiltIn()
        self._capture_screenshot_on_fail = capture_screenshot_on_fail
        
        if screenshot_directory:
            self._screenshot_dir = screenshot_directory
        else:
            output_dir = self._builtin.get_variable_value("${OUTPUT_DIR}")
            self._screenshot_dir = os.path.join(output_dir, "screenshots")
            
        os.makedirs(self._screenshot_dir, exist_ok=True)
    
    @keyword
    def log_info(self, message):
        """
        Logs a message at INFO level.
        
        Arguments:
            message: Message to log
            
        Example:
            Log Info    Starting test execution
        """
        logger.info(message)
    
    @keyword
    def log_warning(self, message):
        """
        Logs a message at WARN level.
        
        Arguments:
            message: Warning message to log
            
        Example:
            Log Warning    API response time exceeds threshold
        """
        logger.warn(message)
    
    @keyword
    def log_error(self, message):
        """
        Logs a message at ERROR level.
        
        Arguments:
            message: Error message to log
            
        Example:
            Log Error    Failed to connect to database
        """
        logger.error(message)
        
    @keyword
    def capture_and_embed_screenshot(self, filename=None):
        """
        Captures a screenshot and embeds it in the log.
        
        Returns the path to the saved screenshot.
        
        Arguments:
            filename: Optional filename for the screenshot
            
        Example:
            ${path}=    Capture And Embed Screenshot    login_screen
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            filename = f"screenshot_{timestamp}"
            
        # Get Browser library instance
        browser = BuiltIn().get_library_instance('Browser')
        
        # Take screenshot with Browser library
        fullpath = os.path.join(self._screenshot_dir, f"{filename}.png")
        browser.take_screenshot(filename=fullpath)
        
        # Embed in log
        if os.path.exists(fullpath):
            with open(fullpath, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                logger.info(
                    f'<img src="data:image/png;base64,{encoded_string}" width="800px"/>',
                    html=True
                )
            return fullpath
        else:
            logger.warn(f"Failed to capture screenshot: {fullpath}")
            return None
    
    @keyword
    def assert_equal(self, actual, expected, message=None, capture_screenshot=None):
        """
        Asserts that two values are equal.
        
        Arguments:
            actual: Actual value
            expected: Expected value
            message: Custom failure message
            capture_screenshot: Whether to capture a screenshot on failure
            
        Example:
            Assert Equal    ${count}    5    User count should be 5
        """
        capture = self._capture_screenshot_on_fail if capture_screenshot is None else capture_screenshot
        
        try:
            self._builtin.should_be_equal(actual, expected, message)
        except AssertionError as e:
            if capture:
                self.capture_and_embed_screenshot(f"assertion_failure_{int(time.time())}")
            raise e
    
    @keyword
    def assert_contains(self, actual, expected, message=None, capture_screenshot=None):
        """
        Asserts that a value contains the expected substring or item.
        
        Arguments:
            actual: Actual value (string or list)
            expected: Expected substring or item
            message: Custom failure message
            capture_screenshot: Whether to capture a screenshot on failure
            
        Example:
            Assert Contains    ${response_text}    success    Response should indicate success
        """
        capture = self._capture_screenshot_on_fail if capture_screenshot is None else capture_screenshot
        
        try:
            self._builtin.should_contain(actual, expected, message)
        except AssertionError as e:
            if capture:
                self.capture_and_embed_screenshot(f"assertion_failure_{int(time.time())}")
            raise e
            
    @keyword
    def assert_true(self, condition, message=None, capture_screenshot=None):
        """
        Asserts that a condition is true.
        
        Arguments:
            condition: Condition to check
            message: Custom failure message
            capture_screenshot: Whether to capture a screenshot on failure
            
        Example:
            Assert True    ${status} == 200    API should return success status
        """
        capture = self._capture_screenshot_on_fail if capture_screenshot is None else capture_screenshot
        
        try:
            self._builtin.should_be_true(condition, message)
        except AssertionError as e:
            if capture:
                self.capture_and_embed_screenshot(f"assertion_failure_{int(time.time())}")
            raise e
            
    @keyword
    def log_and_fail(self, message, capture_screenshot=True):
        """
        Logs an error message, optionally captures a screenshot, and fails the test.
        
        Arguments:
            message: Error message
            capture_screenshot: Whether to capture a screenshot
            
        Example:
            Log And Fail    Critical error: Database connection lost
        """
        self.log_error(message)
        
        if capture_screenshot:
            self.capture_and_embed_screenshot(f"failure_{int(time.time())}")
            
        self._builtin.fail(message) 