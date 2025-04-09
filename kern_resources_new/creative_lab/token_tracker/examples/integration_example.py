"""
Example script for integrating the Token Tracker with an existing application.

This script demonstrates how to integrate the Token Tracker with an existing
application that uses LLM providers.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add parent directory to path to import from token_tracker
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("token_tracker.examples")

# Load environment variables
load_dotenv()

class LLMClient:
    """
    Example LLM client that uses the Token Tracker.
    
    This class demonstrates how to integrate the Token Tracker with an existing
    application that uses LLM providers.
    """
    
    def __init__(self, provider: str = "openai", use_token_tracker: bool = True):
        """
        Initialize the LLM client.
        
        Args:
            provider: The LLM provider to use (openai, anthropic, groq).
            use_token_tracker: Whether to use the Token Tracker.
        """
        self.provider = provider.lower()
        self.use_token_tracker = use_token_tracker
        
        # Initialize the client based on the provider
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "anthropic":
            self._init_anthropic()
        elif self.provider == "groq":
            self._init_groq()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _init_openai(self):
        """Initialize the OpenAI client."""
        import openai
        
        # Set API key
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        
        # Set API base to the token tracker proxy if enabled
        if self.use_token_tracker:
            openai.api_base = "http://localhost:8000/v1"
        
        self.client = openai
        self.model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    
    def _init_anthropic(self):
        """Initialize the Anthropic client."""
        import anthropic
        
        # Set API key
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        # Set API base to the token tracker proxy if enabled
        if self.use_token_tracker:
            base_url = "http://localhost:8000/v1"
            self.client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
        else:
            self.client = anthropic.Anthropic(api_key=api_key)
        
        self.model = os.environ.get("ANTHROPIC_MODEL", "claude-3-haiku")
    
    def _init_groq(self):
        """Initialize the GroqCloud client."""
        import groq
        
        # Set API key
        api_key = os.environ.get("GROQ_API_KEY")
        
        # Set API base to the token tracker proxy if enabled
        if self.use_token_tracker:
            base_url = "http://localhost:8000/v1"
            self.client = groq.Groq(api_key=api_key, base_url=base_url)
        else:
            self.client = groq.Groq(api_key=api_key)
        
        self.model = os.environ.get("GROQ_MODEL", "llama-4-scout")
    
    def generate_text(self, prompt: str, max_tokens: int = 100) -> Dict[str, Any]:
        """
        Generate text using the LLM provider.
        
        Args:
            prompt: The prompt to generate text from.
            max_tokens: The maximum number of tokens to generate.
            
        Returns:
            A dictionary containing the generated text and token usage.
        """
        if self.provider == "openai":
            return self._generate_openai(prompt, max_tokens)
        elif self.provider == "anthropic":
            return self._generate_anthropic(prompt, max_tokens)
        elif self.provider == "groq":
            return self._generate_groq(prompt, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _generate_openai(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate text using OpenAI."""
        response = self.client.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=max_tokens,
        )
        
        return {
            "text": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }
    
    def _generate_anthropic(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate text using Anthropic."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        
        return {
            "text": response.content[0].text,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
        }
    
    def _generate_groq(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Generate text using GroqCloud."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=max_tokens,
        )
        
        return {
            "text": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }

def main():
    """Main function."""
    print("Token Tracker Integration Example")
    print("================================")
    
    # Check if the token tracker proxy is running
    if os.environ.get("USE_TOKEN_TRACKER", "true").lower() == "true":
        try:
            import requests
            
            response = requests.get("http://localhost:8000/health")
            if response.status_code != 200:
                logger.error("Token Tracker proxy is not running. Please start it first.")
                logger.error("python -m token_tracker.proxy.server")
                return
        except Exception:
            logger.error("Token Tracker proxy is not running. Please start it first.")
            logger.error("python -m token_tracker.proxy.server")
            return
    
    # Create LLM clients
    providers = ["openai", "anthropic", "groq"]
    use_token_tracker = os.environ.get("USE_TOKEN_TRACKER", "true").lower() == "true"
    
    for provider in providers:
        try:
            print(f"\nTesting {provider.capitalize()}...")
            
            # Create client
            client = LLMClient(provider=provider, use_token_tracker=use_token_tracker)
            
            # Generate text
            prompt = "Explain what token tracking is and why it's important for LLM applications."
            response = client.generate_text(prompt, max_tokens=100)
            
            # Print response
            print(f"\n{provider.capitalize()} Response:")
            print("-" * 40)
            print(response["text"])
            print("-" * 40)
            print(f"Prompt Tokens: {response['usage']['prompt_tokens']}")
            print(f"Completion Tokens: {response['usage']['completion_tokens']}")
            print(f"Total Tokens: {response['usage']['total_tokens']}")
            
            print(f"✅ {provider.capitalize()} test passed!")
        except Exception as e:
            logger.error(f"{provider.capitalize()} test failed: {e}")
            print(f"❌ {provider.capitalize()} test failed!")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
