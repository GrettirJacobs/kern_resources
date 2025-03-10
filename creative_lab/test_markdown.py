from session_manager import CreativeSession
import os

# Create a new session
session = CreativeSession()

# Test conversation content
test_conversation = "Human: How can we implement this feature?\n\n" + \
                   "Assistant: Let me show you step by step.\n\n" + \
                   "Human: That sounds good.\n\n" + \
                   "Assistant: Here's the implementation..."

# Test metadata
test_metadata = {
    "topic": "Markdown Implementation",
    "duration": "15 minutes",
    "purpose": "Testing markdown conversation saving"
}

# Save the markdown conversation
print("\nSaving markdown conversation...")
md_path = session.save_markdown_conversation("test_model", test_conversation, test_metadata)

# Verify file exists
print(f"\nChecking if markdown file exists at: {md_path}")
print(f"File exists: {md_path.exists()}")