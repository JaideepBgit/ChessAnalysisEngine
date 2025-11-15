# Packaging Guide for Desktop Distribution

This guide explains how to package your Chess Analysis app with AI features into a distributable desktop application.

## Overview

We'll use **Electron** to package the React frontend and Flask backend into a single desktop app that includes:
- React frontend
- Flask backend (as executable)
- Stockfish engine
- Ollama (optional: bundled or auto-downloaded)
- Whisper models (auto-downloaded on first use)

## Architecture

```
Desktop App (Electron)
├── Frontend (React - bundled)
├── Backend (Flask - PyInstaller executable)
├── Stockfish (bundled binary)
└── Ollama (user installs or auto-installed)
    └── Models (downloaded on first run)
```

## Step 1: Prepare Backend for Packaging

### Install PyInstaller

```bash
pip install pyinstaller
```

### Create Backend Executable

```bash
cd backend
pyinstaller --onefile --name chess-backend app.py
```

This creates `dist/chess-backend.exe` (Windows) or `dist/chess-backend` (Mac/Linux).

### Test the Executable

```bash
cd dist
./chess-backend  # or chess-backend.exe on Windows
```

## Step 2: Set Up Electron

### Install Electron Dependencies

```bash
cd frontend
npm install --save-dev electron electron-builder
npm install --save-dev concurrently wait-on
```

### Create Electron Main Process

Create `frontend/electron/main.js`:

```javascript
const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let backendProcess;

// Determine if running in development or production
const isDev = !app.isPackaged;

// Get the correct backend path
function getBackendPath() {
  if (isDev) {
    // Development: use Python directly
    return {
      command: 'python',
      args: [path.join(__dirname, '../../backend/app.py')]
    };
  } else {
    // Production: use packaged executable
    const platform = process.platform;
    const backendName = platform === 'win32' ? 'chess-backend.exe' : 'chess-backend';
    return {
      command: path.join(process.resourcesPath, 'backend', backendName),
      args: []
    };
  }
}

// Start Flask backend
function startBackend() {
  const backend = getBackendPath();
  
  backendProcess = spawn(backend.command, backend.args, {
    cwd: isDev ? path.join(__dirname, '../../backend') : process.resourcesPath
  });

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
  });
}

// Create main window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    icon: path.join(__dirname, '../public/icon.png')
  });

  // Load the app
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../build/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Check if Ollama is installed
async function checkOllama() {
  return new Promise((resolve) => {
    const checkProcess = spawn('ollama', ['--version']);
    checkProcess.on('close', (code) => {
      resolve(code === 0);
    });
    checkProcess.on('error', () => {
      resolve(false);
    });
  });
}

// Show setup wizard if needed
async function showSetupWizard() {
  const ollamaInstalled = await checkOllama();
  
  if (!ollamaInstalled) {
    const { dialog, shell } = require('electron');
    const result = await dialog.showMessageBox({
      type: 'info',
      title: 'AI Features Setup',
      message: 'Ollama is required for AI Coach features',
      detail: 'Would you like to download and install Ollama now? (Recommended)',
      buttons: ['Download Ollama', 'Skip (AI features disabled)'],
      defaultId: 0
    });

    if (result.response === 0) {
      shell.openExternal('https://ollama.ai/download');
    }
  }
}

// App lifecycle
app.on('ready', async () => {
  // Start backend
  startBackend();
  
  // Wait a bit for backend to start
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Create window
  createWindow();
  
  // Check for Ollama (first run)
  const isFirstRun = !fs.existsSync(path.join(app.getPath('userData'), '.setup-complete'));
  if (isFirstRun) {
    await showSetupWizard();
    fs.writeFileSync(path.join(app.getPath('userData'), '.setup-complete'), 'true');
  }
});

app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
  app.quit();
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Cleanup on quit
app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});
```

### Update package.json

Edit `frontend/package.json`:

```json
{
  "name": "chess-analysis-pro",
  "version": "1.0.0",
  "description": "AI-Powered Chess Game Analysis",
  "author": "Your Name",
  "main": "electron/main.js",
  "homepage": "./",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "electron": "electron .",
    "electron-dev": "concurrently \"npm start\" \"wait-on http://localhost:3000 && electron .\"",
    "electron-build": "npm run build && electron-builder",
    "dist": "npm run build && electron-builder --win --mac --linux"
  },
  "build": {
    "appId": "com.yourcompany.chess-analysis",
    "productName": "Chess Analysis Pro",
    "files": [
      "build/**/*",
      "electron/**/*",
      "node_modules/**/*"
    ],
    "extraResources": [
      {
        "from": "../backend/dist/chess-backend.exe",
        "to": "backend/chess-backend.exe",
        "filter": ["**/*"]
      },
      {
        "from": "../backend/stockfish",
        "to": "backend/stockfish",
        "filter": ["**/*"]
      }
    ],
    "win": {
      "target": ["nsis"],
      "icon": "public/icon.ico"
    },
    "mac": {
      "target": ["dmg"],
      "icon": "public/icon.icns",
      "category": "public.app-category.games"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "icon": "public/icon.png",
      "category": "Game"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
```

## Step 3: Build the Application

### Build Backend

```bash
cd backend
pyinstaller --onefile --name chess-backend app.py
```

### Build Frontend + Package Everything

```bash
cd frontend
npm run build
npm run electron-build
```

This creates installers in `frontend/dist/`:
- Windows: `Chess Analysis Pro Setup 1.0.0.exe`
- macOS: `Chess Analysis Pro-1.0.0.dmg`
- Linux: `Chess Analysis Pro-1.0.0.AppImage`

## Step 4: Distribution Strategies

