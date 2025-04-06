"""
Custom LLM provider for CrewAI that uses Ollama to run Llama 4 Scout Instruct.

This module provides a custom LLM provider that can be used with CrewAI to run
Llama 4 Scout Instruct through Ollama.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# Try to import CrewAI classes, but don't fail if they're not installed
try:
    from crewai.llm import BaseLLM
    from crewai.utilities import RPMController
    CREWAI_AVAILABLE = True
except ImportError:
    # Create placeholder classes if CrewAI is not installed
    class BaseLLM:
        pass

    class RPMController:
        def __init__(self, rpm):
            self.rpm = rpm

    CREWAI_AVAILABLE = False

class OllamaProvider(BaseLLM):
    """
    Custom LLM provider for CrewAI that uses Ollama to run Llama 4 models.

    This provider allows CrewAI to use Llama 4 models through Ollama, which
    enables running the models locally.
    """

    def __init__(
        self,
        model: str = "llama4-scout-instruct",
        api_base: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        rpm: Optional[int] = 10,
        context_window: int = 128000,
        model_info_path: Optional[str] = None,
        remote: bool = False,
        timeout: int = 120,
    ):
        """
        Initialize the Ollama provider.

        Args:
            model: The name of the model to use.
            api_base: The base URL for the Ollama API.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            rpm: The maximum number of requests per minute.
            context_window: The context window size of the model.
            model_info_path: Path to a JSON file with model information.
            remote: Whether the Ollama instance is remote (affects error handling).
            timeout: Request timeout in seconds for API calls.
        """
        if not CREWAI_AVAILABLE:
            print("Warning: CrewAI is not installed. This provider will not work with CrewAI.")

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.context_window = context_window

        # Load model info from file if provided
        if model_info_path:
            self._load_model_info(model_info_path)

        # Use provided API base or default
        self.api_base = api_base or os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")

        # Configure remote settings
        self.remote = remote
        self.timeout = timeout

        # Set up RPM controller if CrewAI is available
        if CREWAI_AVAILABLE:
            self.rpm_controller = RPMController(rpm=rpm)

        # Log configuration
        print(f"Initialized OllamaProvider with model: {self.model}")
        print(f"API Base: {self.api_base}")
        print(f"Remote mode: {self.remote}")

    def _load_model_info(self, model_info_path: str) -> None:
        """
        Load model information from a JSON file.

        Args:
            model_info_path: Path to a JSON file with model information.
        """
        try:
            with open(model_info_path, "r") as f:
                model_info = json.load(f)

            self.model = model_info.get("name", self.model)
            self.api_base = model_info.get("api_base", self.api_base)
            self.context_window = model_info.get("context_window", self.context_window)

            print(f"Loaded model information for {self.model}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Failed to load model information: {e}")

    def generate(self, prompt: str) -> str:
        """
        Generate text based on the prompt.

        Args:
            prompt: The prompt to generate text from.

        Returns:
            The generated text.
        """
        # Wait for RPM controller if CrewAI is available
        if CREWAI_AVAILABLE:
            self.rpm_controller.wait_if_needed()

        try:
            # Prepare request parameters
            request_params = {
                "model": self.model,
                "prompt": prompt,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False
            }

            # Add remote-specific parameters if needed
            if self.remote:
                # Add any remote-specific parameters here
                pass

            # Make the request with timeout
            response = requests.post(
                f"{self.api_base}/api/generate",
                json=request_params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()["response"]
            else:
                error_msg = f"Ollama API returned status code {response.status_code}"
                print(error_msg)
                return f"Error: {error_msg}"
        except requests.RequestException as e:
            error_msg = f"Failed to communicate with Ollama API: {e}"
            print(error_msg)
            return f"Error: {error_msg}"

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response based on a list of chat messages.

        Args:
            messages: A list of message dictionaries with 'role' and 'content'.

        Returns:
            The generated response.
        """
        # Wait for RPM controller if CrewAI is available
        if CREWAI_AVAILABLE:
            self.rpm_controller.wait_if_needed()

        try:
            # Format messages for Ollama chat API
            formatted_messages = []
            for message in messages:
                role = message.get("role", "user")
                # Map OpenAI roles to Ollama roles
                if role == "system":
                    role = "system"
                elif role == "assistant":
                    role = "assistant"
                else:
                    role = "user"

                formatted_messages.append({
                    "role": role,
                    "content": message.get("content", "")
                })

            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": self.temperature,
                "stream": False
            }

            # Add remote-specific parameters if needed
            if self.remote:
                # Add any remote-specific parameters here
                pass

            # Make the request with timeout
            response = requests.post(
                f"{self.api_base}/api/chat",
                json=request_params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                error_msg = f"Ollama API returned status code {response.status_code}"
                print(error_msg)
                return f"Error: {error_msg}"
        except requests.RequestException as e:
            error_msg = f"Failed to communicate with Ollama API: {e}"
            print(error_msg)
            return f"Error: {error_msg}"

    def get_model_name(self) -> str:
        """Get the name of the model being used."""
        return self.model

    def get_context_window(self) -> int:
        """Get the context window size of the model."""
        return self.context_window


# Example usage
if __name__ == "__main__":
    # Find the model_info.json file
    script_dir = Path(__file__).parent.parent
    model_info_path = script_dir / "models" / "model_info.json"

    # Create provider
    if model_info_path.exists():
        provider = OllamaProvider(model_info_path=str(model_info_path))
    else:
        provider = OllamaProvider()

    # Test generation
    response = provider.generate("Explain what Kern Resources is in one sentence.")
    print(f"Generation response: {response}")

    # Test chat
    chat_response = provider.chat([
        {"role": "system", "content": "You are a helpful assistant for Kern Resources."},
        {"role": "user", "content": "What is Kern Resources?"}
    ])
    print(f"Chat response: {chat_response}")
