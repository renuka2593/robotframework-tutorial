#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration library for Robot Framework test automation.
Handles environment-specific configurations and test settings.
"""

import os
from typing import Dict, Any
from robot.api.deco import keyword

class Config:
    """Configuration library for managing test environment settings."""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        """Initialize Config library with default settings."""
        self.env = os.getenv('TEST_ENV', 'staging')
        self.browser = os.getenv('BROWSER', 'chromium')
        self.headless = os.getenv('HEADLESS', 'True').lower() == 'true'
        
        # Environment URLs
        self._urls = {
            'staging': 'https://www.saucedemo.com',
            'prod': 'https://www.saucedemo.com'
        }
        
        # Test users
        self._users = {
            'standard': {
                'username': 'standard_user',
                'password': 'secret_sauce'
            },
            'locked': {
                'username': 'locked_out_user',
                'password': 'secret_sauce'
            },
            'problem': {
                'username': 'problem_user',
                'password': 'secret_sauce'
            }
        }
    
    @keyword
    def get_base_url(self) -> str:
        """
        Get the base URL for the current environment.
        
        Returns:
            str: Base URL for the current environment
            
        Example:
            ${BASE_URL}=    Get Base URL
        """
        return self._urls.get(self.env, self._urls['staging'])
    
    @keyword
    def get_user_credentials(self, user_type: str = 'standard') -> Dict[str, str]:
        """
        Get user credentials for the specified user type.
        
        Args:
            user_type: Type of user (standard, locked, problem)
            
        Returns:
            dict: Dictionary containing username and password
            
        Example:
            ${credentials}=    Get User Credentials    standard
            Log    Username: ${credentials}[username]
        """
        return self._users.get(user_type, self._users['standard'])
    
    @keyword
    def get_browser_config(self) -> Dict[str, Any]:
        """
        Get browser configuration for test execution.
        
        Returns:
            dict: Browser configuration settings
            
        Example:
            ${config}=    Get Browser Config
            New Browser    ${config}[browser]    headless=${config}[headless]
        """
        return {
            'browser': self.browser,
            'headless': self.headless
        }
    
    @keyword
    def set_test_environment(self, env: str) -> None:
        """
        Set the test environment.
        
        Args:
            env: Environment name (staging, prod)
            
        Example:
            Set Test Environment    prod
        """
        if env in self._urls:
            self.env = env
        else:
            raise ValueError(f"Invalid environment: {env}. Valid options: {', '.join(self._urls.keys())}") 