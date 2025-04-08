# CrewAI Providers

This directory contains custom LLM providers for CrewAI that can be used with the Kern Resources project.

## GroqCloud Provider

The `groq_provider.py` file contains a custom LLM provider for CrewAI that uses GroqCloud to run Llama 4 models. This provider offers a cost-effective way to use high-quality models like Llama 4 Scout Instruct with CrewAI.

### Features

- **Cost-Effective**: GroqCloud offers Llama 4 Scout at $0.11 per million input tokens and $0.34 per million output tokens, making it one of the most affordable options for high-quality models.
- **High Performance**: GroqCloud is known for its low-latency inference, providing fast responses for CrewAI agents.
- **Easy Integration**: The provider integrates seamlessly with CrewAI, allowing you to use Llama 4 models with your existing CrewAI code.

### Usage

```python
from providers.groq_provider import GroqCloudProvider
from crewai import Agent, Task, Crew

# Set your API key in the environment variable or pass it directly
# os.environ["GROQ_API_KEY"] = "your_api_key_here"

# Create the GroqCloud provider
llm = GroqCloudProvider(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.7
)

# Create an agent using the GroqCloud provider
researcher = Agent(
    role="Resource Researcher",
    goal="Discover and document social service resources in Kern County",
    backstory="You are an expert at finding and analyzing social service resources",
    llm=llm
)

# Create tasks and crew as usual
```

### Configuration

The GroqCloud provider can be configured with the following parameters:

- `api_key`: The API key for GroqCloud. If not provided, it will be read from the `GROQ_API_KEY` environment variable.
- `model`: The name of the model to use. Default is `"meta-llama/llama-4-scout-17b-16e-instruct"`.
- `temperature`: The temperature to use for generation. Default is `0.7`.
- `max_tokens`: The maximum number of tokens to generate. Default is `4096`.
- `timeout`: The timeout for API requests in seconds. Default is `60`.

### Available Models

GroqCloud offers several models, including:

- `meta-llama/llama-4-scout-17b-16e-instruct`: Llama 4 Scout Instruct (17B parameters)
- `meta-llama/llama-4-scout-8b-16e-instruct`: Llama 4 Scout Instruct (8B parameters)
- `meta-llama/llama-4-maverick-8b-16e-instruct`: Llama 4 Maverick Instruct (8B parameters)

### Security

Always keep your API key secure:

1. Never hardcode your API key in your code
2. Use environment variables to store your API key
3. Add `.env` files to your `.gitignore` to prevent accidental commits
4. Rotate your API key regularly

## Other Providers

Additional providers may be added in the future to support other LLM services.
