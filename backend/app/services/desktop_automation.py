"""Desktop Automation Service — REAL desktop control primitives.

This is the ACTUAL implementation that controls Windows desktop:
- Open applications (Chrome, Notepad, Explorer, etc.)
- Click at coordinates
- Type text
- Keyboard shortcuts (Ctrl+C, Ctrl+V, Alt+Tab, etc.)
- File operations (copy, move, delete)
- Screenshot capture
- Window management

NO MOCKING. NO FAKING. This runs REAL actions.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


class DesktopAutomationService:
    """Executes real desktop automation actions on Windows."""

    def __init__(self, screenshots_dir: str = "./data/screenshots"):
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self._action_log: List[Dict[str, Any]] = []

    def _log_action(self, action: str, params: dict, result: dict) -> dict:
        """Log every action with timestamp for audit trail."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "parameters": params,
            "result": result,
        }
        self._action_log.append(entry)
        return entry

    @property
    def action_log(self) -> List[Dict[str, Any]]:
        """Full audit trail of all actions executed."""
        return list(self._action_log)

    # ── Application Launch ──────────────────────────────────

    async def open_application(self, app_name: str, args: list[str] | None = None) -> Dict[str, Any]:
        """Open an application by name or path.
        
        Supports: chrome, notepad, explorer, calc, cmd, powershell, 
        or any full executable path.
        """
        start = time.perf_counter()
        app_map = {
            "chrome": self._find_chrome,
            "google chrome": self._find_chrome,
            "notepad": lambda: "notepad.exe",
            "calculator": lambda: "calc.exe",
            "calc": lambda: "calc.exe",
            "explorer": lambda: "explorer.exe",
            "file explorer": lambda: "explorer.exe",
            "cmd": lambda: "cmd.exe",
            "command prompt": lambda: "cmd.exe",
            "powershell": lambda: "powershell.exe",
            "paint": lambda: "mspaint.exe",
            "wordpad": lambda: "wordpad.exe",
            "task manager": lambda: "taskmgr.exe",
        }

        app_lower = app_name.lower().strip()
        
        # Try known app map first
        if app_lower in app_map:
            exe_path = app_map[app_lower]()
        elif os.path.exists(app_name):
            exe_path = app_name
        else:
            # Try to find in PATH
            exe_path = shutil.which(app_name)
            if exe_path is None:
                result = {
                    "success": False,
                    "error": f"Application '{app_name}' not found",
                    "pid": None,
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
                self._log_action("open_application", {"app_name": app_name}, result)
                return result

        try:
            cmd = [exe_path] + (args or [])
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            )
            
            # Wait briefly to see if it crashes immediately
            await asyncio.sleep(1.0)
            
            if process.poll() is not None and process.returncode != 0:
                result = {
                    "success": False,
                    "error": f"Application crashed on start (exit code: {process.returncode})",
                    "pid": None,
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
            else:
                result = {
                    "success": True,
                    "pid": process.pid,
                    "exe_path": exe_path,
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
                
        except FileNotFoundError:
            result = {
                "success": False,
                "error": f"Executable not found: {exe_path}",
                "pid": None,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "pid": None,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._log_action("open_application", {"app_name": app_name, "args": args}, result)
        return result

    def _find_chrome(self) -> str:
        """Find Chrome executable on Windows."""
        paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        # Fallback: try PATH
        found = shutil.which("chrome") or shutil.which("chrome.exe")
        if found:
            return found
        raise FileNotFoundError("Chrome not found in standard locations")

    # ── Window Management ───────────────────────────────────

    async def list_windows(self) -> List[Dict[str, Any]]:
        """List all visible windows with titles."""
        import pygetwindow as gw
        windows = gw.getAllWindows()
        result = []
        for w in windows:
            if w.title and w.visible:
                result.append({
                    "title": w.title,
                    "left": w.left,
                    "top": w.top,
                    "width": w.width,
                    "height": w.height,
                    "visible": w.visible,
                })
        return result

    async def focus_window(self, title_contains: str) -> Dict[str, Any]:
        """Bring a window to the foreground by partial title match."""
        import pygetwindow as gw
        start = time.perf_counter()
        
        windows = gw.getWindowsWithTitle(title_contains)
        if not windows:
            result = {
                "success": False,
                "error": f"No window found containing '{title_contains}'",
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        else:
            try:
                win = windows[0]
                if win.isMinimized:
                    win.restore()
                win.activate()
                await asyncio.sleep(0.3)
                result = {
                    "success": True,
                    "window_title": win.title,
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
            except Exception as e:
                result = {
                    "success": False,
                    "error": str(e),
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }

        self._log_action("focus_window", {"title_contains": title_contains}, result)
        return result

    # ── Mouse Actions ───────────────────────────────────────

    async def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> Dict[str, Any]:
        """Click at screen coordinates."""
        import pyautogui
        start = time.perf_counter()
        
        try:
            screen_w, screen_h = pyautogui.size()
            if not (0 <= x <= screen_w and 0 <= y <= screen_h):
                result = {
                    "success": False,
                    "error": f"Coordinates ({x}, {y}) out of screen bounds ({screen_w}x{screen_h})",
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
            else:
                pyautogui.click(x=x, y=y, button=button, clicks=clicks)
                result = {
                    "success": True,
                    "x": x,
                    "y": y,
                    "button": button,
                    "clicks": clicks,
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._log_action("click", {"x": x, "y": y, "button": button}, result)
        return result

    # ── Keyboard Actions ────────────────────────────────────

    async def type_text(self, text: str, interval: float = 0.02) -> Dict[str, Any]:
        """Type text at current cursor position."""
        import pyautogui
        start = time.perf_counter()

        try:
            pyautogui.typewrite(text, interval=interval) if text.isascii() else pyautogui.write(text)
            result = {
                "success": True,
                "text_length": len(text),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._log_action("type_text", {"text_length": len(text), "text_preview": text[:50]}, result)
        return result

    async def hotkey(self, *keys: str) -> Dict[str, Any]:
        """Press a keyboard shortcut (e.g., 'ctrl', 'c' for Ctrl+C)."""
        import pyautogui
        start = time.perf_counter()

        try:
            pyautogui.hotkey(*keys)
            result = {
                "success": True,
                "keys": list(keys),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._log_action("hotkey", {"keys": list(keys)}, result)
        return result

    async def press_key(self, key: str) -> Dict[str, Any]:
        """Press a single key (e.g., 'enter', 'tab', 'escape')."""
        import pyautogui
        start = time.perf_counter()

        try:
            pyautogui.press(key)
            result = {
                "success": True,
                "key": key,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._log_action("press_key", {"key": key}, result)
        return result

    # ── Screenshot ──────────────────────────────────────────

    async def take_screenshot(self, filename: str | None = None, region: tuple | None = None) -> Dict[str, Any]:
        """Capture a screenshot of the entire screen or a specific region."""
        import pyautogui
        start = time.perf_counter()

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"screenshot_{timestamp}.png"

        filepath = self.screenshots_dir / filename

        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()

            screenshot.save(str(filepath))
            
            width, height = screenshot.size
            file_size = filepath.stat().st_size

            result = {
                "success": True,
                "filepath": str(filepath),
                "filename": filename,
                "width": width,
                "height": height,
                "file_size_bytes": file_size,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._log_action("take_screenshot", {"filename": filename}, result)
        return result

    # ── File Operations ─────────────────────────────────────

    async def copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy a file from source to destination."""
        start = time.perf_counter()

        try:
            src = Path(source)
            dst = Path(destination)

            if not src.exists():
                result = {
                    "success": False,
                    "error": f"Source file not found: {source}",
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
            else:
                # Create destination directory if needed
                if dst.is_dir():
                    dst = dst / src.name
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)

                shutil.copy2(str(src), str(dst))
                
                # Verify copy
                if dst.exists():
                    src_size = src.stat().st_size
                    dst_size = dst.stat().st_size
                    result = {
                        "success": True,
                        "source": str(src),
                        "destination": str(dst),
                        "source_size": src_size,
                        "destination_size": dst_size,
                        "sizes_match": src_size == dst_size,
                        "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                    }
                else:
                    result = {
                        "success": False,
                        "error": "File copy completed but destination file not found",
                        "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                    }

        except PermissionError:
            result = {
                "success": False,
                "error": f"Permission denied: cannot copy to {destination}",
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._log_action("copy_file", {"source": source, "destination": destination}, result)
        return result

    async def copy_folder(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy an entire folder from source to destination."""
        start = time.perf_counter()

        try:
            src = Path(source)
            dst = Path(destination)

            if not src.exists():
                result = {
                    "success": False,
                    "error": f"Source folder not found: {source}",
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
            elif not src.is_dir():
                result = {
                    "success": False,
                    "error": f"Source is not a directory: {source}",
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
            else:
                # If destination is an existing dir, copy inside it
                final_dst = dst / src.name if dst.is_dir() else dst
                
                if final_dst.exists():
                    shutil.rmtree(str(final_dst))
                
                shutil.copytree(str(src), str(final_dst))
                
                # Count files copied
                src_files = list(src.rglob("*"))
                dst_files = list(final_dst.rglob("*"))
                
                result = {
                    "success": True,
                    "source": str(src),
                    "destination": str(final_dst),
                    "source_file_count": len([f for f in src_files if f.is_file()]),
                    "destination_file_count": len([f for f in dst_files if f.is_file()]),
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }

        except PermissionError:
            result = {
                "success": False,
                "error": f"Permission denied: cannot copy to {destination}",
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._log_action("copy_folder", {"source": source, "destination": destination}, result)
        return result

    async def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Move a file from source to destination."""
        start = time.perf_counter()

        try:
            src = Path(source)
            dst = Path(destination)

            if not src.exists():
                result = {
                    "success": False,
                    "error": f"Source not found: {source}",
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
            else:
                if dst.is_dir():
                    dst = dst / src.name
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)

                shutil.move(str(src), str(dst))
                
                result = {
                    "success": dst.exists() and not src.exists(),
                    "source": str(src),
                    "destination": str(dst),
                    "source_removed": not src.exists(),
                    "destination_exists": dst.exists(),
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }

        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._log_action("move_file", {"source": source, "destination": destination}, result)
        return result

    async def create_file(self, filepath: str, content: str = "") -> Dict[str, Any]:
        """Create a new file with optional content."""
        start = time.perf_counter()

        try:
            p = Path(filepath)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")

            result = {
                "success": True,
                "filepath": str(p),
                "size_bytes": p.stat().st_size,
                "content_length": len(content),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._log_action("create_file", {"filepath": filepath, "content_length": len(content)}, result)
        return result

    async def delete_file(self, filepath: str) -> Dict[str, Any]:
        """Delete a file."""
        start = time.perf_counter()

        try:
            p = Path(filepath)
            if not p.exists():
                result = {
                    "success": False,
                    "error": f"File not found: {filepath}",
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
            else:
                if p.is_dir():
                    shutil.rmtree(str(p))
                else:
                    p.unlink()
                result = {
                    "success": not p.exists(),
                    "filepath": str(p),
                    "deleted": not p.exists(),
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._log_action("delete_file", {"filepath": filepath}, result)
        return result

    async def list_directory(self, path: str) -> Dict[str, Any]:
        """List contents of a directory."""
        start = time.perf_counter()

        try:
            p = Path(path)
            if not p.exists():
                result = {
                    "success": False,
                    "error": f"Directory not found: {path}",
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
            elif not p.is_dir():
                result = {
                    "success": False,
                    "error": f"Not a directory: {path}",
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
            else:
                items = []
                for item in sorted(p.iterdir()):
                    try:
                        stat = item.stat()
                        items.append({
                            "name": item.name,
                            "is_dir": item.is_dir(),
                            "size_bytes": stat.st_size if item.is_file() else 0,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        })
                    except (PermissionError, OSError):
                        items.append({
                            "name": item.name,
                            "is_dir": item.is_dir(),
                            "error": "permission denied",
                        })
                
                result = {
                    "success": True,
                    "path": str(p),
                    "item_count": len(items),
                    "items": items,
                    "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._log_action("list_directory", {"path": path}, result)
        return result

    # ── Open File Explorer at Path ──────────────────────────

    async def open_explorer(self, path: str | None = None) -> Dict[str, Any]:
        """Open Windows File Explorer, optionally at a specific path."""
        start = time.perf_counter()

        try:
            if path:
                p = Path(path)
                if not p.exists():
                    result = {
                        "success": False,
                        "error": f"Path not found: {path}",
                        "duration_ms": round((time.perf_counter() - start) * 1000, 2),
                    }
                    self._log_action("open_explorer", {"path": path}, result)
                    return result
                cmd = ["explorer.exe", str(p)]
            else:
                cmd = ["explorer.exe"]

            subprocess.Popen(cmd)
            await asyncio.sleep(1.5)

            result = {
                "success": True,
                "path": path,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

        self._log_action("open_explorer", {"path": path}, result)
        return result

    # ── Process Management ──────────────────────────────────

    async def is_process_running(self, process_name: str) -> Dict[str, Any]:
        """Check if a process is running by name."""
        start = time.perf_counter()
        
        found = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    found.append({"pid": proc.info['pid'], "name": proc.info['name']})
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        result = {
            "success": True,
            "process_name": process_name,
            "is_running": len(found) > 0,
            "instances": found,
            "instance_count": len(found),
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
        }

        self._log_action("is_process_running", {"process_name": process_name}, result)
        return result

    async def close_application(self, process_name: str) -> Dict[str, Any]:
        """Close an application by process name."""
        start = time.perf_counter()
        
        killed = 0
        errors = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                errors.append(str(e))

        result = {
            "success": killed > 0,
            "process_name": process_name,
            "terminated_count": killed,
            "errors": errors if errors else None,
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
        }

        self._log_action("close_application", {"process_name": process_name}, result)
        return result

    # ── Wait/Delay ──────────────────────────────────────────

    async def wait(self, seconds: float) -> Dict[str, Any]:
        """Wait for specified seconds."""
        start = time.perf_counter()
        await asyncio.sleep(seconds)
        result = {
            "success": True,
            "waited_seconds": seconds,
            "duration_ms": round((time.perf_counter() - start) * 1000, 2),
        }
        self._log_action("wait", {"seconds": seconds}, result)
        return result
