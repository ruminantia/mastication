#!/bin/bash

# Mastication Startup Script
# A simple script to run Mastication with Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[Mastication]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[Mastication]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[Mastication]${NC} $1"
}

print_error() {
    echo -e "${RED}[Mastication]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if required files exist
check_requirements() {
    local missing_files=()

    if [ ! -f "docker-compose.yml" ]; then
        missing_files+=("docker-compose.yml")
    fi

    if [ ! -f "config/config.yaml" ]; then
        print_warning "config/config.yaml not found. Using default configuration."
        # Copy example config if it exists
        if [ -f "config/examples/openrouter.yaml" ]; then
            cp config/examples/openrouter.yaml config/config.yaml
            print_status "Created config/config.yaml from example"
        fi
    fi

    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating template .env file."
        cat > .env << EOF
# Mastication Environment Variables
# Set your API key for your preferred LLM provider

# For OpenRouter (recommended)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Or for OpenAI directly
# OPENAI_API_KEY=your_openai_api_key_here

# For DeepSeek directly (if not using OpenRouter)
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
EOF
        print_status "Created .env template. Please edit it with your API key."
    fi

    # Create directories if they don't exist
    mkdir -p input output config

    return 0
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start      Start Mastication in detached mode (default)"
    echo "  stop       Stop Mastication"
    echo "  restart    Restart Mastication"
    echo "  logs       Show logs from Mastication"
    echo "  status     Show status of Mastication"
    echo "  build      Build the Docker image"
    echo "  clean      Stop and remove containers"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start     # Start the service"
    echo "  $0 logs      # View logs"
    echo "  $0 stop      # Stop the service"
}

# Function to start Mastication
start_mastication() {
    print_status "Starting Mastication..."
    check_docker
    check_requirements

    # Check if API key is set
    if ! grep -q "OPENROUTER_API_KEY=your_openrouter_api_key_here" .env && ! grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env; then
        print_success "API key configuration detected"
    else
        print_warning "Please set your API key in the .env file before starting"
        exit 1
    fi

    docker compose up -d
    print_success "Mastication started successfully!"
    print_status "Place files in the 'input' directory to start processing"
    print_status "View logs with: $0 logs"
}

# Function to stop Mastication
stop_mastication() {
    print_status "Stopping Mastication..."
    docker compose down
    print_success "Mastication stopped successfully!"
}

# Function to restart Mastication
restart_mastication() {
    print_status "Restarting Mastication..."
    docker compose restart
    print_success "Mastication restarted successfully!"
}

# Function to show logs
show_logs() {
    print_status "Showing Mastication logs (Ctrl+C to exit)..."
    docker compose logs -f mastication
}

# Function to show status
show_status() {
    print_status "Mastication status:"
    docker compose ps
}

# Function to build the image
build_image() {
    print_status "Building Mastication Docker image..."
    docker compose build
    print_success "Docker image built successfully!"
}

# Function to clean up
clean_up() {
    print_status "Cleaning up Mastication containers..."
    docker compose down
    print_success "Cleanup completed!"
}

# Main script logic
COMMAND=${1:-start}

case $COMMAND in
    start)
        start_mastication
        ;;
    stop)
        stop_mastication
        ;;
    restart)
        restart_mastication
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    build)
        build_image
        ;;
    clean)
        clean_up
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        echo ""
        show_usage
        exit 1
        ;;
esac
