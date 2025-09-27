# Mastication

A production-ready Python tool that monitors a directory for new files, classifies them with an LLM, and saves structured JSON output. Designed to be API-agnostic and support any OpenAI-compatible endpoint.

## Features

- **File Monitoring**: Watches a specified directory for new markdown and text files
- **LLM Integration**: Supports any OpenAI-compatible API (OpenRouter, OpenAI, DeepSeek, Gemini, etc.)
- **Smart Classification**: Automatically categorizes content into predefined types with confidence scores
- **Structured JSON Output**: Clean, predictable JSON responses for easy integration
- **Configurable**: Easy configuration via YAML file and environment variables
- **Containerized**: Fully Dockerized for easy deployment

## Quick Start

Before starting, ensure the `fodder_transcriptions` Docker volume exists and contains transcriptions from the Fodder project.

### Prerequisites

- Docker and Docker Compose
- API key from your preferred LLM provider (OpenRouter recommended)

### Configuration Options

Mastication is optimized for classification but supports two modes:

1. **Classification Mode** (Default): Automatic categorization into content types
2. **Generic Processing**: Basic file processing with custom prompts

The default configuration (`config/config.yaml`) uses classification mode.

### 1. Clone and Setup

```bash
git clone https://github.com/ruminantia/mastication.git
cd mastication
```

### 2. Configure Environment

Create or edit the `.env` file:

```bash
# For OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Or everything else
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Configure the Application

**Example config:**
```yaml
llm:
  base_url: "https://openrouter.ai/api/v1"
  model: "google/gemini-2.5-flash-preview-09-2025"
  temperature: 0.1 # Lower temperature for consistent classification
  max_tokens: 500
  system_prompt: |
    You are a classification assistant that analyzes text content and categorizes it into specific types.
    Your task is to classify the input text into one of the predefined categories based on its content and purpose.

monitoring:
  input_dir: "./input"
  output_dir: "./output"
  file_extensions: [".txt", ".md", ".markdown"]
  polling_interval: 5

# API Headers (optional)
headers:
  # Optional headers for OpenRouter or other services
  HTTP-Referer: "" # Site URL for rankings on openrouter.ai
  X-Title: "" # Site title for rankings on openrouter.ai

processing:
  delete_after_processing: false
  overwrite_existing: false
  max_file_size: 10485760 # 10MB

classification:
  categories:
    - "notes_rants"
    - "questions_research"
    - "events_calendar"
    - "tasks_todos"
    - "personal_matters"
    - "news_stories"
    - "emails"
    - "misc"

  response_format:
    type: "json"
    schema:
      category: "string"
      confidence: "number"
      subcategory: "string|null"
      summary: "string"
      tags: "array"

  guidelines:
    notes_rants: "Personal thoughts, reflections, ideas, creative writing, journal entries, unstructured content"
    questions_research: "Questions seeking answers, research topics, knowledge gaps, things to investigate"
    events_calendar: "Appointments, meetings, dates, deadlines, time-sensitive events"
    tasks_todos: "Action items, chores, work tasks, things that need to be done"
    personal_matters: "Health observations, dietary notes, fitness tracking, personal well-being"
    news_stories: "Scraped web content, articles, news, informational reading material"
    emails: "Email drafts, correspondence, communication that needs sending"
    misc: "Anything that doesn't fit other categories, ambiguous content"
```

### 4. Run with Docker Compose

Using the convenience script:
```bash
./run-docker.sh start
```

Or directly:
```bash
docker compose up -d
```

### 5. Start Processing Files

Drop files into the `input/` directory:

```bash
echo "Hello, world!" > input/test.txt
```

Check the `output/` directory for processed results.

## Manual Installation (Without Docker)

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python src/mastication.py
```

Or with custom config:

```bash
python src/mastication.py --config config/config.yaml --verbose
```

## Available Scripts

### Docker Management
```bash
./run-docker.sh start    # Start the service
./run-docker.sh stop     # Stop the service
./run-docker.sh restart  # Restart the service
./run-docker.sh logs     # View logs
./run-docker.sh status   # Check service status
./run-docker.sh build    # Rebuild Docker image
./run-docker.sh clean    # Clean up containers
```

## Configuration

### Volume Configuration

This Mastication instance is configured to:
- Mount the `fodder_transcriptions` Docker volume as a read-only input directory
- Process files with extensions: `.txt`, `.md`, `.markdown`
- Never delete files from the input volume (read-only mount)
- Save processed results to the local `./output` directory using a structured organization system

### Output Structure

Processed files are organized in a structured directory hierarchy:

```
output/
├── notes_rants/
│   └── 2025/
│       └── 09/
│           └── 27/
│               └── 1758994294.json
├── questions_research/
│   └── 2025/
│       └── 09/
│           └── 27/
│               └── 1758994295.json
├── events_calendar/
│   └── 2025/
│       └── 09/
│           └── 27/
│               └── 1758994296.json
└── ... (other categories)
```

