#!/usr/bin/env python
"""
Setup script for Llama 4 Scout Instruct model using Ollama.

This script:
1. Checks if Ollama is installed
2. Pulls the Llama 4 Scout Instruct model
3. Tests the model with a simple prompt
4. Saves model information for CrewAI integration
"""

import os
import sys
import json
import subprocess
import requests
import time
from pathlib import Path

# Configuration
OLLAMA_API_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
MODEL_NAME = os.environ.get("SCOUT_MODEL_NAME", "llama4-scout-instruct")
MODEL_INFO_PATH = Path(__file__).parent.parent / "models" / "model_info.json"
REMOTE_MODE = os.environ.get("OLLAMA_REMOTE", "false").lower() == "true"
TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "120"))

def check_ollama_installed():
    """Check if Ollama is installed and running."""
    if REMOTE_MODE:
        print(f"Remote mode enabled, connecting to {OLLAMA_API_BASE}")
        try:
            response = requests.get(f"{OLLAMA_API_BASE}/api/tags", timeout=TIMEOUT)
            if response.status_code == 200:
                print("✅ Remote Ollama server is accessible")
            else:
                print(f"❌ Remote Ollama server returned status code {response.status_code}")
                sys.exit(1)
        except requests.RequestException as e:
            print(f"❌ Cannot connect to remote Ollama server: {e}")
            print(f"Please check if the server at {OLLAMA_API_BASE} is running")
            sys.exit(1)
    else:
        try:
            # Check if Ollama is in PATH
            subprocess.run(["ollama", "--version"],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          check=True)
            print("✅ Ollama is installed")
        except (subprocess.SubprocessError, FileNotFoundError):
            print("❌ Ollama is not installed or not in PATH")
            print("Please install Ollama from https://ollama.com/download")
            sys.exit(1)

        # Check if Ollama server is running
        try:
            response = requests.get(f"{OLLAMA_API_BASE}/api/tags", timeout=TIMEOUT)
            if response.status_code == 200:
                print("✅ Ollama server is running")
            else:
                print(f"❌ Ollama server returned status code {response.status_code}")
                sys.exit(1)
        except requests.RequestException:
            print("❌ Ollama server is not running")
            print("Please start Ollama server with 'ollama serve'")
            sys.exit(1)

def pull_model():
    """Pull the Llama 4 Scout Instruct model using Ollama."""
    print(f"Checking for {MODEL_NAME} model...")

    try:
        # Check if model already exists
        response = requests.get(f"{OLLAMA_API_BASE}/api/tags", timeout=TIMEOUT)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if any(model["name"] == MODEL_NAME for model in models):
                print(f"✅ Model {MODEL_NAME} is already pulled")
                return True
    except requests.RequestException as e:
        print(f"❌ Failed to check existing models: {e}")

    if REMOTE_MODE:
        print("⚠️ In remote mode, models must be pulled on the server")
        print(f"Please ensure {MODEL_NAME} is pulled on the remote Ollama server")
        # We'll assume the model exists and continue
        return True
    else:
        print(f"Pulling {MODEL_NAME} model (this may take a while)...")
        # Pull the model locally
        try:
            subprocess.run(["ollama", "pull", MODEL_NAME], check=True)
            print(f"✅ Successfully pulled {MODEL_NAME}")
            return True
        except subprocess.SubprocessError as e:
            print(f"❌ Failed to pull {MODEL_NAME}: {e}")
            return False

def test_model():
    """Test the model with a simple prompt."""
    print("Testing model with a simple prompt...")

    test_prompt = "Explain what Kern Resources is in one sentence."

    try:
        response = requests.post(
            f"{OLLAMA_API_BASE}/api/generate",
            json={"model": MODEL_NAME, "prompt": test_prompt, "stream": False},
            timeout=TIMEOUT
        )

        if response.status_code == 200:
            result = response.json()
            print("\nModel response:")
            print(f"Prompt: {test_prompt}")
            print(f"Response: {result['response']}")
            print("\n✅ Model test successful")
            return True
        else:
            print(f"❌ Model test failed with status code {response.status_code}")
            if REMOTE_MODE:
                print("This may indicate that the model is not available on the remote server")
                print(f"Please ensure {MODEL_NAME} is pulled on the remote Ollama server")
            return False
    except requests.RequestException as e:
        print(f"❌ Model test failed: {e}")
        if REMOTE_MODE:
            print("This may indicate connectivity issues with the remote server")
            print(f"Please check if the server at {OLLAMA_API_BASE} is accessible")
        return False

def save_model_info():
    """Save model information for CrewAI integration."""
    model_info = {
        "name": MODEL_NAME,
        "type": "ollama",
        "api_base": OLLAMA_API_BASE,
        "context_window": 128000,  # Llama 4 Scout context window
        "setup_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "description": "Llama 4 Scout Instruct - 8B parameter instruction-following model",
        "remote": REMOTE_MODE,
        "timeout": TIMEOUT
    }

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(MODEL_INFO_PATH), exist_ok=True)

    # Save model info
    with open(MODEL_INFO_PATH, "w") as f:
        json.dump(model_info, f, indent=2)

    print(f"✅ Model information saved to {MODEL_INFO_PATH}")
    return True

def main():
    """Main function to set up Llama 4 Scout Instruct model."""
    print("=" * 50)
    print("Llama 4 Scout Instruct Setup")
    print("=" * 50)

    check_ollama_installed()
    if pull_model():
        if test_model():
            save_model_info()
            print("\n🎉 Setup complete! Llama 4 Scout Instruct is ready for use with CrewAI.")
        else:
            print("\n❌ Setup incomplete. Model test failed.")
    else:
        print("\n❌ Setup incomplete. Failed to pull model.")

if __name__ == "__main__":
    main()
