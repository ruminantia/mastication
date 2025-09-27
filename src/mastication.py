#!/usr/bin/env python3
"""
Mastication - A simple file monitoring and LLM processing tool
Monitors a directory for new files, processes them with an LLM, and saves responses.
"""

import os
import time
import logging
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Load environment variables
load_dotenv()


class FileProcessor(FileSystemEventHandler):
    """Handles file creation events and processes files with LLM"""

    def __init__(self, config, client):
        self.config = config
        self.client = client
        self.processed_files = set()

    def on_created(self, event):
        """Called when a file is created"""
        if not event.is_directory:
            self.process_file(event.src_path)

    def on_moved(self, event):
        """Called when a file is moved into the watched directory"""
        if not event.is_directory:
            self.process_file(event.dest_path)

    def process_file(self, file_path):
        """Process a file with the LLM"""
        try:
            # Check if file should be processed
            if not self.should_process_file(file_path):
                return

            # Mark as processed to avoid duplicate processing
            if file_path in self.processed_files:
                return
            self.processed_files.add(file_path)

            logging.info(f"Processing file: {file_path}")

            # Read file content
            content = self.read_file_content(file_path)
            if content is None:
                return

            # Process with LLM
            response = self.process_with_llm(content, file_path)
            if response:
                # Save response
                self.save_response(response, file_path)

                # Delete input file if configured
                if self.config["processing"]["delete_after_processing"]:
                    os.remove(file_path)
                    logging.info(f"Deleted input file: {file_path}")

        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")

    def should_process_file(self, file_path):
        """Check if file should be processed based on configuration"""
        file_path = Path(file_path)

        # Check file extension
        valid_extensions = self.config["monitoring"]["file_extensions"]
        if file_path.suffix.lower() not in valid_extensions:
            return False

        # Check file size
        max_size = self.config["processing"]["max_file_size"]
        if file_path.stat().st_size > max_size:
            logging.warning(f"File {file_path} exceeds maximum size limit")
            return False

        return True

    def read_file_content(self, file_path):
        """Read file content with proper encoding handling"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    return f.read()
            except Exception as e:
                logging.error(f"Error reading file {file_path}: {e}")
                return None
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return None

    def process_with_llm(self, content, file_path):
        """Process content with LLM"""
        try:
            # Prepare messages
            messages = []

            # Add system prompt if configured
            system_prompt = self.config["llm"]["system_prompt"]
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Check if this is a classification task
            is_classification = "classification" in self.config

            if is_classification:
                # Add classification-specific user prompt
                classification_prompt = self._build_classification_prompt(
                    content, file_path
                )
                messages.append({"role": "user", "content": classification_prompt})
            else:
                # Add generic user message
                messages.append(
                    {
                        "role": "user",
                        "content": f"Process the following content from file '{Path(file_path).name}':\n\n{content}",
                    }
                )

            # Prepare headers
            extra_headers = {}
            if "headers" in self.config:
                for header, value in self.config["headers"].items():
                    if value:  # Only add non-empty headers
                        extra_headers[header] = value

            # Make API call
            completion = self.client.chat.completions.create(
                model=self.config["llm"]["model"],
                messages=messages,
                temperature=self.config["llm"]["temperature"],
                max_tokens=self.config["llm"]["max_tokens"],
                **({"extra_headers": extra_headers} if extra_headers else {}),
            )

            response_content = completion.choices[0].message.content

            # If this is classification, parse the JSON response
            if is_classification:
                return self._parse_classification_response(response_content, file_path)
            else:
                return response_content

        except Exception as e:
            logging.error(f"Error processing with LLM: {e}")
            return None

    def get_output_path(self, input_path, category):
        """Generate structured output file path"""
        input_path = Path(input_path)
        output_dir = Path(self.config["monitoring"]["output_dir"])

        # Get current date for directory structure
        now = datetime.now()
        year = str(now.year)
        month = f"{now.month:02d}"
        day = f"{now.day:02d}"

        # Create category directory with date subfolders
        category_dir = output_dir / category / year / month / day
        category_dir.mkdir(parents=True, exist_ok=True)

        # Create filename with timestamp
        timestamp = int(time.time())
        output_filename = f"{timestamp}.json"

        return category_dir / output_filename

    def save_response(self, response, input_path):
        """Save LLM response to output directory"""
        try:
            # Check if response is a dictionary (JSON classification result)
            if isinstance(response, dict):
                # Add input filename to response
                input_filename = Path(input_path).name
                response["input_filename"] = input_filename

                # Get category for directory structure
                category = response.get("category", "misc")

                # Validate category against allowed categories from config
                allowed_categories = self.config["classification"]["categories"]
                if category not in allowed_categories:
                    logging.warning(
                        f"Invalid category '{category}', defaulting to 'misc'"
                    )
                    category = "misc"

                # Generate output path based on category and date
                output_path = self.get_output_path(input_path, category)

                # Check if output file already exists
                if (
                    output_path.exists()
                    and not self.config["processing"]["overwrite_existing"]
                ):
                    logging.info(f"Output file already exists, skipping: {input_path}")
                    return

                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)

                import json

                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(response, f, indent=2, ensure_ascii=False)
            else:
                # For non-JSON responses, use the misc category
                output_path = self.get_output_path(input_path, "misc")

                # Check if output file already exists
                if (
                    output_path.exists()
                    and not self.config["processing"]["overwrite_existing"]
                ):
                    logging.info(f"Output file already exists, skipping: {input_path}")
                    return

                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(response)

            logging.info(f"Saved response to: {output_path}")

        except Exception as e:
            logging.error(f"Error saving response for {input_path}: {e}")
            logging.error(f"Error saving response: {e}")

    def _build_classification_prompt(self, content, file_path):
        """Build the classification prompt with categories and format requirements"""
        categories = self.config["classification"]["categories"]
        guidelines = self.config["classification"]["guidelines"]

        prompt = f"""
