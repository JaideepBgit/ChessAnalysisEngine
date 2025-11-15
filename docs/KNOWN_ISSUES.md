# Known Issues and Solutions

## 1. Source Map Warning (chess.js)

### Issue
```
WARNING in ./node_modules/chess.js/dist/esm/chess.js
Module Warning (from ./node_modules/source-map-loader/dist/cjs.js):
Failed to parse source map from 'D:\personal\chess\frontend\node_modules\src\chess.ts' file: 
Error: ENOENT: no such file or directory
```

### Explanation
This is a **harmless warning** from the chess.js library. The library is looking for a source map file that doesn't exist in the distribution package.

### Impact
- ✅ **No functional impact** - the app works perfectly
- ✅ **No performance impact** - doesn't slow anything down
- ✅ **No security impact** - completely safe
- ⚠️ **Visual annoyance** - shows up in console

### Why It Happens
The chess.js library was compiled from TypeScript to JavaScript, and the source map reference wasn't removed from the compiled code. Source maps are only used for debugging and aren't needed for the app to function.

### Solutions

#### Option 1: Ignore It (Recommended)
Just ignore the warning. It doesn't affect anything.

#### Option 2: Suppress the Warning
Add this to `frontend/package.json`:
```json
{
  "scripts": {
    "start": "GENERATE_SOURCEMAP=false react-scripts start",
    "build": "GENERATE_SOURCEMAP=false react-scripts build"
  }
}
```

For Windows, use:
```json
{
  "scripts": {
    "start": "set GENERATE_SOURCEMAP=false && react-scripts start",
    "build": "set GENERATE_SOURCEMAP=false && react-scripts build"
  }
}
```

#### Option 3: Disable Source Map Loader
Create `frontend/.env` file:
```
GENERATE_SOURCEMAP=false
```

## 2. Analysis Takes Long Time

### Issue
Game analysis takes 1-3 minutes for a typical game.

### Explanation
This is **expected behavior**. The engine analyzes each position deeply (depth 18) to provide accurate statistics.

### Why It's Slow
- Depth 18 analysis = ~2-3 seconds per move
- 40-move game = 80 positions to analyze
- 80 × 2.5 seconds = ~200 seconds (3+ minutes)

### Solutions

#### Option 1: Reduce Depth
In `frontend/src/GameAnalysis.js`, change:
```javascript
depth: 18  // Change to 15 for faster analysis
```

Depth comparison:
- **Depth 15**: ~1 second per move, good accuracy
- **Depth 18**: ~2.5 seconds per move, excellent accuracy
- **Depth 20**: ~5 seconds per move, near-perfect accuracy

#### Option 2: Increase Engine Resources
In `backend/app.py`, increase:
```python
engine.configure({"Hash": 512, "Threads": 8})  # More RAM and CPU
```

#### Option 3: Be Patient
Deep analysis provides the most accurate results. The wait is worth it!

## 3. Backend Connection Refused

### Issue
```
Error: connect ECONNREFUSED 127.0.0.1:5000
```

### Causes
1. Backend not running
2. Backend crashed
3. Port 5000 in use by another app
4. Firewall blocking connection

### Solutions
1. **Start backend**: `cd backend && python app.py`
2. **Check backend terminal** for error messages
3. **Change port** in both `backend/app.py` and `frontend/src/GameAnalysis.js`
4. **Check firewall** settings
5. **Restart both servers**

## 4. Stockfish Not Found

### Issue
```
FileNotFoundError: [Errno 2] No such file or directory: 'stockfish'
```

### Solution
1. Download Stockfish from https://stockfishchess.org/download/
2. Extract to a known location (e.g., `C:\stockfish\`)
3. Update path in `backend/app.py`:
```python
STOCKFISH_PATH = r"C:\stockfish\stockfish-windows-x86-64-avx2.exe"
```
4. Restart backend

## 5. Invalid PGN Error

### Issue
```
Error analyzing game: Invalid PGN
```

### Causes
1. PGN format is incorrect
2. Missing required headers
3. Corrupted move notation
4. Extra characters in PGN

### Solutions
1. **Copy PGN directly** from Chess.com or Lichess
2. **Include all headers** (Event, Site, Date, etc.)
3. **Check for typos** in move notation
4. **Test with sample games** from `example_games.txt`
5. **Validate PGN** at https://www.chess.com/analysis

## 6. Frontend Build Warnings

### Issue
Various warnings during `npm install` or `npm start`

### Common Warnings
- Deprecated packages
- Peer dependency warnings
- Optional dependency warnings

### Solution
These are **normal** and can be ignored. They don't affect functionality.

To suppress:
```bash
npm install --legacy-peer-deps
```

## 7. Memory Issues

### Issue
Browser becomes slow or crashes during analysis

### Causes
1. Too many browser tabs open
2. Insufficient RAM
3. Large game being analyzed
4. Memory leak (rare)

### Solutions
1. **Close other tabs**
2. **Restart browser**
3. **Reduce analysis depth**
4. **Analyze shorter games first**
5. **Increase system RAM** (if possible)

## 8. CORS Errors

### Issue
```
Access to XMLHttpRequest blocked by CORS policy
```

### Causes
1. Backend not running
2. Wrong API URL
3. CORS not configured

### Solutions
1. **Verify backend is running** on port 5000
2. **Check API_URL** in `frontend/src/GameAnalysis.js`
3. **Ensure flask-cors is installed**: `pip install flask-cors`
4. **Restart backend**

## 9. Move Navigation Issues

### Issue
Clicking moves doesn't update the board

### Causes
1. JavaScript error
2. Invalid move data
3. State management issue

### Solutions
1. **Check browser console** (F12) for errors
2. **Refresh the page**
3. **Re-analyze the game**
4. **Try a different game**

## 10. Performance Issues

### Issue
UI is slow or laggy

### Causes
1. Too many moves in game
2. Browser extensions interfering
3. Low-end hardware
4. Background processes

### Solutions
1. **Close unnecessary tabs**
2. **Disable browser extensions**
3. **Use Chrome or Edge** (best performance)
4. **Close background applications**
5. **Restart browser**

## Prevention Tips

### For Best Experience
1. ✅ Use latest Chrome or Edge browser
2. ✅ Keep backend and frontend updated
3. ✅ Close unnecessary applications
4. ✅ Use valid PGN from trusted sources
5. ✅ Start with shorter games for testing
6. ✅ Monitor console for errors
7. ✅ Restart servers if issues occur

### Regular Maintenance
1. Clear browser cache occasionally
2. Update Node.js and Python
3. Update npm packages: `npm update`
4. Update pip packages: `pip install --upgrade -r requirements.txt`
5. Keep Stockfish updated

## Getting Help

If you encounter an issue not listed here:

1. **Check browser console** (F12) for error messages
2. **Check backend terminal** for Python errors
3. **Review documentation** in README.md
4. **Try example games** to isolate the issue
5. **Restart everything** (backend, frontend, browser)

## Reporting Issues

When reporting an issue, include:
- Operating system and version
- Python version (`python --version`)
- Node.js version (`node --version`)
- Browser and version
- Error messages (full text)
- Steps to reproduce
- PGN that caused the issue (if applicable)

## Summary

Most issues are minor and easily resolved:
- ⚠️ **Source map warning**: Ignore it
- ⏱️ **Slow analysis**: Expected, reduce depth if needed
- 🔌 **Connection errors**: Ensure backend is running
- 📝 **PGN errors**: Use valid PGN from chess sites
- 🐛 **Other issues**: Check console, restart servers

The application is stable and reliable when properly configured!
