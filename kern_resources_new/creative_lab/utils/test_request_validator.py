"""
Test script for the request validator.

This script tests the request validator to ensure that it can properly
validate API requests and parameters.
"""

import logging
from request_validator import request_validator, ValidationError

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_key_validation():
    """Test API key validation."""
    logger.info("Testing API key validation...")
    
    # Test valid API keys
    valid_keys = [
        "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",  # GroqCloud
        "sk-1234567890abcdefghijklmnopqrstuvwxyz1234",  # OpenAI
        "sk-ant-api03-1234567890abcdefghijklmnopqrstuvwxyz1234"  # Anthropic
    ]
    
    for key in valid_keys:
        try:
            request_validator.validate_api_key(key)
            logger.info(f"Valid API key passed validation: {key[:4]}...{key[-4:]}")
        except ValidationError as e:
            logger.error(f"Valid API key failed validation: {key[:4]}...{key[-4:]} - {e}")
    
    # Test invalid API keys
    invalid_keys = [
        "",  # Empty
        "short",  # Too short
        "gsk_invalid",  # Invalid GroqCloud format
        "sk-invalid",  # Invalid OpenAI format
        "sk-ant-invalid",  # Invalid Anthropic format
        "invalid@key"  # Invalid characters
    ]
    
    for key in invalid_keys:
        try:
            request_validator.validate_api_key(key)
            logger.warning(f"Invalid API key passed validation: {key}")
        except ValidationError as e:
            logger.info(f"Invalid API key correctly failed validation: {key} - {e}")

def test_model_name_validation():
    """Test model name validation."""
    logger.info("Testing model name validation...")
    
    # Test valid model names
    valid_models = [
        ("meta-llama/llama-4-scout-17b-16e-instruct", "GROQ"),
        ("gpt-3.5-turbo", "OPENAI"),
        ("claude-3-haiku-20240307", "ANTHROPIC"),
        ("mistralai/Mistral-7B-Instruct-v0.2", None)
    ]
    
    for model, provider in valid_models:
        try:
            request_validator.validate_model_name(model, provider)
            logger.info(f"Valid model name passed validation: {model}")
        except ValidationError as e:
            logger.error(f"Valid model name failed validation: {model} - {e}")
    
    # Test invalid model names
    invalid_models = [
        "",  # Empty
        "invalid@model",  # Invalid characters
        "gpt-3.5-turbo", "GROQ"  # Mismatched provider
    ]
    
    for model in invalid_models[:2]:
        try:
            request_validator.validate_model_name(model)
            logger.warning(f"Invalid model name passed validation: {model}")
        except ValidationError as e:
            logger.info(f"Invalid model name correctly failed validation: {model} - {e}")
    
    # Test mismatched provider
    try:
        request_validator.validate_model_name(invalid_models[2], invalid_models[3])
        logger.warning(f"Mismatched provider passed validation: {invalid_models[2]} for {invalid_models[3]}")
    except ValidationError as e:
        logger.info(f"Mismatched provider correctly failed validation: {invalid_models[2]} for {invalid_models[3]} - {e}")

def test_parameter_validation():
    """Test parameter validation."""
    logger.info("Testing parameter validation...")
    
    # Test temperature validation
    logger.info("Testing temperature validation...")
    valid_temps = [0, 0.5, 1, 1.5, 2]
    invalid_temps = [-1, 3, "invalid", None]
    
    for temp in valid_temps:
        try:
            request_validator.validate_temperature(temp)
            logger.info(f"Valid temperature passed validation: {temp}")
        except ValidationError as e:
            logger.error(f"Valid temperature failed validation: {temp} - {e}")
    
    for temp in invalid_temps:
        try:
            request_validator.validate_temperature(temp)
            logger.warning(f"Invalid temperature passed validation: {temp}")
        except ValidationError as e:
            logger.info(f"Invalid temperature correctly failed validation: {temp} - {e}")
    
    # Test max_tokens validation
    logger.info("Testing max_tokens validation...")
    valid_tokens = [1, 100, 1000, 4096, 8192]
    invalid_tokens = [0, -1, "invalid", None]
    
    for tokens in valid_tokens:
        try:
            request_validator.validate_max_tokens(tokens)
            logger.info(f"Valid max_tokens passed validation: {tokens}")
        except ValidationError as e:
            logger.error(f"Valid max_tokens failed validation: {tokens} - {e}")
    
    for tokens in invalid_tokens:
        try:
            request_validator.validate_max_tokens(tokens)
            logger.warning(f"Invalid max_tokens passed validation: {tokens}")
        except ValidationError as e:
            logger.info(f"Invalid max_tokens correctly failed validation: {tokens} - {e}")

