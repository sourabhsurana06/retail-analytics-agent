#!/bin/bash

echo "Setting up Retail Analytics Agent..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Install Python 3.10+ first."
    exit 1
fi

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 not found."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Set up .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Add your OPENAI_API_KEY to it before running the agent."
fi

# Build database
echo "Building database..."
python3 core/CreateDB.py

# Build FAISS index
echo "Building vector index..."
python3 build_index.py

echo ""
echo "Setup complete."
echo ""
echo "To run:"
echo "  Terminal 1: python3 server.py"
echo "  Terminal 2: python3 agent.py"