### Option 1: Full Bundle (Large but Complete)

**Pros:**
- Everything included
- Works offline immediately
- Best user experience

**Cons:**
- Large download (2-3GB with Ollama)
- Longer build time

**Implementation:**
Include Ollama in `extraResources`:

```json
"extraResources": [
  {
    "from": "path/to/ollama-installer.exe",
    "to": "ollama/ollama-installer.exe"
  }
]
```

### Option 2: Minimal + Auto-Download (Recommended)

**Pros:**
- Small initial download (~200MB)
- Fast to distribute
- Downloads AI features on demand

**Cons:**
- Requires internet for first setup
- User waits for downloads

**Implementation:**
- Package only core app + Stockfish
- On first run, prompt to download Ollama
- Auto-download Whisper models when first used

### Option 3: Hybrid Approach

**Pros:**
- Medium size (~700MB)
- Ollama included, models downloaded
- Good compromise

**Cons:**
- Still requires internet for models
- Larger than minimal

**Implementation:**
- Bundle Ollama installer
- Auto-install on first run
- Download models as needed

## Step 5: Code Signing (Optional but Recommended)

### Windows

1. Get a code signing certificate ($100-300/year)
2. Install certificate
3. Update `package.json`:

```json
"win": {
  "certificateFile": "path/to/cert.pfx",
  "certificatePassword": "your-password",
  "signingHashAlgorithms": ["sha256"]
}
```

### macOS

1. Join Apple Developer Program ($99/year)
2. Get Developer ID certificate
3. Update `package.json`:

```json
"mac": {
  "identity": "Developer ID Application: Your Name (TEAM_ID)"
}
```

### Why Code Sign?

- Windows won't show "Unknown Publisher" warning
- macOS won't block the app
- Users trust signed apps more
- Required for Mac App Store

## Step 6: Testing

### Test on Clean Machines

1. **Windows 10/11** - Fresh VM
2. **macOS** - Different Mac
3. **Linux** - Ubuntu VM

### Test Checklist

- [ ] App installs without errors
- [ ] Backend starts automatically
- [ ] Stockfish works
- [ ] Game analysis works
- [ ] Ollama detection works
- [ ] Voice features work (if Ollama installed)
- [ ] App uninstalls cleanly
- [ ] No leftover files after uninstall

## Step 7: Distribution Platforms

### Your Own Website

**Setup:**
1. Create landing page
2. Add download buttons
3. Integrate Stripe/Gumroad for payments
4. Provide license keys

**Pros:**
- Keep 100% of revenue
- Full control

**Cons:**
- Need to handle payments
- Need to market yourself

### Gumroad (Easiest)

**Setup:**
1. Create account at gumroad.com
2. Upload installer
3. Set price
4. Share link

**Pros:**
- Super easy
- Handles payments
- Instant setup

**Cons:**
- 10% fee
- Less control

### Steam

**Setup:**
1. Pay $100 Steamworks fee
2. Submit app for review
3. Set up store page

**Pros:**
- Huge audience
- Built-in updates
- Trusted platform

**Cons:**
- 30% revenue share
- Review process
- More complex

### Microsoft Store

**Setup:**
1. Create developer account ($19)
2. Package as MSIX
3. Submit for review

**Pros:**
- Windows users trust it
- Auto-updates
- Good visibility

**Cons:**
- 15% fee
- Windows only
- Strict requirements

## Step 8: Auto-Updates

### Using electron-updater

```bash
npm install electron-updater
```

Update `electron/main.js`:

```javascript
const { autoUpdater } = require('electron-updater');

app.on('ready', () => {
  autoUpdater.checkForUpdatesAndNotify();
});

autoUpdater.on('update-available', () => {
  dialog.showMessageBox({
    type: 'info',
    title: 'Update Available',
    message: 'A new version is available. Download now?',
    buttons: ['Yes', 'No']
  });
});
```

Host updates on:
- GitHub Releases (free)
- Your own server
- S3 bucket

## Installer Sizes

| Component | Size |
|-----------|------|
| React app | 5MB |
| Electron | 50MB |
| Flask backend | 20MB |
| Stockfish | 5MB |
| **Base app** | **~80MB** |
| + Ollama | +500MB |
| + Whisper | +150MB |
| + LLM model | +2GB |
| **Full bundle** | **~2.7GB** |

## Recommended Approach

**For Best Results:**

1. **Base Installer:** 80MB
   - Core app + Stockfish
   - No AI features bundled

2. **First Run Setup:**
   - Detect if Ollama installed
   - If not, show dialog:
     - "Download Ollama for AI Coach features?"
     - Link to ollama.ai
   - Auto-download Whisper on first voice use

3. **User Experience:**
   - Fast initial download
   - Optional AI features
   - Clear setup instructions
   - Works without AI (basic analysis)

## Pricing Strategy

Based on installer size and features:

- **Basic Edition** ($29)
  - Game analysis
  - Stockfish engine
  - No AI features
  - 80MB download

- **Pro Edition** ($49)
  - Everything in Basic
  - AI Coach included
  - Voice features
  - Setup wizard for AI
  - 80MB + auto-download

- **Complete Bundle** ($59)
  - Everything pre-installed
  - No setup needed
  - 2.7GB download
  - Best for offline use

## Next Steps

1. Build and test locally
2. Test on clean VMs
3. Get code signing certificate
4. Choose distribution platform
5. Create marketing materials
6. Launch!

## Resources

- Electron Builder: https://www.electron.build/
- PyInstaller: https://pyinstaller.org/
- Ollama: https://ollama.ai/
- Code Signing: https://www.electron.build/code-signing

Good luck with your launch! 🚀
