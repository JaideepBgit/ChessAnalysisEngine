# Setup Checklist

## Prerequisites
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Stockfish chess engine downloaded
- [ ] Git (optional, for version control)

## Backend Setup
- [ ] Navigate to `backend` folder
- [ ] Run `pip install -r requirements.txt`
- [ ] Update Stockfish path in `backend/app.py` (line 11)
- [ ] Test backend: `python app.py`
- [ ] Verify backend runs on http://localhost:5000
- [ ] Test API: Visit http://localhost:5000/api/analyze-position (should see error, that's OK)

## Frontend Setup
- [ ] Navigate to `frontend` folder
- [ ] Run `npm install`
- [ ] Wait for dependencies to install (~2-3 minutes)
- [ ] Test frontend: `npm start`
- [ ] Verify frontend opens in browser at http://localhost:3000
- [ ] Check for any console errors (source map warning is OK)

## Quick Start (Alternative)
- [ ] Double-click `start.bat` (Windows only)
- [ ] Wait for both servers to start
- [ ] Browser should open automatically

## Verification Tests

### Test 1: Play Mode
- [ ] Open http://localhost:3000
- [ ] Make a move on the board (e.g., e2-e4)
- [ ] Check that analysis appears on the right
- [ ] Verify evaluation bar updates
- [ ] Check best moves are shown

### Test 2: Analysis Mode
- [ ] Click "📊 Analyze Game" button
- [ ] Paste a PGN from `example_games.txt`
- [ ] Enter a player name (e.g., "Player1")
- [ ] Click "Analyze Game"
- [ ] Wait for analysis to complete (~1-2 minutes)
- [ ] Verify statistics appear
- [ ] Click through moves
- [ ] Check board comparison works

### Test 3: Navigation
- [ ] In analysis mode, click different moves
- [ ] Use Previous/Next buttons
- [ ] Verify boards update correctly
- [ ] Check position info updates

## Troubleshooting

### Backend Issues
- [ ] Check Python version: `python --version`
- [ ] Verify Stockfish path is correct
- [ ] Check port 5000 is not in use
- [ ] Look for error messages in terminal

### Frontend Issues
- [ ] Check Node version: `node --version`
- [ ] Clear npm cache: `npm cache clean --force`
- [ ] Delete `node_modules` and reinstall
- [ ] Check port 3000 is not in use
- [ ] Look for errors in browser console (F12)

### Analysis Issues
- [ ] Verify backend is running
- [ ] Check PGN format is valid
- [ ] Ensure Stockfish is accessible
- [ ] Try reducing analysis depth
- [ ] Check browser console for errors

## Performance Optimization
- [ ] Increase Stockfish hash size (if you have RAM)
- [ ] Adjust thread count in `backend/app.py`
- [ ] Use SSD for better performance
- [ ] Close unnecessary applications
- [ ] Use depth 15 for faster analysis

## Documentation Review
- [ ] Read `README.md` for overview
- [ ] Check `QUICK_START.md` for usage guide
- [ ] Review `FEATURES.md` for capabilities
- [ ] Look at `example_games.txt` for test data

## Ready to Use!
Once all items are checked, you're ready to analyze your chess games!

## Next Steps
1. Get a PGN from Chess.com or Lichess
2. Paste it into the analysis interface
3. Review your statistics
4. Learn from your mistakes
5. Improve your chess!

## Support
If you encounter issues:
1. Check the troubleshooting section
2. Review error messages carefully
3. Verify all prerequisites are met
4. Try the example games first
5. Check that Stockfish path is correct

## Tips for Best Results
- Use your actual chess.com or Lichess username
- Analyze games you lost (most learning potential)
- Focus on blunders first
- Review phase-specific accuracy
- Compare your moves to best moves
- Track improvement over multiple games
