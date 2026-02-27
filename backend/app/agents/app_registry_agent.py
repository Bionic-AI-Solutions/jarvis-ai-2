"""App Registry Agent (Agent 12) — Application discovery and availability verification.

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 4, Agent 12
Role: System scanner — discovers installed applications
Model: None (pure system introspection, NO LLM)
Responsibilities:
  1. Full system scan at startup (Program Files, AppData, PATH, Registry)
  2. Cache results in memory (refresh if >1h old)
  3. On-demand lookup for specific apps
  4. Prevent wasted execution by verifying apps before EA launches them
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.agents.protocol import BaseAgent
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AppRegistryAgent(BaseAgent):
    """System App Registry — discovers and caches installed applications.
    
    Architecture V3, Agent 12:
    Input:  {app_name: str} for on-demand lookup
    Output: {app_exists: bool, path: str, launch_command: str, aliases: []}
    Performance: Instant from cache; full scan on startup/hourly
    """

    def __init__(self):
        super().__init__(
            agent_name="app_registry_agent",
            agent_type="system",
            description="Application discovery — scans and caches installed apps",
        )
        self._app_cache: Dict[str, Dict[str, Any]] = {}
        self._last_scan: float = 0.0
        self._scan_interval: float = 3600.0  # 1 hour

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BaseAgent interface: handle app registry queries.
        
        Operations:
        - "scan": Full system scan
        - "lookup": Check if specific app exists
        - "list": List all cached apps
        """
        start = time.perf_counter()
        operation = input_data.get("operation", "lookup")

        if operation == "scan":
            result = await self._full_scan()
        elif operation == "lookup":
            app_name = input_data.get("app_name", "")
            result = self._lookup_app(app_name)
        elif operation == "list":
            result = {"apps": list(self._app_cache.keys()), "count": len(self._app_cache)}
        else:
            result = {"error": f"Unknown operation: {operation}"}

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._record_call(duration_ms)

        return {
            "status": "success",
            "result": result,
            "duration_ms": duration_ms,
            "context_updates": {},
        }

    async def _full_scan(self) -> Dict[str, Any]:
        """Scan the system for installed applications."""
        scan_start = time.time()
        apps_found = 0

        # Scan common Windows paths
        scan_dirs = [
            os.environ.get("ProgramFiles", r"C:\Program Files"),
            os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
            os.path.join(os.environ.get("APPDATA", ""), ""),
        ]

        for scan_dir in scan_dirs:
            if scan_dir and os.path.isdir(scan_dir):
                try:
                    for entry in os.scandir(scan_dir):
                        if entry.is_dir():
                            self._scan_app_directory(entry.path, entry.name)
                            apps_found += 1
                except PermissionError:
                    pass

        # Scan PATH entries
        path_entries = os.environ.get("PATH", "").split(os.pathsep)
        for path_dir in path_entries:
            if os.path.isdir(path_dir):
                try:
                    for entry in os.scandir(path_dir):
                        if entry.is_file() and entry.name.endswith(".exe"):
                            name = entry.name.replace(".exe", "").lower()
                            if name not in self._app_cache:
                                self._app_cache[name] = {
                                    "app_name": name,
                                    "executable_path": entry.path,
                                    "launch_command": name,
                                    "is_in_path": True,
                                    "last_scan": time.time(),
                                }
                except PermissionError:
                    pass

        # Add well-known Windows apps
        self._add_well_known_apps()

        self._last_scan = time.time()
        logger.info("app_registry_scan_complete", apps_found=len(self._app_cache))

        return {
            "scanned": True,
            "apps_found": len(self._app_cache),
            "scan_time_ms": round((time.time() - scan_start) * 1000, 2),
        }

    def _scan_app_directory(self, dir_path: str, dir_name: str) -> None:
        """Scan a single app directory for executables."""
        try:
            for root, dirs, files in os.walk(dir_path):
                for f in files:
                    if f.endswith(".exe"):
                        name = f.replace(".exe", "").lower()
                        full_path = os.path.join(root, f)
                        if name not in self._app_cache:
                            self._app_cache[name] = {
                                "app_name": name,
                                "aliases": [dir_name.lower()],
                                "executable_path": full_path,
                                "launch_command": name,
                                "is_in_path": False,
                                "last_scan": time.time(),
                            }
                # Only go 2 levels deep
                if root.count(os.sep) - dir_path.count(os.sep) >= 2:
                    dirs.clear()
        except (PermissionError, OSError):
            pass

    def _add_well_known_apps(self) -> None:
        """Add well-known Windows apps that might not be in scanned paths."""
        well_known = {
            "notepad": {
                "app_name": "notepad",
                "aliases": ["notepad", "text editor"],
                "executable_path": r"C:\Windows\notepad.exe",
                "launch_command": "notepad",
                "is_in_path": True,
            },
            "calculator": {
                "app_name": "calculator",
                "aliases": ["calc", "calculator"],
                "executable_path": "calc.exe",
                "launch_command": "calc",
                "is_in_path": True,
            },
            "explorer": {
                "app_name": "explorer",
                "aliases": ["file explorer", "windows explorer"],
                "executable_path": r"C:\Windows\explorer.exe",
                "launch_command": "explorer",
                "is_in_path": True,
            },
            "cmd": {
                "app_name": "cmd",
                "aliases": ["command prompt", "terminal"],
                "executable_path": r"C:\Windows\System32\cmd.exe",
                "launch_command": "cmd",
                "is_in_path": True,
            },
            "powershell": {
                "app_name": "powershell",
                "aliases": ["ps", "powershell"],
                "executable_path": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                "launch_command": "powershell",
                "is_in_path": True,
            },
        }
        for name, info in well_known.items():
            if name not in self._app_cache:
                info["last_scan"] = time.time()
                self._app_cache[name] = info

    def _lookup_app(self, app_name: str) -> Dict[str, Any]:
        """Look up a specific application by name or alias."""
        app_lower = app_name.lower().strip()

        # Direct match
        if app_lower in self._app_cache:
            return {"app_exists": True, **self._app_cache[app_lower]}

        # Search aliases
        for name, info in self._app_cache.items():
            aliases = info.get("aliases", [])
            if app_lower in [a.lower() for a in aliases]:
                return {"app_exists": True, **info}

        # Partial match
        for name, info in self._app_cache.items():
            if app_lower in name or name in app_lower:
                return {"app_exists": True, **info}

        return {
            "app_exists": False,
            "app_name": app_name,
            "message": f"Application '{app_name}' not found in registry",
        }
