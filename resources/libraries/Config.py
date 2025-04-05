#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Configuration library for Robot Framework tests."""

from robot.api.deco import keyword

class Config:
    """Configuration library for Robot Framework tests."""

    BROWSER_CONFIG = {
        'browser': 'chromium',
        'headless': False
    }

    USER_CREDENTIALS = {
        'standard': {
            'username': 'standard_user',
            'password': 'secret_sauce'
        },
        'locked': {
            'username': 'locked_out_user',
            'password': 'secret_sauce'
        }
    }

    BASE_URL = 'https://www.saucedemo.com'

    @keyword
    def get_browser_config(self):
        """Returns the browser configuration."""
        return self.BROWSER_CONFIG

    @keyword
    def get_user_credentials(self, user_type='standard'):
        """Returns the credentials for the specified user type."""
        if user_type not in self.USER_CREDENTIALS:
            raise ValueError(f"Unknown user type: {user_type}")
        return self.USER_CREDENTIALS[user_type]

    @keyword
    def get_base_url(self):
        """Returns the base URL for the application."""
        return self.BASE_URL 