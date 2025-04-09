"""
Main script for running the Token Tracker.

This script provides a command-line interface for running the Token Tracker
components (proxy, dashboard, and API).
"""

import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("token_tracker")

def run_proxy():
    """Run the LiteLLM proxy server."""
    logger.info("Starting Token Tracker proxy...")
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run the proxy server
    from proxy.server import main
    main()

def run_dashboard():
    """Run the dashboard application."""
    logger.info("Starting Token Tracker dashboard...")
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run the dashboard
    from dashboard.app import app
    
    # Get host and port from environment variables or config
    import yaml
    config_path = Path(__file__).parent / "config" / "dashboard.yaml"
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        host = os.environ.get("DASHBOARD_HOST", config.get("general", {}).get("host", "0.0.0.0"))
        port = int(os.environ.get("DASHBOARD_PORT", config.get("general", {}).get("port", 8050)))
        debug = os.environ.get("DASHBOARD_DEBUG", config.get("general", {}).get("debug", True))
    except Exception as e:
        logger.error(f"Failed to load dashboard configuration: {e}")
        host = "0.0.0.0"
        port = 8050
        debug = True
    
    # Run the app
    app.run_server(host=host, port=port, debug=debug)

def run_api():
    """Run the API server."""
    logger.info("Starting Token Tracker API...")
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run the API
    from api.app import app
    
    # Get host and port from environment variables or config
    import yaml
    config_path = Path(__file__).parent / "config" / "api.yaml"
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        host = os.environ.get("API_HOST", config.get("general", {}).get("host", "0.0.0.0"))
        port = int(os.environ.get("API_PORT", config.get("general", {}).get("port", 5000)))
        debug = os.environ.get("API_DEBUG", config.get("general", {}).get("debug", True))
    except Exception as e:
        logger.error(f"Failed to load API configuration: {e}")
        host = "0.0.0.0"
        port = 5000
        debug = True
    
    # Run the app
    app.run(host=host, port=port, debug=debug)

def run_all():
    """Run all Token Tracker components."""
    logger.info("Starting all Token Tracker components...")
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run the components in separate processes
    proxy_process = subprocess.Popen([sys.executable, "-m", "token_tracker.proxy.server"])
    api_process = subprocess.Popen([sys.executable, "-m", "token_tracker.api.app"])
    dashboard_process = subprocess.Popen([sys.executable, "-m", "token_tracker.dashboard.app"])
    
    try:
        # Wait for the processes to complete
        proxy_process.wait()
        api_process.wait()
        dashboard_process.wait()
    except KeyboardInterrupt:
        logger.info("Stopping Token Tracker components...")
        
        # Terminate the processes
        proxy_process.terminate()
        api_process.terminate()
        dashboard_process.terminate()
        
        # Wait for the processes to terminate
        proxy_process.wait()
        api_process.wait()
        dashboard_process.wait()
        
        logger.info("Token Tracker components stopped.")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Token Tracker")
    parser.add_argument(
        "component",
        choices=["proxy", "dashboard", "api", "all"],
        help="The component to run",
    )
    
    args = parser.parse_args()
    
    if args.component == "proxy":
        run_proxy()
    elif args.component == "dashboard":
        run_dashboard()
    elif args.component == "api":
        run_api()
    elif args.component == "all":
        run_all()

if __name__ == "__main__":
    main()
