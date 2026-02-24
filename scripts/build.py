"""
JARVIS AI — Build & Package Script

Packages the Python backend (via PyInstaller) and Electron frontend
into a distributable desktop application.

Usage:
    python scripts/build.py          # Build both backend and frontend
    python scripts/build.py --backend-only
    python scripts/build.py --frontend-only
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
DIST_DIR = ROOT / "dist"


def run(cmd: list[str], cwd: Path, label: str) -> None:
    """Run a subprocess, printing output live."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}\n")
    result = subprocess.run(cmd, cwd=str(cwd), shell=True)
    if result.returncode != 0:
        print(f"\n[ERROR] {label} failed (exit {result.returncode})")
        sys.exit(result.returncode)


def build_backend() -> None:
    """Package the FastAPI backend with PyInstaller."""
    print("\n[1/3] Installing PyInstaller (if needed)...")
    pip = BACKEND_DIR / "venv" / "Scripts" / "pip.exe"
    if not pip.exists():
        pip = Path("pip")  # fallback to system pip
    run([str(pip), "install", "pyinstaller"], cwd=BACKEND_DIR, label="Install PyInstaller")

    print("\n[2/3] Packaging backend with PyInstaller...")
    pyinstaller = BACKEND_DIR / "venv" / "Scripts" / "pyinstaller.exe"
    if not pyinstaller.exists():
        pyinstaller = Path("pyinstaller")

    spec_args = [
        str(pyinstaller),
        "--noconfirm",
        "--onedir",
        "--name", "jarvis-backend",
        "--add-data", f"app;app",
        "--hidden-import", "aiosqlite",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "uvicorn.lifespan.off",
        "--collect-all", "uvicorn",
        "--collect-all", "sqlalchemy",
        "--collect-all", "jose",
        "--distpath", str(DIST_DIR / "backend"),
        "run_server.py",
    ]
    run(spec_args, cwd=BACKEND_DIR, label="PyInstaller build")

    print("[3/3] Backend build complete.")


def build_frontend() -> None:
    """Build the Electron + React frontend."""
    print("\n[1/2] Building React (Vite)...")
    run(["npm", "run", "build"], cwd=FRONTEND_DIR, label="Vite build")

    print("\n[2/2] Packaging Electron...")
    run(["npm", "run", "electron:build"], cwd=FRONTEND_DIR, label="Electron build")

    # Copy Electron output to dist/
    electron_dist = FRONTEND_DIR / "dist"
    if electron_dist.exists():
        target = DIST_DIR / "frontend"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(str(electron_dist), str(target))

    print("Frontend build complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="JARVIS AI build script")
    parser.add_argument("--backend-only", action="store_true")
    parser.add_argument("--frontend-only", action="store_true")
    args = parser.parse_args()

    DIST_DIR.mkdir(exist_ok=True)

    if args.backend_only:
        build_backend()
    elif args.frontend_only:
        build_frontend()
    else:
        build_backend()
        build_frontend()

    print(f"\n{'='*60}")
    print(f"  Build artifacts in: {DIST_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
