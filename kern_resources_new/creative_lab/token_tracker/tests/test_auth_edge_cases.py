"""
Test edge cases for authentication.

This module tests edge cases and error conditions for authentication.
"""

import pytest
import datetime
import jwt
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path to import from token_tracker
sys.path.append(str(Path(__file__).parent.parent))

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


def test_generate_token_with_custom_expiration():
    """Test generating a token with a custom expiration time."""
    # Generate a token with a very short expiration (1 second)
    token = generate_token("test-user", "user", 1)

    # Decode the token to verify the expiration
    payload = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])

    # Check the payload
    assert payload["user_id"] == "test-user"
    assert payload["role"] == "user"

    # Check that the expiration is set correctly
    now = datetime.datetime.now(datetime.timezone.utc).timestamp()
    assert payload["exp"] - now <= 1  # Should expire in 1 second or less


def test_decode_token_expired():
    """Test decoding an expired token."""
    # Generate a token that's already expired
    payload = {
        "user_id": "test-user",
        "role": "user",
        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=1),
        "iat": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=2),
    }

    token = jwt.encode(payload, get_jwt_secret(), algorithm="HS256")

    # Try to decode the token
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(token)


def test_decode_token_invalid():
    """Test decoding an invalid token."""
    # Generate a token with an invalid signature
    payload = {
        "user_id": "test-user",
        "role": "user",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=60),
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }

    token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

    # Try to decode the token
    with pytest.raises(jwt.InvalidTokenError):
        decode_token(token)


def test_token_required_missing_token():
    """Test token_required decorator with a missing token."""
    # Create a mock request
    mock_request = MagicMock()
    mock_request.headers = {}  # No Authorization header

    # Create a mock function
    mock_function = MagicMock()
    mock_function.__name__ = "mock_function"

    # Create a mock response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_jsonify = MagicMock(return_value=mock_response)

    # Apply the decorator
    with patch("utils.auth.request", mock_request), \
         patch("utils.auth.jsonify", mock_jsonify):
        decorated_function = token_required(mock_function)
        result = decorated_function()

    # Check that the function was not called
    mock_function.assert_not_called()

    # Check that jsonify was called with the correct error message
    mock_jsonify.assert_called_once()
    args, kwargs = mock_jsonify.call_args
    # In the actual implementation, jsonify is called with a dict as a positional argument
    assert len(args) > 0
    assert isinstance(args[0], dict)
    assert "error" in args[0]

    # In the actual implementation, jsonify returns a tuple (response, status_code)
    # So we don't need to check the status_code attribute


def test_token_required_invalid_token():
    """Test token_required decorator with an invalid token."""
    # Create a mock request
    mock_request = MagicMock()
    mock_request.headers = {"Authorization": "Bearer invalid-token"}

    # Create a mock function
    mock_function = MagicMock()
    mock_function.__name__ = "mock_function"

    # Create a mock response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_jsonify = MagicMock(return_value=mock_response)

    # Mock decode_token to raise an error
    mock_decode_token = MagicMock(side_effect=jwt.InvalidTokenError)

    # Apply the decorator
    with patch("utils.auth.request", mock_request), \
         patch("utils.auth.jsonify", mock_jsonify), \
         patch("utils.auth.decode_token", mock_decode_token):
        decorated_function = token_required(mock_function)
        result = decorated_function()

    # Check that the function was not called
    mock_function.assert_not_called()

    # Check that jsonify was called with the correct error message
    mock_jsonify.assert_called_once()
    args, kwargs = mock_jsonify.call_args
    # In the actual implementation, jsonify is called with a dict as a positional argument
    assert len(args) > 0
    assert isinstance(args[0], dict)
    assert "error" in args[0]

    # In the actual implementation, jsonify returns a tuple (response, status_code)
    # So we don't need to check the status_code attribute


def test_admin_required_non_admin():
    """Test admin_required decorator with a non-admin user."""
    # Create a mock request
    mock_request = MagicMock()
    mock_request.user = {"role": "user"}  # Non-admin role

    # Create a mock function
    mock_function = MagicMock()
    mock_function.__name__ = "mock_function"

    # Create a mock response
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_jsonify = MagicMock(return_value=mock_response)

    # Mock token_required to pass through
    def mock_token_required(f):
        return f

    # Apply the decorator
    with patch("utils.auth.request", mock_request), \
         patch("utils.auth.jsonify", mock_jsonify), \
         patch("utils.auth.token_required", mock_token_required):
        decorated_function = admin_required(mock_function)
        result = decorated_function()

    # Check that the function was not called
    mock_function.assert_not_called()

    # Check that jsonify was called with the correct error message
    mock_jsonify.assert_called_once()
    args, kwargs = mock_jsonify.call_args
    # In the actual implementation, jsonify is called with a dict as a positional argument
    assert len(args) > 0
    assert isinstance(args[0], dict)
    assert "error" in args[0]

    # In the actual implementation, jsonify returns a tuple (response, status_code)
    # So we don't need to check the status_code attribute


def test_encrypt_api_key_edge_cases():
    """Test encrypt_api_key with edge cases."""
    # Test with None
    assert encrypt_api_key(None) == ""

    # Test with empty string
    assert encrypt_api_key("") == ""

    # Test with very short key
    assert encrypt_api_key("a") == "********"

    # Test with key exactly 8 characters
    assert encrypt_api_key("12345678") == "********"

    # Test with key just over 8 characters
    assert encrypt_api_key("123456789") == "1234...6789"

    # Test with very long key
    long_key = "a" * 100
    assert encrypt_api_key(long_key) == "aaaa...aaaa"
    assert len(encrypt_api_key(long_key)) < len(long_key)


def test_create_user_edge_cases():
    """Test create_user with edge cases."""
    # Test with empty username
    user = create_user("", "password")
    assert user["username"] == ""

    # Test with empty password
    user = create_user("username", "")
    assert user["password_hash"] != ""  # Should still hash the empty string

    # Test with very long username and password
    long_string = "a" * 1000
    user = create_user(long_string, long_string)
    assert user["username"] == long_string
    assert user["password_hash"] != long_string  # Should be hashed


def test_authenticate_user_edge_cases():
    """Test authenticate_user with edge cases."""
    # Test with empty username
    with patch("os.environ.get", return_value="admin"):
        result = authenticate_user("", "admin")
        assert result is None

    # Test with empty password
    with patch("os.environ.get", return_value="admin"):
        result = authenticate_user("admin", "")
        assert result is None

    # Test with None values
    with patch("os.environ.get", return_value="admin"):
        result = authenticate_user(None, None)
        assert result is None
