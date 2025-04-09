"""
Script to run the request validator test.

This script is a simple wrapper around the test_request_validator.py script
that makes it easier to run the test from the command line.
"""

import os
import sys
from pathlib import Path

# Add the utils directory to the path
sys.path.append(str(Path(__file__).parent / "utils"))

# Import and run the test
from utils.test_request_validator import main

if __name__ == "__main__":
    main()
