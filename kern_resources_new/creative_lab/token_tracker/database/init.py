"""
Database initialization script.
"""

import os
import sys
import logging
import yaml
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the models
from database.models import Base, RateLimit, Budget, BudgetAlert, ModelCost

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from YAML file."""
    config_path = Path(__file__).parent.parent / "config" / "proxy.yaml"

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return None

def init_db(database_url=None):
    """Initialize the database."""
    # Load configuration
    config = load_config()
    if not config:
        logger.error("Failed to load configuration. Exiting.")
        return False

    # Get database URL from config or parameter
    if not database_url:
        database_url = config.get("general", {}).get("database_url", "sqlite:///token_tracker.db")

    # Create engine and session
    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Create tables
        Base.metadata.create_all(engine)
        logger.info(f"Created database tables in {database_url}")

        # Initialize rate limits
        init_rate_limits(session, config)

        # Initialize budget
        init_budget(session, config)

        # Initialize model costs
        init_model_costs(session, config)

        # Initialize admin user
        init_admin_user(session)

        session.close()
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def init_rate_limits(session, config):
    """Initialize rate limits from configuration."""
    try:
        # Clear existing rate limits
        session.query(RateLimit).delete()

        # Add rate limits from config
        rate_limits = config.get("rate_limits", [])
        for rate_limit in rate_limits:
            model = rate_limit.get("model")
            limit = rate_limit.get("limit")
            period = rate_limit.get("period")

            if model and limit and period:
                session.add(RateLimit(model=model, limit=limit, period=period))

        session.commit()
        logger.info(f"Initialized {len(rate_limits)} rate limits")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to initialize rate limits: {e}")

def init_budget(session, config):
    """Initialize budget from configuration."""
    try:
        # Clear existing budgets
        session.query(Budget).delete()

        # Add budget from config
        budget_config = config.get("budget", {})
        total_budget = budget_config.get("total")
        daily_budget = budget_config.get("daily")

        if total_budget:
            total = Budget(name="Total", amount=total_budget, period="total")
            session.add(total)

            # Add budget alerts
            alerts = budget_config.get("alerts", [])
            for alert in alerts:
                threshold = alert.get("threshold")
                email = alert.get("email")

                if threshold and email:
                    session.add(BudgetAlert(budget=total, threshold=threshold, email=email))

        if daily_budget:
            session.add(Budget(name="Daily", amount=daily_budget, period="daily"))

        session.commit()
        logger.info("Initialized budget settings")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to initialize budget: {e}")

def init_model_costs(session, config):
    """Initialize model costs from configuration."""
    try:
        # Clear existing model costs
        session.query(ModelCost).delete()

        # Add model costs from config
        costs = config.get("costs", {})
        for model, cost in costs.items():
            input_cost = cost.get("input", 0)
            output_cost = cost.get("output", 0)

            session.add(ModelCost(model=model, input_cost=input_cost, output_cost=output_cost))

        session.commit()
        logger.info(f"Initialized costs for {len(costs)} models")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to initialize model costs: {e}")

def init_admin_user(session):
    """Initialize admin user."""
    # Admin user initialization is handled by the auth module
    pass

def init_database(database_url=None):
    """Initialize the database. This is the main entry point for database initialization."""
    return init_db(database_url)

if __name__ == "__main__":
    logger.info("Initializing database...")
    success = init_database()

    if success:
        logger.info("Database initialization complete")
    else:
        logger.error("Database initialization failed")
        sys.exit(1)
