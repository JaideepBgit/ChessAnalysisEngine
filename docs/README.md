# Chess Analysis Pro

A modern AI-powered chess analysis application with voice interaction and comprehensive game analysis.

## ✨ New: AI Chess Coach with Voice Features!

- **🤖 AI Coach**: Ask questions about positions and get natural language explanations
- **🎤 Voice Input**: Speak your questions hands-free
- **🔊 Voice Output**: Hear AI responses spoken aloud
- **💬 Natural Conversations**: "Why is this move bad?" "What should I look for?"
- **🔒 100% Offline**: All AI processing happens locally (after setup)
- **🆓 No API Costs**: Uses free, open-source Ollama

[See AI Setup Guide](AI_SETUP_GUIDE.md) | [Packaging Guide](PACKAGING_GUIDE.md)

## Features

### Interactive Chess Board
- **Interactive Chessboard**: Click and drag pieces to make moves
- **Real-time Engine Analysis**: Powered by Stockfish
- **Move Evaluation**: See evaluation scores for each position
- **Best Move Suggestions**: Get top 3 best moves with scores
- **Move History**: Navigate through game moves
- **Adjustable Depth**: Control engine analysis depth (1-30)

### Comprehensive Game Analysis (NEW!)
- **Paste PGN and analyze complete games** with detailed statistics
- **Move-by-Move Analysis**:
  - Centipawn loss for each move
  - Move quality classification (Excellent ✓, Good ○, Inaccuracy ?!, Mistake ?, Blunder ??, Severe Blunder ???)
  - Best move suggestions for every position
  - Side-by-side board comparison (your move vs best move)

### Advanced Statistics
- **Overall Accuracy**: Chess.com-style accuracy percentage
- **Performance Rating**: Calculated based on your play quality vs opponent rating
- **Phase-Specific Analysis**: 
  - Opening accuracy and move count
  - Middlegame accuracy and move count
  - Endgame accuracy and move count
- **Move Quality Breakdown**:
  - Count of excellent moves, good moves, inaccuracies, mistakes, blunders, severe blunders
  - Average centipawn loss per move
- **Material tracking** throughout the game
- **Visual indicators** for move quality with color coding

## Project Structure

```
chess-engine-interface/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── App.css         # Styles
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Global styles
│   └── package.json        # Node dependencies
└── README.md
```

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- Stockfish chess engine

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Update Stockfish path in `app.py`:
```python
STOCKFISH_PATH = r"C:\path\to\your\stockfish.exe"
```

4. Run the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

### Play Mode
1. **Make Moves**: Click on a piece to see legal moves (green dots), then click destination square
2. **Analyze Position**: Engine automatically analyzes after each move
3. **View Best Moves**: See top 3 engine recommendations with evaluations
4. **Navigate History**: Click on moves in the list or use Previous/Next buttons
5. **Adjust Depth**: Change analysis depth for stronger/faster analysis
6. **New Game**: Reset the board to starting position

### Game Analysis Mode
1. **Click "📊 Analyze Game"** button in the header
2. **Enter your username** (optional) - helps identify which player to focus on
3. **Paste your PGN** from Chess.com, Lichess, or any chess platform
4. **Click "Analyze Game"** - the engine will analyze every move (takes 1-2 minutes)
5. **Review comprehensive statistics**:
   - Your overall accuracy and performance rating
   - Phase-specific accuracy (opening, middlegame, endgame)
   - Move quality breakdown
6. **Navigate through moves** to see:
   - Side-by-side comparison of your move vs best move
   - Centipawn loss and move quality for each position
   - Evaluation changes throughout the game
7. **Identify mistakes** - moves with high centipawn loss are highlighted

## API Endpoints

### POST `/api/analyze-position`
Analyze a chess position
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "depth": 18
}
```

### POST `/api/make-move`
Make a move on the board
```json
{
  "fen": "current_position_fen",
  "move": "e2e4"
}
```

### POST `/api/get-legal-moves`
Get all legal moves for current position
```json
{
  "fen": "current_position_fen"
}
```

### POST `/api/analyze-game`
Analyze a complete game from PGN
```json
{
  "pgn": "1. e4 e5 2. Nf3...",
  "targetPlayer": "player_name"
}
```

### POST `/api/chat-analysis` (NEW!)
Get AI coach analysis of a position
```json
{
  "fen": "position_fen",
  "move": "e4",
  "bestMove": "Nf3",
  "evaluation": 50,
  "cpLoss": 25,
  "quality": "Inaccuracy",
  "phase": "middlegame",
  "question": "Why is this move bad?"
}
```

### POST `/api/voice-to-text` (NEW!)
Convert voice recording to text
- Upload audio file (WAV format)
- Returns transcribed text

### POST `/api/text-to-speech` (NEW!)
Convert text to speech
```json
{
  "text": "Your move loses a piece..."
}
```
- Returns audio file (MP3)

### GET `/api/check-ai-status` (NEW!)
Check if AI features are available
- Returns Ollama status and available models

## Technologies Used

### Frontend
- React 18
- chess.js (chess logic)
- react-chessboard (board UI)
- axios (HTTP client)

### Backend
- Flask (web framework)
- python-chess (chess library)
- Flask-CORS (cross-origin support)
- Ollama (AI coach - local LLM)
- Whisper (speech-to-text)
- pyttsx3 (text-to-speech)

## Customization

### Change Board Theme
Edit `frontend/src/App.js` and modify the `Chessboard` component props.

### Adjust Analysis Depth
Default depth is 18. Higher values = stronger but slower analysis.

### Modify Stockfish Settings
Edit `backend/app.py` to configure Stockfish parameters like hash size and threads.

## Troubleshooting

**Backend won't start:**
- Check Stockfish path is correct
- Ensure port 5000 is available
- Verify Python dependencies are installed

**Frontend won't connect:**
- Ensure backend is running on port 5000
- Check CORS settings in `app.py`
- Verify API_URL in `App.js` matches backend URL

**Slow analysis:**
- Reduce analysis depth
- Increase Stockfish hash size
- Add more CPU threads in engine configuration

**Source map warning (chess.js):**
- This is a harmless warning from the chess.js library
- It doesn't affect functionality
- Can be safely ignored

**Game analysis takes long:**
- Analysis depth is set to 18 (very strong)
- A typical 40-move game takes 1-2 minutes to analyze
- This is normal for deep engine analysis

## License

MIT License - Feel free to use and modify!
