"""
Tests for notification utilities.

This module tests the notification utilities for the Token Tracker.
"""

import pytest
from unittest.mock import patch, MagicMock

# Import the actual notification functions
import sys
import os
from pathlib import Path

# Add parent directory to path to import from token_tracker
sys.path.append(str(Path(__file__).parent.parent))

# Import the actual notification functions
from utils.notifications import send_email_notification, send_budget_alert, send_budget_exceeded


@patch("utils.notifications.smtplib.SMTP")
def test_send_email_notification(mock_smtp):
    """Test sending an email notification."""
    # Set up mock
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    # Test configuration
    config = {
        "smtp_server": "test-smtp-server",
        "smtp_port": 587,
        "username": "test-username",
        "password": "test-password",
        "from_address": "test-from@example.com",
    }

    # Call the function
    result = send_email_notification(
        subject="Test Subject",
        message="Test Message",
        to_email="test-to@example.com",
        config=config,
    )

    # Check the result
    assert result is True

    # Check that the SMTP server was used correctly
    mock_smtp.assert_called_once_with("test-smtp-server", 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("test-username", "test-password")
    mock_server.send_message.assert_called_once()
    mock_server.quit.assert_called_once()


@patch("utils.notifications.smtplib.SMTP")
def test_send_email_notification_failure(mock_smtp):
    """Test sending an email notification with a failure."""
    # Set up mock to raise an exception
    mock_smtp.side_effect = Exception("Test exception")

    # Test configuration
    config = {
        "smtp_server": "test-smtp-server",
        "smtp_port": 587,
        "username": "test-username",
        "password": "test-password",
        "from_address": "test-from@example.com",
    }

    # Call the function
    result = send_email_notification(
        subject="Test Subject",
        message="Test Message",
        to_email="test-to@example.com",
        config=config,
    )

    # Check the result
    assert result is False


@patch("utils.notifications.send_email_notification")
def test_send_budget_alert(mock_send_email):
    """Test sending a budget alert."""
    # Set up mock
    mock_send_email.return_value = True

    # Call the function
    result = send_budget_alert(
        budget_name="Total",
        threshold=80,
        current_amount=80.0,
        budget_amount=100.0,
        to_email="test@example.com",
    )

    # Check the result
    assert result is True

    # Check that send_email_notification was called correctly
    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args

    # Check arguments
    assert args[0] == "Token Tracker - Total Budget Alert (80%)"  # subject is the first positional argument

    # Check message contains key information
    assert "Total budget has reached 80%" in args[1]  # message is the second positional argument
    assert "Current Amount: $80.00" in args[1]
    assert "Budget Amount: $100.00" in args[1]
    assert "Percentage Used: 80.0%" in args[1]

    # Check recipient
    assert kwargs.get("to_email") == "test@example.com" or args[2] == "test@example.com"  # to_email could be a positional or keyword argument


@patch("utils.notifications.send_email_notification")
def test_send_budget_exceeded(mock_send_email):
    """Test sending a budget exceeded notification."""
    # Set up mock
    mock_send_email.return_value = True

    # Call the function
    result = send_budget_exceeded(
        budget_name="Daily",
        current_amount=12.0,
        budget_amount=10.0,
        to_email="test@example.com",
    )

    # Check the result
    assert result is True

    # Check that send_email_notification was called correctly
    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args

    # Check arguments
    assert args[0] == "Token Tracker - Daily Budget Exceeded"  # subject is the first positional argument

    # Check message contains key information
    assert "Daily budget has been exceeded" in args[1]  # message is the second positional argument
    assert "Current Amount: $12.00" in args[1]
    assert "Budget Amount: $10.00" in args[1]
    assert "Percentage Used: 120.0%" in args[1]

    # Check recipient
    assert kwargs.get("to_email") == "test@example.com" or args[2] == "test@example.com"  # to_email could be a positional or keyword argument