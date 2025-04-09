"""
Dashboard application for the Token Tracker.

This module provides a Dash application for visualizing token usage,
managing rate limits, and monitoring budgets.
"""

import os
import sys
import yaml
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash_auth
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
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
        logging.FileHandler("logs/dashboard.log"),
    ],
)
logger = logging.getLogger("token_tracker.dashboard")

# Load configuration
config_path = Path(__file__).parent.parent / "config" / "dashboard.yaml"
try:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logger.info(f"Loaded configuration from {config_path}")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    config = {}

# Get configuration values
host = os.environ.get("DASHBOARD_HOST", config.get("general", {}).get("host", "0.0.0.0"))
port = int(os.environ.get("DASHBOARD_PORT", config.get("general", {}).get("port", 8050)))
debug = os.environ.get("DASHBOARD_DEBUG", config.get("general", {}).get("debug", True))
title = os.environ.get("DASHBOARD_TITLE", config.get("general", {}).get("title", "Token Tracker"))
theme = config.get("general", {}).get("theme", "bootstrap")
refresh_interval = config.get("general", {}).get("refresh_interval", 60)

# Database configuration
database_url = os.environ.get("DATABASE_URL", config.get("database", {}).get("url", "sqlite:///token_tracker.db"))

# Authentication configuration
auth_enabled = config.get("auth", {}).get("enabled", True)
auth_users = config.get("auth", {}).get("users", {"admin": "admin"})

# Override auth users from environment variables
dashboard_username = os.environ.get("DASHBOARD_USERNAME")
dashboard_password = os.environ.get("DASHBOARD_PASSWORD")
if dashboard_username and dashboard_password:
    auth_users = {dashboard_username: dashboard_password}

# UI configuration
ui_config = config.get("ui", {})
colors = ui_config.get("colors", {})
default_date_range = ui_config.get("default_date_range", 7)
chart_config = ui_config.get("charts", {})

# Initialize database
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title=title,
    update_title=None,
    suppress_callback_exceptions=True,
)

# Add authentication if enabled
if auth_enabled and auth_users:
    auth = dash_auth.BasicAuth(app, auth_users)

# Define the layout
app.layout = dbc.Container(
    [
        dcc.Interval(
            id="interval-component",
            interval=refresh_interval * 1000,  # in milliseconds
            n_intervals=0,
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.H1(title, className="text-center mb-4"),
                    width=12,
                ),
            ],
            className="mt-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Date Range"),
                                dbc.CardBody(
                                    [
                                        dcc.DatePickerRange(
                                            id="date-picker-range",
                                            start_date=(
                                                datetime.datetime.now() - datetime.timedelta(days=default_date_range)
                                            ).date(),
                                            end_date=datetime.datetime.now().date(),
                                            display_format="YYYY-MM-DD",
                                        ),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "Last 7 Days",
                                                    id="btn-last-7-days",
                                                    color="primary",
                                                    className="me-2",
                                                    size="sm",
                                                ),
                                                dbc.Button(
                                                    "Last 30 Days",
                                                    id="btn-last-30-days",
                                                    color="primary",
                                                    className="me-2",
                                                    size="sm",
                                                ),
                                                dbc.Button(
                                                    "This Month",
                                                    id="btn-this-month",
                                                    color="primary",
                                                    className="me-2",
                                                    size="sm",
                                                ),
                                            ],
                                            className="mt-2",
                                        ),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Card(
                            [
                                dbc.CardHeader("Summary"),
                                dbc.CardBody(id="summary-card"),
                            ],
                            className="mb-4",
                        ),
                    ],
                    width=12,
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Token Usage"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="token-usage-chart"),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Estimated Cost"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="cost-chart"),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                    ],
                    width=6,
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Model Distribution"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="model-distribution-chart"),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Rate Limit Usage"),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(id="rate-limit-chart"),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                    ],
                    width=6,
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Rate Limits"),
                                dbc.CardBody(
                                    [
                                        html.Div(id="rate-limits-table"),
                                        html.Hr(),
                                        html.H5("Update Rate Limit"),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Model"),
                                                        dcc.Dropdown(
                                                            id="rate-limit-model-dropdown",
                                                            placeholder="Select a model",
                                                        ),
                                                    ],
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Limit"),
                                                        dbc.Input(
                                                            id="rate-limit-value-input",
                                                            type="number",
                                                            min=1,
                                                            step=1,
                                                        ),
                                                    ],
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Period"),
                                                        dcc.Dropdown(
                                                            id="rate-limit-period-dropdown",
                                                            options=[
                                                                {"label": "Minute", "value": "minute"},
                                                                {"label": "Hour", "value": "hour"},
                                                                {"label": "Day", "value": "day"},
                                                            ],
                                                            value="minute",
                                                        ),
                                                    ],
                                                    width=4,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Button(
                                            "Update Rate Limit",
                                            id="update-rate-limit-button",
                                            color="primary",
                                        ),
                                        html.Div(id="update-rate-limit-result", className="mt-2"),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Budget Settings"),
                                dbc.CardBody(
                                    [
                                        html.Div(id="budget-table"),
                                        html.Hr(),
                                        html.H5("Update Budget"),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Budget Type"),
                                                        dcc.Dropdown(
                                                            id="budget-type-dropdown",
                                                            options=[
                                                                {"label": "Total", "value": "Total"},
                                                                {"label": "Daily", "value": "Daily"},
                                                            ],
                                                            value="Total",
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Amount (USD)"),
                                                        dbc.Input(
                                                            id="budget-amount-input",
                                                            type="number",
                                                            min=0,
                                                            step=0.01,
                                                        ),
                                                    ],
                                                    width=6,
                                                ),
                                            ],
                                            className="mb-3",
                                        ),
                                        dbc.Button(
                                            "Update Budget",
                                            id="update-budget-button",
                                            color="primary",
                                        ),
                                        html.Div(id="update-budget-result", className="mt-2"),
                                    ]
                                ),
                            ],
                            className="mb-4",
                        ),
                    ],
                    width=6,
                ),
            ],
        ),
    ],
    fluid=True,
    className="mt-4",
)


