# AI Chess Coach Setup Guide

This guide will help you set up the AI voice features in your Chess Analysis application.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Microphone (for voice input)
- Speakers/Headphones (for voice output)

## Step 1: Install Ollama

Ollama is required for the AI chess coach feature.

### Windows
1. Download Ollama from: https://ollama.ai/download
2. Run the installer
3. Ollama will start automatically

### macOS
```bash
brew install ollama
ollama serve
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

### Verify Installation
Open a terminal and run:
```bash
ollama --version
```

## Step 2: Download AI Model

After installing Ollama, download the chess coach model:

```bash
ollama pull llama3.2
```

This will download a 2GB model. It may take a few minutes depending on your internet speed.

### Alternative Models

If you want better analysis (but slower):
```bash
ollama pull llama3.1:8b
```

If you want faster responses (but less detailed):
```bash
ollama pull llama3.2:1b
```

## Step 3: Install Python Dependencies

Navigate to the backend directory and install the required packages:

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- `ollama` - Python client for Ollama
- `openai-whisper` - Speech-to-text (150MB model download on first use)
- `pyttsx3` - Text-to-speech
- `sounddevice` - Audio recording
- `numpy` and `scipy` - Audio processing

### Note on Whisper
The first time you use voice input, Whisper will download a ~150MB model. This is automatic and only happens once.

## Step 4: Start the Application

### Start Backend
```bash
cd backend
python app.py
```

### Start Frontend (in a new terminal)
```bash
cd frontend
npm start
```

## Step 5: Test AI Features

1. Open the application in your browser (http://localhost:3000)
2. Go to "Analyze Game" mode
3. Paste a PGN and analyze a game
4. Navigate to any move
5. You should see the "🤖 AI Chess Coach" section
6. Try:
   - Clicking "🎤 Ask Coach" to use voice
   - Typing a question in the text box
   - Clicking quick question buttons

## Troubleshooting

### "Ollama not detected" Warning

**Problem:** The app shows "Ollama not detected"

**Solutions:**
1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```
2. Check if the model is installed:
   ```bash
   ollama list
   ```
3. If no models are listed, pull one:
   ```bash
   ollama pull llama3.2
   ```

### Voice Input Not Working

**Problem:** Microphone doesn't work

**Solutions:**
1. Check browser permissions - allow microphone access
2. Make sure your microphone is connected and working
3. Try a different browser (Chrome/Edge recommended)
4. Check Windows/macOS microphone permissions

### Voice Output Not Working

**Problem:** No audio when AI responds

**Solutions:**
1. Check your speakers/headphones are connected
2. Check system volume
3. On Windows, make sure SAPI voices are installed:
   - Settings → Time & Language → Speech → Manage voices
4. On macOS, voices should work by default
5. On Linux, install espeak:
   ```bash
   sudo apt-get install espeak
   ```

### Slow AI Responses

**Problem:** AI takes too long to respond

**Solutions:**
1. Use a smaller model:
   ```bash
   ollama pull llama3.2:1b
   ```
2. Close other applications to free up RAM
3. Make sure you have at least 4GB free RAM
4. Consider upgrading your hardware (8GB+ RAM recommended)

### Whisper Model Download Issues

**Problem:** Whisper fails to download

**Solutions:**
1. Check your internet connection
2. Try manually downloading:
   ```python
   import whisper
   whisper.load_model("base")
   ```
3. If behind a proxy, configure it:
   ```bash
   export HTTP_PROXY=your_proxy
   export HTTPS_PROXY=your_proxy
   ```

## System Requirements

### Minimum
- CPU: Dual-core 2.0 GHz
- RAM: 4GB
- Storage: 5GB free space
- Internet: For initial setup only

### Recommended
- CPU: Quad-core 2.5 GHz or better
- RAM: 8GB or more
- Storage: 10GB free space (for multiple models)
- GPU: Optional, but speeds up Whisper transcription

## Privacy & Offline Use

Once everything is installed:
- ✅ **100% offline** - No data sent to external servers
- ✅ **Private** - All analysis happens on your computer
- ✅ **No API costs** - Everything runs locally
- ✅ **No internet required** - After initial setup

## Model Sizes

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| llama3.2:1b | 1GB | Fast | Good |
| llama3.2 (3b) | 2GB | Medium | Better |
| llama3.1:8b | 5GB | Slow | Best |
| mistral | 4GB | Medium | Excellent |

## Usage Tips

### Voice Input
1. Click "🎤 Ask Coach"
2. Wait for the red recording indicator
3. Speak clearly: "Why is this move bad?"
4. Click again to stop recording
5. Wait for transcription and AI response

### Text Input
1. Type your question in the text box
2. Press Enter or click "Send"
3. AI will respond in text and voice

### Quick Questions
- Use the pre-made question buttons for common queries
- Great for beginners who don't know what to ask

### Best Practices
- Ask specific questions about the current position
- Use phrases like:
  - "Why is this move good/bad?"
  - "What should I look for?"
  - "What are better alternatives?"
  - "Explain the tactics here"
  - "What's the plan in this position?"

## Updating

### Update Ollama
```bash
# Windows: Download new installer from ollama.ai
# macOS/Linux:
brew upgrade ollama  # macOS
# or re-run install script on Linux
```

### Update AI Models
```bash
ollama pull llama3.2  # Re-downloads latest version
```

### Update Python Dependencies
```bash
cd backend
pip install --upgrade -r requirements.txt
```

## Uninstalling

### Remove Ollama
- **Windows:** Control Panel → Uninstall Programs → Ollama
- **macOS:** `brew uninstall ollama`
- **Linux:** `sudo rm /usr/local/bin/ollama`

### Remove Models
```bash
ollama rm llama3.2
```

### Remove Python Packages
```bash
pip uninstall ollama openai-whisper pyttsx3 sounddevice
```

## Support

If you encounter issues:
1. Check this guide first
2. Verify all prerequisites are installed
3. Check the console for error messages
4. Make sure Ollama is running (`ollama serve`)
5. Try restarting the application

## Advanced Configuration

### Change AI Model in Code

Edit `frontend/src/VoiceChat.js`:
```javascript
// Line ~115
const response = await axios.post(`${API_URL}/api/chat-analysis`, {
  model: 'llama3.1:8b'  // Change model here
  // ... rest of the code
});
```

Edit `backend/app.py`:
```python
# Line ~280
response = ollama.chat(model='llama3.1:8b', messages=[...])
```

### Change Voice Speed

Edit `backend/app.py`:
```python
# Line ~45
tts_engine.setProperty('rate', 150)  # Change to 120 (slower) or 180 (faster)
```

### Change Whisper Model

Edit `backend/app.py`:
```python
# Line ~40
whisper_model = whisper.load_model("small")  # Options: tiny, base, small, medium, large
```

Larger models are more accurate but slower:
- **tiny** - 75MB, fastest, least accurate
- **base** - 150MB, fast, good accuracy (default)
- **small** - 500MB, medium speed, better accuracy
- **medium** - 1.5GB, slow, very accurate
- **large** - 3GB, very slow, best accuracy

## Next Steps

Once everything is working:
1. Analyze your games
2. Ask the AI coach questions about your moves
3. Learn from the explanations
4. Improve your chess!

Enjoy your AI-powered chess coach! 🎉