CLASSIFICATION TASK

Analyze the following content and classify it into one of these categories:

"""

        # Add category descriptions
        for category in categories:
            description = guidelines.get(category, "No description available")
            prompt += f"- {category}: {description}\n"

        prompt += f"""
CONTENT TO CLASSIFY (from file: {Path(file_path).name}):

{content}

RESPONSE FORMAT REQUIREMENTS:
You MUST respond with a valid JSON object using this exact structure:
{{
    "category": "string",           // The primary category from the list above
    "confidence": number,           // Confidence score from 0.0 to 1.0
    "subcategory": "string|null",   // Optional more specific classification
    "summary": "string",            // Brief 1-2 sentence summary of the content
    "tags": ["array", "of", "tags"] // Array of relevant tags/keywords
}}

IMPORTANT: Only output the JSON object, nothing else. Do not include any explanatory text.
"""
        return prompt

    def _parse_classification_response(self, response_content, file_path):
        """Parse the classification response and validate the JSON structure"""
        try:
            import json
            import re

            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                classification_result = json.loads(json_str)
            else:
                # Try to parse the entire response as JSON
                classification_result = json.loads(response_content)

            # Validate required fields
            required_fields = [
                "category",
                "confidence",
                "summary",
                "tags",
            ]
            for field in required_fields:
                if field not in classification_result:
                    raise ValueError(f"Missing required field: {field}")

            # Validate category is in the allowed list
            allowed_categories = self.config["classification"]["categories"]
            if classification_result["category"] not in allowed_categories:
                raise ValueError(
                    f"Invalid category: {classification_result['category']}"
                )

            # Validate confidence score
            confidence = classification_result["confidence"]
            if not isinstance(confidence, (int, float)) or not (
                0.0 <= confidence <= 1.0
            ):
                raise ValueError(f"Invalid confidence score: {confidence}")

            return classification_result

        except Exception as e:
            logging.error(f"Error parsing classification response for {file_path}: {e}")
            logging.error(f"Raw response: {response_content}")

            # Return a fallback classification with error information
            return {
                "category": "misc",
                "confidence": 0.0,
                "subcategory": "parsing_error",
                "summary": f"Error parsing classification: {str(e)}",
                "tags": ["error", "parsing_failed"],
            }


def load_config(config_path):
    """Load configuration from YAML file"""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Set default values for optional fields
        if "headers" not in config:
            config["headers"] = {}

        return config
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        raise


def create_client(config):
    """Create OpenAI client with configuration"""
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "No API key found. Set OPENROUTER_API_KEY or OPENAI_API_KEY in .env file"
        )

    return OpenAI(base_url=config["llm"]["base_url"], api_key=api_key)


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="Mastication - File monitoring and LLM processing"
    )
    parser.add_argument(
        "--config",
        "-c",
        default="config/config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    setup_logging()

    try:
        # Load configuration
        config_path = Path(args.config)
        if not config_path.exists():
            logging.error(f"Configuration file not found: {config_path}")
            return 1

        config = load_config(config_path)
        logging.info(f"Loaded configuration from: {config_path}")

        # Create LLM client
        client = create_client(config)
        logging.info(f"Created LLM client for: {config['llm']['base_url']}")

        # Create file processor
        processor = FileProcessor(config, client)

        # Setup file observer
        input_dir = Path(config["monitoring"]["input_dir"])
        input_dir.mkdir(parents=True, exist_ok=True)

        observer = Observer()
        observer.schedule(processor, str(input_dir), recursive=True)
        observer.start()

        logging.info(f"Started monitoring directory: {input_dir}")
        logging.info("Press Ctrl+C to stop...")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Stopping...")
        finally:
            observer.stop()
            observer.join()

    except Exception as e:
        logging.error(f"Application error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
