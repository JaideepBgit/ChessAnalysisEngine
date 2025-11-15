# Chess Engine Interface

A professional chess analysis platform with AI-powered coaching, game analysis, and real-time position evaluation.

## 🎨 New Features

- **Material-UI Icons** - Professional icons throughout the interface
- **Light & Dark Themes** - Switch between bright and dark modes
- **Theme Persistence** - Your preference is automatically saved
- **AI Chess Coach** - Voice-enabled coaching with Ollama integration
- **Game Analysis** - Comprehensive move-by-move analysis with statistics

## 🚀 Quick Start

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8+
- Stockfish chess engine

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chess
   ```

2. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. **Start the application**
   
   **Option 1: Using the start script (Windows)**
   ```bash
   start.bat
   ```
   
   **Option 2: Manual start**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python app.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

5. **Open your browser**
   ```
   http://localhost:3000
   ```

## 🎯 Features

### Chess Engine
- Real-time position analysis with Stockfish
- Adjustable analysis depth (1-30)
- Best move suggestions with evaluations
- Move history and navigation

### Game Analysis
- Upload PGN files for analysis
- Move-by-move evaluation
- Accuracy statistics by game phase
- Performance rating calculation
- Visual evaluation graph
- Side-by-side board comparison

### AI Chess Coach (Optional)
- Voice-enabled coaching with Ollama
- Position-specific advice
- Move quality explanations
- Text and voice input/output

### Theme System
- **Light Theme** - Professional purple palette with cream backgrounds
- **Dark Theme** - Sleek dark interface with muted purple accents
- Easy toggle with sun/moon icon
- Persistent preference

## 📚 Documentation

All documentation is available in the `docs/` folder:

### Getting Started
- [START_HERE.md](docs/START_HERE.md) - Complete setup guide
- [QUICK_START.md](docs/QUICK_START.md) - Quick start instructions
- [SETUP_CHECKLIST.md](docs/SETUP_CHECKLIST.md) - Installation checklist

### Features
- [FEATURES.md](docs/FEATURES.md) - Complete feature list
- [THEME_README.md](docs/THEME_README.md) - Theme system guide
- [AI_FEATURES_SUMMARY.md](docs/AI_FEATURES_SUMMARY.md) - AI features overview

### Theme System
- [THEME_UPDATE.md](docs/THEME_UPDATE.md) - Theme implementation details
- [THEME_PREVIEW.md](docs/THEME_PREVIEW.md) - Color palettes and preview
- [QUICK_START_THEMES.md](docs/QUICK_START_THEMES.md) - Theme quick start
- [VISUAL_CHANGES_GUIDE.md](docs/VISUAL_CHANGES_GUIDE.md) - Before/after visual guide

### AI Setup (Optional)
- [AI_SETUP_GUIDE.md](docs/AI_SETUP_GUIDE.md) - AI coach setup instructions
- [QUICK_START_AI.md](docs/QUICK_START_AI.md) - AI quick start guide

### Advanced
- [IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md) - Implementation details
- [IMPLEMENTATION_SUMMARY_THEMES.md](docs/IMPLEMENTATION_SUMMARY_THEMES.md) - Theme implementation
- [PACKAGING_GUIDE.md](docs/PACKAGING_GUIDE.md) - Packaging instructions
- [KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) - Known issues and solutions
- [COMPETITIVE_COMPARISON.md](docs/COMPETITIVE_COMPARISON.md) - Feature comparison

## 🎨 Theme System

### Light Theme
- Primary Purple: `#633394`
- Secondary Purple: `#967CB2`
- Dark Purple: `#3B1C55`
- Brown Accent: `#61382E`
- Background: `#FBFAFA` (cream)
- Paper: `#FFFFFF` (white)

### Dark Theme
- Accent Primary: `#8b7fc8`
- Accent Secondary: `#6b5fb0`
- Background: `#0a0a0f` (very dark)
- Cards: `#13131a` (dark gray)

### Switching Themes
Click the sun/moon icon in the top-right corner to toggle between themes.

## 🛠️ Technology Stack

### Frontend
- React 18
- Material-UI Icons
- chess.js
- react-chessboard
- Axios

### Backend
- Flask
- python-chess
- Stockfish engine
- Ollama (optional, for AI features)
- Whisper (optional, for voice input)

## 📦 Project Structure

```
chess/
├── frontend/           # React frontend application
│   ├── src/
│   │   ├── App.js              # Main application
│   │   ├── GameAnalysis.js     # Game analysis component
│   │   ├── VoiceChat.js        # AI coach component
│   │   ├── theme.js            # Theme configuration
│   │   └── *.css               # Styling
│   └── package.json
├── backend/            # Flask backend API
│   ├── app.py                  # Main API server
│   └── requirements.txt
├── docs/               # Documentation
└── README.md           # This file
```

## 🎮 Usage

### Playing Chess
1. Make moves by clicking pieces and target squares
2. View real-time position evaluation
3. See best move suggestions
4. Navigate through move history

### Analyzing Games
1. Click "Analyze Game" button
2. Paste your PGN
3. Optionally enter your username
4. Click "Analyze Game"
5. Review move-by-move analysis
6. Check accuracy statistics
7. Use AI coach for position advice

### Using AI Coach (Optional)
1. Ensure Ollama is installed and running
2. Click microphone icon or type question
3. Get position-specific coaching
4. Listen to voice responses

## 🔧 Configuration

### Stockfish Path
Edit `backend/app.py` to set your Stockfish path:
```python
STOCKFISH_PATH = r"path\to\stockfish.exe"
```

### Analysis Depth
Adjust in the UI (1-30) or modify default in code.

### Theme Colors
Edit `frontend/src/theme.js` to customize colors.

## 🐛 Troubleshooting

### Backend won't start
- Check Stockfish path is correct
- Ensure Python dependencies are installed
- Verify port 5000 is available

### Frontend won't start
- Run `npm install` in frontend directory
- Check Node.js version (v14+)
- Verify port 3000 is available

### AI features not working
- Install Ollama: https://ollama.ai
- Run `ollama pull llama2`
- Install Whisper: `pip install openai-whisper`

### Theme not switching
- Clear browser cache
- Check browser console for errors
- Verify localStorage is enabled

## 📄 License

This project is provided as-is for educational and personal use.

## 🤝 Contributing

Contributions are welcome! Please check the documentation in the `docs/` folder for implementation details.

## 📞 Support

For detailed documentation, see the `docs/` folder:
- Setup issues: [START_HERE.md](docs/START_HERE.md)
- Feature questions: [FEATURES.md](docs/FEATURES.md)
- Theme help: [THEME_README.md](docs/THEME_README.md)
- AI setup: [AI_SETUP_GUIDE.md](docs/AI_SETUP_GUIDE.md)

---

**Version**: 2.0.0  
**Last Updated**: November 2025  
**Status**: ✅ Production Ready
