"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const child_process_1 = require("child_process");
const path = __importStar(require("path"));
const http = __importStar(require("http"));
let mainWindow = null;
let pythonProcess = null;
let serverPort = 8080;
function findPythonCommand() {
    // On Windows, 'python' is standard; on Linux/macOS, prefer 'python3'
    if (process.platform === "win32") {
        return "python";
    }
    return "python3";
}
function startPythonBackend() {
    return new Promise((resolve, reject) => {
        const pythonCmd = findPythonCommand();
        const serverScript = path.join(electron_1.app.getAppPath(), "server.py");
        // Spawn server.py with --electron to prevent opening browser
        pythonProcess = (0, child_process_1.spawn)(pythonCmd, [serverScript, "8080", "--electron"], {
            cwd: electron_1.app.getAppPath(),
            stdio: ["pipe", "pipe", "pipe"],
            env: { ...process.env, PYTHONUNBUFFERED: "1" }
        });
        let resolved = false;
        let pollInterval = null;
        const cleanup = () => {
            if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
            }
        };
        pythonProcess.stdout?.on("data", (data) => {
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
        pythonProcess.stderr?.on("data", (data) => {
            console.error("[Python Backend Error]: " + data.toString().trim());
        });
        pythonProcess.on("error", (err) => {
            console.error("[Python Process Failed]:", err);
            if (!resolved) {
                resolved = true;
                cleanup();
                reject(err);
            }
        });
        pythonProcess.on("exit", (code) => {
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
                    resolve(serverPort); // Try loading anyway
                }
            });
        }, 400);
    });
}
function createMainWindow(port) {
    mainWindow = new electron_1.BrowserWindow({
        width: 1260,
        height: 860,
        minWidth: 980,
        minHeight: 680,
        title: "CryptoGuard - Ed25519 Document Verification System",
        backgroundColor: "#0d1117",
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
            contextIsolation: true,
            nodeIntegration: false,
            sandbox: false
        },
        autoHideMenuBar: true,
        show: false
    });
    mainWindow.loadURL("http://localhost:" + port);
    mainWindow.once("ready-to-show", () => {
        mainWindow?.show();
    });
    // Open external links in default system browser, not in Electron window
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        if (url.startsWith("http://") || url.startsWith("https://")) {
            electron_1.shell.openExternal(url);
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
                // Force kill child process tree on Windows
                (0, child_process_1.spawn)("taskkill", ["/pid", pythonProcess.pid.toString(), "/f", "/t"]);
            }
            else {
                pythonProcess.kill("SIGTERM");
            }
        }
        catch (e) {
            console.error("Error stopping Python backend:", e);
        }
        pythonProcess = null;
    }
}
// Window control IPC handlers
electron_1.ipcMain.on("window-minimize", () => mainWindow?.minimize());
electron_1.ipcMain.on("window-maximize", () => {
    if (mainWindow?.isMaximized()) {
        mainWindow.unmaximize();
    }
    else {
        mainWindow?.maximize();
    }
});
electron_1.ipcMain.on("window-close", () => mainWindow?.close());
electron_1.app.whenReady().then(async () => {
    try {
        const port = await startPythonBackend();
        createMainWindow(port);
    }
    catch (err) {
        console.error("Failed to start backend, launching with default port:", err);
        createMainWindow(8080);
    }
    electron_1.app.on("activate", () => {
        if (electron_1.BrowserWindow.getAllWindows().length === 0) {
            createMainWindow(serverPort);
        }
    });
});
electron_1.app.on("window-all-closed", () => {
    stopPythonBackend();
    if (process.platform !== "darwin") {
        electron_1.app.quit();
    }
});
electron_1.app.on("before-quit", () => {
    stopPythonBackend();
});
electron_1.app.on("will-quit", () => {
    stopPythonBackend();
});
