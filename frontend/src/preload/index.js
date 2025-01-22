import { contextBridge,ipcRenderer } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI)
    contextBridge.exposeInMainWorld('pythonAPI', {
      call: (command, args = [], kwargs = {}) =>
        ipcRenderer.send('call-python', { command, args, kwargs }),
      onResponse: (callback) =>
        ipcRenderer.on('python-response', (_, response) => callback(response)),
    });
  } catch (error) {
    console.error(error)
  }
} else {
  window.electron = electronAPI
  window.api = api
}
