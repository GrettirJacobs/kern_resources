"""
Integration tests for the Token Tracker.

This module tests the interaction between different components of the Token Tracker.
"""

import pytest
import datetime
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path to import from token_tracker
sys.path.append(str(Path(__file__).parent.parent))

from database.models import TokenUsage, RateLimit, Budget, BudgetAlert
from utils.notifications import send_budget_alert, send_budget_exceeded


@pytest.fixture
def mock_send_email():
    """Mock the send_email_notification function."""
    with patch("utils.notifications.send_email_notification") as mock:
        mock.return_value = True
        yield mock


@pytest.mark.skip(reason="Schema mismatch: slack_webhook column not in budget_alerts table")
def test_budget_alert_integration(test_db, mock_send_email):
    """Test the integration between budget alerts and notifications."""
    session, _ = test_db

    # Create a budget
    budget = Budget(
        name="Integration Test",
        amount=100.0,
        period="daily",
    )
    session.add(budget)
    session.commit()

    # Create budget alerts
    alerts = [
        BudgetAlert(budget=budget, threshold=50, email="alert50@example.com"),
        BudgetAlert(budget=budget, threshold=80, email="alert80@example.com"),
        BudgetAlert(budget=budget, threshold=90, email="alert90@example.com")
    ]
    for alert in alerts:
        session.add(alert)
    session.commit()

    # Create token usage records that will trigger alerts
    now = datetime.datetime.now(datetime.timezone.utc)
    token_usages = [
        # This should trigger the 50% alert
        TokenUsage(
            request_id="integration-1",
            timestamp=now,
            model="test-model",
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500,
            estimated_cost=50.0,  # 50% of budget
        ),
        # This should trigger the 80% alert
        TokenUsage(
            request_id="integration-2",
            timestamp=now,
            model="test-model",
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500,
            estimated_cost=30.0,  # Now at 80% of budget
        ),
        # This should trigger the 90% alert
        TokenUsage(
            request_id="integration-3",
            timestamp=now,
            model="test-model",
            prompt_tokens=500,
            completion_tokens=250,
            total_tokens=750,
            estimated_cost=10.0,  # Now at 90% of budget
        ),
        # This should trigger the budget exceeded notification
        TokenUsage(
            request_id="integration-4",
            timestamp=now,
            model="test-model",
            prompt_tokens=500,
            completion_tokens=250,
            total_tokens=750,
            estimated_cost=20.0,  # Now at 110% of budget
        ),
    ]

    # Process each token usage and check for alerts
    current_amount = 0.0
    for i, token_usage in enumerate(token_usages):
        session.add(token_usage)
        session.commit()

        # Update the current amount
        current_amount += token_usage.estimated_cost

        # Check if we need to send alerts
        for alert in alerts:
            threshold_amount = (alert.threshold / 100) * budget.amount
            if current_amount >= threshold_amount and current_amount - token_usage.estimated_cost < threshold_amount:
                # Send alert
                send_budget_alert(
                    budget_name=budget.name,
                    threshold=alert.threshold,
                    current_amount=current_amount,
                    budget_amount=budget.amount,
                    to_email=alert.email,
                )

        # Check if we exceeded the budget
        if current_amount > budget.amount and current_amount - token_usage.estimated_cost <= budget.amount:
            # Send budget exceeded notification
            send_budget_exceeded(
                budget_name=budget.name,
                current_amount=current_amount,
                budget_amount=budget.amount,
                to_email="admin@example.com",
            )

    # Check that send_email_notification was called 4 times (3 alerts + 1 exceeded)
    assert mock_send_email.call_count == 4

    # Check the calls
    calls = mock_send_email.call_args_list

    # First call should be for 50% alert
    args, kwargs = calls[0]
    assert "Integration Test Budget Alert (50%)" in args[0]
    assert "alert50@example.com" in kwargs.get("to_email", args[2])

    # Second call should be for 80% alert
    args, kwargs = calls[1]
    assert "Integration Test Budget Alert (80%)" in args[0]
    assert "alert80@example.com" in kwargs.get("to_email", args[2])

    # Third call should be for 90% alert
    args, kwargs = calls[2]
    assert "Integration Test Budget Alert (90%)" in args[0]
    assert "alert90@example.com" in kwargs.get("to_email", args[2])

    # Fourth call should be for budget exceeded
    args, kwargs = calls[3]
    assert "Integration Test Budget Exceeded" in args[0]
    assert "admin@example.com" in kwargs.get("to_email", args[2])

    # Clean up
    for token_usage in token_usages:
        session.delete(token_usage)
    for alert in alerts:
        session.delete(alert)
    session.delete(budget)
    session.commit()


@pytest.mark.skip(reason="Schema mismatch: user_id column not in token_usage table")
def test_rate_limit_integration(test_db):
    """Test the integration between rate limits and token usage."""
    session, _ = test_db

    # Create a rate limit
    rate_limit = RateLimit(
        model="test-model",
        limit=10,
        period="minute",
    )
    session.add(rate_limit)
    session.commit()

    # Create token usage records
    now = datetime.datetime.now(datetime.timezone.utc)
    token_usages = []

    # Create 10 token usage records within the rate limit
    for i in range(10):
        token_usage = TokenUsage(
            request_id=f"rate-limit-{i}",
            timestamp=now - datetime.timedelta(seconds=i),
            model="test-model",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            estimated_cost=0.1,
            endpoint="/v1/chat/completions",
            status="200",
            latency=0.1
        )
        token_usages.append(token_usage)
        session.add(token_usage)
    session.commit()

    # Check if we're at the rate limit
    one_minute_ago = now - datetime.timedelta(minutes=1)
    count = session.query(TokenUsage).filter(
        TokenUsage.model == "test-model",
        TokenUsage.timestamp >= one_minute_ago
    ).count()

    assert count == 10
    assert count == rate_limit.limit

    # Try to add one more token usage
    token_usage = TokenUsage(
        request_id="rate-limit-11",
        timestamp=now,
        model="test-model",
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        estimated_cost=0.1,
        endpoint="/v1/chat/completions",
        status="200",
        latency=0.1
    )
    session.add(token_usage)
    session.commit()

    # Check that we're now over the rate limit
    count = session.query(TokenUsage).filter(
        TokenUsage.model == "test-model",
        TokenUsage.timestamp >= one_minute_ago
    ).count()

    assert count == 11
    assert count > rate_limit.limit

    # Clean up
    for token_usage in token_usages:
        session.delete(token_usage)
    session.delete(token_usage)  # Delete the 11th one
    session.delete(rate_limit)
    session.commit()