# Define callbacks
@app.callback(
    [
        Output("date-picker-range", "start_date"),
        Output("date-picker-range", "end_date"),
    ],
    [
        Input("btn-last-7-days", "n_clicks"),
        Input("btn-last-30-days", "n_clicks"),
        Input("btn-this-month", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def update_date_range(last_7_days, last_30_days, this_month):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    end_date = datetime.datetime.now().date()
    
    if button_id == "btn-last-7-days":
        start_date = end_date - datetime.timedelta(days=7)
    elif button_id == "btn-last-30-days":
        start_date = end_date - datetime.timedelta(days=30)
    elif button_id == "btn-this-month":
        start_date = end_date.replace(day=1)
    else:
        return dash.no_update, dash.no_update
    
    return start_date, end_date


@app.callback(
    [
        Output("summary-card", "children"),
        Output("token-usage-chart", "figure"),
        Output("cost-chart", "figure"),
        Output("model-distribution-chart", "figure"),
        Output("rate-limit-chart", "figure"),
        Output("rate-limits-table", "children"),
        Output("budget-table", "children"),
        Output("rate-limit-model-dropdown", "options"),
    ],
    [
        Input("interval-component", "n_intervals"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    ],
)
def update_dashboard(n_intervals, start_date, end_date):
    """Update the dashboard with the latest data."""
    try:
        # Convert string dates to datetime objects
        if isinstance(start_date, str):
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # Add time to dates
        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
        
        # Create database session
        session = Session()
        
        # Get token usage data
        token_usage_data = (
            session.query(
                func.date(TokenUsage.timestamp).label("date"),
                func.sum(TokenUsage.prompt_tokens).label("prompt_tokens"),
                func.sum(TokenUsage.completion_tokens).label("completion_tokens"),
                func.sum(TokenUsage.total_tokens).label("total_tokens"),
                func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
            )
            .filter(TokenUsage.timestamp >= start_datetime, TokenUsage.timestamp <= end_datetime)
            .group_by(func.date(TokenUsage.timestamp))
            .all()
        )
        
        # Get model distribution data
        model_distribution_data = (
            session.query(
                TokenUsage.model,
                func.sum(TokenUsage.total_tokens).label("total_tokens"),
                func.sum(TokenUsage.estimated_cost).label("estimated_cost"),
            )
            .filter(TokenUsage.timestamp >= start_datetime, TokenUsage.timestamp <= end_datetime)
            .group_by(TokenUsage.model)
            .all()
        )
        
        # Get rate limit data
        rate_limits = session.query(RateLimit).all()
        
        # Get budget data
        budgets = session.query(Budget).all()
        
        # Calculate summary statistics
        total_tokens = sum(row.total_tokens for row in token_usage_data) if token_usage_data else 0
        total_cost = sum(row.estimated_cost for row in token_usage_data) if token_usage_data else 0
        total_requests = (
            session.query(func.count(TokenUsage.id))
            .filter(TokenUsage.timestamp >= start_datetime, TokenUsage.timestamp <= end_datetime)
            .scalar()
        ) or 0
        
        # Create summary card
        summary_card = dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4(f"{total_tokens:,}"),
                        html.P("Total Tokens"),
                    ],
                    width=4,
                    className="text-center",
                ),
                dbc.Col(
                    [
                        html.H4(f"${total_cost:.2f}"),
                        html.P("Total Cost"),
                    ],
                    width=4,
                    className="text-center",
                ),
                dbc.Col(
                    [
                        html.H4(f"{total_requests:,}"),
                        html.P("Total Requests"),
                    ],
                    width=4,
                    className="text-center",
                ),
            ]
        )
        
        # Create token usage chart
        token_usage_df = pd.DataFrame(token_usage_data)
        if not token_usage_df.empty:
            token_usage_chart = px.bar(
                token_usage_df,
                x="date",
                y=["prompt_tokens", "completion_tokens"],
                title="Token Usage by Date",
                labels={"value": "Tokens", "date": "Date", "variable": "Token Type"},
                color_discrete_map={"prompt_tokens": colors.get("primary", "#007BFF"), "completion_tokens": colors.get("info", "#17A2B8")},
                barmode="stack",
            )
        else:
            token_usage_chart = go.Figure()
            token_usage_chart.update_layout(
                title="Token Usage by Date",
                xaxis_title="Date",
                yaxis_title="Tokens",
            )
        
        # Create cost chart
        if not token_usage_df.empty:
            cost_chart = px.line(
                token_usage_df,
                x="date",
                y="estimated_cost",
                title="Estimated Cost by Date",
                labels={"estimated_cost": "Cost (USD)", "date": "Date"},
                color_discrete_sequence=[colors.get("success", "#28A745")],
            )
            
            # Add cumulative cost line
            token_usage_df["cumulative_cost"] = token_usage_df["estimated_cost"].cumsum()
            cost_chart.add_scatter(
                x=token_usage_df["date"],
                y=token_usage_df["cumulative_cost"],
                mode="lines",
                name="Cumulative Cost",
                line=dict(color=colors.get("warning", "#FFC107")),
            )
        else:
            cost_chart = go.Figure()
            cost_chart.update_layout(
                title="Estimated Cost by Date",
                xaxis_title="Date",
                yaxis_title="Cost (USD)",
            )
        
        # Create model distribution chart
        model_distribution_df = pd.DataFrame(model_distribution_data)
        if not model_distribution_df.empty:
            model_distribution_chart = px.pie(
                model_distribution_df,
                values="total_tokens",
                names="model",
                title="Token Usage by Model",
                hole=0.4,
            )
        else:
            model_distribution_chart = go.Figure()
            model_distribution_chart.update_layout(
                title="Token Usage by Model",
            )
        
        # Create rate limit chart
        # This is a placeholder for now, as we don't have rate limit usage data yet
        rate_limit_chart = go.Figure()
        rate_limit_chart.update_layout(
            title="Rate Limit Usage",
            xaxis_title="Time",
            yaxis_title="Requests",
        )
        
        # Create rate limits table
        rate_limits_table = dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Model"),
                            html.Th("Limit"),
                            html.Th("Period"),
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(rate_limit.model),
                                html.Td(rate_limit.limit),
                                html.Td(rate_limit.period),
                            ]
                        )
                        for rate_limit in rate_limits
                    ]
                ),
            ],
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
        )
        
        # Create budget table
        budget_table = dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Name"),
                            html.Th("Amount (USD)"),
                            html.Th("Period"),
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(budget.name),
                                html.Td(f"${budget.amount:.2f}"),
                                html.Td(budget.period),
                            ]
                        )
                        for budget in budgets
                    ]
                ),
            ],
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
        )
        
        # Create model dropdown options
        model_options = [{"label": rate_limit.model, "value": rate_limit.model} for rate_limit in rate_limits]
        
        # Close the session
        session.close()
        
        return (
            summary_card,
            token_usage_chart,
            cost_chart,
            model_distribution_chart,
            rate_limit_chart,
            rate_limits_table,
            budget_table,
            model_options,
        )
    except Exception as e:
        logger.error(f"Failed to update dashboard: {e}")
        return (
            html.Div("Error loading summary"),
            go.Figure(),
            go.Figure(),
            go.Figure(),
            go.Figure(),
            html.Div("Error loading rate limits"),
            html.Div("Error loading budgets"),
            [],
        )


