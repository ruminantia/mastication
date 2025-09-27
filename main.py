#!/usr/bin/env python3
"""
Main entry point for Mastication - File monitoring and LLM processing tool
"""

import sys
import os
from dotenv import load_dotenv

# Add src directory to Python path to enable module imports
# This allows importing from the src package without installation
sys.path.append("src")

# Load environment variables from .env file
# This must happen before importing modules to ensure variables are available
load_dotenv()

# Import the mastication module after environment is loaded
from src import mastication


def main():
    """
    Main entry point for the Mastication pipeline.

    This function:
    1. Validates that required environment variables are set
    2. Starts the file monitoring and processing pipeline
    3. Handles any startup errors gracefully

    The pipeline will run until stopped by external signal (Ctrl+C) or error.
    """
    # Validate that API key is available
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "No API key found. Set OPENROUTER_API_KEY or OPENAI_API_KEY in .env file"
        )

    # Start the mastication pipeline
    # This begins the file monitoring and processing loop
    return mastication.main()


if __name__ == "__main__":
    """
    Standard Python idiom to ensure main() only runs when script is executed directly.

    This prevents the pipeline from starting if the file is imported as a module,
    which is important for testing and other integration scenarios.
    """
    exit(main())
