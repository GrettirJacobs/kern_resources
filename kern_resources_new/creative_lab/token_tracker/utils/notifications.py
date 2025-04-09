"""
Notification utilities for the Token Tracker.

This module provides utilities for sending notifications when budget alerts
are triggered or other important events occur.
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("token_tracker.utils.notifications")

def send_email_notification(
    subject: str,
    message: str,
    to_email: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Send an email notification.

    Args:
        subject: The email subject.
        message: The email message.
        to_email: The recipient email address. If not provided, uses the configured email.
        config: The notification configuration. If not provided, uses environment variables.

    Returns:
        True if the email was sent successfully, False otherwise.
    """
    try:
        # Get configuration from environment variables if not provided
        if config is None:
            config = {
                "smtp_server": os.environ.get("SMTP_SERVER", "smtp.gmail.com"),
                "smtp_port": int(os.environ.get("SMTP_PORT", 587)),
                "username": os.environ.get("SMTP_USERNAME", ""),
                "password": os.environ.get("SMTP_PASSWORD", ""),
                "from_address": os.environ.get("SMTP_FROM_ADDRESS", ""),
            }

        # Get recipient email
        to_email = to_email or os.environ.get("NOTIFICATION_EMAIL", "erik.jacobs@gmail.com")

        # Check if email is enabled
        if not config.get("username") or not config.get("password"):
            logger.warning("Email notifications are not configured. Skipping.")
            return False

        # Create message
        msg = MIMEMultipart()
        msg["From"] = config.get("from_address", config.get("username", ""))
        msg["To"] = to_email
        msg["Subject"] = subject

        # Add message body
        msg.attach(MIMEText(message, "plain"))

        # Connect to SMTP server
        server = smtplib.SMTP(config.get("smtp_server", ""), config.get("smtp_port", 587))
        server.starttls()

        # Login to SMTP server
        server.login(config.get("username", ""), config.get("password", ""))

        # Send email
        server.send_message(msg)

        # Close connection
        server.quit()

        logger.info(f"Email notification sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        return False

def send_budget_alert(
    budget_name: str,
    threshold: float,
    current_amount: float,
    budget_amount: float,
    to_email: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Send a budget alert notification.

    Args:
        budget_name: The name of the budget (e.g., "Total", "Daily").
        threshold: The threshold percentage that was reached.
        current_amount: The current amount spent.
        budget_amount: The total budget amount.
        to_email: The recipient email address. If not provided, uses the configured email.
        config: The notification configuration. If not provided, uses environment variables.

    Returns:
        True if the email was sent successfully, False otherwise.
    """
    subject = f"Token Tracker - {budget_name} Budget Alert ({threshold}%)"

    # Calculate percentage safely
    percentage = "N/A (zero budget)" if budget_amount == 0 else f"{(current_amount / budget_amount) * 100:.1f}%"

    message = f"""
Token Tracker Budget Alert

The {budget_name} budget has reached {threshold}% of its limit.

Current Amount: ${current_amount:.2f}
Budget Amount: ${budget_amount:.2f}
Percentage Used: {percentage}

This is an automated notification from the Token Tracker.
"""

    return send_email_notification(subject, message, to_email, config)

def send_budget_exceeded(
    budget_name: str,
    current_amount: float,
    budget_amount: float,
    to_email: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Send a budget exceeded notification.

    Args:
        budget_name: The name of the budget (e.g., "Total", "Daily").
        current_amount: The current amount spent.
        budget_amount: The total budget amount.
        to_email: The recipient email address. If not provided, uses the configured email.
        config: The notification configuration. If not provided, uses environment variables.

    Returns:
        True if the email was sent successfully, False otherwise.
    """
    subject = f"Token Tracker - {budget_name} Budget Exceeded"

    # Calculate percentage safely
    percentage = "N/A (zero budget)" if budget_amount == 0 else f"{(current_amount / budget_amount) * 100:.1f}%"

    message = f"""
Token Tracker Budget Alert

The {budget_name} budget has been exceeded.

Current Amount: ${current_amount:.2f}
Budget Amount: ${budget_amount:.2f}
Percentage Used: {percentage}

This is an automated notification from the Token Tracker.
"""

    return send_email_notification(subject, message, to_email, config)
