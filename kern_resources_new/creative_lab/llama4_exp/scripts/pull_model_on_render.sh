#!/bin/bash
# Script to pull the Llama 4 Scout Instruct model on Render

echo "Starting model pull process..."
echo "This may take some time depending on network speed and server load."

# Pull the model
ollama pull llama4-scout-instruct

# Check if the pull was successful
if [ $? -eq 0 ]; then
    echo "Successfully pulled llama4-scout-instruct model!"
    
    # List available models to confirm
    echo "Available models:"
    ollama list
else
    echo "Failed to pull the model. Please check the logs for errors."
    exit 1
fi

echo "Model pull process complete!"
