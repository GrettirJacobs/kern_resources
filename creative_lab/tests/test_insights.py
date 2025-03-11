from session_manager import CreativeSession
import os

# Create a new session
session = CreativeSession()

# Create some test insight data
test_insight = {
    "key_points": [
        "First major observation",
        "Second important finding"
    ],
    "reasoning": "This is how we arrived at these conclusions...",
    "questions": [
        "What should we explore next?",
        "How does this connect to previous findings?"
    ],
    "next_steps": [
        "Investigate the first question",
        "Document the process"
    ]
}

# Save the insight
print("\nAttempting to save insight...")
session.save_insight("test_model", test_insight)

# Verify file existence
expected_path = session.base_path / "insights" / session.session_id / "test_model_insight.json"
print(f"\nChecking if file exists at: {expected_path}")
print(f"File exists: {expected_path.exists()}")