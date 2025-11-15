# Quick Start - New Theme System

## 🎨 What's New?

1. **Light Theme** - Bright, professional theme with your purple color palette
2. **Material-UI Icons** - Professional icons replacing all emojis
3. **Theme Toggle** - Easy switching between light and dark modes
4. **Persistent Preference** - Your choice is remembered

## 🚀 Getting Started

### 1. Install Dependencies (Already Done)
```bash
cd frontend
npm install
```

### 2. Start the Application
```bash
npm start
```

### 3. Find the Theme Toggle
Look for the **sun/moon icon button** in the top-right corner:
- In **Main Play Mode**: Next to the "Depth" input
- In **Game Analysis**: In the statistics panel header

### 4. Switch Themes
Click the theme toggle button:
- **Dark Mode** → Shows ☀️ sun icon → Click to switch to light
- **Light Mode** → Shows 🌙 moon icon → Click to switch to dark

## 🎯 Key Locations

### Theme Toggle Buttons
1. **Main App Header** (Play Mode)
   - Location: Top-right, next to depth control
   - Icon: Sun (dark mode) / Moon (light mode)

2. **Game Analysis Header**
   - Location: Statistics panel, top-right
   - Icon: Sun (dark mode) / Moon (light mode)

### Material-UI Icons Used
- **BarChart** - Analyze Game button
- **Mic** - Voice input
- **Stop** - Stop recording
- **VolumeOff** - Stop speaking
- **SmartToy** - AI Coach
- **Flip** - Flip board
- **ExpandLess/More** - Minimize/Expand
- **ArrowBack** - Back button
- **ArrowBackIos/ForwardIos** - Navigation
- **Brightness4/7** - Theme toggle

## 🎨 Light Theme Colors

Your specified color palette is now active in light mode:

| Color | Hex | Usage |
|-------|-----|-------|
| Primary Purple | `#633394` | Buttons, headers, main accents |
| Secondary Purple | `#967CB2` | Hover states, secondary elements |
| Dark Purple | `#3B1C55` | Text, AppBar background |
| Brown Accent | `#61382E` | Secondary text |
| Background | `#FBFAFA` | Main page background (cream) |
| Paper | `#FFFFFF` | Cards and panels (white) |

## ✨ Features

### Automatic Persistence
- Your theme choice is saved to browser localStorage
- Reopening the app uses your last selected theme
- No need to switch every time

### Smooth Transitions
- Instant theme switching
- No page reload
- All colors transition smoothly

### Consistent Design
- All icons properly sized and aligned
- Professional Material-UI icons throughout
- Consistent spacing and styling

## 🔧 Customization

Want to adjust colors? Edit `frontend/src/theme.js`:

```javascript
export const lightTheme = {
  '--primary-purple': '#633394',     // Your primary color
  '--secondary-purple': '#967CB2',   // Hover states
  '--dark-purple': '#3B1C55',        // Text color
  '--brown-accent': '#61382E',       // Secondary text
  '--bg-primary': '#FBFAFA',         // Main background
  // ... more colors
};
```

## 📱 Testing Checklist

- [ ] Theme toggle works in main app
- [ ] Theme toggle works in game analysis
- [ ] Theme persists after page reload
- [ ] All icons display correctly
- [ ] Light theme uses correct colors
- [ ] Dark theme still works
- [ ] Buttons are clickable and styled
- [ ] Text is readable in both themes

## 🐛 Troubleshooting

### Icons Not Showing?
Make sure Material-UI is installed:
```bash
cd frontend
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
```

### Theme Not Switching?
1. Check browser console for errors
2. Clear localStorage: `localStorage.clear()`
3. Refresh the page

### Colors Look Wrong?
1. Check `frontend/src/theme.js` for correct values
2. Verify CSS variables are being applied
3. Inspect element in browser DevTools

## 📚 Files Modified

- `frontend/src/App.js` - Theme state and toggle
- `frontend/src/App.css` - Theme toggle styles
- `frontend/src/GameAnalysis.js` - Theme props and icons
- `frontend/src/GameAnalysis.css` - Icon button styles
- `frontend/src/VoiceChat.js` - Material-UI icons
- `frontend/src/VoiceChat.css` - Header icon styles
- `frontend/src/theme.js` - **NEW** Theme configuration
- `frontend/package.json` - Material-UI dependencies

## 🎉 Enjoy!

Your chess app now has:
- ✅ Professional Material-UI icons
- ✅ Beautiful light theme with your colors
- ✅ Easy theme switching
- ✅ Persistent user preference
- ✅ Modern, polished appearance

Happy coding! 🚀
