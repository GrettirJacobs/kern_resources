"""
GroqCloud provider for CrewAI.

This module provides a custom LLM provider that can be used with CrewAI to run
Llama 4 Scout Instruct through GroqCloud's API.
"""

import os
import sys
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the utils module
sys.path.append(str(Path(__file__).parent.parent.parent))

# Try to import the environment manager
try:
    from utils.env_manager import env_manager
    ENV_MANAGER_AVAILABLE = True
except ImportError:
    logger.warning("Environment manager not available. Using os.environ directly.")
    ENV_MANAGER_AVAILABLE = False

# Try to import the request validator
try:
    from utils.request_validator import request_validator, ValidationError
    REQUEST_VALIDATOR_AVAILABLE = True
except ImportError:
    logger.warning("Request validator not available. Skipping request validation.")
    REQUEST_VALIDATOR_AVAILABLE = False

# Try to import CrewAI classes, but don't fail if they're not installed
try:
    from crewai.llm import BaseLLM
    CREWAI_AVAILABLE = True
except ImportError:
    logger.warning("CrewAI not available. Using placeholder class.")
    CREWAI_AVAILABLE = False

    # Create placeholder class if CrewAI is not installed
    class BaseLLM:
        pass

class GroqCloudProvider(BaseLLM):
    """
    Custom LLM provider for CrewAI that uses GroqCloud to run Llama 4 models.

    This provider allows CrewAI to use Llama 4 models through GroqCloud's API,
    which offers cost-effective inference for these models.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: int = 60
    ):
        """
        Initialize the GroqCloud provider.

        Args:
            api_key: The API key for GroqCloud. If not provided, it will be read from the GROQ_API_KEY environment variable.
            model: The name of the model to use.
            temperature: The temperature to use for generation.
            max_tokens: The maximum number of tokens to generate.
            timeout: The timeout for API requests in seconds.
        """
        if not CREWAI_AVAILABLE:
            logger.warning("CrewAI is not installed. This provider will not work with CrewAI.")

        # Get API key from parameter, environment manager, or environment variable
        if api_key:
            self.api_key = api_key
        elif ENV_MANAGER_AVAILABLE:
            self.api_key = env_manager.get_api_key("GROQ")
        else:
            self.api_key = os.environ.get("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError("GroqCloud API key not provided and GROQ_API_KEY environment variable not set.")

        # Validate the API key if the request validator is available
        if REQUEST_VALIDATOR_AVAILABLE:
            try:
                request_validator.validate_api_key(self.api_key)
            except ValidationError as e:
                logger.warning(f"API key validation warning: {e}")

        # Log a masked version of the API key for debugging
        if self.api_key:
            masked_key = self.api_key[:4] + "..." + self.api_key[-4:] if len(self.api_key) > 8 else "***"
            logger.debug(f"Using GroqCloud API key: {masked_key}")

        # Validate the model name if the request validator is available
        if REQUEST_VALIDATOR_AVAILABLE:
            try:
                request_validator.validate_model_name(self.model, "GROQ")
            except ValidationError as e:
                logger.warning(f"Model name validation warning: {e}")

        # Validate the temperature if the request validator is available
        if REQUEST_VALIDATOR_AVAILABLE:
            try:
                request_validator.validate_temperature(self.temperature)
            except ValidationError as e:
                logger.warning(f"Temperature validation warning: {e}")
                self.temperature = 0.7  # Use a safe default

        # Validate the max_tokens if the request validator is available
        if REQUEST_VALIDATOR_AVAILABLE:
            try:
                request_validator.validate_max_tokens(self.max_tokens)
            except ValidationError as e:
                logger.warning(f"max_tokens validation warning: {e}")
                self.max_tokens = 4096  # Use a safe default

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

        logger.info(f"Initialized GroqCloudProvider with model: {self.model}")

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a response based on a list of chat messages.

        Args:
            messages: A list of message dictionaries with 'role' and 'content'.

        Returns:
            The generated response.
        """
        logger.info(f"Generating response with GroqCloud for {len(messages)} messages")

        # Validate the messages if the request validator is available
        if REQUEST_VALIDATOR_AVAILABLE:
            try:
                request_validator.validate_messages(messages)
            except ValidationError as e:
                logger.warning(f"Messages validation warning: {e}")
                # If validation fails, try to fix the messages
                if not messages:
                    messages = [{"role": "user", "content": "Hello"}]
                for message in messages:
                    if "role" not in message:
                        message["role"] = "user"
                    if "content" not in message:
                        message["content"] = ""
                    if not isinstance(message["content"], str):
                        message["content"] = str(message["content"])

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        # Validate the full request if the request validator is available
        if REQUEST_VALIDATOR_AVAILABLE:
            try:
                request_validator.validate_chat_request(payload)
            except ValidationError as e:
                logger.warning(f"Chat request validation warning: {e}")

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                response_json = response.json()
                return response_json["choices"][0]["message"]["content"]
            else:
                error_msg = f"GroqCloud API returned status code {response.status_code}: {response.text}"
                logger.error(error_msg)
                return f"Error: {error_msg}"
        except requests.RequestException as e:
            error_msg = f"Failed to communicate with GroqCloud API: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"

    def generate(self, prompt: str) -> str:
        """
        Generate text based on the prompt.

        Args:
            prompt: The prompt to generate text from.

        Returns:
            The generated text.
        """
        # Validate the prompt if the request validator is available
        if REQUEST_VALIDATOR_AVAILABLE:
            try:
                request_validator.validate_prompt(prompt)
            except ValidationError as e:
                logger.warning(f"Prompt validation warning: {e}")
                # If validation fails, try to sanitize the prompt
                prompt = request_validator.sanitize_input(prompt)

        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages)

    def get_model_name(self) -> str:
        """Get the name of the model being used."""
        return self.model


# Example usage
if __name__ == "__main__":
    # Set up logging for the example
    logging.basicConfig(level=logging.INFO)

    # Use the environment manager to get the API key
    # No need to set the API key manually

    provider = GroqCloudProvider()

    # Test chat
    response = provider.chat([
        {"role": "system", "content": "You are a helpful assistant for Kern Resources."},
        {"role": "user", "content": "What is Kern Resources?"}
    ])
    print(f"Chat response: {response}")
