"""
Test script for the GroqCloud API integration.

This script tests the connection to the GroqCloud API and verifies that
the Llama 4 Scout model is accessible and responding as expected.
"""

import os
import sys
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the providers module
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from .env file
load_dotenv()

# Import the GroqCloud provider
try:
    from providers.groq_provider import GroqCloudProvider
    logger.info("Successfully imported GroqCloudProvider")
except ImportError as e:
    logger.error(f"Failed to import GroqCloudProvider: {e}")
    sys.exit(1)

def test_api_key():
    """Test that the API key is set."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY environment variable not set.")
        logger.error("Please set it before running this test.")
        logger.error("Example: export GROQ_API_KEY=your_api_key_here")
        return False
    
    logger.info("API key is set")
    # Mask the API key for logging
    masked_key = api_key[:4] + "..." + api_key[-4:]
    logger.info(f"Using API key: {masked_key}")
    return True

def test_simple_generation():
    """Test a simple text generation request."""
    logger.info("Testing simple text generation...")
    
    try:
        provider = GroqCloudProvider()
        prompt = "Explain what Kern Resources is in one sentence."
        
        logger.info(f"Sending prompt: {prompt}")
        response = provider.generate(prompt)
        
        logger.info("Received response:")
        logger.info(response)
        
        return True
    except Exception as e:
        logger.error(f"Error during simple generation test: {e}")
        return False

def test_chat_completion():
    """Test a chat completion request."""
    logger.info("Testing chat completion...")
    
    try:
        provider = GroqCloudProvider()
        messages = [
            {"role": "system", "content": "You are a helpful assistant for Kern Resources."},
            {"role": "user", "content": "What are the top 3 types of resources that might be available in Kern County?"}
        ]
        
        logger.info(f"Sending messages: {json.dumps(messages, indent=2)}")
        response = provider.chat(messages)
        
        logger.info("Received response:")
        logger.info(response)
        
        return True
    except Exception as e:
        logger.error(f"Error during chat completion test: {e}")
        return False

def test_model_parameters():
    """Test different model parameters."""
    logger.info("Testing model parameters...")
    
    try:
        # Test with different temperature
        logger.info("Testing with temperature=0.2 (more focused responses)")
        provider_focused = GroqCloudProvider(temperature=0.2)
        
        # Test with different model
        logger.info("Testing with 8B model")
        provider_small = GroqCloudProvider(model="meta-llama/llama-4-scout-8b-16e-instruct")
        
        prompt = "Give me one creative idea for a social service program."
        
        logger.info("Response with temperature=0.2:")
        response_focused = provider_focused.generate(prompt)
        logger.info(response_focused)
        
        logger.info("Response with 8B model:")
        response_small = provider_small.generate(prompt)
        logger.info(response_small)
        
        return True
    except Exception as e:
        logger.error(f"Error during model parameters test: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("=" * 50)
    logger.info("GroqCloud API Test")
    logger.info("=" * 50)
    
    # Test API key
    if not test_api_key():
        return
    
    # Run tests
    tests = [
        ("Simple Generation", test_simple_generation),
        ("Chat Completion", test_chat_completion),
        ("Model Parameters", test_model_parameters)
    ]
    
    results = []
    for name, test_func in tests:
        logger.info("\n" + "=" * 30)
        logger.info(f"Running test: {name}")
        logger.info("=" * 30)
        
        success = test_func()
        results.append((name, success))
        
        logger.info(f"Test {name}: {'PASSED' if success else 'FAILED'}")
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("Test Summary")
    logger.info("=" * 50)
    
    all_passed = True
    for name, success in results:
        logger.info(f"{name}: {'PASSED' if success else 'FAILED'}")
        if not success:
            all_passed = False
    
    if all_passed:
        logger.info("\nAll tests PASSED!")
        logger.info("The GroqCloud API integration is working correctly.")
    else:
        logger.error("\nSome tests FAILED!")
        logger.error("Please check the logs for details.")

if __name__ == "__main__":
    main()
