#!/bin/bash
# Run script for MP3 to Video Generator

echo "Starting MP3 to Video Generator..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import cv2" 2>/dev/null; then
    echo "Installing missing dependencies..."
    pip install -r requirements.txt
fi

# Run the application
echo "Launching application..."
python main.py



