const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    icon: path.join(__dirname, 'assets/logo_WZ7_4.ico'),
  });

  mainWindow.loadFile('app/index.html');
  
  // Hide the default menu bar for a cleaner look
  mainWindow.setMenuBarVisibility(false);
  mainWindow.setMenu(null);

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }
}

function startPythonBackend() {
  const pythonPath = isDev ? 'python' : path.join(process.resourcesPath, 'python/python.exe');
  const scriptPath = isDev
    ? path.join(__dirname, '../backend/zoom_capture.py')
    : path.join(process.resourcesPath, 'zoom_capture.py');
  
  pythonProcess = spawn(pythonPath, [scriptPath]);

  pythonProcess.stdout.on('data', (data) => {
    const output = data.toString();
    console.log(`Python stdout: ${output}`);
    if (mainWindow) {
      mainWindow.webContents.send('python-stdout', output);
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    const error = data.toString();
    console.error(`Python stderr: ${error}`);
    if (mainWindow) {
      mainWindow.webContents.send('python-stderr', error);
    }
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
    if (mainWindow) {
      mainWindow.webContents.send('status-update', 'Python process stopped');
    }
  });
}

// Handle configuration updates
ipcMain.on('update-config', (event, config) => {
  if (pythonProcess && pythonProcess.stdin) {
    // Send config to Python process
    pythonProcess.stdin.write(JSON.stringify(config) + '\n');
  }
});

app.whenReady().then(() => {
  createWindow();
  startPythonBackend();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (pythonProcess) {
      pythonProcess.kill();
    }
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
