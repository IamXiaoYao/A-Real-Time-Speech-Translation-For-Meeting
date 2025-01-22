"use strict";
const electron = require("electron");
const path = require("path");
const utils = require("@electron-toolkit/utils");
const icon = path.join(__dirname, "../../resources/icon.png");
const { spawn } = require("child_process");
function createWindow() {
  const mainWindow2 = new electron.BrowserWindow({
    width: 900,
    height: 670,
    minWidth: 900,
    minHeight: 670,
    maxWidth: 900,
    maxHeight: 670,
    show: false,
    autoHideMenuBar: true,
    ...process.platform === "linux" ? { icon } : {},
    webPreferences: {
      preload: path.join(__dirname, "../preload/index.js"),
      sandbox: false
    }
  });
  electron.app.setName("VoiceFlow");
  const template = [
    {
      label: electron.app.name,
      // Use the app name dynamically
      submenu: [
        { role: "about" },
        { type: "separator" },
        { role: "services" },
        { type: "separator" },
        { role: "hide" },
        { role: "hideOthers" },
        { role: "unhide" },
        { type: "separator" },
        { role: "quit" }
      ]
    },
    {
      label: "File",
      submenu: [{ role: "close" }]
    },
    {
      label: "Edit",
      submenu: [
        { role: "undo" },
        { role: "redo" },
        { type: "separator" },
        { role: "cut" },
        { role: "copy" },
        { role: "paste" },
        { role: "selectAll" }
      ]
    },
    {
      label: "View",
      submenu: [
        { role: "reload" },
        { role: "forceReload" },
        { role: "toggleDevTools" },
        { type: "separator" },
        { role: "resetZoom" },
        { role: "zoomIn" },
        { role: "zoomOut" },
        { type: "separator" },
        { role: "togglefullscreen" }
      ]
    },
    {
      label: "Window",
      submenu: [{ role: "minimize" }, { role: "zoom" }, { role: "close" }]
    },
    {
      label: "Help",
      submenu: [
        {
          label: "Learn More",
          click: async () => {
            const { shell: shell2 } = require("electron");
            await shell2.openExternal("https://electronjs.org");
          }
        }
      ]
    }
  ];
  const menu = electron.Menu.buildFromTemplate(template);
  electron.Menu.setApplicationMenu(menu);
  mainWindow2.on("ready-to-show", () => {
    mainWindow2.show();
  });
  mainWindow2.webContents.setWindowOpenHandler((details) => {
    electron.shell.openExternal(details.url);
    return { action: "deny" };
  });
  mainWindow2.webContents.on("before-input-event", (event, input) => {
    if (input.type === "keyDown" && (input.key === "ArrowDown" || input.key === "ArrowUp")) {
      event.preventDefault();
    }
  });
  electron.app.setName("VoiceFlow");
  if (utils.is.dev && process.env["ELECTRON_RENDERER_URL"]) {
    mainWindow2.loadURL(process.env["ELECTRON_RENDERER_URL"]);
  } else {
    mainWindow2.loadFile(path.join(__dirname, "../renderer/index.html"));
  }
}
const pythonProcess = spawn("python", ["src/whisper/Whisper_transc.py"]);
pythonProcess.stdout.on("data", (data) => {
  const message = data.toString();
  console.log("Python Output:", message);
  mainWindow.webContents.send("python-response", JSON.parse(message));
});
pythonProcess.stderr.on("data", (data) => {
  console.error("Python Error:", data.toString());
});
electron.ipcMain.on("call-python", (event, { command, args, kwargs }) => {
  const request = JSON.stringify({ command, args, kwargs });
  pythonProcess.stdin.write(request + "\n");
});
electron.app.whenReady().then(() => {
  utils.electronApp.setAppUserModelId("com.electron");
  electron.app.on("browser-window-created", (_, window) => {
    utils.optimizer.watchWindowShortcuts(window);
  });
  electron.ipcMain.on("ping", () => console.log("pong"));
  createWindow();
  electron.app.on("activate", function() {
    if (electron.BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});
electron.app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    electron.app.quit();
  }
});
