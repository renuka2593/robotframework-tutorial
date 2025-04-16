#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YAML reader utility for Robot Framework.
This module helps with reading YAML configuration files for test data.
"""

import os
import yaml
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

def get_yaml_data(file_path):
    """
    Read and parse a YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Dictionary containing the parsed YAML data
    """
    try:
        # Handle paths relative to the resources directory
        if not os.path.isabs(file_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, file_path)
            
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except Exception as e:
        logger.error(f"Error reading YAML file {file_path}: {str(e)}")
        return {}

def get_test_data(yaml_path="variables/test_data.yaml"):
    """
    Get test data from a YAML file.
    
    Args:
        yaml_path: Path to the YAML file (relative to resources directory)
        
    Returns:
        Dictionary containing the test data
    """
    return get_yaml_data(yaml_path)

def get_user_credentials(user_key, yaml_path="variables/test_data.yaml"):
    """
    Get user credentials from the test data.
    
    Args:
        user_key: Key of the user (e.g., standard_user, admin_user)
        yaml_path: Path to the YAML file
        
    Returns:
        Dictionary containing the user credentials
    """
    data = get_test_data(yaml_path)
    return data.get('users', {}).get(user_key, {})

def get_product_data(product_key, yaml_path="variables/test_data.yaml"):
    """
    Get product data from the test data.
    
    Args:
        product_key: Key of the product (e.g., product1, product2)
        yaml_path: Path to the YAML file
        
    Returns:
        Dictionary containing the product data
    """
    data = get_test_data(yaml_path)
    return data.get('products', {}).get(product_key, {})

def get_api_test_data(key, yaml_path="variables/test_data.yaml"):
    """
    Get API test data from the test data.
    
    Args:
        key: Key of the API test data (e.g., valid_order, invalid_order)
        yaml_path: Path to the YAML file
        
    Returns:
        Dictionary containing the API test data
    """
    data = get_test_data(yaml_path)
    return data.get('api_test_data', {}).get(key, {})

def get_environment_settings(yaml_path="variables/test_data.yaml"):
    """
    Get environment settings from the test data.
    
    Args:
        yaml_path: Path to the YAML file
        
    Returns:
        Dictionary containing the environment settings
    """
    data = get_test_data(yaml_path)
    return data.get('environment', {}) 