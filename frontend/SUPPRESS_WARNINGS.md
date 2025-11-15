# Suppress Source Map Warning

## The Warning

```
Failed to parse source map from 'D:\personal\chess\frontend\node_modules\src\chess.ts'
```

## What It Means

This is a harmless warning from the `chess.js` library. The library is missing a source map file, but this doesn't affect functionality at all.

## Should You Fix It?

**No need!** The app works perfectly. This is just a development warning.

## If You Want to Suppress It

### Option 1: Environment Variable (Recommended)

Create a `.env` file in the `frontend` folder:

```bash
# frontend/.env
GENERATE_SOURCEMAP=false
```

Then restart the dev server.

### Option 2: Ignore in webpack config

The warning is already being ignored by webpack, but you're seeing it in the console. You can safely ignore it.

### Option 3: Update chess.js

Wait for the chess.js library to fix their source maps in a future version.

## Summary

✅ **App works fine** - This doesn't affect functionality  
✅ **Safe to ignore** - Just a missing source map  
✅ **Optional fix** - Add `GENERATE_SOURCEMAP=false` to `.env`  

---

**Recommendation:** Just ignore it. It's harmless! 🎉
