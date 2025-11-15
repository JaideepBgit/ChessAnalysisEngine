# Simple Text-to-Speech Setup

## Quick Fix (Recommended)

Use **pyttsx3** - it's simple, works everywhere, and requires no model downloads:

```bash
pip install pyttsx3
```

That's it! Restart your Flask server and TTS will work.

## Why pyttsx3?

- ✅ **Simple:** One command install
- ✅ **No downloads:** Uses system voices (Windows SAPI, macOS NSSpeechSynthesizer, Linux espeak)
- ✅ **Works offline:** Completely local
- ✅ **No dependencies:** No ONNX, no models, no complexity
- ⚠️ **Quality:** Good but not as natural as Piper

## Installation

```bash
cd backend
pip install pyttsx3
python app.py
```

## If You Want Better Quality (Piper)

Piper has more natural voices but is complex to set up:

### Option 1: Install from GitHub
```bash
pip install onnxruntime
pip install git+https://github.com/rhasspy/piper.git
```

### Option 2: Download Voice Model Manually
1. Create `backend/models/` folder
2. Download: https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-en-us-lessac-medium.tar.gz
3. Extract `en_US-lessac-medium.onnx` and `en_US-lessac-medium.onnx.json` to `backend/models/`

## Current Setup

The code now has **automatic fallback**:
1. Tries Piper first (if available and model found)
2. Falls back to pyttsx3 (if Piper fails)
3. Shows clear error if neither works

## Test It

```bash
# Install pyttsx3
pip install pyttsx3

# Restart Flask
python app.py

# You should see:
# ✓ SpeechRecognition available (voice input enabled)
# ✓ Piper TTS library available (or pyttsx3 will be used as fallback)
```

## Summary

**Just use pyttsx3** - it's the easiest solution and works great for a chess coach!

```bash
pip install pyttsx3
```

Done! 🎉
