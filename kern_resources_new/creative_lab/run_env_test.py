"""
Script to run the environment manager test.

This script is a simple wrapper around the test_env_manager.py script
that makes it easier to run the test from the command line.
"""

import os
import sys
from pathlib import Path

# Add the utils directory to the path
sys.path.append(str(Path(__file__).parent / "utils"))

# Import and run the test
from utils.test_env_manager import main

if __name__ == "__main__":
    main()
