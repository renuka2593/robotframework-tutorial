#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Robot Framework library for Browser-specific utilities.
Provides functions for common browser interactions like downloads, element manipulation, and more.
"""

import os
import base64
import time
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn

class BrowserUtilities:
    """Library providing Browser automation utilities for Robot Framework."""

    def __init__(self):
        """Initialize the BrowserUtilities library."""
        self._browser = BuiltIn().get_library_instance('Browser')
        self._builtin = BuiltIn()

    @keyword
    def wait_for_download_from_button(self, button_selector, save_path=None, timeout=None):
        """
        Clicks a button and waits for the download to complete.
        
        Returns download information as a dictionary.
        
        Arguments:
            button_selector: Selector of the button to click
            save_path: Path where to save the file (optional)
            timeout: Maximum time to wait for download (optional)
            
        Example:
            ${download_info}=    Wait For Download From Button    id=download-button
            Log    Downloaded to: ${download_info}[saveAs]
        """
        # Create promise before clicking
        promise = self._browser.promise_to_wait_for_download(save_as=save_path, 
                                                            wait_for_finished=True, 
                                                            download_timeout=timeout)
        
        # Click the button that triggers download
        self._browser.click(button_selector)
        
        # Wait for download to complete
        download_info = self._browser.wait_for(promise)
        return download_info
    
    @keyword
    def verify_download_completed(self, download_info):
        """
        Verifies that a download has completed successfully.
        
        Returns the path to the downloaded file.
        
        Arguments:
            download_info: Download information from wait_for_download_from_button
            
        Example:
            ${file_path}=    Verify Download Completed    ${download_info}
        """
        state = self._browser.get_download_state(download_info)
        self._builtin.should_be_equal(state["state"], "finished")
        return state["saveAs"]
    
    @keyword
    def get_child_element(self, parent_selector, child_relative_selector):
        """
        Returns a reference to a child element using parent as anchor.
        
        Arguments:
            parent_selector: Selector for the parent element
            child_relative_selector: Selector for the child, relative to parent
            
        Example:
            ${child}=    Get Child Element    [data-testid="parent"]    input.email
        """
        parent = self._browser.get_element(parent_selector)
        child = self._browser.get_element(f"{parent} >> {child_relative_selector}")
        return child
    
    @keyword
    def fill_child_input(self, parent_selector, child_selector, text):
        """
        Fills text into a child input field within a parent element.
        
        Arguments:
            parent_selector: Selector for the parent element
            child_selector: Selector for the child input, relative to parent
            text: Text to fill into the input
            
        Example:
            Fill Child Input    [data-testid="user-form"]    input.email    user@example.com
        """
        selector = f"{parent_selector} >> {child_selector}"
        self._browser.fill_text(selector, text)
        
    @keyword
    def click_child_button(self, parent_selector, button_text=None, button_selector=None):
        """
        Clicks a button within a parent element.
        
        Arguments:
            parent_selector: Selector for the parent element
            button_text: Text of the button to click (optional)
            button_selector: Selector for the button, relative to parent (optional)
            
        Example:
            Click Child Button    [data-testid="dialog"]    Submit
            Click Child Button    [data-testid="form"]    button_selector=.submit-btn
        """
        if button_text:
            selector = f"{parent_selector} >> button:has-text(\"{button_text}\")"
        elif button_selector:
            selector = f"{parent_selector} >> {button_selector}"
        else:
            raise ValueError("Either button_text or button_selector must be provided")
        
        self._browser.click(selector)
        
    @keyword
    def wait_for_child_element(self, parent_selector, child_selector, state="visible", timeout=None):
        """
        Waits for a child element to reach a specific state.
        
        Arguments:
            parent_selector: Selector for the parent element
            child_selector: Selector for the child element, relative to parent
            state: Element state to wait for (default: visible)
            timeout: Maximum time to wait
            
        Example:
            Wait For Child Element    [data-testid="container"]    .loading-indicator    state=detached
        """
        selector = f"{parent_selector} >> {child_selector}"
        self._browser.wait_for_elements_state(selector, state, timeout=timeout)
        
    @keyword
    def scroll_to_child_element(self, parent_selector, child_selector):
        """
        Scrolls to a child element within a parent.
        
        Arguments:
            parent_selector: Selector for the parent element
            child_selector: Selector for the child element, relative to parent
            
        Example:
            Scroll To Child Element    .results-container    .item-54
        """
        selector = f"{parent_selector} >> {child_selector}"
        self._browser.scroll_to_element(selector)
    
    @keyword
    def is_child_element_visible(self, parent_selector, child_selector):
        """
        Checks if a child element is visible within a parent.
        
        Returns True if visible, False otherwise.
        
        Arguments:
            parent_selector: Selector for the parent element
            child_selector: Selector for the child element, relative to parent
            
        Example:
            ${visible}=    Is Child Element Visible    .form    .success-message
        """
        selector = f"{parent_selector} >> {child_selector}"
        states = self._browser.get_element_states(selector)
        return "visible" in states 