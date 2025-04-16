#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A simplified Robot Framework library for loading and accessing environment variables from .env files.
"""

import os
from typing import Optional, Dict
from robot.api import logger
from dotenv import load_dotenv, find_dotenv, dotenv_values


class EnvLibrary:
    """EnvLibrary for handling .env files in Robot Framework.

    This library provides simple keywords to load environment variables from .env files
    and get environment variable values.

    Examples:
        | Load Env File |             | # Loads default .env file in the project root |
        | Get Env       | BROWSER     | # Returns value of BROWSER env variable       |
        | Get All Envs  |             | # Returns all environment variables           |
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'
    ROBOT_LIBRARY_DOC_FORMAT = 'reST'

    def __init__(self):
        self.env_file = None

    def load_env_file(self) -> bool:
        """Load environment variables from the default .env file.

        Returns:
            bool: True if the file was loaded successfully, False otherwise.
        """
        try:
            self.env_file = find_dotenv()
            result = load_dotenv(dotenv_path=self.env_file, override=True)
                
            if result:
                logger.info(f"Successfully loaded environment variables from {self.env_file}")
            else:
                logger.warn(f"No environment variables loaded from {self.env_file or '.env'}")
            
            return result
        except Exception as e:
            logger.error(f"Error loading .env file: {str(e)}")
            return False

    def get_env(self, variable_name: str, default: str = None) -> Optional[str]:
        """Get the value of an environment variable.

        Args:
            variable_name: Name of the environment variable.
            default: Default value to return if the variable is not set.

        Returns:
            str: Value of the environment variable or default if not set.
        """
        value = os.environ.get(variable_name, default)
        if value is None:
            logger.info(f"Environment variable '{variable_name}' is not set")
        return value

    def get_all_envs(self) -> Dict[str, str]:
        """Get all environment variables from the loaded .env file.

        Returns:
            dict: Dictionary of all variables in the .env file.
        """
        if not self.env_file:
            logger.warn("No .env file loaded yet")
            return {}
        
        try:
            return dotenv_values(self.env_file)
        except Exception as e:
            logger.error(f"Error reading .env file: {str(e)}")
            return {} 