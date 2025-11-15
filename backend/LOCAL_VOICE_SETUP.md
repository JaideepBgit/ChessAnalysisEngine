# Local Voice Features Setup (Free!)

## Overview

This setup uses **completely free, local** voice features:
- **SpeechRecognition** - Voice input (uses Google's free API)
- **Piper TTS** - Voice output (local, high-quality, neural voices)

✅ No API keys needed  
✅ No costs  
✅ No PyTorch conflicts  
✅ High-quality voices  

## Installation

### 1. Install Python Packages

```bash
cd backend
pip install SpeechRecognition pydub piper-tts
```

### 2. Install Piper TTS

Piper needs to be installed separately:

**Windows:**
```bash
pip install piper-tts
```

Then download a voice model:
```bash
# This will download the en_US-lessac-medium voice (~50MB)
piper --model en_US-lessac-medium --download-dir ./models
```

**Linux:**
```bash
pip install piper-tts
# Or use system package manager
sudo apt-get install piper-tts
```

**Mac:**
```bash
pip install piper-tts
# Or use Homebrew
brew install piper-tts
```

### 3. Verify Installation

```bash
# Test Piper
piper --version

# Test SpeechRecognition
python -c "import speech_recognition; print('SpeechRecognition OK')"
```

### 4. Restart Flask

```bash
python app.py
```

You should see:
```
✓ Ollama available
✓ SpeechRecognition available (voice input enabled)
✓ Piper TTS available (voice output enabled)
```

### 5. Refresh Browser

Press Ctrl+F5

## How It Works

### Voice Input (SpeechRecognition)
- Records your voice
- Sends to Google's free speech-to-text API
- Returns transcribed text
- **Cost:** Free (Google provides this for free)
- **Quality:** Excellent
- **Speed:** Fast (~1-2 seconds)

### Voice Output (Piper TTS)
- Takes text from AI
- Generates speech locally using neural network
- Plays natural-sounding voice
- **Cost:** Free (runs locally)
- **Quality:** Very good (neural voices)
- **Speed:** Fast (~1 second for typical response)

## Available Voices

Piper has many voices. The default is `en_US-lessac-medium` (high quality, natural).

Other options:
- `en_US-amy-low` - Faster, lower quality
- `en_US-amy-medium` - Balanced
- `en_US-lessac-high` - Highest quality (slower)
- `en_GB-alan-medium` - British accent
- Many more at: https://github.com/rhasspy/piper

To change voice, edit `backend/app.py`:
```python
['piper', '--model', 'en_US-amy-medium', '--output_file', output_path]
```

## Troubleshooting

### "SpeechRecognition not available"

**Solution:**
```bash
pip install SpeechRecognition
```

### "Piper TTS not available"

**Solution:**
```bash
pip install piper-tts
piper --version  # Test it works
```

### "Could not request results"

This means Google's API is unreachable.
- Check internet connection
- Google's API might be temporarily down (rare)
- Try again in a few seconds

### "Could not understand audio"

- Speak more clearly
- Reduce background noise
- Check microphone is working
- Try recording again

### Piper voice sounds robotic

- Download a better quality model:
  ```bash
  piper --model en_US-lessac-high --download-dir ./models
  ```
- Update the model name in `app.py`

## Advantages

| Feature | Local (This) | OpenAI API |
|---------|-------------|------------|
| Cost | ✅ Free | ❌ ~$1-2/month |
| Setup | ✅ Simple | ❌ Need API key |
| Privacy | ✅ Mostly local* | ❌ Cloud-based |
| Quality | ✅ Very good | ✅ Excellent |
| Speed | ✅ Fast | ✅ Fast |
| Offline | ⚠️ Partial** | ❌ No |

*Voice input uses Google's free API (requires internet)  
**Voice output is fully local, voice input needs internet

## Performance

- **Voice input:** ~1-2 seconds (Google API)
- **Voice output:** ~1 second (local generation)
- **Total latency:** ~2-3 seconds for full conversation

## Privacy Note

- **Voice input:** Audio sent to Google (free API)
- **Voice output:** Completely local (no data sent anywhere)
- **AI coaching:** Uses local Ollama (no data sent)

If you need fully offline voice input, you'd need to use Vosk or similar (more complex setup).

## Summary

1. Install: `pip install SpeechRecognition pydub piper-tts`
2. Test: `piper --version`
3. Restart Flask: `python app.py`
4. Refresh browser
5. Enjoy free, high-quality voice features! 🎤

---

**No API keys, no costs, no PyTorch conflicts!**
