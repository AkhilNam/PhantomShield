const { ipcRenderer } = require('electron');

// Update status elements
const statusEl = document.getElementById('status');
const activeTilesEl = document.getElementById('activeTiles');
const alertsEl = document.getElementById('alerts');
const logEl = document.getElementById('log');

// Configuration elements
const gridRowsEl = document.getElementById('gridRows');
const gridColsEl = document.getElementById('gridCols');
const thresholdEl = document.getElementById('threshold');
const gainEl = document.getElementById('gain');
const bufferSizeEl = document.getElementById('bufferSize');

function updateConfig() {
  const config = {
    type: 'config',
    gridRows: parseInt(gridRowsEl.value),
    gridCols: parseInt(gridColsEl.value),
    threshold: parseInt(thresholdEl.value),
    gain: parseFloat(gainEl.value),
    bufferSize: parseInt(bufferSizeEl.value)
  };
  
  ipcRenderer.send('update-config', config);
}

// Listen for messages from main process
ipcRenderer.on('python-stdout', (event, data) => {
  try {
    const message = JSON.parse(data);
    
    switch (message.type) {
      case 'alert':
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert';
        alertDiv.textContent = `${message.tile} may be a deepfake. Risk: ${message.risk}%`;
        alertsEl.insertBefore(alertDiv, alertsEl.firstChild);
        
        // Remove old alerts after 10 seconds
        setTimeout(() => {
          alertDiv.remove();
        }, 10000);
        break;
        
      case 'status':
        statusEl.textContent = message.message;
        break;
        
      case 'tiles':
        activeTilesEl.textContent = message.count;
        break;
        
      case 'config-response':
        if (message.success) {
          statusEl.textContent = 'Configuration updated successfully';
        } else {
          statusEl.textContent = 'Failed to update configuration: ' + message.error;
        }
        break;
    }
  } catch (e) {
    // If not JSON, treat as regular log message
    logEl.textContent += data + '\n';
    logEl.scrollTop = logEl.scrollHeight;
  }
});

ipcRenderer.on('python-stderr', (event, data) => {
  logEl.textContent += 'ERROR: ' + data + '\n';
  logEl.scrollTop = logEl.scrollHeight;
});
