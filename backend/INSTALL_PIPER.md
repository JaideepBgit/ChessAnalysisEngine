# How to Install Piper TTS Properly

## The Issue

The `piper-tts` package on PyPI is outdated and doesn't work properly. We need to install it correctly.

## Solution: Install from GitHub

### Step 1: Uninstall old version (if installed)
```bash
pip uninstall piper-tts -y
```

### Step 2: Install dependencies
```bash
pip install onnxruntime
```

### Step 3: Install Piper from GitHub
```bash
pip install git+https://github.com/rhasspy/piper.git
```

### Step 4: Install SpeechRecognition
```bash
pip install SpeechRecognition
```

### Step 5: Restart Flask
```bash
cd backend
python app.py
```

You should see:
```
✓ Ollama available
✓ SpeechRecognition available (voice input enabled)
✓ Piper TTS available (voice output enabled)
Loading Piper voice model...
✓ Piper voice model loaded
```

The first time it runs, it will download the voice model (~50MB). This only happens once.

## Alternative: Use pyttsx3 (Simpler but lower quality)

If Piper installation is too complex, you can use pyttsx3 instead:

```bash
pip install pyttsx3
```

Then I can update the code to use pyttsx3 instead.

## Verification

Test if Piper is working:

```python
python -c "from piper.voice import PiperVoice; print('Piper OK')"
```

If this works, restart Flask and it should work!

## Troubleshooting

### "No module named 'piper'"

**Solution:** Install from GitHub:
```bash
pip install git+https://github.com/rhasspy/piper.git
```

### "No module named 'onnxruntime'"

**Solution:**
```bash
pip install onnxruntime
```

### Still not working?

Let me know and I can switch to pyttsx3 which is simpler (but lower voice quality).

## Summary

```bash
# Quick install
pip uninstall piper-tts -y
pip install onnxruntime
pip install git+https://github.com/rhasspy/piper.git
pip install SpeechRecognition

# Restart Flask
python app.py
```

The voice model will download automatically on first use.
