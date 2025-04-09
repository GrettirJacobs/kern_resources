"""
API for the Token Tracker.

This module provides a Flask API for programmatic access to the token tracker,
allowing retrieval of token usage data and management of rate limits and budgets.
"""

import os
import sys
import yaml
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS

# Import authentication utilities
from utils.auth import token_required, admin_required, generate_token, authenticate_user
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import from token_tracker
sys.path.append(str(Path(__file__).parent.parent))

from database.models import TokenUsage, RateLimit, Budget, ModelCost, Base
from database.init import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/api.log"),
    ],
)
logger = logging.getLogger("token_tracker.api")

# Load configuration
config_path = Path(__file__).parent.parent / "config" / "api.yaml"
try:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logger.info(f"Loaded configuration from {config_path}")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    config = {}

# Get configuration values
host = os.environ.get("API_HOST", config.get("general", {}).get("host", "0.0.0.0"))
port = int(os.environ.get("API_PORT", config.get("general", {}).get("port", 5000)))
debug = os.environ.get("API_DEBUG", config.get("general", {}).get("debug", True))

# Database configuration
database_url = os.environ.get("DATABASE_URL", config.get("database", {}).get("url", "sqlite:///token_tracker.db"))

# Initialize database
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()})


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login endpoint."""
    try:
        # Get request data
        data = request.json

        # Validate request data
        if not data or not data.get("username") or not data.get("password"):
            return jsonify({"error": "Missing username or password"}), 400

        # Authenticate user
        user = authenticate_user(data["username"], data["password"])

        if not user:
            return jsonify({"error": "Invalid username or password"}), 401

        # Generate token
        token = generate_token(user["username"], user["role"])

        # Return token
        return jsonify({
            "token": token,
            "user": {
                "username": user["username"],
                "role": user["role"],
            },
        })
    except Exception as e:
        logger.error(f"Failed to login: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/token-usage", methods=["GET"])
@token_required
def get_token_usage():
    """Get token usage data."""
    try:
        # Get query parameters
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        model = request.args.get("model")

        # Convert string dates to datetime objects
        if start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        else:
            start_datetime = datetime.datetime.now() - datetime.timedelta(days=7)

        if end_date:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
        else:
            end_datetime = datetime.datetime.now()

        # Create database session
        session = Session()

        # Build query
        query = session.query(TokenUsage).filter(
            TokenUsage.timestamp >= start_datetime,
            TokenUsage.timestamp <= end_datetime,
        )

        # Filter by model if provided
        if model:
            query = query.filter(TokenUsage.model == model)

        # Execute query
        token_usage = query.all()

        # Convert to dictionary
        result = [
            {
                "id": item.id,
                "request_id": item.request_id,
                "timestamp": item.timestamp.isoformat(),
                "model": item.model,
                "prompt_tokens": item.prompt_tokens,
                "completion_tokens": item.completion_tokens,
                "total_tokens": item.total_tokens,
                "estimated_cost": item.estimated_cost,
                "endpoint": item.endpoint,
                "status": item.status,
                "latency": item.latency,
            }
            for item in token_usage
        ]

        # Close the session
        session.close()

        return jsonify(result)
    except Exception as e:
        logger.error(f"Failed to get token usage: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/token-usage/summary", methods=["GET"])
@token_required
def get_token_usage_summary():
    """Get token usage summary."""
    try:
        # Get query parameters
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        # Convert string dates to datetime objects
        if start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        else:
            start_datetime = datetime.datetime.now() - datetime.timedelta(days=7)

        if end_date:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
        else:
            end_datetime = datetime.datetime.now()

        # Create database session
        session = Session()

        # Get token usage summary
        token_usage_summary = (
            session.query(
                func.sum(TokenUsage.prompt_tokens).label("prompt_tokens"),
                func.sum(TokenUsage.completion_tokens).label("completion_tokens"),
                func.sum(TokenUsage.total_tokens).label("total_tokens"),
                func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
                func.count(TokenUsage.id).label("request_count"),
            )
            .filter(TokenUsage.timestamp >= start_datetime, TokenUsage.timestamp <= end_datetime)
            .first()
        )

        # Get token usage by model
        token_usage_by_model = (
            session.query(
                TokenUsage.model,
                func.sum(TokenUsage.prompt_tokens).label("prompt_tokens"),
                func.sum(TokenUsage.completion_tokens).label("completion_tokens"),
                func.sum(TokenUsage.total_tokens).label("total_tokens"),
                func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
                func.count(TokenUsage.id).label("request_count"),
            )
            .filter(TokenUsage.timestamp >= start_datetime, TokenUsage.timestamp <= end_datetime)
            .group_by(TokenUsage.model)
            .all()
        )

        # Get token usage by day
        token_usage_by_day = (
            session.query(
                func.date(TokenUsage.timestamp).label("date"),
                func.sum(TokenUsage.prompt_tokens).label("prompt_tokens"),
                func.sum(TokenUsage.completion_tokens).label("completion_tokens"),
                func.sum(TokenUsage.total_tokens).label("total_tokens"),
                func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
                func.count(TokenUsage.id).label("request_count"),
            )
            .filter(TokenUsage.timestamp >= start_datetime, TokenUsage.timestamp <= end_datetime)
            .group_by(func.date(TokenUsage.timestamp))
            .all()
        )

        # Create result
        result = {
            "summary": {
                "prompt_tokens": token_usage_summary.prompt_tokens or 0,
                "completion_tokens": token_usage_summary.completion_tokens or 0,
                "total_tokens": token_usage_summary.total_tokens or 0,
                "estimated_cost": token_usage_summary.estimated_cost or 0,
                "request_count": token_usage_summary.request_count or 0,
            },
            "by_model": [
                {
                    "model": item.model,
                    "prompt_tokens": item.prompt_tokens or 0,
                    "completion_tokens": item.completion_tokens or 0,
                    "total_tokens": item.total_tokens or 0,
                    "estimated_cost": item.estimated_cost or 0,
                    "request_count": item.request_count or 0,
                }
                for item in token_usage_by_model
            ],
            "by_day": [
                {
                    "date": item.date.isoformat(),
                    "prompt_tokens": item.prompt_tokens or 0,
                    "completion_tokens": item.completion_tokens or 0,
                    "total_tokens": item.total_tokens or 0,
                    "estimated_cost": item.estimated_cost or 0,
                    "request_count": item.request_count or 0,
                }
                for item in token_usage_by_day
            ],
        }

        # Close the session
        session.close()

        return jsonify(result)
    except Exception as e:
        logger.error(f"Failed to get token usage summary: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/rate-limits", methods=["GET"])
@token_required
def get_rate_limits():
    """Get rate limits."""
    try:
        # Create database session
        session = Session()

        # Get rate limits
        rate_limits = session.query(RateLimit).all()

        # Convert to dictionary
        result = [
            {
                "id": item.id,
                "model": item.model,
                "limit": item.limit,
                "period": item.period,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat(),
            }
            for item in rate_limits
        ]

        # Close the session
        session.close()

        return jsonify(result)
    except Exception as e:
        logger.error(f"Failed to get rate limits: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/rate-limits", methods=["POST"])
@admin_required
def create_rate_limit():
    """Create or update a rate limit."""
    try:
        # Get request data
        data = request.json

        # Validate request data
        if not data or not data.get("model") or not data.get("limit") or not data.get("period"):
            return jsonify({"error": "Missing required fields"}), 400

        # Create database session
        session = Session()

        # Check if rate limit exists
        rate_limit = session.query(RateLimit).filter_by(model=data["model"]).first()

        if rate_limit:
            # Update existing rate limit
            rate_limit.limit = data["limit"]
            rate_limit.period = data["period"]
            rate_limit.updated_at = datetime.datetime.now(datetime.timezone.utc)
            message = f"Updated rate limit for {data['model']}"
        else:
            # Create new rate limit
            rate_limit = RateLimit(
                model=data["model"],
                limit=data["limit"],
                period=data["period"],
            )
            session.add(rate_limit)
            message = f"Created rate limit for {data['model']}"

        # Commit changes
        session.commit()

        # Get updated rate limit
        result = {
            "id": rate_limit.id,
            "model": rate_limit.model,
            "limit": rate_limit.limit,
            "period": rate_limit.period,
            "created_at": rate_limit.created_at.isoformat(),
            "updated_at": rate_limit.updated_at.isoformat(),
            "message": message,
        }

        # Close the session
        session.close()

        return jsonify(result)
    except Exception as e:
        logger.error(f"Failed to create rate limit: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/budgets", methods=["GET"])
@token_required
def get_budgets():
    """Get budgets."""
    try:
        # Create database session
        session = Session()

        # Get budgets
        budgets = session.query(Budget).all()

        # Convert to dictionary
        result = [
            {
                "id": item.id,
                "name": item.name,
                "amount": item.amount,
                "period": item.period,
                "reset_day": item.reset_day,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat(),
            }
            for item in budgets
        ]

        # Close the session
        session.close()

        return jsonify(result)
    except Exception as e:
        logger.error(f"Failed to get budgets: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/budgets", methods=["POST"])
@admin_required
def create_budget():
    """Create or update a budget."""
    try:
        # Get request data
        data = request.json

        # Validate request data
        if not data or not data.get("name") or not data.get("amount") or not data.get("period"):
            return jsonify({"error": "Missing required fields"}), 400

        # Create database session
        session = Session()

        # Check if budget exists
        budget = session.query(Budget).filter_by(name=data["name"]).first()

        if budget:
            # Update existing budget
            budget.amount = data["amount"]
            budget.period = data["period"]
            budget.reset_day = data.get("reset_day")
            budget.updated_at = datetime.datetime.now(datetime.timezone.utc)
            message = f"Updated {data['name']} budget"
        else:
            # Create new budget
            budget = Budget(
                name=data["name"],
                amount=data["amount"],
                period=data["period"],
                reset_day=data.get("reset_day"),
            )
            session.add(budget)
            message = f"Created {data['name']} budget"

        # Commit changes
        session.commit()

        # Get updated budget
        result = {
            "id": budget.id,
            "name": budget.name,
            "amount": budget.amount,
            "period": budget.period,
            "reset_day": budget.reset_day,
            "created_at": budget.created_at.isoformat(),
            "updated_at": budget.updated_at.isoformat(),
            "message": message,
        }

        # Close the session
        session.close()

        return jsonify(result)
    except Exception as e:
        logger.error(f"Failed to create budget: {e}")
        return jsonify({"error": str(e)}), 500


# Run the app
if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Initialize the database
    init_database(database_url)

    # Run the app
    app.run(host=host, port=port, debug=debug)
