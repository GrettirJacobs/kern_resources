"""
Example script for using the Token Tracker.

This script demonstrates how to use the Token Tracker with different LLM providers.
"""

import os
import sys
import json
import logging
from pathlib import Path
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

def test_openai():
    """Test OpenAI API with token tracking."""
    try:
        import openai
        
        # Set API key
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        
        # Set API base to the token tracker proxy
        openai.api_base = "http://localhost:8000/v1"
        
        logger.info("Testing OpenAI API with token tracking...")
        
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
        
        # Print response
        print("\nOpenAI Response:")
        print("-" * 40)
        print(response.choices[0].message.content)
        print("-" * 40)
        print(f"Tokens: {response.usage.total_tokens}")
        
        return True
    except Exception as e:
        logger.error(f"OpenAI test failed: {e}")
        return False

def test_anthropic():
    """Test Anthropic API with token tracking."""
    try:
        import anthropic
        
        # Set API key
        client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            base_url="http://localhost:8000/v1",
        )
        
        logger.info("Testing Anthropic API with token tracking...")
        
        # Create a chat completion
        response = client.messages.create(
            model="claude-3-haiku",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "What is token tracking?"},
            ],
        )
        
        # Print response
        print("\nAnthropic Response:")
        print("-" * 40)
        print(response.content[0].text)
        print("-" * 40)
        print(f"Input Tokens: {response.usage.input_tokens}")
        print(f"Output Tokens: {response.usage.output_tokens}")
        
        return True
    except Exception as e:
        logger.error(f"Anthropic test failed: {e}")
        return False

def test_groq():
    """Test GroqCloud API with token tracking."""
    try:
        import groq
        
        # Set API key
        client = groq.Groq(
            api_key=os.environ.get("GROQ_API_KEY"),
            base_url="http://localhost:8000/v1",
        )
        
        logger.info("Testing GroqCloud API with token tracking...")
        
        # Create a chat completion
        response = client.chat.completions.create(
            model="llama-4-scout",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is token tracking?"},
            ],
            temperature=0.7,
            max_tokens=100,
        )
        
        # Print response
        print("\nGroqCloud Response:")
        print("-" * 40)
        print(response.choices[0].message.content)
        print("-" * 40)
        print(f"Tokens: {response.usage.total_tokens}")
        
        return True
    except Exception as e:
        logger.error(f"GroqCloud test failed: {e}")
        return False

def test_api():
    """Test the Token Tracker API."""
    try:
        import requests
        
        logger.info("Testing Token Tracker API...")
        
        # Get token usage summary
        response = requests.get("http://localhost:5000/api/token-usage/summary")
        
        if response.status_code == 200:
            data = response.json()
            
            # Print summary
            print("\nToken Usage Summary:")
            print("-" * 40)
            print(f"Total Tokens: {data['summary']['total_tokens']:,}")
            print(f"Estimated Cost: ${data['summary']['estimated_cost']:.2f}")
            print(f"Request Count: {data['summary']['request_count']:,}")
            
            # Print by model
            print("\nToken Usage by Model:")
            print("-" * 40)
            for model in data["by_model"]:
                print(f"{model['model']}: {model['total_tokens']:,} tokens, ${model['estimated_cost']:.2f}")
            
            return True
        else:
            logger.error(f"API test failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"API test failed: {e}")
        return False

def main():
    """Main function."""
    print("Token Tracker Usage Example")
    print("==========================")
    
    # Check if the token tracker proxy is running
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
    
    # Check if the token tracker API is running
    try:
        import requests
        
        response = requests.get("http://localhost:5000/api/health")
        if response.status_code != 200:
            logger.error("Token Tracker API is not running. Please start it first.")
            logger.error("python -m token_tracker.api.app")
            return
    except Exception:
        logger.error("Token Tracker API is not running. Please start it first.")
        logger.error("python -m token_tracker.api.app")
        return
    
    # Run tests
    tests = [
        ("OpenAI", test_openai),
        ("Anthropic", test_anthropic),
        ("GroqCloud", test_groq),
        ("API", test_api),
    ]
    
    for name, test_func in tests:
        print(f"\nTesting {name}...")
        if test_func():
            print(f"✅ {name} test passed!")
        else:
            print(f"❌ {name} test failed!")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
