from session_manager import CreativeSession
import os

# Create a new session
session = CreativeSession()

# Test conversation content
test_conversation = """
This is a test conversation.
It will be linked to an insight.
"""

# Test insight data
test_insight = {
    "key_points": ["Test point"],
    "reasoning": "Test reasoning",
    "questions": ["Test question"],
    "next_steps": ["Test next step"]
}

# Save both and get their paths
print("\nSaving conversation and insight...")
conv_path = session.save_conversation("test_model", test_conversation)
insight_path = session.save_insight("test_model", test_insight)

# Create link between them
print("\nCreating link...")
session.link_conversation_to_insight(conv_path, insight_path)

# Verify link file exists
print(f"\nChecking if links file exists: {session.links_file.exists()}")