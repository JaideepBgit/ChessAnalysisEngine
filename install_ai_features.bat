@echo off
echo ========================================
echo Chess Analysis Pro - AI Features Setup
echo ========================================
echo.

echo Step 1: Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+ first.
    pause
    exit /b 1
)
echo Python found!
echo.

echo Step 2: Installing Python dependencies...
cd backend
pip install ollama openai-whisper pyttsx3 sounddevice numpy scipy
if errorlevel 1 (
    echo ERROR: Failed to install Python packages
    pause
    exit /b 1
)
echo Python packages installed!
echo.

echo Step 3: Checking Ollama...
ollama --version
if errorlevel 1 (
    echo.
    echo WARNING: Ollama not found!
    echo Please install Ollama from: https://ollama.ai/download
    echo.
    echo After installing Ollama, run this command:
    echo   ollama pull llama3.2
    echo.
    pause
) else (
    echo Ollama found!
    echo.
    echo Step 4: Downloading AI model (this may take a few minutes)...
    ollama pull llama3.2
    if errorlevel 1 (
        echo ERROR: Failed to download model
        pause
        exit /b 1
    )
    echo AI model downloaded!
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the application:
echo   1. Open a terminal and run: cd backend ^&^& python app.py
echo   2. Open another terminal and run: cd frontend ^&^& npm start
echo   3. Open http://localhost:3000 in your browser
echo.
echo For detailed instructions, see: AI_SETUP_GUIDE.md
echo.
pause
