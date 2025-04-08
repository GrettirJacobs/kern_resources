"""
Script to run the GroqCloud API test.

This script is a simple wrapper around the test_groq_api.py script
that makes it easier to run the test from the command line.
"""

import os
import sys
from pathlib import Path

# Add the tests directory to the path
sys.path.append(str(Path(__file__).parent))

# Import and run the test
from tests.test_groq_api import main

if __name__ == "__main__":
    main()
