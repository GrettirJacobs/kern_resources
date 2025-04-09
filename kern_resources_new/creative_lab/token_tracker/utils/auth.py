"""
Authentication utilities for the Token Tracker.

This module provides utilities for authentication and security.
"""

import os
import jwt
import logging
import datetime
from functools import wraps
from typing import Dict, Any, Optional, Callable
from flask import request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("token_tracker.utils.auth")


def get_jwt_secret() -> str:
    """
    Get the JWT secret key from environment variables.
    
    Returns:
        The JWT secret key.
    """
    secret = os.environ.get("JWT_SECRET_KEY")
    if not secret:
        logger.warning("JWT_SECRET_KEY not set. Using default secret key.")
        secret = "default-secret-key-change-in-production"
    return secret


def generate_token(user_id: str, role: str = "user", expiration: int = 86400) -> str:
    """
    Generate a JWT token.
    
    Args:
        user_id: The user ID.
        role: The user role (default: "user").
        expiration: The token expiration time in seconds (default: 24 hours).
        
    Returns:
        The JWT token.
    """
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expiration),
        "iat": datetime.datetime.now(datetime.timezone.utc),
    }
    
    token = jwt.encode(payload, get_jwt_secret(), algorithm="HS256")
    return token


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token.
    
    Args:
        token: The JWT token.
        
    Returns:
        The decoded token payload.
        
    Raises:
        jwt.InvalidTokenError: If the token is invalid.
        jwt.ExpiredSignatureError: If the token has expired.
    """
    return jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])


def token_required(f: Callable) -> Callable:
    """
    Decorator to require a valid JWT token for API endpoints.
    
    Args:
        f: The function to decorate.
        
    Returns:
        The decorated function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            # Decode token
            payload = decode_token(token)
            
            # Add user info to request
            request.user = payload
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def admin_required(f: Callable) -> Callable:
    """
    Decorator to require an admin role for API endpoints.
    
    Args:
        f: The function to decorate.
        
    Returns:
        The decorated function.
    """
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.user.get("role") != "admin":
            return jsonify({"error": "Admin privileges required"}), 403
        
        return f(*args, **kwargs)
    
    return decorated


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key.
    
    Args:
        api_key: The API key to encrypt.
        
    Returns:
        The encrypted API key.
    """
    # In a real implementation, this would use a proper encryption algorithm
    # For now, we'll just return a masked version for demonstration
    if not api_key:
        return ""
    
    if len(api_key) <= 8:
        return "********"
    
    return api_key[:4] + "..." + api_key[-4:]


def create_user(username: str, password: str, role: str = "user") -> Dict[str, Any]:
    """
    Create a new user.
    
    Args:
        username: The username.
        password: The password.
        role: The user role (default: "user").
        
    Returns:
        The user data.
    """
    # In a real implementation, this would store the user in a database
    # For now, we'll just return the user data for demonstration
    import hashlib
    
    # Hash the password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    return {
        "username": username,
        "password_hash": password_hash,
        "role": role,
    }


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user.
    
    Args:
        username: The username.
        password: The password.
        
    Returns:
        The user data if authentication is successful, None otherwise.
    """
    # In a real implementation, this would check the user in a database
    # For now, we'll just check against environment variables for demonstration
    import hashlib
    
    # Get admin credentials from environment variables
    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin")
    
    # Check if username matches
    if username != admin_username:
        return None
    
    # Hash the provided password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Hash the expected password
    expected_hash = hashlib.sha256(admin_password.encode()).hexdigest()
    
    # Check if password matches
    if password_hash != expected_hash:
        return None
    
    # Return user data
    return {
        "username": username,
        "role": "admin",
    }
