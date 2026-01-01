const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  createVideo: (data) => ipcRenderer.invoke('create-video', data),
  onProgress: (callback) => ipcRenderer.on('video-progress', callback),
  onComplete: (callback) => ipcRenderer.on('video-complete', callback),
  onBackendReady: (callback) => ipcRenderer.on('backend-ready', callback),
});
