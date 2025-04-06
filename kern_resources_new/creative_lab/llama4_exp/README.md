# Llama 4 Integration for Kern Resources

This directory contains the integration of Llama 4 models with the Kern Resources project, following a dual-track approach:

1. **Immediate Implementation**: Using Llama 4 Scout Instruct (8B) as the lead AI for CrewAI
2. **Parallel Training**: Simultaneously training Llama 4 E (17B) model for eventual replacement

## Directory Structure

```
llama4_exp/
├── models/             # Model information and configuration
├── scripts/            # Setup and utility scripts
├── integration/        # Integration with CrewAI and other components
├── DEVELOPMENT_LOG.md  # Development log and notes
└── README.md           # This file
```

## Getting Started

### Prerequisites

#### Option 1: Local Deployment
- [Ollama](https://ollama.com/download) installed and running
- Python 3.8+ with pip
- CrewAI installed (`pip install crewai`)
- Sufficient disk space for models (approximately 5GB for Scout Instruct)
- GPU with at least 16GB VRAM for optimal performance

#### Option 2: Remote Deployment (Recommended)
- Render.com account with GPU instance
- Python 3.8+ with pip
- CrewAI installed (`pip install crewai`)

### Setup

#### Option 1: Local Setup (High-end GPU Required)

1. **Install Ollama**:
   - Download and install from [ollama.com/download](https://ollama.com/download)
   - Start the Ollama server

2. **Pull the Llama 4 Scout Instruct model**:
   ```bash
   python scripts/setup_llama4_scout.py
   ```

3. **Test the integration with CrewAI**:
   ```bash
   python integration/crewai_example.py
   ```

#### Option 2: Remote Setup on Render (Recommended)

1. **Deploy Ollama on Render**:
   - Follow the instructions in [docs/render_deployment.md](docs/render_deployment.md)
   - This will set up Ollama on a GPU-enabled Render instance

2. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Update the `OLLAMA_API_BASE` to point to your Render instance
   - Set `OLLAMA_REMOTE=true`

3. **Run the setup script**:
   ```bash
   python scripts/setup_llama4_scout.py
   ```

4. **Test the integration with CrewAI**:
   ```bash
   python integration/crewai_example.py
   ```

## Components

### OllamaProvider

A custom LLM provider for CrewAI that uses Ollama to run Llama 4 models locally. This provider implements the necessary methods for CrewAI to use Llama 4 Scout Instruct for agent reasoning and task execution.

```python
from integration.ollama_provider import OllamaProvider
from crewai import Agent

# Create a provider using Llama 4 Scout Instruct
llm = OllamaProvider(model="llama4-scout-instruct")

# Create an agent using this provider
agent = Agent(
    role="Resource Researcher",
    goal="Find comprehensive information about resources in Kern County",
    backstory="You are an expert at finding and analyzing social service resources",
    llm=llm
)
```

### Setup Script

The `setup_llama4_scout.py` script automates the process of:
- Checking if Ollama is installed and running
- Pulling the Llama 4 Scout Instruct model
- Testing the model with a simple prompt
- Saving model information for CrewAI integration

### CrewAI Example

The `crewai_example.py` script demonstrates how to use Llama 4 Scout Instruct with CrewAI to create a crew of agents that can help with resource discovery and analysis.

## Dual-Track Approach

This implementation follows a dual-track approach:

1. **Track 1: Immediate Implementation**
   - Use Llama 4 Scout Instruct (8B) for immediate integration with CrewAI
   - Leverage its instruction-following capabilities out-of-the-box
   - Deploy for production use in the application

2. **Track 2: Parallel Training** (Coming Soon)
   - Set up training pipeline for Llama 4 E (17B) model
   - Use LoRA/QLoRA for efficient fine-tuning on domain-specific data
   - Periodically evaluate against Scout Instruct
   - Gradually transition tasks as the E model improves

## Future Work

- Implement the training pipeline for Llama 4 E
- Create evaluation framework to compare models
- Develop model switching mechanism based on task requirements
- Integrate with the main Kern Resources application

## Hardware Considerations

Running Llama 4 models requires significant GPU resources:

- **Llama 4 Scout Instruct (8B)**: Minimum 16GB VRAM (RTX 3090/4090 or better)
- **Llama 4 E (17B)**: Minimum 32GB VRAM (A100 or better)

For most users, the recommended approach is to use a cloud GPU instance on Render.com or a similar platform. See [docs/render_deployment.md](docs/render_deployment.md) for detailed instructions.

## Resources

- [Llama 4 Technical Report](https://ai.meta.com/research/publications/llama-4-technical-report/)
- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/README.md)
- [CrewAI Documentation](https://docs.crewai.com/)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [QLoRA Paper](https://arxiv.org/abs/2305.14314)
- [Render.com Documentation](https://render.com/docs)
