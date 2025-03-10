from session_manager import CreativeSession
import os

# Create a new session
session = CreativeSession()

# First, let's create some linked files
print("\nCreating new linked files...")
# Test conversation content
test_conversation = "This is a test conversation for retrieval testing."
# Test insight data
test_insight = {
    "key_points": ["Retrieval test point"],
    "reasoning": "Testing retrieval functionality",
    "questions": ["Can we retrieve linked files?"],
    "next_steps": ["Verify retrieval works"]
}

# Save both and link them
conv_path = session.save_conversation("test_model", test_conversation)
insight_path = session.save_insight("test_model", test_insight)
session.link_conversation_to_insight(conv_path, insight_path)

# Now test retrieval
print("\nTesting retrieval...")
linked_files = session.get_linked_files()

print("\nRetrieved links:")
for link in linked_files:
    print(f"\nSession: {link['session_id']}")
    print(f"Conversation: {link['conversation']}")
    print(f"Insight: {link['insight']}")
    print(f"Timestamp: {link['timestamp']}")