from session_manager import CreativeSession
import os
from pathlib import Path

# Print current directory information
print(f"Current working directory: {os.getcwd()}")

# Create a new session
session = CreativeSession()

# Print session information
print(f"Base path: {session.base_path}")
print(f"Session ID: {session.session_id}")

# Test saving a conversation
test_content = """
This is a test conversation.
Testing our creative session manager.
Date: February 3, 2024
"""

# Save the conversation
session.save_conversation("test_model", test_content)

# Verify file existence
expected_path = session.base_path / "conversations" / session.session_id / "test_model_conversation.txt"
print(f"\nChecking if file exists at: {expected_path}")
print(f"File exists: {expected_path.exists()}")