"""
Test script for the environment manager.

This script tests the environment manager to ensure that it can properly
load and access environment variables, including API keys.
"""

import os
import logging
from env_manager import env_manager

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_keys():
    """Test that API keys can be loaded and accessed."""
    logger.info("Testing API keys...")
    
    # Test GroqCloud API key
    groq_api_key = env_manager.get_api_key("GROQ")
    if groq_api_key:
        masked_key = groq_api_key[:4] + "..." + groq_api_key[-4:]
        logger.info(f"GroqCloud API key: {masked_key}")
    else:
        logger.warning("GroqCloud API key not found.")
    
    # Test OpenAI API key
    openai_api_key = env_manager.get_api_key("OPENAI")
    if openai_api_key:
        masked_key = openai_api_key[:4] + "..." + openai_api_key[-4:]
        logger.info(f"OpenAI API key: {masked_key}")
    else:
        logger.info("OpenAI API key not found (this is expected if not configured).")
    
    # Test Anthropic API key
    anthropic_api_key = env_manager.get_api_key("ANTHROPIC")
    if anthropic_api_key:
        masked_key = anthropic_api_key[:4] + "..." + anthropic_api_key[-4:]
        logger.info(f"Anthropic API key: {masked_key}")
    else:
        logger.info("Anthropic API key not found (this is expected if not configured).")

def test_models():
    """Test that model names can be loaded and accessed."""
    logger.info("Testing model names...")
    
    # Test GroqCloud model
    groq_model = env_manager.get_model("GROQ")
    if groq_model:
        logger.info(f"GroqCloud model: {groq_model}")
    else:
        logger.warning("GroqCloud model not found.")
    
    # Test OpenAI model
    openai_model = env_manager.get_model("OPENAI")
    if openai_model:
        logger.info(f"OpenAI model: {openai_model}")
    else:
        logger.info("OpenAI model not found (this is expected if not configured).")
    
    # Test Anthropic model
    anthropic_model = env_manager.get_model("ANTHROPIC")
    if anthropic_model:
        logger.info(f"Anthropic model: {anthropic_model}")
    else:
        logger.info("Anthropic model not found (this is expected if not configured).")

def test_general_env_vars():
    """Test that general environment variables can be accessed."""
    logger.info("Testing general environment variables...")
    
    # Test a few common environment variables
    path = env_manager.get("PATH")
    if path:
        logger.info(f"PATH environment variable found (length: {len(path)})")
    else:
        logger.warning("PATH environment variable not found.")
    
    # Test a non-existent environment variable
    non_existent = env_manager.get("NON_EXISTENT_VAR", "default_value")
    logger.info(f"Non-existent variable: {non_existent}")

def main():
    """Run all tests."""
    logger.info("=" * 50)
    logger.info("Environment Manager Test")
    logger.info("=" * 50)
    
    # Run tests
    test_api_keys()
    logger.info("-" * 30)
    test_models()
    logger.info("-" * 30)
    test_general_env_vars()
    
    logger.info("=" * 50)
    logger.info("Environment Manager Test Complete")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
