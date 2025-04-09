"""
Test edge cases for notifications.

This module tests edge cases and error conditions for notifications.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path to import from token_tracker
sys.path.append(str(Path(__file__).parent.parent))

from utils.notifications import (
    send_email_notification,
    send_budget_alert,
    send_budget_exceeded,
)


def test_send_email_notification_empty_values():
    """Test sending an email notification with empty values."""
    with patch("utils.notifications.smtplib.SMTP") as mock_smtp:
        # Set up mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Call the function with empty values
        result = send_email_notification(
            subject="",
            message="",
            to_email="",
            config={
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "username": "test",
                "password": "test",
                "from_address": "test@example.com",
            }
        )
        
        # Check the result
        assert result is True
        
        # Check that SMTP was called correctly
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test", "test")
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()


def test_send_email_notification_missing_config():
    """Test sending an email notification with missing configuration."""
    with patch("utils.notifications.smtplib.SMTP") as mock_smtp, \
         patch("utils.notifications.os.environ.get") as mock_env_get:
        # Set up mocks
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Mock environment variables
        mock_env_get.side_effect = lambda key, default: {
            "SMTP_SERVER": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_USERNAME": "test",
            "SMTP_PASSWORD": "test",
            "SMTP_FROM_ADDRESS": "test@example.com",
            "NOTIFICATION_EMAIL": "admin@example.com",
        }.get(key, default)
        
        # Call the function with no config
        result = send_email_notification(
            subject="Test Subject",
            message="Test Message",
        )
        
        # Check the result
        assert result is True
        
        # Check that SMTP was called correctly
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test", "test")
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()


def test_send_email_notification_smtp_error():
    """Test sending an email notification with SMTP error."""
    with patch("utils.notifications.smtplib.SMTP") as mock_smtp, \
         patch("utils.notifications.logger") as mock_logger:
        # Set up mock to raise an exception
        mock_smtp.side_effect = Exception("SMTP Error")
        
        # Call the function
        result = send_email_notification(
            subject="Test Subject",
            message="Test Message",
            to_email="test@example.com",
            config={
                "smtp_server": "smtp.example.com",
                "smtp_port": 587,
                "username": "test",
                "password": "test",
                "from_address": "test@example.com",
            }
        )
        
        # Check the result
        assert result is False
        
        # Check that the error was logged
        mock_logger.error.assert_called_once()
        args, kwargs = mock_logger.error.call_args
        assert "Failed to send email notification" in args[0]
        assert "SMTP Error" in args[0]


def test_send_budget_alert_edge_cases():
    """Test sending budget alerts with edge cases."""
    with patch("utils.notifications.send_email_notification") as mock_send_email:
        # Set up mock
        mock_send_email.return_value = True
        
        # Test with zero values
        result = send_budget_alert(
            budget_name="Test",
            threshold=0,
            current_amount=0.0,
            budget_amount=0.0,
            to_email="test@example.com",
        )
        
        # Check the result
        assert result is True
        
        # Check that send_email_notification was called correctly
        mock_send_email.assert_called_once()
        args, kwargs = mock_send_email.call_args
        
        # Check subject
        assert args[0] == "Token Tracker - Test Budget Alert (0%)"
        
        # Check message contains key information
        assert "Test budget has reached 0%" in args[1]
        assert "Current Amount: $0.00" in args[1]
        assert "Budget Amount: $0.00" in args[1]
        
        # With zero budget, percentage should be handled gracefully
        assert "Percentage Used: " in args[1]


def test_send_budget_exceeded_edge_cases():
    """Test sending budget exceeded notifications with edge cases."""
    with patch("utils.notifications.send_email_notification") as mock_send_email:
        # Set up mock
        mock_send_email.return_value = True
        
        # Test with zero budget
        result = send_budget_exceeded(
            budget_name="Test",
            current_amount=10.0,
            budget_amount=0.0,
            to_email="test@example.com",
        )
        
        # Check the result
        assert result is True
        
        # Check that send_email_notification was called correctly
        mock_send_email.assert_called_once()
        args, kwargs = mock_send_email.call_args
        
        # Check subject
        assert args[0] == "Token Tracker - Test Budget Exceeded"
        
        # Check message contains key information
        assert "Test budget has been exceeded" in args[1]
        assert "Current Amount: $10.00" in args[1]
        assert "Budget Amount: $0.00" in args[1]
        
        # With zero budget, percentage should be handled gracefully
        assert "Percentage Used: " in args[1]


def test_send_budget_alert_very_large_values():
    """Test sending budget alerts with very large values."""
    with patch("utils.notifications.send_email_notification") as mock_send_email:
        # Set up mock
        mock_send_email.return_value = True
        
        # Test with very large values
        result = send_budget_alert(
            budget_name="Test",
            threshold=80,
            current_amount=800000.0,
            budget_amount=1000000.0,
            to_email="test@example.com",
        )
        
        # Check the result
        assert result is True
        
        # Check that send_email_notification was called correctly
        mock_send_email.assert_called_once()
        args, kwargs = mock_send_email.call_args
        
        # Check subject
        assert args[0] == "Token Tracker - Test Budget Alert (80%)"
        
        # Check message contains key information
        assert "Test budget has reached 80%" in args[1]
        assert "Current Amount: $800000.00" in args[1]
        assert "Budget Amount: $1000000.00" in args[1]
        assert "Percentage Used: 80.0%" in args[1]
