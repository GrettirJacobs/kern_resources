"""
Tests for authentication utilities.

This module tests the authentication utilities for the Token Tracker.
"""

import os
import pytest
import datetime
from unittest.mock import patch, MagicMock

# Import the actual auth functions
import sys
from pathlib import Path

# Add parent directory to path to import from token_tracker
sys.path.append(str(Path(__file__).parent.parent))

# Import the actual auth functions
from utils.auth import (
    get_jwt_secret,
    generate_token,
    decode_token,
    token_required,
    admin_required,
    encrypt_api_key,
    create_user,
    authenticate_user,
)


def test_get_jwt_secret():
    """Test getting the JWT secret key."""
    # Test with environment variable set
    with patch.dict(os.environ, {"JWT_SECRET_KEY": "test-secret-key"}):
        assert get_jwt_secret() == "test-secret-key"

    # Test with environment variable not set
    with patch.dict(os.environ, {}, clear=True):
        assert get_jwt_secret() == "default-secret-key-change-in-production"


def test_generate_token():
    """Test generating a JWT token."""
    # Set a fixed secret key
    with patch("utils.auth.get_jwt_secret", return_value="test-secret-key"):
        # Generate a token
        token = generate_token("test-user", "admin", 3600)

        # Decode the token
        payload = decode_token(token)

        # Check the payload
        assert payload["user_id"] == "test-user"
        assert payload["role"] == "admin"

        # Check expiration
        exp = datetime.datetime.fromtimestamp(payload["exp"], tz=datetime.timezone.utc)
        iat = datetime.datetime.fromtimestamp(payload["iat"], tz=datetime.timezone.utc)
        assert (exp - iat).total_seconds() == 3600


def test_decode_token():
    """Test decoding a JWT token."""
    # Set a fixed secret key
    with patch("utils.auth.get_jwt_secret", return_value="test-secret-key"):
        # Generate a token
        token = generate_token("test-user", "admin", 3600)

        # Decode the token
        payload = decode_token(token)

        # Check the payload
        assert payload["user_id"] == "test-user"
        assert payload["role"] == "admin"


def test_token_required():
    """Test the token_required decorator."""
    # Create a mock Flask request
    mock_request = MagicMock()
    mock_request.headers = {"Authorization": "Bearer test-token"}

    # Create a mock function
    mock_function = MagicMock()
    mock_function.__name__ = "mock_function"

    # Create a mock decode_token function
    mock_decode_token = MagicMock(return_value={"user_id": "test-user", "role": "admin"})

    # Apply the decorator
    with patch("utils.auth.request", mock_request), \
         patch("utils.auth.decode_token", mock_decode_token):
        decorated_function = token_required(mock_function)
        result = decorated_function()

    # Check that the function was called
    mock_function.assert_called_once()

    # Check that the user was added to the request
    assert mock_request.user == {"user_id": "test-user", "role": "admin"}


def test_admin_required():
    """Test the admin_required decorator."""
    # Create a mock Flask request
    mock_request = MagicMock()
    mock_request.headers = {"Authorization": "Bearer test-token"}
    mock_request.user = {"user_id": "test-user", "role": "admin"}

    # Create a mock function
    mock_function = MagicMock()
    mock_function.__name__ = "mock_function"

    # Create a mock token_required decorator
    def mock_token_required(f):
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper

    # Apply the decorator
    with patch("utils.auth.request", mock_request), \
         patch("utils.auth.token_required", mock_token_required):
        decorated_function = admin_required(mock_function)
        result = decorated_function()

    # Check that the function was called
    mock_function.assert_called_once()


def test_encrypt_api_key():
    """Test encrypting an API key."""
    # Test with a short API key
    assert encrypt_api_key("short") == "********"

    # Test with a long API key
    assert encrypt_api_key("this-is-a-long-api-key") == "this...-key"

    # Test with an empty API key
    assert encrypt_api_key("") == ""


def test_create_user():
    """Test creating a user."""
    # Create a user
    user = create_user("test-user", "test-password", "admin")

    # Check the user data
    assert user["username"] == "test-user"
    assert "password_hash" in user
    assert user["role"] == "admin"


def test_authenticate_user():
    """Test authenticating a user."""
    # Test with correct credentials
    with patch.dict(os.environ, {"ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": "password"}):
        user = authenticate_user("admin", "password")
        assert user is not None
        assert user["username"] == "admin"
        assert user["role"] == "admin"

    # Test with incorrect username
    with patch.dict(os.environ, {"ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": "password"}):
        user = authenticate_user("wrong-user", "password")
        assert user is None

    # Test with incorrect password
    with patch.dict(os.environ, {"ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": "password"}):
        user = authenticate_user("admin", "wrong-password")
        assert user is None
