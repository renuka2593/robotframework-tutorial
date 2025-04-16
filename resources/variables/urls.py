#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
URL configuration for Robot Framework tests.
This file contains URLs for different environments.
"""

def get_variables(env="dev"):
    """
    Return URL variables for the specified environment.
    
    Args:
        env: Environment name (dev, stage, prod)
        
    Returns:
        Dictionary of URLs for the specified environment
    """
    urls = {
        "dev": {
            "BASE_URL": "https://dev.example.com",
            "API_URL": "https://api-dev.example.com/v1",
            "ADMIN_URL": "https://admin-dev.example.com",
        },
        "stage": {
            "BASE_URL": "https://stage.example.com",
            "API_URL": "https://api-stage.example.com/v1",
            "ADMIN_URL": "https://admin-stage.example.com",
        },
        "prod": {
            "BASE_URL": "https://example.com",
            "API_URL": "https://api.example.com/v1",
            "ADMIN_URL": "https://admin.example.com",
        }
    }
    
    # If the environment doesn't exist, default to dev
    selected_env = urls.get(env, urls["dev"])
    
    # Add common endpoints
    selected_env.update({
        "LOGIN_ENDPOINT": "/login",
        "DASHBOARD_ENDPOINT": "/dashboard",
        "PRODUCTS_ENDPOINT": "/products",
        "USERS_ENDPOINT": "/users",
        "ORDERS_ENDPOINT": "/orders",
    })
    
    return selected_env 