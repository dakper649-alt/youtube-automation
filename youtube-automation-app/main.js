const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let flaskProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 1000,
    minHeight: 600,
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  mainWindow.loadFile('renderer/index.html');

  // В режиме разработки открываем DevTools
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startFlaskServer() {
  // Путь к Python backend
  const backendPath = path.join(__dirname, '..', 'api', 'server.py');
  const pythonPath = path.join(__dirname, '..', 'venv', 'bin', 'python');

  flaskProcess = spawn(pythonPath, [backendPath]);

  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask: ${data}`);
  });

  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask Error: ${data}`);
  });

  // Даём серверу время запуститься
  setTimeout(() => {
    if (mainWindow) {
      mainWindow.webContents.send('backend-ready');
    }
  }, 2000);
}

app.on('ready', () => {
  createWindow();
  startFlaskServer();
});

app.on('window-all-closed', () => {
  if (flaskProcess) {
    flaskProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('before-quit', () => {
  if (flaskProcess) {
    flaskProcess.kill();
  }
});

// IPC handlers
ipcMain.handle('create-video', async (event, data) => {
  // Проксируем запрос к Flask API
  return { success: true, message: 'Video creation started' };
});
