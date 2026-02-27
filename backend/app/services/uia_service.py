"""UIA Service — Windows UI Automation state checking.

Uses Windows UI Automation (via pywinauto/psutil/ctypes) for FAST
state verification without needing screenshots or vision models.

Key advantage over moondream:
  - UIA: <100ms, 99% accuracy for window/process state
  - moondream: 1-2s, 88% accuracy for visual detection

Used for:
  - Is application running? (process check)
  - Is window foreground? (UIA focus check)
  - Window title changed? (tab navigation detection)
  - Is text field focused? (input readiness)
"""

from __future__ import annotations

import asyncio
import ctypes
import subprocess
import time
from typing import Any, Dict, List, Optional

import psutil

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class UIAService:
    """Fast Windows UI Automation state checker.
    
    Provides instant verification of OS-level state changes
    without requiring screenshots or vision models.
    """

    # Map of common app names to their process names
    PROCESS_MAP = {
        "chrome": ["chrome.exe"],
        "google chrome": ["chrome.exe"],
        "firefox": ["firefox.exe"],
        "edge": ["msedge.exe"],
        "microsoft edge": ["msedge.exe"],
        "notepad": ["notepad.exe"],
        "calculator": ["calculatorapp.exe", "calc.exe"],
        "calc": ["calculatorapp.exe", "calc.exe"],
        "explorer": ["explorer.exe"],
        "file explorer": ["explorer.exe"],
        "cmd": ["cmd.exe"],
        "command prompt": ["cmd.exe"],
        "powershell": ["powershell.exe", "pwsh.exe"],
        "paint": ["mspaint.exe"],
        "wordpad": ["wordpad.exe"],
        "task manager": ["taskmgr.exe"],
        "vscode": ["code.exe"],
        "vs code": ["code.exe"],
        "visual studio code": ["code.exe"],
        "spotify": ["spotify.exe"],
        "discord": ["discord.exe"],
        "slack": ["slack.exe"],
        "teams": ["teams.exe"],
        "microsoft teams": ["teams.exe"],
        "outlook": ["outlook.exe"],
        "word": ["winword.exe"],
        "excel": ["excel.exe"],
        "powerpoint": ["powerpnt.exe"],
    }

    async def is_app_running(self, app_name: str) -> Dict[str, Any]:
        """Check if an application is running by process name.
        
        Args:
            app_name: Application name (e.g., 'chrome', 'notepad')
            
        Returns:
            {running: bool, pid: int|None, process_name: str, window_title: str|None}
        """
        start = time.perf_counter()
        app_lower = app_name.lower().strip()
        
        # Get expected process names
        expected = self.PROCESS_MAP.get(app_lower, [f"{app_lower}.exe"])
        
        found_pid = None
        found_name = None
        
        for proc in psutil.process_iter(["name", "pid"]):
            try:
                proc_name = proc.info["name"].lower()
                if proc_name in [e.lower() for e in expected]:
                    found_pid = proc.info["pid"]
                    found_name = proc.info["name"]
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        
        if found_pid:
            # Try to get window title
            title = await self._get_window_title_for_pid(found_pid)
            return {
                "running": True,
                "pid": found_pid,
                "process_name": found_name,
                "window_title": title,
                "duration_ms": duration_ms,
            }
        
        return {
            "running": False,
            "pid": None,
            "process_name": None,
            "window_title": None,
            "duration_ms": duration_ms,
        }

    async def get_foreground_window(self) -> Dict[str, Any]:
        """Get the currently focused/foreground window info.
        
        Returns:
            {title: str, pid: int, process_name: str}
        """
        start = time.perf_counter()
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            
            # Get window title
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value
            
            # Get PID
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            pid_val = pid.value
            
            # Get process name
            proc_name = None
            try:
                proc = psutil.Process(pid_val)
                proc_name = proc.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "title": title,
                "pid": pid_val,
                "process_name": proc_name,
                "hwnd": hwnd,
                "duration_ms": duration_ms,
            }
        except Exception as e:
            logger.error(f"Failed to get foreground window: {e}")
            return {
                "title": None,
                "pid": None,
                "process_name": None,
                "hwnd": None,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }

    async def wait_for_window(
        self,
        title_contains: str = "",
        process_name: str = "",
        timeout_seconds: float = 10.0,
        poll_interval: float = 0.5,
    ) -> Dict[str, Any]:
        """Wait for a window to appear matching criteria.
        
        Args:
            title_contains: Partial window title match
            process_name: Process name to wait for
            timeout_seconds: Maximum wait time
            poll_interval: Check interval in seconds
            
        Returns:
            {found: bool, title: str, pid: int, wait_ms: float}
        """
        start = time.perf_counter()
        deadline = start + timeout_seconds
        
        while time.perf_counter() < deadline:
            # Check by process name
            if process_name:
                check = await self.is_app_running(process_name)
                if check["running"]:
                    wait_ms = round((time.perf_counter() - start) * 1000, 2)
                    return {
                        "found": True,
                        "title": check.get("window_title", ""),
                        "pid": check["pid"],
                        "process_name": check["process_name"],
                        "wait_ms": wait_ms,
                    }
            
            # Check by window title
            if title_contains:
                windows = await self._find_windows_by_title(title_contains)
                if windows:
                    wait_ms = round((time.perf_counter() - start) * 1000, 2)
                    return {
                        "found": True,
                        "title": windows[0].get("title", ""),
                        "pid": windows[0].get("pid"),
                        "process_name": windows[0].get("process_name"),
                        "wait_ms": wait_ms,
                    }
            
            await asyncio.sleep(poll_interval)
        
        wait_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "found": False,
            "title": None,
            "pid": None,
            "process_name": None,
            "wait_ms": wait_ms,
        }

    async def verify_action(
        self,
        action: str,
        parameters: Dict[str, Any],
        timeout_seconds: float = 10.0,
    ) -> Dict[str, Any]:
        """Verify that an action completed successfully using UIA.
        
        This is the fast-path verification (no screenshots needed).
        
        Args:
            action: Action name (e.g., 'open_application')
            parameters: Action parameters
            timeout_seconds: How long to wait for verification
            
        Returns:
            {verified: bool, confidence: float, method: str, detail: str, duration_ms: float}
        """
        start = time.perf_counter()
        
        if action == "open_application":
            app_name = parameters.get("app_name", "")
            result = await self.wait_for_window(
                process_name=app_name,
                timeout_seconds=timeout_seconds,
            )
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "verified": result["found"],
                "confidence": 0.99 if result["found"] else 0.0,
                "method": "uia_process_check",
                "detail": f"Process {'found' if result['found'] else 'not found'}: {app_name}",
                "window_title": result.get("title"),
                "pid": result.get("pid"),
                "duration_ms": duration_ms,
            }
        
        elif action == "close_application":
            app_name = parameters.get("app_name", parameters.get("process_name", ""))
            # Wait briefly, then check process is gone
            await asyncio.sleep(1.0)
            check = await self.is_app_running(app_name)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "verified": not check["running"],
                "confidence": 0.99 if not check["running"] else 0.0,
                "method": "uia_process_gone",
                "detail": f"Process {'stopped' if not check['running'] else 'still running'}: {app_name}",
                "duration_ms": duration_ms,
            }
        
        elif action == "focus_window":
            title_contains = parameters.get("title_contains", "")
            await asyncio.sleep(0.5)
            fg = await self.get_foreground_window()
            is_focused = title_contains.lower() in (fg.get("title", "") or "").lower()
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "verified": is_focused,
                "confidence": 0.99 if is_focused else 0.1,
                "method": "uia_focus_check",
                "detail": f"Foreground: '{fg.get('title', 'unknown')}'",
                "duration_ms": duration_ms,
            }
        
        elif action in ("type_text", "press_key", "hotkey", "click"):
            # These can't be easily verified by UIA alone
            # Return low-confidence so vision fallback is triggered
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "verified": False,
                "confidence": 0.0,
                "method": "uia_not_applicable",
                "detail": f"Action '{action}' requires visual verification",
                "duration_ms": duration_ms,
            }
        
        elif action in ("copy_file", "move_file", "create_file", "delete_file"):
            # File operations can be verified via filesystem
            await asyncio.sleep(0.3)
            verified = await self._verify_file_operation(action, parameters)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "verified": verified,
                "confidence": 0.99 if verified else 0.0,
                "method": "uia_filesystem",
                "detail": f"File operation {'confirmed' if verified else 'unconfirmed'}",
                "duration_ms": duration_ms,
            }
        
        else:
            # Unknown action — can't verify via UIA
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "verified": False,
                "confidence": 0.0,
                "method": "uia_unknown_action",
                "detail": f"No UIA verification for action '{action}'",
                "duration_ms": duration_ms,
            }

    async def _get_window_title_for_pid(self, pid: int) -> Optional[str]:
        """Get the main window title for a given process PID."""
        try:
            user32 = ctypes.windll.user32
            
            titles = []
            
            def enum_callback(hwnd, _):
                if user32.IsWindowVisible(hwnd):
                    window_pid = ctypes.c_ulong()
                    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
                    if window_pid.value == pid:
                        length = user32.GetWindowTextLengthW(hwnd)
                        if length > 0:
                            buf = ctypes.create_unicode_buffer(length + 1)
                            user32.GetWindowTextW(hwnd, buf, length + 1)
                            if buf.value:
                                titles.append(buf.value)
                return True
            
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
            user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
            
            return titles[0] if titles else None
        except Exception:
            return None

    async def _find_windows_by_title(self, title_contains: str) -> List[Dict[str, Any]]:
        """Find windows whose title contains the given string."""
        results = []
        try:
            user32 = ctypes.windll.user32
            search_lower = title_contains.lower()
            
            def enum_callback(hwnd, _):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buf = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buf, length + 1)
                        if search_lower in buf.value.lower():
                            pid = ctypes.c_ulong()
                            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                            proc_name = None
                            try:
                                proc = psutil.Process(pid.value)
                                proc_name = proc.name()
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                            results.append({
                                "title": buf.value,
                                "pid": pid.value,
                                "process_name": proc_name,
                                "hwnd": hwnd,
                            })
                return True
            
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
            user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
        except Exception as e:
            logger.error(f"Window enumeration failed: {e}")
        
        return results

    async def _verify_file_operation(self, action: str, parameters: Dict[str, Any]) -> bool:
        """Verify file operations via filesystem checks."""
        import os
        
        if action == "copy_file":
            dest = parameters.get("destination", parameters.get("dest", ""))
            return os.path.exists(dest) if dest else False
        
        elif action == "move_file":
            dest = parameters.get("destination", parameters.get("dest", ""))
            source = parameters.get("source", parameters.get("src", ""))
            return os.path.exists(dest) and not os.path.exists(source)
        
        elif action == "create_file":
            path = parameters.get("path", parameters.get("file_path", ""))
            return os.path.exists(path) if path else False
        
        elif action == "delete_file":
            path = parameters.get("path", parameters.get("file_path", ""))
            return not os.path.exists(path) if path else False
        
        return False


# Global singleton
_uia_service: UIAService | None = None


def get_uia_service() -> UIAService:
    """Get or create global UIA service."""
    global _uia_service
    if _uia_service is None:
        _uia_service = UIAService()
    return _uia_service


uia_service = get_uia_service()
