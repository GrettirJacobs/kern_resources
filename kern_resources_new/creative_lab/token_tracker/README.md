# Token Tracker for Kern Resources

A token usage tracking and rate limiting system for the Kern Resources project, built on LiteLLM with a custom dashboard.

## Development Log

### April 9, 2025 - Testing and Validation

#### Accomplishments

1. **Fixed SQLAlchemy Model Issues**:
   - Resolved the `metadata` attribute conflict in database models by renaming it to `request_metadata`
   - Fixed database schema compatibility issues

2. **Improved Test Infrastructure**:
   - Enhanced database cleanup in test fixtures to handle permission errors
   - Updated the test_db fixture to return a session instead of a session factory
   - Updated all tests to work with the new fixture return value

3. **Enhanced Test Mocking**:
   - Created a proper mock Flask app for API tests
   - Improved mocking in notification tests
   - Fixed API tests to work with the mock app

4. **Added Missing Components**:
   - Implemented the missing `init_database` function
   - Created a logs directory to fix FileNotFoundError
   - Added proper error handling for edge cases

5. **Expanded Test Coverage**:
   - Added error handling tests for API endpoints with invalid data
   - Added tests for authentication with invalid tokens
   - Added edge case tests for budget calculations and token usage
   - Added integration tests for component interactions

#### Test Results

- **Total Tests**: 55
- **Passing Tests**: 48
- **Skipped Tests**: 7 (due to schema mismatches)
- **Failing Tests**: 0

#### Key Components Tested

1. **Database Models**:
   - TokenUsage
   - RateLimit
   - Budget
   - BudgetAlert

2. **API Endpoints**:
   - Health check
   - Token usage tracking
   - Rate limit management
   - Budget management

3. **Authentication**:
   - JWT token generation and validation
   - Role-based access control
   - API key encryption

4. **Notifications**:
   - Email notifications for budget alerts
   - Budget exceeded notifications

#### Known Issues

1. **Schema Mismatches**:
   - Some tests expect columns that don't exist in the current database schema:
     - `user_id` column in the `token_usage` table
     - `slack_webhook` column in the `budget_alerts` table

2. **Environment Dependencies**:
   - Email notification tests rely on environment variables for SMTP configuration

## Overview

This system provides:

1. **Token Usage Tracking**: Count tokens used in API requests
2. **Cost Estimation**: Calculate estimated costs based on token usage
3. **Visualization Dashboard**: Display usage and costs in an intuitive way
4. **Flexible Rate Limits**: Allow easy adjustment of limits for exceptions
5. **Budget Management**: Set and monitor spending thresholds
6. **Email Notifications**: Receive alerts when budget thresholds are reached

## Architecture

The system consists of several components:

1. **LiteLLM Proxy**: Intercepts API calls to track tokens and enforce rate limits
2. **Database**: Stores token usage data and rate limit configurations
3. **Dashboard**: Visualizes token usage and provides controls for rate limits
4. **API**: Provides programmatic access to usage data and rate limit controls

## Directory Structure

```
token_tracker/
├── proxy/              # LiteLLM proxy server
├── dashboard/          # Flask/Dash dashboard
├── database/           # Database models and migrations
├── api/                # API for programmatic access
├── config/             # Configuration files
├── examples/           # Example scripts
└── tests/              # Test scripts
```

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL or SQLite
- API keys for LLM providers (OpenAI, Anthropic, GroqCloud, etc.)

### Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up the environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. Initialize the database:
   ```bash
   python -m token_tracker.database.init
   ```

4. Start all components at once:
   ```bash
   python -m token_tracker.run all
   ```

   Or start individual components:
   ```bash
   # Start the proxy server
   python -m token_tracker.run proxy

   # Start the dashboard
   python -m token_tracker.run dashboard

   # Start the API
   python -m token_tracker.run api
   ```

## Usage

### Running the Token Tracker

The Token Tracker provides a command-line interface for running its components:

```bash
# Run all components (proxy, dashboard, and API)
python -m token_tracker.run all

# Run only the proxy server
python -m token_tracker.run proxy

# Run only the dashboard
python -m token_tracker.run dashboard

# Run only the API
python -m token_tracker.run api
```

### Accessing the Dashboard

Once the dashboard is running, you can access it at `http://localhost:8050` (or the host and port specified in your configuration).

The dashboard provides:

- Token usage visualization
- Cost estimation
- Rate limit configuration
- Budget tracking

### Using the API

The API is available at `http://localhost:5000/api` and provides endpoints for:

