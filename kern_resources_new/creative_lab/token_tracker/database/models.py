"""
Database models for token tracking.
"""

import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

# Create the base class
Base = declarative_base()

class TokenUsage(Base):
    """
    Model for tracking token usage.
    """
    __tablename__ = "token_usage"

    id = Column(Integer, primary_key=True)
    request_id = Column(String(36), nullable=False)  # UUID
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    model = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    user_id = Column(String(100), nullable=True)
    endpoint = Column(String(100), nullable=True)
    status = Column(String(20), nullable=True)
    latency = Column(Float, nullable=True)  # in seconds
    request_metadata = Column(JSON, nullable=True)  # Renamed from metadata to avoid conflict with SQLAlchemy

    def __repr__(self):
        return f"<TokenUsage(id={self.id}, model={self.model}, total_tokens={self.total_tokens})>"

class RateLimit(Base):
    """
    Model for storing rate limit configurations.
    """
    __tablename__ = "rate_limits"

    id = Column(Integer, primary_key=True)
    model = Column(String(100), nullable=False, unique=True)
    limit = Column(Integer, nullable=False)
    period = Column(String(20), nullable=False)  # minute, hour, day
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return f"<RateLimit(model={self.model}, limit={self.limit}, period={self.period})>"

class Budget(Base):
    """
    Model for storing budget configurations.
    """
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    amount = Column(Float, nullable=False)
    period = Column(String(20), nullable=False)  # daily, monthly, total
    reset_day = Column(Integer, nullable=True)  # day of month for monthly reset
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    alerts = relationship("BudgetAlert", back_populates="budget", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Budget(name={self.name}, amount={self.amount}, period={self.period})>"

class BudgetAlert(Base):
    """
    Model for storing budget alert configurations.
    """
    __tablename__ = "budget_alerts"

    id = Column(Integer, primary_key=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    threshold = Column(Float, nullable=False)  # percentage (0-100)
    email = Column(String(100), nullable=True)
    slack_webhook = Column(String(200), nullable=True)
    triggered = Column(Boolean, default=False)
    last_triggered = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    budget = relationship("Budget", back_populates="alerts")

    def __repr__(self):
        return f"<BudgetAlert(budget_id={self.budget_id}, threshold={self.threshold})>"

class ModelCost(Base):
    """
    Model for storing cost per token for different models.
    """
    __tablename__ = "model_costs"

    id = Column(Integer, primary_key=True)
    model = Column(String(100), nullable=False, unique=True)
    input_cost = Column(Float, nullable=False)  # cost per 1000 tokens
    output_cost = Column(Float, nullable=False)  # cost per 1000 tokens
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return f"<ModelCost(model={self.model}, input_cost={self.input_cost}, output_cost={self.output_cost})>"

class User(Base):
    """
    Model for storing user information.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(200), nullable=False)
    email = Column(String(100), nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return f"<User(username={self.username}, is_admin={self.is_admin})>"

class ApiKey(Base):
    """
    Model for storing API keys.
    """
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<ApiKey(name={self.name}, user_id={self.user_id})>"
