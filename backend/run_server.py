"""
JARVIS AI — Backend entry point for PyInstaller bundling.

Starts the Uvicorn server on the configured host/port.
Used by the build script to create a standalone executable.
"""

from __future__ import annotations

import os
import sys

# Ensure the backend directory is on the path when running from a bundle
if getattr(sys, "frozen", False):
    # Running inside a PyInstaller bundle
    bundle_dir = os.path.dirname(sys.executable)
    sys.path.insert(0, bundle_dir)


def main() -> None:
    import uvicorn
    from app.config import get_settings

    cfg = get_settings()
    uvicorn.run(
        "app.main:app",
        host=cfg.host,
        port=cfg.port,
        log_level=cfg.log_level.lower(),
        reload=False,  # Never reload in production
    )


if __name__ == "__main__":
    main()
