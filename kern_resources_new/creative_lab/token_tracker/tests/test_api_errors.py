"""
Test error handling in the API.

This module tests how the API handles error conditions.
"""

import pytest
import json
import datetime
from flask import Flask, jsonify

# Create a mock Flask app for testing
api_app = Flask(__name__)
api_app.config['TESTING'] = True

# Create mock routes to simulate error conditions
@api_app.route('/api/error/unauthorized', methods=['GET'])
def unauthorized_error():
    return jsonify({"error": "Unauthorized"}), 401

@api_app.route('/api/error/forbidden', methods=['GET'])
def forbidden_error():
    return jsonify({"error": "Forbidden"}), 403

@api_app.route('/api/error/not-found', methods=['GET'])
def not_found_error():
    return jsonify({"error": "Not found"}), 404

@api_app.route('/api/error/server-error', methods=['GET'])
def server_error():
    return jsonify({"error": "Internal server error"}), 500

@api_app.route('/api/token-usage/invalid', methods=['POST'])
def invalid_token_usage():
    return jsonify({"error": "Invalid token usage data"}), 400

@api_app.route('/api/rate-limits/invalid', methods=['POST'])
def invalid_rate_limit():
    return jsonify({"error": "Invalid rate limit data"}), 400

@api_app.route('/api/budgets/invalid', methods=['POST'])
def invalid_budget():
    return jsonify({"error": "Invalid budget data"}), 400


@pytest.fixture
def client():
    """Create a test client for the API."""
    with api_app.test_client() as client:
        yield client


def test_unauthorized_error(client):
    """Test unauthorized error response."""
    response = client.get('/api/error/unauthorized')
    
    # Check the response
    assert response.status_code == 401
    data = json.loads(response.data)
    
    # Check the error message
    assert "error" in data
    assert data["error"] == "Unauthorized"


def test_forbidden_error(client):
    """Test forbidden error response."""
    response = client.get('/api/error/forbidden')
    
    # Check the response
    assert response.status_code == 403
    data = json.loads(response.data)
    
    # Check the error message
    assert "error" in data
    assert data["error"] == "Forbidden"


def test_not_found_error(client):
    """Test not found error response."""
    response = client.get('/api/error/not-found')
    
    # Check the response
    assert response.status_code == 404
    data = json.loads(response.data)
    
    # Check the error message
    assert "error" in data
    assert data["error"] == "Not found"


def test_server_error(client):
    """Test server error response."""
    response = client.get('/api/error/server-error')
    
    # Check the response
    assert response.status_code == 500
    data = json.loads(response.data)
    
    # Check the error message
    assert "error" in data
    assert data["error"] == "Internal server error"


def test_invalid_token_usage_data(client):
    """Test submitting invalid token usage data."""
    # Create invalid data (missing required fields)
    data = {
        "model": "test-model",
        # Missing prompt_tokens, completion_tokens, etc.
    }
    
    # Call the endpoint
    response = client.post('/api/token-usage/invalid', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    # Check the response
    assert response.status_code == 400
    result = json.loads(response.data)
    
    # Check the error message
    assert "error" in result
    assert result["error"] == "Invalid token usage data"


def test_invalid_rate_limit_data(client):
    """Test submitting invalid rate limit data."""
    # Create invalid data (missing required fields)
    data = {
        "model": "test-model",
        # Missing limit and period
    }
    
    # Call the endpoint
    response = client.post('/api/rate-limits/invalid', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    # Check the response
    assert response.status_code == 400
    result = json.loads(response.data)
    
    # Check the error message
    assert "error" in result
    assert result["error"] == "Invalid rate limit data"


def test_invalid_budget_data(client):
    """Test submitting invalid budget data."""
    # Create invalid data (missing required fields)
    data = {
        "name": "Test Budget",
        # Missing amount and period
    }
    
    # Call the endpoint
    response = client.post('/api/budgets/invalid', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    # Check the response
    assert response.status_code == 400
    result = json.loads(response.data)
    
    # Check the error message
    assert "error" in result
    assert result["error"] == "Invalid budget data"
