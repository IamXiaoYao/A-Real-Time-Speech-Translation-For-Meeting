"use strict";
const electron = require("electron");
const preload = require("@electron-toolkit/preload");
if (process.contextIsolated) {
  try {
    electron.contextBridge.exposeInMainWorld("electron", preload.electronAPI);
    electron.contextBridge.exposeInMainWorld("pythonAPI", {
      call: (command, args = [], kwargs = {}) => electron.ipcRenderer.send("call-python", { command, args, kwargs }),
      onResponse: (callback) => electron.ipcRenderer.on("python-response", (_, response) => callback(response))
    });
  } catch (error) {
    console.error(error);
  }
} else {
  window.electron = preload.electronAPI;
  window.api = api;
}
