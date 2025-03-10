"""
Configuration file for pytest.
Contains shared fixtures and settings for all tests.
"""

import pytest
import os
import tempfile

@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    Automatically used fixture to set up test environment variables
    and configurations before each test.
    """
    # Store original environment
    original_env = dict(os.environ)
    
    # Set up test environment variables
    os.environ["TESTING"] = "true"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
