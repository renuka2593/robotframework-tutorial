#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Library for enhanced logging and assertions in Robot Framework."""

import os
from datetime import datetime
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.api.deco import keyword

class LoggerLibrary:
    """Library for enhanced logging and assertions with screenshot capabilities."""

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.builtin = BuiltIn()
        self.browser = None
        self.screenshot_dir = "screenshots"

    def _get_browser(self):
        """Get the Browser library instance."""
        if not self.browser:
            self.browser = self.builtin.get_library_instance('Browser')
        return self.browser

    def _capture_screenshot(self, name=None):
        """Capture a screenshot and return its path."""
        if not name:
            name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        os.makedirs(self.screenshot_dir, exist_ok=True)
        path = os.path.join(self.screenshot_dir, f"{name}.png")
        self._get_browser().take_screenshot(path)
        return path

    @keyword
    def log_info(self, message, take_screenshot=False):
        """Log a message at INFO level with optional screenshot."""
        logger.info(message)
        if take_screenshot:
            path = self._capture_screenshot("info")
            logger.info(f'<img src="{path}" width="800px">', html=True)

    @keyword
    def log_warning(self, message, take_screenshot=True):
        """Log a message at WARN level with optional screenshot."""
        logger.warn(message)
        if take_screenshot:
            path = self._capture_screenshot("warning")
            logger.warn(f'<img src="{path}" width="800px">', html=True)

    @keyword
    def log_error(self, message, take_screenshot=True):
        """Log a message at ERROR level with optional screenshot."""
        logger.error(message)
        if take_screenshot:
            path = self._capture_screenshot("error")
            logger.error(f'<img src="{path}" width="800px">', html=True)

    @keyword
    def capture_and_embed_screenshot(self, name=None):
        """Capture a screenshot and embed it in the log."""
        path = self._capture_screenshot(name)
        logger.info(f'<img src="{path}" width="800px">', html=True)
        return path

    @keyword
    def assert_equal(self, actual, expected, message=None, take_screenshot=True):
        """Assert that two values are equal with optional screenshot on failure."""
        try:
            self.builtin.should_be_equal(actual, expected)
        except AssertionError as e:
            if take_screenshot:
                path = self._capture_screenshot("assert_equal_failed")
                logger.error(f'<img src="{path}" width="800px">', html=True)
            raise AssertionError(message or str(e))

    @keyword
    def assert_not_equal(self, actual, expected, message=None, take_screenshot=True):
        """Assert that two values are not equal with optional screenshot on failure."""
        try:
            self.builtin.should_not_be_equal(actual, expected)
        except AssertionError as e:
            if take_screenshot:
                path = self._capture_screenshot("assert_not_equal_failed")
                logger.error(f'<img src="{path}" width="800px">', html=True)
            raise AssertionError(message or str(e))

    @keyword
    def assert_true(self, condition, message=None, take_screenshot=True):
        """Assert that a condition is true with optional screenshot on failure."""
        try:
            self.builtin.should_be_true(condition)
        except AssertionError as e:
            if take_screenshot:
                path = self._capture_screenshot("assert_true_failed")
                logger.error(f'<img src="{path}" width="800px">', html=True)
            raise AssertionError(message or str(e))

    @keyword
    def assert_false(self, condition, message=None, take_screenshot=True):
        """Assert that a condition is false with optional screenshot on failure."""
        try:
            self.builtin.should_not_be_true(condition)
        except AssertionError as e:
            if take_screenshot:
                path = self._capture_screenshot("assert_false_failed")
                logger.error(f'<img src="{path}" width="800px">', html=True)
            raise AssertionError(message or str(e))

    @keyword
    def assert_contains(self, container, item, message=None, take_screenshot=True):
        """Assert that a container contains an item with optional screenshot on failure."""
        try:
            self.builtin.should_contain(container, item)
        except AssertionError as e:
            if take_screenshot:
                path = self._capture_screenshot("assert_contains_failed")
                logger.error(f'<img src="{path}" width="800px">', html=True)
            raise AssertionError(message or str(e))

    @keyword
    def assert_not_contains(self, container, item, message=None, take_screenshot=True):
        """Assert that a container does not contain an item with optional screenshot on failure."""
        try:
            self.builtin.should_not_contain(container, item)
        except AssertionError as e:
            if take_screenshot:
                path = self._capture_screenshot("assert_not_contains_failed")
                logger.error(f'<img src="{path}" width="800px">', html=True)
            raise AssertionError(message or str(e))

    @keyword
    def assert_matches(self, string, pattern, message=None, take_screenshot=True):
        """Assert that a string matches a pattern with optional screenshot on failure."""
        try:
            self.builtin.should_match(string, pattern)
        except AssertionError as e:
            if take_screenshot:
                path = self._capture_screenshot("assert_matches_failed")
                logger.error(f'<img src="{path}" width="800px">', html=True)
            raise AssertionError(message or str(e))

    @keyword
    def log_and_fail(self, message, take_screenshot=True):
        """Log an error message, optionally take a screenshot, and fail the test."""
        self.log_error(message, take_screenshot)
        self.builtin.fail(message) 