**Directory Structure:**
- **Category directories** (e.g., `notes_rants/`, `questions_research/`) based on classification
- **Date hierarchy** (`YYYY/MM/DD/`) for organized time-based storage
- **Timestamp filenames** (e.g., `1758994294.json`) using Unix timestamps

**JSON Output Format:**
Each processed file generates a JSON file containing:
- Original classification response (category, confidence, summary, tags)
- Additional `input_filename` field showing the source file name
- Example:
```json
{
  "category": "notes_rants",
  "confidence": 0.95,
  "subcategory": "personal_reflection",
  "summary": "Summary of the processed content",
  "tags": ["tag1", "tag2"],
  "input_filename": "original_transcription.txt"
}
```

### Environment Variables

- `OPENROUTER_API_KEY`: API key for OpenRouter
- `OPENAI_API_KEY`: API key for OpenAI (alternative)

### Categories

The default configuration automatically categorizes content. This mode:

- **Categories Content** into 8 predefined types:
  - `notes_rants`: Personal thoughts, ideas, journal entries
  - `questions_research`: Questions seeking answers, research topics
  - `events_calendar`: Appointments, meetings, deadlines
  - `tasks_todos`: Action items, chores, work tasks
  - `personal_matters`: Health observations, dietary notes
  - `news_stories`: Scraped web content, articles
  - `emails`: Email drafts, correspondence
  - `misc`: Anything that doesn't fit other categories

- **Returns Structured JSON** with:
  - Category classification
  - Confidence score
  - Brief summary
  - Relevant tags

# File Monitoring
monitoring:
  input_dir: "./input"                      # Directory to watch
  output_dir: "./output"                    # Directory for outputs
  file_extensions: [".txt", ".md"]          # File types to process
  polling_interval: 5                       # Check interval in seconds

# Optional API Headers
headers:
  HTTP-Referer: "https://your-site.com"     # For OpenRouter rankings
  X-Title: "Your Site Name"                 # For OpenRouter rankings

# Processing Options
processing:
  delete_after_processing: false            # Delete input files after processing
  overwrite_existing: false                 # Overwrite existing output files
  max_file_size: 10485760                   # Maximum file size (10MB)
```

## Supported LLM Providers

Mastication works with any OpenAI-compatible API. Here are some examples:

### OpenRouter
```yaml
base_url: "https://openrouter.ai/api/v1"
model: "openai/gpt-4o"
```

## Usage Examples

### Basic File Processing
1. Place a text file in `input/` directory
2. Mastication detects the new file
3. Sends content to LLM with your configured prompt
4. Saves response to `output/` with timestamp

## Troubleshooting

### Common Issues

**File not being processed:**
- Check file extension matches config
- Verify file size is under limit
- Check logs for errors

**API errors:**
- Verify API key in `.env` file
- Check base URL and model name
- Ensure provider supports the model

**Docker issues:**
- Check Docker is running
- Verify file permissions on mounted volumes

### Viewing Logs

Using the convenience script:
```bash
./run-docker.sh logs
```

Or directly:
```bash
docker compose logs -f mastication
```

Manual installation:
```bash
python src/mastication.py --verbose
```

## Development

### Building the Docker Image

```bash
./run-docker.sh build
```

Or directly:
```bash
docker build -t mastication .
```

### Testing the System

```bash
# Test classification with sample content
echo "Meeting with team on Monday at 2pm" > input/test_event.txt
echo "What's the best way to learn Python?" > input/test_question.txt

# Monitor results
tail -f output/*.json
```

### File Structure

```
mastication/
├── src/mastication.py          # Main application
├── config/
│   └── config.yaml            # Default config
├── input/                     # Monitored directory
├── output/                    # Processed JSON files
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Container orchestration
├── run-docker.sh              # Docker management script
├── README.md                  # This file
└── EXAMPLES.md                # Classification examples
```

### Example Workflow

**Input file** (`input/meeting.txt`):
```
Team sync meeting on Friday at 10am to discuss Q2 goals
```

**Output JSON** (`output/meeting_processed_1234567890.json`):
```json
{
  "category": "events_calendar",
  "confidence": 0.92,
  "subcategory": "team_meeting",
  "summary": "Scheduled team sync meeting to discuss Q2 goals",
  "tags": ["meeting", "team", "planning"]
}
```

See `EXAMPLES.md` for comprehensive classification examples.

## Next Steps

After classification, you can:
- Route different content types to specialized processing pipelines
- Build workflows based on confidence scores and categories
- Integrate with task management or calendar systems
- Analyze patterns in your content types over time

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and feature requests, please open an issue on the GitHub repository.
