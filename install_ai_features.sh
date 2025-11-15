#!/bin/bash

echo "========================================"
echo "Chess Analysis Pro - AI Features Setup"
echo "========================================"
echo ""

echo "Step 1: Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found! Please install Python 3.8+ first."
    exit 1
fi
python3 --version
echo "Python found!"
echo ""

echo "Step 2: Installing Python dependencies..."
cd backend
pip3 install ollama openai-whisper pyttsx3 sounddevice numpy scipy
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python packages"
    exit 1
fi
echo "Python packages installed!"
echo ""

echo "Step 3: Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo ""
    echo "WARNING: Ollama not found!"
    echo "Please install Ollama:"
    echo ""
    echo "macOS:   brew install ollama"
    echo "Linux:   curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    echo "After installing Ollama, run:"
    echo "  ollama serve"
    echo "  ollama pull llama3.2"
    echo ""
    read -p "Press Enter to continue..."
else
    echo "Ollama found!"
    echo ""
    echo "Step 4: Starting Ollama service..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 2
    
    echo "Step 5: Downloading AI model (this may take a few minutes)..."
    ollama pull llama3.2
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to download model"
        kill $OLLAMA_PID 2>/dev/null
        exit 1
    fi
    echo "AI model downloaded!"
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To start the application:"
echo "  1. Terminal 1: cd backend && python3 app.py"
echo "  2. Terminal 2: cd frontend && npm start"
echo "  3. Open http://localhost:3000 in your browser"
echo ""
echo "For detailed instructions, see: AI_SETUP_GUIDE.md"
echo ""