@app.callback(
    [
        Output("update-rate-limit-result", "children"),
        Output("rate-limit-model-dropdown", "value"),
        Output("rate-limit-value-input", "value"),
    ],
    [
        Input("update-rate-limit-button", "n_clicks"),
    ],
    [
        State("rate-limit-model-dropdown", "value"),
        State("rate-limit-value-input", "value"),
        State("rate-limit-period-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def update_rate_limit(n_clicks, model, limit, period):
    """Update a rate limit."""
    if not model or not limit or not period:
        return dbc.Alert("Please fill in all fields", color="danger"), dash.no_update, dash.no_update
    
    try:
        # Create database session
        session = Session()
        
        # Check if rate limit exists
        rate_limit = session.query(RateLimit).filter_by(model=model).first()
        
        if rate_limit:
            # Update existing rate limit
            rate_limit.limit = limit
            rate_limit.period = period
            rate_limit.updated_at = datetime.datetime.utcnow()
            message = f"Updated rate limit for {model}"
        else:
            # Create new rate limit
            rate_limit = RateLimit(model=model, limit=limit, period=period)
            session.add(rate_limit)
            message = f"Created rate limit for {model}"
        
        # Commit changes
        session.commit()
        session.close()
        
        return dbc.Alert(message, color="success"), None, None
    except Exception as e:
        logger.error(f"Failed to update rate limit: {e}")
        return dbc.Alert(f"Error: {str(e)}", color="danger"), dash.no_update, dash.no_update


@app.callback(
    [
        Output("update-budget-result", "children"),
        Output("budget-type-dropdown", "value"),
        Output("budget-amount-input", "value"),
    ],
    [
        Input("update-budget-button", "n_clicks"),
    ],
    [
        State("budget-type-dropdown", "value"),
        State("budget-amount-input", "value"),
    ],
    prevent_initial_call=True,
)
def update_budget(n_clicks, budget_type, amount):
    """Update a budget."""
    if not budget_type or not amount:
        return dbc.Alert("Please fill in all fields", color="danger"), dash.no_update, dash.no_update
    
    try:
        # Create database session
        session = Session()
        
        # Check if budget exists
        budget = session.query(Budget).filter_by(name=budget_type).first()
        
        if budget:
            # Update existing budget
            budget.amount = amount
            budget.updated_at = datetime.datetime.utcnow()
            message = f"Updated {budget_type} budget to ${amount:.2f}"
        else:
            # Create new budget
            period = "total" if budget_type == "Total" else "daily"
            budget = Budget(name=budget_type, amount=amount, period=period)
            session.add(budget)
            message = f"Created {budget_type} budget of ${amount:.2f}"
        
        # Commit changes
        session.commit()
        session.close()
        
        return dbc.Alert(message, color="success"), None, None
    except Exception as e:
        logger.error(f"Failed to update budget: {e}")
        return dbc.Alert(f"Error: {str(e)}", color="danger"), dash.no_update, dash.no_update


# Run the app
if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Initialize the database
    init_database(database_url)
    
    # Run the app
    app.run_server(host=host, port=port, debug=debug)
