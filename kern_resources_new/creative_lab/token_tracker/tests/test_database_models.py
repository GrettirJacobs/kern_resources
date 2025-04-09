"""
Tests for database models.

This module tests the database models for the Token Tracker.
"""

import pytest
import datetime
from sqlalchemy import func

# Define test models directly
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import datetime

# Create the base class for testing
Base = declarative_base()

# Define test models
class TokenUsage(Base):
    """Model for tracking token usage."""
    __tablename__ = "token_usage"

    id = Column(Integer, primary_key=True)
    request_id = Column(String(36), nullable=False)  # UUID
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    model = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    endpoint = Column(String(100), nullable=True)
    status = Column(String(20), nullable=True)
    latency = Column(Float, nullable=True)  # in seconds

class RateLimit(Base):
    """Model for storing rate limit configurations."""
    __tablename__ = "rate_limits"

    id = Column(Integer, primary_key=True)
    model = Column(String(100), nullable=False, unique=True)
    limit = Column(Integer, nullable=False)
    period = Column(String(20), nullable=False)  # minute, hour, day
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

class Budget(Base):
    """Model for storing budget configurations."""
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    amount = Column(Float, nullable=False)
    period = Column(String(20), nullable=False)  # daily, monthly, total
    reset_day = Column(Integer, nullable=True)  # day of month for monthly reset
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    alerts = relationship("BudgetAlert", back_populates="budget", cascade="all, delete-orphan")

class BudgetAlert(Base):
    """Model for storing budget alerts."""
    __tablename__ = "budget_alerts"

    id = Column(Integer, primary_key=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    threshold = Column(Float, nullable=False)  # percentage (0-100)
    email = Column(String(100), nullable=True)
    triggered = Column(Boolean, default=False)
    last_triggered = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    budget = relationship("Budget", back_populates="alerts")


def test_token_usage_model(test_db):
    """Test the TokenUsage model."""
    session, _ = test_db

    # Create a token usage record
    token_usage = TokenUsage(
        request_id="test-request",
        model="test-model",
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        estimated_cost=0.0025,
        endpoint="/v1/chat/completions",
        status="200",
        latency=0.5,
    )

    # Add to database
    session.add(token_usage)
    session.commit()

    # Query the database
    result = session.query(TokenUsage).filter_by(request_id="test-request").first()

    # Check the result
    assert result is not None
    assert result.request_id == "test-request"
    assert result.model == "test-model"
    assert result.prompt_tokens == 100
    assert result.completion_tokens == 50
    assert result.total_tokens == 150
    assert result.estimated_cost == 0.0025
    assert result.endpoint == "/v1/chat/completions"
    assert result.status == "200"
    assert result.latency == 0.5

    # Clean up
    session.query(TokenUsage).delete()
    session.commit()
    session.close()


def test_rate_limit_model(test_db):
    """Test the RateLimit model."""
    session, _ = test_db

    # Create a rate limit record
    rate_limit = RateLimit(
        model="test-model",
        limit=10,
        period="minute",
    )

    # Add to database
    session.add(rate_limit)
    session.commit()

    # Query the database
    result = session.query(RateLimit).filter_by(model="test-model").first()

    # Check the result
    assert result is not None
    assert result.model == "test-model"
    assert result.limit == 10
    assert result.period == "minute"

    # Clean up
    session.query(RateLimit).delete()
    session.commit()
    session.close()


def test_budget_model(test_db):
    """Test the Budget model."""
    session, _ = test_db

    # Create a budget record
    budget = Budget(
        name="Total",
        amount=100.0,
        period="total",
    )

    # Add to database
    session.add(budget)
    session.commit()

    # Query the database
    result = session.query(Budget).filter_by(name="Total").first()

    # Check the result
    assert result is not None
    assert result.name == "Total"
    assert result.amount == 100.0
    assert result.period == "total"

    # Clean up
    session.query(Budget).delete()
    session.commit()
    session.close()


def test_budget_alert_model(test_db):
    """Test the BudgetAlert model."""
    session, _ = test_db

    # Create a budget record
    budget = Budget(
        name="Total",
        amount=100.0,
        period="total",
    )

    # Add to database
    session.add(budget)
    session.commit()

    # Create a budget alert record
    budget_alert = BudgetAlert(
        budget_id=budget.id,
        threshold=80,
        email="test@example.com",
    )

    # Add to database
    session.add(budget_alert)
    session.commit()

    # Query the database
    result = session.query(BudgetAlert).filter_by(budget_id=budget.id).first()

    # Check the result
    assert result is not None
    assert result.budget_id == budget.id
    assert result.threshold == 80
    assert result.email == "test@example.com"
    assert result.triggered is False

    # Clean up
    session.query(BudgetAlert).delete()
    session.query(Budget).delete()
    session.commit()
    session.close()


def test_budget_alert_relationship(test_db):
    """Test the relationship between Budget and BudgetAlert."""
    session, _ = test_db

    # Create a budget record
    budget = Budget(
        name="Total",
        amount=100.0,
        period="total",
    )

    # Add budget alerts
    budget.alerts.append(
        BudgetAlert(
            threshold=50,
            email="test1@example.com",
        )
    )

    budget.alerts.append(
        BudgetAlert(
            threshold=80,
            email="test2@example.com",
        )
    )

    # Add to database
    session.add(budget)
    session.commit()

    # Query the database
    result = session.query(Budget).filter_by(name="Total").first()

    # Check the result
    assert result is not None
    assert len(result.alerts) == 2
    assert result.alerts[0].threshold == 50
    assert result.alerts[0].email == "test1@example.com"
    assert result.alerts[1].threshold == 80
    assert result.alerts[1].email == "test2@example.com"

    # Clean up
    session.query(BudgetAlert).delete()
    session.query(Budget).delete()
    session.commit()
    session.close()


def test_token_usage_aggregation(test_token_usage):
    """Test aggregation of token usage data."""
    session = test_token_usage

    # Get total tokens
    total_tokens = session.query(func.sum(TokenUsage.total_tokens)).scalar()
    assert total_tokens == 750  # 5 records * 150 tokens

    # Get total cost
    total_cost = session.query(func.sum(TokenUsage.estimated_cost)).scalar()
    assert total_cost == 0.0125  # 5 records * 0.0025 cost

    # Get token usage by model
    model_usage = (
        session.query(
            TokenUsage.model,
            func.sum(TokenUsage.total_tokens).label("total_tokens"),
            func.sum(TokenUsage.estimated_cost).label("total_cost"),
        )
        .group_by(TokenUsage.model)
        .all()
    )

    assert len(model_usage) == 1
    assert model_usage[0].model == "test-model"
    assert model_usage[0].total_tokens == 750
    assert model_usage[0].total_cost == 0.0125
