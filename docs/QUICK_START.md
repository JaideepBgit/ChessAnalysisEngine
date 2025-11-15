# Quick Start Guide

## Setup (5 minutes)

### 1. Install Stockfish
Download from: https://stockfishchess.org/download/
- Windows: Extract to `C:\stockfish\`
- Update path in `backend/app.py` line 11

### 2. Start Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 3. Start Frontend
```bash
cd frontend
npm install
npm start
```

## Using Game Analysis

### Step 1: Get Your PGN
1. Go to Chess.com or Lichess
2. Open a completed game
3. Click "Share" or "Export"
4. Copy the PGN text

### Step 2: Analyze
1. Click **"📊 Analyze Game"** button
2. Paste your username (optional)
3. Paste the PGN
4. Click **"Analyze Game"**
5. Wait 1-2 minutes for analysis

### Step 3: Review Results
- **Top Section**: Your accuracy, performance rating, opponent stats
- **Phase Accuracy**: How you performed in opening/middlegame/endgame
- **Move Quality**: Count of excellent moves, mistakes, blunders
- **Move List**: Click any move to see detailed analysis
- **Board Comparison**: See your move vs best move side-by-side

## Understanding the Stats

### Accuracy
- **90-100%**: Excellent game, very few mistakes
- **80-90%**: Good game, some minor errors
- **70-80%**: Average game, several mistakes
- **Below 70%**: Many mistakes, review carefully

### Move Quality
- **Excellent (✓)**: 0-10 centipawn loss
- **Good (○)**: 11-25 centipawn loss
- **Inaccuracy (?!)**: 26-50 centipawn loss
- **Mistake (?)**: 51-100 centipawn loss
- **Blunder (??)**: 101-300 centipawn loss
- **Severe Blunder (???)**: 300+ centipawn loss

### Performance Rating
Shows what rating level you played at based on:
- Your accuracy percentage
- Opponent's rating
- Game result

If your performance rating is higher than your actual rating, you played well!

## Tips

1. **Focus on blunders first** - these are the most critical mistakes
2. **Check phase accuracy** - identify which part of the game needs work
3. **Compare boards** - understand why the best move was better
4. **Review inaccuracies** - small improvements add up
5. **Track progress** - analyze multiple games to see improvement

## Sample PGN

A sample game is included in `sample_game.pgn` for testing.
