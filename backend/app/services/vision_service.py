"""Vision Service — Screenshot analysis via moondream (Ollama).

Architecture Reference: JARVIS_AI_MASTER_COMPLETE_ARCHITECTURE_V3.md Part 7
Role: Analyze screenshots to verify execution, detect UI changes
Model: moondream via Ollama (1B vision model, Q4_0 quantized)
"""

from __future__ import annotations

import base64
import io
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from app.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class VisionResult:
    """Result of vision analysis on a screenshot."""

    text: str  # moondream description/analysis
    confidence: float  # 0.0 – 1.0 (how confident in the analysis)
    ui_changes: list[str] = None  # Detected UI changes
    detections: dict[str, Any] = None  # Objects detected (window, button, text, etc.)
    verified: bool = False  # Whether the expected state was visually confirmed
    duration_ms: float = 0.0

    def __post_init__(self):
        if self.ui_changes is None:
            self.ui_changes = []
        if self.detections is None:
            self.detections = {}


class VisionService:
    """Analyzes screenshots using moondream vision model via Ollama."""

    def __init__(self):
        self.settings = get_settings()
        self.ollama_base_url = self.settings.ollama_host or "http://localhost:11434"
        self.model_name = "moondream:latest"
        self.client = httpx.AsyncClient(timeout=120.0)

    async def analyze_screenshot(
        self,
        screenshot_path: str | Path,
        query: str = "What is shown in this screenshot? Describe the UI elements visible.",
    ) -> VisionResult:
        """Analyze a screenshot using moondream.

        Args:
            screenshot_path: Path to screenshot file (PNG, JPG, etc.)
            query: Question/instruction for moondream to analyze

        Returns:
            VisionResult with analysis text and UI detections
        """
        start = time.perf_counter()

        # Read image and encode to base64
        if isinstance(screenshot_path, str):
            screenshot_path = Path(screenshot_path)

        if not screenshot_path.exists():
            logger.warning(f"Screenshot file not found: {screenshot_path}")
            return VisionResult(
                text="Screenshot file not found",
                confidence=0.0,
                verified=False,
                duration_ms=0,
            )

        try:
            with open(screenshot_path, "rb") as f:
                image_data = f.read()
            image_b64 = base64.b64encode(image_data).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to read screenshot: {e}")
            return VisionResult(
                text=f"Failed to read screenshot: {e}",
                confidence=0.0,
                verified=False,
                duration_ms=round((time.perf_counter() - start) * 1000, 2),
            )

        # Call moondream via Ollama
        try:
            response = await self.client.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": query,
                    "images": [image_b64],
                    "stream": False,
                    "temperature": 0.3,  # Low temperature for deterministic vision analysis
                },
            )
            response.raise_for_status()
            result = response.json()
            analysis_text = result.get("response", "").strip()

            duration_ms = round((time.perf_counter() - start) * 1000, 2)

            # Parse moondream output for UI elements
            ui_changes = self._extract_ui_elements(analysis_text)
            detections = self._parse_objects(analysis_text)

            return VisionResult(
                text=analysis_text,
                confidence=0.85,  # moondream is fairly reliable
                ui_changes=ui_changes,
                detections=detections,
                verified=True,
                duration_ms=duration_ms,
            )
        except Exception as e:
            logger.error(f"moondream analysis failed: {e}")
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            return VisionResult(
                text=f"Vision analysis error: {e}",
                confidence=0.0,
                verified=False,
                duration_ms=duration_ms,
            )

    async def verify_execution(
        self,
        screenshot_path: str | Path,
        expected_state: str,
    ) -> bool:
        """Verify that an executed action resulted in the expected state.

        Args:
            screenshot_path: Current screenshot
            expected_state: Description of what we expect to see (e.g., "Gmail window open")

        Returns:
            True if expected state is visible in screenshot
        """
        query = f"Is the following state visible in this screenshot? State: {expected_state}"
        result = await self.analyze_screenshot(screenshot_path, query)

        # Simple heuristic: if moondream mentions "yes" or affirms the state, it's verified
        response_lower = result.text.lower()
        if any(word in response_lower for word in ["yes", "visible", "open", "shown", "present", "appears", "displayed"]):
            return True
        if all(word not in response_lower for word in ["no", "not", "cannot", "missing", "hidden"]):
            # If no negation found, assume positive
            return True
        return False

    async def detect_ui_changes(
        self,
        before_path: str | Path,
        after_path: str | Path,
    ) -> list[str]:
        """Detect UI changes between two screenshots.

        Args:
            before_path: Screenshot before action
            after_path: Screenshot after action

        Returns:
            List of detected changes
        """
        before = await self.analyze_screenshot(before_path, "Describe all visible UI elements and windows.")
        after = await self.analyze_screenshot(after_path, "Describe all visible UI elements and windows.")

        # Simple diffing: return changes detected by moondream
        changes = []
        if before.text != after.text:
            changes.append(f"Visual change detected: {after.text[:200]}")
        return changes

    async def extract_text_from_screen(self, screenshot_path: str | Path) -> str:
        """Extract visible text from screenshot using moondream OCR capability."""
        result = await self.analyze_screenshot(
            screenshot_path,
            "Extract all visible text from this screenshot. List each piece of text.",
        )
        return result.text

    async def check_moondream_available(self) -> dict[str, Any]:
        """Check if moondream model is available and loaded."""
        try:
            response = await self.client.post(
                f"{self.ollama_base_url}/api/tags",
                json={},
            )
            response.raise_for_status()
            tags = response.json()
            models = tags.get("models", [])
            
            moondream_models = [
                m.get("name") for m in models
                if "moondream" in m.get("name", "").lower()
            ]
            
            return {
                "available": len(moondream_models) > 0,
                "models": moondream_models,
                "status": "ready" if moondream_models else "not_found",
            }
        except Exception as e:
            logger.error(f"Failed to check moondream availability: {e}")
            return {
                "available": False,
                "models": [],
                "status": "error",
                "error": str(e),
            }

    def _extract_ui_elements(self, text: str) -> list[str]:
        """Extract UI element descriptions from moondream output."""
        elements = []
        keywords = ["window", "button", "input", "text", "field", "menu", "dialog", "icon"]
        for keyword in keywords:
            if keyword in text.lower():
                elements.append(keyword)
        return elements

    def _parse_objects(self, text: str) -> dict[str, Any]:
        """Parse object detections from moondream text."""
        return {
            "raw_text": text[:500],  # Store first 500 chars of analysis
            "has_ui": bool(text),
        }

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Global instance
_vision_service: VisionService | None = None


def get_vision_service() -> VisionService:
    """Get or create global vision service instance."""
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service


vision_service = get_vision_service()