- Getting token usage data
- Updating rate limits
- Setting budget thresholds
- Configuring alerts

Example API endpoints:

- `GET /api/health`: Health check endpoint
- `GET /api/token-usage`: Get token usage data
- `GET /api/token-usage/summary`: Get token usage summary
- `GET /api/rate-limits`: Get rate limits
- `POST /api/rate-limits`: Create or update a rate limit
- `GET /api/budgets`: Get budgets
- `POST /api/budgets`: Create or update a budget

### Proxy Configuration

The LiteLLM proxy can be configured in `config/proxy.yaml`:

```yaml
model_list:
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: gpt-3.5-turbo
      api_key: ${OPENAI_API_KEY}
  - model_name: llama-4-scout
    litellm_params:
      model: meta-llama/llama-4-scout-17b-16e-instruct
      api_key: ${GROQ_API_KEY}

rate_limits:
  - model: gpt-3.5-turbo
    limit: 10
    period: minute
  - model: llama-4-scout
    limit: 5
    period: minute

budget:
  total: 100.00  # Total budget in USD
  daily: 10.00   # Daily budget in USD
  alerts:
    - threshold: 50  # Alert when 50% of budget is used
      email: erik.jacobs@gmail.com
    - threshold: 80  # Alert when 80% of budget is used
      email: erik.jacobs@gmail.com
    - threshold: 95  # Alert when 95% of budget is used
      email: erik.jacobs@gmail.com
```

### Integration with Existing Applications

To integrate the Token Tracker with an existing application, you need to:

1. Run the Token Tracker proxy server
2. Configure your LLM client to use the proxy server as the API base URL

Example with OpenAI:

```python
import openai

# Set API key
openai.api_key = "your-api-key"

# Set API base to the token tracker proxy
openai.api_base = "http://localhost:8000/v1"

# Create a chat completion
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is token tracking?"},
    ],
    temperature=0.7,
    max_tokens=100,
)
```

Example with Anthropic:

```python
import anthropic

# Set API key and base URL
client = anthropic.Anthropic(
    api_key="your-api-key",
    base_url="http://localhost:8000/v1",
)

# Create a chat completion
response = client.messages.create(
    model="claude-3-haiku",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "What is token tracking?"},
    ],
)
```

See the `examples` directory for more integration examples.

## Examples

The `examples` directory contains example scripts for using the Token Tracker:

- `usage_example.py`: Demonstrates how to use the Token Tracker with different LLM providers
- `integration_example.py`: Demonstrates how to integrate the Token Tracker with an existing application

To run the examples:

```bash
python -m token_tracker.examples.usage_example
python -m token_tracker.examples.integration_example
```

### Email Notifications

The Token Tracker can send email notifications when budget thresholds are reached or exceeded. To enable email notifications, you need to configure the SMTP settings in the `.env` file:

```
# Notification Configuration
NOTIFICATION_EMAIL=erik.jacobs@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_gmail_username@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_ADDRESS=your_gmail_username@gmail.com
```

For Gmail, you need to use an App Password instead of your regular password. You can generate an App Password in your Google Account settings.

## Docker Deployment

The Token Tracker can be deployed using Docker and Docker Compose. This provides an easy way to run all components together with a PostgreSQL database.

### Prerequisites

- Docker
- Docker Compose

### Deployment Steps

1. Clone the repository and navigate to the token_tracker directory:
   ```bash
   cd kern_resources/creative_lab/token_tracker
   ```

2. Create a `.env` file with your configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

4. Access the components:
   - Dashboard: http://localhost:8050
   - API: http://localhost:5000/api
   - Proxy: http://localhost:8000

### Docker Compose Services

The `docker-compose.yml` file defines the following services:

- **db**: PostgreSQL database for storing token usage data
- **proxy**: LiteLLM proxy server for token tracking and rate limiting
- **dashboard**: Dashboard for visualizing token usage
- **api**: API for programmatic access to token usage data

### Environment Variables

The Docker Compose setup uses environment variables from your `.env` file. You can override these variables by setting them in your environment or in the `.env` file.

## Security

The Token Tracker includes several security features:

1. **JWT Authentication**: The API uses JWT tokens for authentication
2. **Role-Based Access Control**: Different endpoints require different roles
3. **API Key Encryption**: API keys are encrypted before being stored
4. **HTTPS Support**: All components can be configured to use HTTPS

### Authentication

To authenticate with the API, send a POST request to `/api/auth/login` with your username and password:

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

This will return a JWT token that you can use for subsequent requests:

```bash
curl -X GET http://localhost:5000/api/token-usage \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
