"""
LiteLLM proxy server for token tracking and rate limiting.
"""

import os
import sys
import logging
import yaml
import uuid
import time
import datetime
from pathlib import Path
from typing import Dict, Optional
from sqlalchemy import func

# Import notification utilities
from utils.notifications import send_budget_alert, send_budget_exceeded

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("token_tracker.proxy")

# Try to import litellm
try:
    import litellm
    from litellm.proxy.proxy_server import ProxyConfig
    from fastapi import FastAPI, Request
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Import the models
    from database.models import TokenUsage, RateLimit, Budget, Base

    LITELLM_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.error("Please install the required dependencies: pip install -r requirements.txt")
    LITELLM_AVAILABLE = False

class TokenTrackingProxy:
    """
    LiteLLM proxy server with token tracking and rate limiting.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the proxy server.

        Args:
            config_path: Path to the configuration file.
        """
        self.config_path = config_path or str(Path(__file__).parent.parent / "config" / "proxy.yaml")
        self.config = self._load_config()

        if not self.config:
            logger.error("Failed to load configuration. Exiting.")
            sys.exit(1)

        # Initialize database
        self._init_database()

        # Initialize LiteLLM proxy
        self._init_proxy()

    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return None

    def _init_database(self):
        """Initialize database connection."""
        if not LITELLM_AVAILABLE:
            logger.error("LiteLLM is not available. Cannot initialize database.")
            return

        try:
            database_url = self.config.get("general", {}).get("database_url", "sqlite:///token_tracker.db")
            self.engine = create_engine(database_url)
            self.Session = sessionmaker(bind=self.engine)
            Base.metadata.create_all(self.engine)
            logger.info(f"Connected to database: {database_url}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            sys.exit(1)

    def _init_proxy(self):
        """Initialize LiteLLM proxy."""
        if not LITELLM_AVAILABLE:
            logger.error("LiteLLM is not available. Cannot initialize proxy.")
            return

        try:
            # Create proxy configuration
            self.proxy_config = ProxyConfig()

            # Set model list
            self.proxy_config.model_list = self.config.get("model_list", [])

            # Set rate limits
            rate_limits = []
            for rate_limit in self.config.get("rate_limits", []):
                rate_limits.append({
                    "model": rate_limit.get("model"),
                    "limit": rate_limit.get("limit"),
                    "window": rate_limit.get("period", "minute")
                })
            self.proxy_config.rate_limits = rate_limits

            # Set up logging
            log_level = self.config.get("logging", {}).get("level", "INFO")
            self.proxy_config.log_level = log_level

            # Create FastAPI app
            self.app = FastAPI()

            # Add middleware for token tracking
            @self.app.middleware("http")
            async def token_tracking_middleware(request: Request, call_next):
                # Generate request ID
                request_id = str(uuid.uuid4())
                request.state.request_id = request_id

                # Record start time
                start_time = time.time()

                # Process request
                response = await call_next(request)

                # Record end time
                end_time = time.time()
                latency = end_time - start_time

                # Track tokens if it's a completion request
                if request.url.path in ["/v1/chat/completions", "/v1/completions"]:
                    try:
                        # Get response data
                        response_data = getattr(request.state, "response_data", None)

                        if response_data:
                            # Extract token usage
                            usage = response_data.get("usage", {})
                            prompt_tokens = usage.get("prompt_tokens", 0)
                            completion_tokens = usage.get("completion_tokens", 0)
                            total_tokens = usage.get("total_tokens", 0)

                            # Extract model
                            model = response_data.get("model", "unknown")

                            # Calculate estimated cost
                            estimated_cost = self._calculate_cost(model, prompt_tokens, completion_tokens)

                            # Save token usage to database
                            self._save_token_usage(
                                request_id=request_id,
                                model=model,
                                prompt_tokens=prompt_tokens,
                                completion_tokens=completion_tokens,
                                total_tokens=total_tokens,
                                estimated_cost=estimated_cost,
                                endpoint=request.url.path,
                                status=response.status_code,
                                latency=latency
                            )
                    except Exception as e:
                        logger.error(f"Failed to track tokens: {e}")

                return response

            # Initialize LiteLLM proxy
            litellm.proxy.proxy_server.initialize_proxy(self.proxy_config)

            # Add routes from LiteLLM proxy
            self.app.include_router(litellm.proxy.proxy_server.router)

            logger.info("Initialized LiteLLM proxy")
        except Exception as e:
            logger.error(f"Failed to initialize LiteLLM proxy: {e}")
            sys.exit(1)

    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Calculate the estimated cost for token usage.

        Args:
            model: The model name.
            prompt_tokens: The number of prompt tokens.
            completion_tokens: The number of completion tokens.

        Returns:
            The estimated cost in USD.
        """
        try:
            # Get costs from config
            costs = self.config.get("costs", {})
            model_costs = costs.get(model, {})

            if model_costs:
                # Calculate cost from config
                input_cost = (prompt_tokens / 1000) * model_costs.get("input", 0.001)
                output_cost = (completion_tokens / 1000) * model_costs.get("output", 0.002)
                total_cost = input_cost + output_cost
            else:
                # Use default cost if model not found
                logger.warning(f"Model cost not found for {model}. Using default cost.")
                input_cost = (prompt_tokens / 1000) * 0.001
                output_cost = (completion_tokens / 1000) * 0.002
                total_cost = input_cost + output_cost

            return total_cost
        except Exception as e:
            logger.error(f"Failed to calculate cost: {e}")
            return 0.0

    def _save_token_usage(self, request_id: str, model: str, prompt_tokens: int,
                         completion_tokens: int, total_tokens: int, estimated_cost: float,
                         endpoint: str = None, status: int = None, latency: float = None):
        """
        Save token usage to database.

        Args:
            request_id: The request ID.
            model: The model name.
            prompt_tokens: The number of prompt tokens.
            completion_tokens: The number of completion tokens.
            total_tokens: The total number of tokens.
            estimated_cost: The estimated cost in USD.
            endpoint: The API endpoint.
            status: The response status code.
            latency: The request latency in seconds.
        """
        try:
            session = self.Session()

            # Create token usage record
            token_usage = TokenUsage(
                request_id=request_id,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost=estimated_cost,
                endpoint=endpoint,
                status=status,
                latency=latency
            )

            # Save to database
            session.add(token_usage)
            session.commit()

            logger.debug(f"Saved token usage: {model}, {total_tokens} tokens, ${estimated_cost:.6f}")

            # Check budget
            self._check_budget(session, estimated_cost)

            session.close()
        except Exception as e:
            logger.error(f"Failed to save token usage: {e}")

    def _check_budget(self, session, cost: float):
        """
        Check if the budget has been exceeded.

        Args:
            session: The database session.
            cost: The cost of the current request.
        """
        try:
            # Get total budget
            total_budget = session.query(Budget).filter_by(name="Total").first()

            if total_budget:
                # Calculate total cost
                total_cost = session.query(TokenUsage).with_entities(
                    func.sum(TokenUsage.estimated_cost)
                ).scalar() or 0

                # Add current cost
                total_cost += cost

                # Check if budget exceeded
                if total_cost > total_budget.amount:
                    logger.warning(f"Total budget exceeded: ${total_cost:.2f} / ${total_budget.amount:.2f}")
                    # Send budget exceeded notification
                    send_budget_exceeded(
                        budget_name="Total",
                        current_amount=total_cost,
                        budget_amount=total_budget.amount
                    )

                # Check budget alerts
                for alert in total_budget.alerts:
                    threshold_amount = total_budget.amount * (alert.threshold / 100)

                    if not alert.triggered and total_cost >= threshold_amount:
                        logger.warning(f"Budget alert triggered: {alert.threshold}% (${threshold_amount:.2f})")
                        # Send budget alert notification
                        send_budget_alert(
                            budget_name="Total",
                            threshold=alert.threshold,
                            current_amount=total_cost,
                            budget_amount=total_budget.amount,
                            to_email=alert.email
                        )

                        # Mark alert as triggered
                        alert.triggered = True
                        alert.last_triggered = datetime.datetime.now(datetime.timezone.utc)
                        session.commit()

            # Get daily budget
            daily_budget = session.query(Budget).filter_by(name="Daily").first()

            if daily_budget:
                # Calculate today's cost
                today = datetime.datetime.now(datetime.timezone.utc).date()
                today_start = datetime.datetime.combine(today, datetime.time.min)
                today_end = datetime.datetime.combine(today, datetime.time.max)

                daily_cost = session.query(TokenUsage).with_entities(
                    func.sum(TokenUsage.estimated_cost)
                ).filter(
                    TokenUsage.timestamp >= today_start,
                    TokenUsage.timestamp <= today_end
                ).scalar() or 0

                # Add current cost
                daily_cost += cost

                # Check if daily budget exceeded
                if daily_cost > daily_budget.amount:
                    logger.warning(f"Daily budget exceeded: ${daily_cost:.2f} / ${daily_budget.amount:.2f}")
                    # Send budget exceeded notification
                    send_budget_exceeded(
                        budget_name="Daily",
                        current_amount=daily_cost,
                        budget_amount=daily_budget.amount
                    )
        except Exception as e:
            logger.error(f"Failed to check budget: {e}")

    def run(self):
        """Run the proxy server."""
        if not LITELLM_AVAILABLE:
            logger.error("LiteLLM is not available. Cannot run proxy server.")
            return

        try:
            import uvicorn

            # Get host and port from config
            host = self.config.get("general", {}).get("host", "0.0.0.0")
            port = self.config.get("general", {}).get("port", 8000)

            # Run server
            logger.info(f"Starting proxy server on {host}:{port}")
            uvicorn.run(self.app, host=host, port=port)
        except Exception as e:
            logger.error(f"Failed to run proxy server: {e}")
            sys.exit(1)

def main():
    """Main function."""
    logger.info("Starting Token Tracking Proxy...")

    # Check if LiteLLM is available
    if not LITELLM_AVAILABLE:
        logger.error("LiteLLM is not available. Please install the required dependencies.")
        logger.error("pip install -r requirements.txt")
        sys.exit(1)

    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Create and run proxy
    proxy = TokenTrackingProxy()
    proxy.run()

if __name__ == "__main__":
    main()
