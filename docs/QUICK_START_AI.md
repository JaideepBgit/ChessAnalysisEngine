# Quick Start: AI Features

Get your AI Chess Coach running in 5 minutes!

## Prerequisites

- Python 3.8+
- Node.js 16+
- Microphone (for voice input)

## Step 1: Install Ollama (2 minutes)

### Windows
1. Download: https://ollama.ai/download
2. Run installer
3. Done! (Ollama starts automatically)

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

## Step 2: Download AI Model (2 minutes)

```bash
ollama pull llama3.2
```

Wait for the 2GB download to complete.

## Step 3: Install Python Dependencies (1 minute)

```bash
cd backend
pip install ollama openai-whisper pyttsx3 sounddevice numpy scipy
```

## Step 4: Start the App

### Terminal 1 - Backend
```bash
cd backend
python app.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm start
```

## Step 5: Try It Out!

1. Open http://localhost:3000
2. Click "📊 Analyze Game"
3. Paste a PGN (or use sample from `example_games.txt`)
4. Click "Analyze Game"
5. Navigate to any move
6. Scroll down to see "🤖 AI Chess Coach"
7. Click "🎤 Ask Coach" and say: "Why is this move good or bad?"
8. Or type your question and click "Send"

## That's It! 🎉

You now have an AI chess coach that:
- Explains positions in plain English
- Responds to voice commands
- Speaks answers aloud
- Works 100% offline

## Troubleshooting

### "Ollama not detected"
```bash
# Check if Ollama is running
ollama --version

# If not running, start it
ollama serve
```

### "Model not found"
```bash
# Download the model
ollama pull llama3.2

# Verify it's installed
ollama list
```

### Voice not working
- Allow microphone access in browser
- Check system microphone settings
- Try Chrome/Edge (best compatibility)

## Next Steps

- Read [AI_SETUP_GUIDE.md](AI_SETUP_GUIDE.md) for detailed info
- Read [PACKAGING_GUIDE.md](PACKAGING_GUIDE.md) to create desktop app
- Read [AI_FEATURES_SUMMARY.md](AI_FEATURES_SUMMARY.md) for full feature list

## Quick Tips

### Ask Better Questions
- "Why is this move bad?"
- "What should I look for in this position?"
- "What are better alternatives?"
- "Explain the tactics here"
- "What's the plan for white?"

### Use Quick Questions
- Click the pre-made question buttons
- Great for beginners
- Saves typing

### Type Instead of Speaking
- Use the text input box
- Faster for some users
- Works without microphone

Enjoy your AI chess coach! 🚀
