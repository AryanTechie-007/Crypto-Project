import { app, BrowserWindow, ipcMain, shell } from "electron";
import { spawn, ChildProcess } from "child_process";
import * as path from "path";
import * as http from "http";

// Disable hardware acceleration to prevent GPU blank screen glitches on Windows
app.disableHardwareAcceleration();

let mainWindow: BrowserWindow | null = null;
let pythonProcess: ChildProcess | null = null;
let serverPort: number = 8080;

function findPythonCommand(): string {
  if (process.platform === "win32") {
    return "python";
  }
  return "python3";
}

function startPythonBackend(): Promise<number> {
  return new Promise((resolve, reject) => {
    const pythonCmd = findPythonCommand();
    const serverScript = path.join(app.getAppPath(), "server.py");

    pythonProcess = spawn(pythonCmd, [serverScript, "8080", "--electron"], {
      cwd: app.getAppPath(),
      stdio: ["pipe", "pipe", "pipe"],
      env: { ...process.env, PYTHONUNBUFFERED: "1" }
    });

    let resolved = false;
    let pollInterval: NodeJS.Timeout | null = null;

    const cleanup = () => {
      if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
      }
    };

    pythonProcess.stdout?.on("data", (data: Buffer) => {
      const text = data.toString();
      console.log("[Python Backend]: " + text.trim());

      const portMatch = text.match(/SERVER_READY_PORT:(\d+)/);
      if (portMatch && !resolved) {
        resolved = true;
        cleanup();
        serverPort = parseInt(portMatch[1], 10);
        resolve(serverPort);
      }
    });

    pythonProcess.stderr?.on("data", (data: Buffer) => {
      console.error("[Python Backend Error]: " + data.toString().trim());
    });

    pythonProcess.on("error", (err: Error) => {
      console.error("[Python Process Failed]:", err);
      if (!resolved) {
        resolved = true;
        cleanup();
        reject(err);
      }
    });

    pythonProcess.on("exit", (code: number | null) => {
      console.log("[Python Backend Exited]: code " + code);
      cleanup();
    });

    // Fallback: poll server readiness if port token wasn't captured immediately
    let attempts = 0;
    pollInterval = setInterval(() => {
      if (resolved) {
        cleanup();
        return;
      }
      attempts++;
      const req = http.get("http://localhost:" + serverPort + "/api/sample-artifacts", { method: "POST" }, (res) => {
        if (!resolved) {
          resolved = true;
          cleanup();
          resolve(serverPort);
        }
      });
      req.on("error", () => {
        if (attempts > 25 && !resolved) {
          resolved = true;
          cleanup();
          resolve(serverPort);
        }
      });
    }, 400);
  });
}

function createMainWindow(port: number) {
  mainWindow = new BrowserWindow({
    width: 1260,
    height: 860,
    minWidth: 980,
    minHeight: 680,
    title: "CryptoGuard - Ed25519 Document Verification System",
    backgroundColor: "#0b0f19",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    },
    autoHideMenuBar: true,
    show: false
  });

  // Diagnostics
  mainWindow.webContents.on("did-fail-load", (event, errorCode, errorDescription, validatedURL) => {
    console.error("[Electron Error] Page failed to load:", errorCode, errorDescription, validatedURL);
  });

  mainWindow.webContents.on("console-message", (event, level, message, line, sourceId) => {
    // Forward renderer warnings and messages
    if (level >= 2) {
      console.warn("[Renderer]: " + message + " (" + sourceId + ":" + line + ")");
    }
  });

  mainWindow.loadURL("http://localhost:" + port);

  mainWindow.once("ready-to-show", () => {
    mainWindow?.show();
  });

  mainWindow.webContents.on("did-finish-load", () => {
    if (mainWindow && !mainWindow.isVisible()) {
      mainWindow.show();
    }
  });

  // Fallback to guarantee display if compositor events are delayed
  setTimeout(() => {
    if (mainWindow && !mainWindow.isDestroyed() && !mainWindow.isVisible()) {
      mainWindow.show();
    }
  }, 1200);

  // Open external links in default system browser, not inside the Electron window
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("http://") || url.startsWith("https://")) {
      shell.openExternal(url);
    }
    return { action: "deny" };
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

function stopPythonBackend() {
  if (pythonProcess && !pythonProcess.killed) {
    try {
      if (process.platform === "win32" && pythonProcess.pid) {
        spawn("taskkill", ["/pid", pythonProcess.pid.toString(), "/f", "/t"]);
      } else {
        pythonProcess.kill("SIGTERM");
      }
    } catch (e) {
      console.error("Error stopping Python backend:", e);
    }
    pythonProcess = null;
  }
}

// Window control IPC handlers
ipcMain.on("window-minimize", () => mainWindow?.minimize());
ipcMain.on("window-maximize", () => {
  if (mainWindow?.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow?.maximize();
  }
});
ipcMain.on("window-close", () => mainWindow?.close());

app.whenReady().then(async () => {
  try {
    const port = await startPythonBackend();
    createMainWindow(port);
  } catch (err) {
    console.error("Failed to start backend, launching with default port:", err);
    createMainWindow(8080);
  }

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow(serverPort);
    }
  });
});

app.on("window-all-closed", () => {
  stopPythonBackend();
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("before-quit", () => {
  stopPythonBackend();
});

app.on("will-quit", () => {
  stopPythonBackend();
});
