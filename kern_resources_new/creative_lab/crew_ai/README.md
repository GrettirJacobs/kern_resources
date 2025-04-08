# CrewAI Integration for Kern Resources

This directory contains the integration of CrewAI with the Kern Resources project, focusing on using GroqCloud for cost-effective Llama 4 inference.

## Overview

CrewAI is a framework for creating and orchestrating autonomous AI agents. This integration allows Kern Resources to leverage CrewAI's capabilities with Llama 4 models via GroqCloud, providing a powerful and cost-effective solution for multi-agent collaboration.

## Directory Structure

```
crew_ai/
├── providers/           # Custom LLM providers for CrewAI
│   └── groq_provider.py # GroqCloud provider for Llama 4 models
├── examples/            # Example scripts demonstrating the integration
│   ├── kern_resources_crew.py       # Example of a resource discovery crew
│   └── simple_integration_example.py # Simple example of using the integration
├── tests/               # Test scripts for the integration
│   └── test_groq_api.py # Test script for the GroqCloud API
├── integration.py       # High-level integration module
├── requirements.txt     # Required dependencies
└── run_groq_test.py     # Script to run the GroqCloud API test
```

## Features

- **GroqCloud Provider**: Custom provider for using Llama 4 models with CrewAI
- **Integration Module**: High-level interface for creating and managing CrewAI components
- **Example Scripts**: Demonstrations of how to use the integration
- **Test Scripts**: Tools for testing the integration

## Getting Started

### Prerequisites

- Python 3.8+
- GroqCloud API key
- CrewAI installed (`pip install crewai`)

### Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your GroqCloud API key:
   ```bash
   # On Windows (PowerShell)
   $env:GROQ_API_KEY = "your_groq_api_key_here"
   
   # On Windows (Command Prompt)
   set GROQ_API_KEY=your_groq_api_key_here
   
   # On Linux/Mac
   export GROQ_API_KEY=your_groq_api_key_here
   ```

3. Test the GroqCloud API:
   ```bash
   python run_groq_test.py
   ```

### Usage

#### Basic Usage

```python
from integration import create_default_integration

# Create the integration
integration = create_default_integration()

# Create an agent
agent = integration.create_agent(
    role="Resource Researcher",
    goal="Find information about resources",
    backstory="You are an expert at finding resources."
)

# Create a task
task = integration.create_task(
    description="Find resources for housing assistance",
    agent=agent
)

# Create a crew
crew = integration.create_crew(agents=[agent])

# Run the crew
result = integration.run_crew(crew, tasks=[task])
```

#### Advanced Usage

See the example scripts in the `examples/` directory for more advanced usage scenarios.

## GroqCloud Provider

The GroqCloud provider (`providers/groq_provider.py`) allows CrewAI to use Llama 4 models through GroqCloud's API. This provider offers a cost-effective way to use high-quality models with CrewAI.

### Features

- **Cost-Effective**: GroqCloud offers Llama 4 Scout at $0.11 per million input tokens and $0.34 per million output tokens
- **High Performance**: GroqCloud is known for its low-latency inference
- **Easy Integration**: The provider integrates seamlessly with CrewAI

### Configuration

The GroqCloud provider can be configured with the following parameters:

- `api_key`: The API key for GroqCloud
- `model`: The name of the model to use (default: `"meta-llama/llama-4-scout-17b-16e-instruct"`)
- `temperature`: The temperature to use for generation (default: `0.7`)
- `max_tokens`: The maximum number of tokens to generate (default: `4096`)
- `timeout`: The timeout for API requests in seconds (default: `60`)

## Examples

### Kern Resources Crew

The `examples/kern_resources_crew.py` script demonstrates how to use the GroqCloud provider with CrewAI to create a crew of agents for resource discovery, analysis, and recommendation.

```bash
python examples/kern_resources_crew.py
```

### Simple Integration Example

The `examples/simple_integration_example.py` script demonstrates how to use the integration module to create and run a simple crew.

```bash
python examples/simple_integration_example.py
```

## Testing

The `tests/test_groq_api.py` script tests the GroqCloud API integration to ensure that it's working correctly.

```bash
python run_groq_test.py
```

## Future Development

### Planned Enhancements

1. **Security Measures**
   - API key management
   - Request validation
   - Monitoring and logging
   - Access control

2. **Limitations and Monitoring**
   - Token usage limits
   - Cost controls
   - Performance monitoring

3. **Tools for CrewAI**
   - Web search and crawling
   - Database integration
   - Email and notification tools

4. **Team of AI Experts**
   - Integration with Claude, GPT, Grok, Gemini, etc.
   - Specialized roles for different models
   - Routing and orchestration

### Integration with Dream Lab

Future development will include integration with the Dream Lab module for continuous learning and improvement of the CrewAI agents.

## Security Considerations

- Never hardcode your API key in your code
- Use environment variables to store your API key
- Add `.env` files to your `.gitignore` to prevent accidental commits
- Rotate your API key regularly

## Resources

- [CrewAI Documentation](https://docs.crewai.com/)
- [GroqCloud Documentation](https://console.groq.com/docs/quickstart)
- [Llama 4 Documentation](https://ai.meta.com/llama/)