def test_message_validation():
    """Test message validation."""
    logger.info("Testing message validation...")
    
    # Test valid messages
    valid_messages = [
        [{"role": "system", "content": "You are a helpful assistant."}],
        [{"role": "user", "content": "Hello, world!"}],
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"},
            {"role": "assistant", "content": "Hello! How can I help you today?"}
        ]
    ]
    
    for messages in valid_messages:
        try:
            request_validator.validate_messages(messages)
            logger.info(f"Valid messages passed validation: {len(messages)} messages")
        except ValidationError as e:
            logger.error(f"Valid messages failed validation: {len(messages)} messages - {e}")
    
    # Test invalid messages
    invalid_messages = [
        [],  # Empty
        [{}],  # Missing role and content
        [{"role": "invalid", "content": "Hello"}],  # Invalid role
        [{"role": "user"}],  # Missing content
        [{"content": "Hello"}],  # Missing role
        [{"role": "user", "content": 123}]  # Non-string content
    ]
    
    for messages in invalid_messages:
        try:
            request_validator.validate_messages(messages)
            logger.warning(f"Invalid messages passed validation: {messages}")
        except ValidationError as e:
            logger.info(f"Invalid messages correctly failed validation: {messages} - {e}")

def test_request_validation():
    """Test request validation."""
    logger.info("Testing request validation...")
    
    # Test valid chat request
    valid_chat_request = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    try:
        request_validator.validate_chat_request(valid_chat_request)
        logger.info("Valid chat request passed validation")
    except ValidationError as e:
        logger.error(f"Valid chat request failed validation: {e}")
    
    # Test invalid chat request
    invalid_chat_requests = [
        {},  # Empty
        {"model": "meta-llama/llama-4-scout-17b-16e-instruct"},  # Missing messages
        {"messages": [{"role": "user", "content": "Hello"}]},  # Missing model
        {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": []  # Empty messages
        },
        {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 3  # Invalid temperature
        }
    ]
    
    for request in invalid_chat_requests:
        try:
            request_validator.validate_chat_request(request)
            logger.warning(f"Invalid chat request passed validation: {request}")
        except ValidationError as e:
            logger.info(f"Invalid chat request correctly failed validation: {e}")
    
    # Test valid completion request
    valid_completion_request = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "prompt": "Hello, world!",
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    try:
        request_validator.validate_completion_request(valid_completion_request)
        logger.info("Valid completion request passed validation")
    except ValidationError as e:
        logger.error(f"Valid completion request failed validation: {e}")
    
    # Test invalid completion request
    invalid_completion_requests = [
        {},  # Empty
        {"model": "meta-llama/llama-4-scout-17b-16e-instruct"},  # Missing prompt
        {"prompt": "Hello, world!"},  # Missing model
        {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "prompt": ""  # Empty prompt
        },
        {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "prompt": "Hello, world!",
            "temperature": 3  # Invalid temperature
        }
    ]
    
    for request in invalid_completion_requests:
        try:
            request_validator.validate_completion_request(request)
            logger.warning(f"Invalid completion request passed validation: {request}")
        except ValidationError as e:
            logger.info(f"Invalid completion request correctly failed validation: {e}")

def test_input_sanitization():
    """Test input sanitization."""
    logger.info("Testing input sanitization...")
    
    # Test sanitization
    inputs = [
        "Hello, world!",  # Normal text
        "SELECT * FROM users;",  # SQL injection attempt
        "<script>alert('XSS')</script>",  # XSS attempt
        "rm -rf /",  # Command injection attempt
        "Hello\nworld",  # Newline
        "Hello\tworld",  # Tab
        "Hello\rworld",  # Carriage return
        "Hello\0world",  # Null byte
        "Hello\x1fworld",  # Control character
        "Hello\x7fworld",  # Delete character
        "Hello\u0080world",  # Non-ASCII character
        "Hello\u2022world",  # Unicode bullet
        "Hello\u3042world",  # Japanese character
        "Hello\U0001F600world"  # Emoji
    ]
    
    for input_str in inputs:
        sanitized = request_validator.sanitize_input(input_str)
        logger.info(f"Original: {repr(input_str)}")
        logger.info(f"Sanitized: {repr(sanitized)}")
        logger.info("-" * 30)

def main():
    """Run all tests."""
    logger.info("=" * 50)
    logger.info("Request Validator Test")
    logger.info("=" * 50)
    
    # Run tests
    test_api_key_validation()
    logger.info("-" * 30)
    test_model_name_validation()
    logger.info("-" * 30)
    test_parameter_validation()
    logger.info("-" * 30)
    test_message_validation()
    logger.info("-" * 30)
    test_request_validation()
    logger.info("-" * 30)
    test_input_sanitization()
    
    logger.info("=" * 50)
    logger.info("Request Validator Test Complete")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
