"""
Configuration for pytest.

This module provides fixtures and configuration for testing the Token Tracker.
"""

import os
import sys
import pytest
import tempfile
import datetime
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

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


@pytest.fixture
def test_db():
    """Create a temporary database for testing."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    db_url = f"sqlite:///{db_path}"

    # Create the database and tables
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)

    # Create a session factory
    Session = sessionmaker(bind=engine)

    # Create a session
    session = Session()

    # Yield the session and engine
    yield session, engine

    # Clean up
    session.close()
    engine.dispose()

    try:
        # Close the file descriptor
        os.close(db_fd)
        # Try to remove the file
        if os.path.exists(db_path):
            os.unlink(db_path)
    except (OSError, PermissionError) as e:
        # Log the error but don't fail the test
        print(f"Warning: Could not remove temporary database file {db_path}: {e}")


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return {
        "general": {
            "host": "127.0.0.1",
            "port": 8000,
            "environment": "testing",
            "database_url": "sqlite:///:memory:",
        },
        "model_list": [
            {
                "model_name": "test-model",
                "litellm_params": {
                    "model": "test-model",
                    "api_key": "test-api-key",
                },
            },
        ],
        "rate_limits": [
            {
                "model": "test-model",
                "limit": 10,
                "period": "minute",
            },
        ],
        "budget": {
            "total": 100.0,
            "daily": 10.0,
            "alerts": [
                {
                    "threshold": 80,
                    "email": "test@example.com",
                },
            ],
        },
        "costs": {
            "test-model": {
                "input": 0.001,
                "output": 0.002,
            },
        },
        "logging": {
            "level": "DEBUG",
            "file": None,
        },
    }


@pytest.fixture
def test_token_usage(test_db):
    """Create test token usage data."""
    session, _ = test_db

    # Create token usage records
    token_usages = [
        TokenUsage(
            request_id=f"test-request-{i}",
            model="test-model",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            estimated_cost=0.0025,
            endpoint="/v1/chat/completions",
            status="200",
            latency=0.5,
        )
        for i in range(5)
    ]

    # Add to database
    for token_usage in token_usages:
        session.add(token_usage)

    # Commit changes
    session.commit()

    # Return the session
    yield session

    # Clean up
    session.query(TokenUsage).delete()
    session.commit()
    session.close()


@pytest.fixture
def test_rate_limits(test_db):
    """Create test rate limit data."""
    session, _ = test_db

    # Create rate limit records
    rate_limits = [
        RateLimit(
            model=f"test-model-{i}",
            limit=10 * (i + 1),
            period="minute",
        )
        for i in range(3)
    ]

    # Add to database
    for rate_limit in rate_limits:
        session.add(rate_limit)

    # Commit changes
    session.commit()

    # Return the session
    yield session

    # Clean up
    session.query(RateLimit).delete()
    session.commit()
    session.close()


@pytest.fixture
def test_budgets(test_db):
    """Create test budget data."""
    session, _ = test_db

    # Create budget records
    total_budget = Budget(
        name="Total",
        amount=100.0,
        period="total",
    )

    daily_budget = Budget(
        name="Daily",
        amount=10.0,
        period="daily",
    )

    # Add budget alerts
    total_budget.alerts.append(
        BudgetAlert(
            threshold=80,
            email="test@example.com",
        )
    )

    # Add to database
    session.add(total_budget)
    session.add(daily_budget)

    # Commit changes
    session.commit()

    # Return the session
    yield session

    # Clean up
    session.query(BudgetAlert).delete()
    session.query(Budget).delete()
    session.commit()
    session.close()
