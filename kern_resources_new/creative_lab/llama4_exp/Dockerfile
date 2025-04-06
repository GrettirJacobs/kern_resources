FROM ollama/ollama:latest

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for models
RUN mkdir -p /root/.ollama/models

# Expose the Ollama API port
EXPOSE 11434

# Start Ollama server
CMD ["ollama", "serve"]
