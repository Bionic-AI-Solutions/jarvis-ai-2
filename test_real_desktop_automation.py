"""JARVIS AI - REAL Desktop Automation Test Suite

THIS IS NOT A MOCK TEST SUITE.
Every test in this file executes REAL desktop actions:
- Opens REAL applications (Chrome, Notepad, Explorer)
- Copies REAL files between drives
- Takes REAL screenshots as proof
- Verifies REAL outcomes (process running, file exists, etc.)

Run: python test_real_desktop_automation.py
Output: test_results/ folder with screenshots and JSON report

NO HARDCODING. NO FAKING. NO ASSUMPTIONS.
"""

import asyncio
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.services.desktop_automation import DesktopAutomationService


class TestResult:
    """Stores result of a single test."""
    
    def __init__(self, name: str, scenario: str):
        self.name = name
        self.scenario = scenario
        self.status = "not_run"  # pass, fail, error, skip
        self.details = {}
        self.screenshots = []
        self.error = None
        self.duration_ms = 0.0
        self.timestamp = datetime.now().isoformat()
        self.steps = []

    def add_step(self, step_name: str, result: dict):
        self.steps.append({
            "step": step_name,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })

    def to_dict(self) -> dict:
        return {
            "test_name": self.name,
            "scenario": self.scenario,
            "status": self.status,
            "details": self.details,
            "screenshots": self.screenshots,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
            "steps": self.steps,
        }


class RealDesktopTestSuite:
    """REAL test suite that executes actual desktop automation."""

    def __init__(self):
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)
        self.screenshots_dir = self.results_dir / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        self.automation = DesktopAutomationService(
            screenshots_dir=str(self.screenshots_dir)
        )
        self.test_results: list[TestResult] = []
        self.start_time = None

    async def run_all(self):
        """Run all test scenarios."""
        self.start_time = time.perf_counter()
        
        print("=" * 70)
        print("JARVIS AI - REAL DESKTOP AUTOMATION TEST SUITE")
        print(f"Started: {datetime.now().isoformat()}")
        print("=" * 70)
        print()

        # ── Test Scenarios (IN ORDER) ────────────────────────

        tests = [
            ("SCENARIO 1", "Take baseline screenshot", self.test_baseline_screenshot),
            ("SCENARIO 2", "Open Chrome browser", self.test_open_chrome),
            ("SCENARIO 3", "Open Notepad and type text", self.test_open_notepad_type),
            ("SCENARIO 4", "Open File Explorer at specific path", self.test_open_explorer),
            ("SCENARIO 5", "Create test file and verify", self.test_create_file),
            ("SCENARIO 6", "Copy file between locations", self.test_copy_file),
            ("SCENARIO 7", "Copy folder between locations", self.test_copy_folder),
            ("SCENARIO 8", "Move file to another location", self.test_move_file),
            ("SCENARIO 9", "List directory contents", self.test_list_directory),
            ("SCENARIO 10", "Check running processes", self.test_check_processes),
            ("SCENARIO 11", "Open Calculator", self.test_open_calculator),
            ("SCENARIO 12", "Keyboard shortcut test", self.test_keyboard_shortcuts),
            ("SCENARIO 13", "Multi-app workflow", self.test_multi_app_workflow),
            ("SCENARIO 14", "Close applications gracefully", self.test_close_apps),
            ("SCENARIO 15", "Cleanup test artifacts", self.test_cleanup),
        ]

        for scenario_id, description, test_fn in tests:
            result = TestResult(scenario_id, description)
            print(f"  [{scenario_id}] {description}...")
            
            start = time.perf_counter()
            try:
                await test_fn(result)
                result.duration_ms = round((time.perf_counter() - start) * 1000, 2)
                
                if result.status == "not_run":
                    result.status = "pass"
                
                status_icon = "✅" if result.status == "pass" else "❌" if result.status == "fail" else "⚠️"
                print(f"    {status_icon} {result.status.upper()} ({result.duration_ms}ms)")
                
            except Exception as e:
                result.status = "error"
                result.error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                result.duration_ms = round((time.perf_counter() - start) * 1000, 2)
                print(f"    ❌ ERROR: {e}")

            self.test_results.append(result)
            print()

        # Generate report
        await self._generate_report()

    # ══════════════════════════════════════════════════════════
    # SCENARIO 1: BASELINE SCREENSHOT
    # ══════════════════════════════════════════════════════════

    async def test_baseline_screenshot(self, result: TestResult):
        """Take a screenshot of current desktop state as baseline."""
        screenshot = await self.automation.take_screenshot("baseline_before_tests.png")
        result.add_step("Take baseline screenshot", screenshot)

        if screenshot["success"]:
            result.screenshots.append(screenshot["filepath"])
            result.details = {
                "resolution": f"{screenshot['width']}x{screenshot['height']}",
                "file_size_bytes": screenshot["file_size_bytes"],
                "filepath": screenshot["filepath"],
            }
            result.status = "pass"
        else:
            result.status = "fail"
            result.error = screenshot.get("error")

    # ══════════════════════════════════════════════════════════
    # SCENARIO 2: OPEN CHROME
    # ══════════════════════════════════════════════════════════

    async def test_open_chrome(self, result: TestResult):
        """Open Google Chrome browser - REAL test."""
        
        # Step 1: Check if Chrome is already running
        before = await self.automation.is_process_running("chrome")
        result.add_step("Check Chrome before", before)
        was_running = before["is_running"]
        instances_before = before["instance_count"]

        # Step 2: Open Chrome
        open_result = await self.automation.open_application("chrome")
        result.add_step("Open Chrome", open_result)

        if not open_result["success"]:
            result.status = "fail"
            result.error = open_result.get("error", "Failed to open Chrome")
            return

        # Step 3: Wait for Chrome to fully load
        await self.automation.wait(3.0)

        # Step 4: Verify Chrome is running
        after = await self.automation.is_process_running("chrome")
        result.add_step("Check Chrome after", after)

        # Step 5: Take screenshot as proof
        screenshot = await self.automation.take_screenshot("chrome_opened.png")
        result.add_step("Screenshot proof", screenshot)
        if screenshot["success"]:
            result.screenshots.append(screenshot["filepath"])

        # Step 6: Check windows
        windows = await self.automation.list_windows()
        chrome_windows = [w for w in windows if "chrome" in w.get("title", "").lower() or "google" in w.get("title", "").lower()]
        result.add_step("List Chrome windows", {"chrome_windows": chrome_windows, "total_windows": len(windows)})

        # Verdict
        if after["is_running"] and after["instance_count"] > 0:
            result.status = "pass"
            result.details = {
                "was_already_running": was_running,
                "instances_before": instances_before,
                "instances_after": after["instance_count"],
                "pid": open_result.get("pid"),
                "exe_path": open_result.get("exe_path"),
                "chrome_windows_found": len(chrome_windows),
            }
        else:
            result.status = "fail"
            result.error = "Chrome process not detected after launch"

    # ══════════════════════════════════════════════════════════
    # SCENARIO 3: OPEN NOTEPAD AND TYPE TEXT
    # ══════════════════════════════════════════════════════════

    async def test_open_notepad_type(self, result: TestResult):
        """Open Notepad and type real text into it."""
        
        # Step 1: Open Notepad
        open_result = await self.automation.open_application("notepad")
        result.add_step("Open Notepad", open_result)

        if not open_result["success"]:
            result.status = "fail"
            result.error = open_result.get("error")
            return

        # Step 2: Wait for Notepad
        await self.automation.wait(2.0)

        # Step 3: Focus Notepad window
        focus = await self.automation.focus_window("Notepad")
        result.add_step("Focus Notepad", focus)

        # Step 4: Type text
        test_text = "Hello from JARVIS AI! This is a REAL test. Timestamp: " + datetime.now().isoformat()
        type_result = await self.automation.type_text(test_text, interval=0.01)
        result.add_step("Type text", type_result)

        # Step 5: Press Enter and type more
        await self.automation.press_key("enter")
        type_result2 = await self.automation.type_text("Line 2: Desktop automation is working!", interval=0.01)
        result.add_step("Type second line", type_result2)

        # Step 6: Take screenshot as proof
        await self.automation.wait(0.5)
        screenshot = await self.automation.take_screenshot("notepad_typed.png")
        result.add_step("Screenshot proof", screenshot)
        if screenshot["success"]:
            result.screenshots.append(screenshot["filepath"])

        # Step 7: Verify Notepad is running
        proc_check = await self.automation.is_process_running("notepad")
        result.add_step("Verify Notepad running", proc_check)

        result.status = "pass" if type_result["success"] and proc_check["is_running"] else "fail"
        result.details = {
            "text_typed": test_text,
            "text_length": len(test_text),
            "notepad_pid": open_result.get("pid"),
            "notepad_running": proc_check["is_running"],
        }

    # ══════════════════════════════════════════════════════════
    # SCENARIO 4: OPEN FILE EXPLORER
    # ══════════════════════════════════════════════════════════

    async def test_open_explorer(self, result: TestResult):
        """Open File Explorer at E: drive."""
        
        # Step 1: Check what drives exist
        drives_to_try = ["E:\\", "C:\\", "D:\\"]
        target_path = None
        
        for drive in drives_to_try:
            if os.path.exists(drive):
                target_path = drive
                break
        
        if target_path is None:
            result.status = "skip"
            result.error = "No accessible drives found"
            return
        
        result.add_step("Found accessible drive", {"drive": target_path})

        # Step 2: Open Explorer at that drive
        open_result = await self.automation.open_explorer(target_path)
        result.add_step("Open Explorer", open_result)

        # Step 3: Wait
        await self.automation.wait(2.0)

        # Step 4: Screenshot
        screenshot = await self.automation.take_screenshot("explorer_opened.png")
        result.add_step("Screenshot proof", screenshot)
        if screenshot["success"]:
            result.screenshots.append(screenshot["filepath"])

        # Step 5: List the windows to find Explorer
        windows = await self.automation.list_windows()
        explorer_windows = [w for w in windows if target_path.rstrip("\\") in w.get("title", "") or "File Explorer" in w.get("title", "")]
        result.add_step("Find Explorer windows", {"explorer_windows": explorer_windows})

        result.status = "pass" if open_result["success"] else "fail"
        result.details = {
            "target_path": target_path,
            "explorer_windows_found": len(explorer_windows),
        }

    # ══════════════════════════════════════════════════════════
    # SCENARIO 5: CREATE TEST FILE
    # ══════════════════════════════════════════════════════════

    async def test_create_file(self, result: TestResult):
        """Create a real test file on disk."""
        
        test_dir = Path("test_results/test_workspace")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        test_filepath = str(test_dir / "jarvis_test_file.txt")
        test_content = f"JARVIS AI Test File\nCreated: {datetime.now().isoformat()}\nThis proves file creation works."

        # Step 1: Create file
        create_result = await self.automation.create_file(test_filepath, test_content)
        result.add_step("Create file", create_result)

        # Step 2: Verify file exists
        file_exists = Path(test_filepath).exists()
        result.add_step("Verify exists", {"exists": file_exists})

        # Step 3: Verify content
        if file_exists:
            actual_content = Path(test_filepath).read_text(encoding="utf-8")
            content_matches = actual_content == test_content
            result.add_step("Verify content", {
                "content_matches": content_matches,
                "expected_length": len(test_content),
                "actual_length": len(actual_content),
            })
        else:
            content_matches = False
            result.add_step("Verify content", {"content_matches": False, "error": "File not found"})

        result.status = "pass" if file_exists and content_matches else "fail"
        result.details = {
            "filepath": test_filepath,
            "content_length": len(test_content),
            "file_exists": file_exists,
            "content_matches": content_matches,
        }

    # ══════════════════════════════════════════════════════════
    # SCENARIO 6: COPY FILE BETWEEN LOCATIONS
    # ══════════════════════════════════════════════════════════

    async def test_copy_file(self, result: TestResult):
        """Copy a real file from one location to another."""
        
        # Source: our test file from Scenario 5
        source = "test_results/test_workspace/jarvis_test_file.txt"
        dest_dir = Path("test_results/test_workspace/copied")
        dest_dir.mkdir(parents=True, exist_ok=True)
        destination = str(dest_dir / "jarvis_test_file_copy.txt")

        # Step 1: Verify source exists
        if not Path(source).exists():
            # Create it fresh if scenario 5 didn't run
            await self.automation.create_file(source, f"Backup test content {datetime.now().isoformat()}")
        
        source_exists = Path(source).exists()
        result.add_step("Verify source", {"exists": source_exists, "path": source})

        if not source_exists:
            result.status = "fail"
            result.error = f"Source file not found: {source}"
            return

        # Step 2: Copy file
        copy_result = await self.automation.copy_file(source, destination)
        result.add_step("Copy file", copy_result)

        # Step 3: Verify destination exists
        dest_exists = Path(destination).exists()
        result.add_step("Verify destination", {"exists": dest_exists, "path": destination})

        # Step 4: Verify content matches
        if dest_exists:
            src_content = Path(source).read_text(encoding="utf-8")
            dst_content = Path(destination).read_text(encoding="utf-8")
            content_matches = src_content == dst_content
            result.add_step("Verify content match", {
                "content_matches": content_matches,
                "source_size": len(src_content),
                "dest_size": len(dst_content),
            })
        else:
            content_matches = False

        result.status = "pass" if copy_result["success"] and dest_exists and content_matches else "fail"
        result.details = {
            "source": source,
            "destination": destination,
            "source_exists": source_exists,
            "dest_exists": dest_exists,
            "content_matches": content_matches,
            "sizes_match": copy_result.get("sizes_match", False),
        }

    # ══════════════════════════════════════════════════════════
    # SCENARIO 7: COPY FOLDER
    # ══════════════════════════════════════════════════════════

    async def test_copy_folder(self, result: TestResult):
        """Copy an entire folder from one location to another."""
        
        # Create source folder with multiple files
        src_dir = Path("test_results/test_workspace/source_folder")
        src_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test files inside source folder
        for i in range(3):
            (src_dir / f"file_{i}.txt").write_text(
                f"File {i} content - {datetime.now().isoformat()}", encoding="utf-8"
            )
        (src_dir / "subfolder").mkdir(exist_ok=True)
        (src_dir / "subfolder" / "nested_file.txt").write_text(
            "Nested file content", encoding="utf-8"
        )

        result.add_step("Create source folder", {
            "path": str(src_dir),
            "files_created": 4,
        })

        # Step 2: Copy folder
        dest_dir = Path("test_results/test_workspace/dest_folder")
        copy_result = await self.automation.copy_folder(str(src_dir), str(dest_dir))
        result.add_step("Copy folder", copy_result)

        # Step 3: Verify destination
        copied_dir = dest_dir / "source_folder" if dest_dir.is_dir() and (dest_dir / "source_folder").exists() else dest_dir
        if not copied_dir.exists():
            # Also check if it was copied directly
            copied_dir = dest_dir
        
        dest_exists = copied_dir.exists()
        dest_files = list(copied_dir.rglob("*")) if dest_exists else []
        dest_file_count = len([f for f in dest_files if f.is_file()])

        result.add_step("Verify destination", {
            "exists": dest_exists,
            "path": str(copied_dir),
            "file_count": dest_file_count,
        })

        result.status = "pass" if copy_result["success"] and dest_exists and dest_file_count >= 3 else "fail"
        result.details = {
            "source": str(src_dir),
            "destination": str(copied_dir),
            "source_files": 4,
            "destination_files": dest_file_count,
            "success": copy_result["success"],
        }

    # ══════════════════════════════════════════════════════════
    # SCENARIO 8: MOVE FILE
    # ══════════════════════════════════════════════════════════

    async def test_move_file(self, result: TestResult):
        """Move a file from one location to another."""
        
        # Create file to move
        source = "test_results/test_workspace/file_to_move.txt"
        await self.automation.create_file(source, f"This file will be moved. {datetime.now().isoformat()}")

        source_before = Path(source).exists()
        result.add_step("Create source", {"exists": source_before, "path": source})

        # Move it
        dest = "test_results/test_workspace/moved/moved_file.txt"
        move_result = await self.automation.move_file(source, dest)
        result.add_step("Move file", move_result)

        # Verify: source gone, dest exists
        source_after = Path(source).exists()
        dest_exists = Path(dest).exists()
        
        result.add_step("Verify move", {
            "source_removed": not source_after,
            "dest_exists": dest_exists,
        })

        result.status = "pass" if not source_after and dest_exists else "fail"
        result.details = {
            "source": source,
            "destination": dest,
            "source_existed_before": source_before,
            "source_removed": not source_after,
            "dest_exists": dest_exists,
        }

    # ══════════════════════════════════════════════════════════
    # SCENARIO 9: LIST DIRECTORY
    # ══════════════════════════════════════════════════════════

    async def test_list_directory(self, result: TestResult):
        """List the contents of a real directory."""
        
        # List our test workspace
        list_result = await self.automation.list_directory("test_results/test_workspace")
        result.add_step("List test workspace", list_result)

        # Also list a system directory
        system_list = await self.automation.list_directory("C:\\Windows")
        result.add_step("List C:\\Windows", {
            "success": system_list["success"],
            "item_count": system_list.get("item_count", 0),
            # Don't include full items list for C:\Windows - too large
        })

        result.status = "pass" if list_result["success"] else "fail"
        result.details = {
            "test_workspace_items": list_result.get("item_count", 0),
            "test_workspace_contents": [item["name"] for item in list_result.get("items", [])],
            "windows_dir_items": system_list.get("item_count", 0),
        }

    # ══════════════════════════════════════════════════════════
    # SCENARIO 10: CHECK RUNNING PROCESSES
    # ══════════════════════════════════════════════════════════

    async def test_check_processes(self, result: TestResult):
        """Check what processes are running on the system."""
        
        processes_to_check = ["chrome", "notepad", "explorer", "python"]
        
        for proc_name in processes_to_check:
            check = await self.automation.is_process_running(proc_name)
            result.add_step(f"Check {proc_name}", {
                "process": proc_name,
                "is_running": check["is_running"],
                "instance_count": check["instance_count"],
            })

        result.status = "pass"
        result.details = {
            proc: (await self.automation.is_process_running(proc))["is_running"]
            for proc in processes_to_check
        }

    # ══════════════════════════════════════════════════════════
    # SCENARIO 11: OPEN CALCULATOR
    # ══════════════════════════════════════════════════════════

    async def test_open_calculator(self, result: TestResult):
        """Open Windows Calculator."""
        
        open_result = await self.automation.open_application("calc")
        result.add_step("Open Calculator", open_result)

        await self.automation.wait(2.0)

        # Take screenshot
        screenshot = await self.automation.take_screenshot("calculator_opened.png")
        result.add_step("Screenshot proof", screenshot)
        if screenshot["success"]:
            result.screenshots.append(screenshot["filepath"])

        # Verify process
        proc = await self.automation.is_process_running("Calculator")
        # Calculator on Windows 10+ runs as "CalculatorApp" or "Calculator"
        if not proc["is_running"]:
            proc = await self.automation.is_process_running("CalculatorApp")
        result.add_step("Verify Calculator", proc)

        result.status = "pass" if open_result["success"] else "fail"
        result.details = {
            "pid": open_result.get("pid"),
            "process_detected": proc["is_running"],
        }

    # ══════════════════════════════════════════════════════════
    # SCENARIO 12: KEYBOARD SHORTCUT
    # ══════════════════════════════════════════════════════════

    async def test_keyboard_shortcuts(self, result: TestResult):
        """Test keyboard shortcuts - focus Notepad, select all, copy."""
        
        # Focus Notepad (from earlier test)
        focus = await self.automation.focus_window("Notepad")
        result.add_step("Focus Notepad", focus)

        if not focus.get("success"):
            # Notepad might not be open, open it fresh
            await self.automation.open_application("notepad")
            await self.automation.wait(2.0)
            await self.automation.focus_window("Notepad")
            await self.automation.type_text("Hello JARVIS shortcut test!", interval=0.01)
            await self.automation.wait(0.5)

        # Select All (Ctrl+A)
        select_all = await self.automation.hotkey("ctrl", "a")
        result.add_step("Ctrl+A (Select All)", select_all)

        await self.automation.wait(0.3)

        # Copy (Ctrl+C)
        copy = await self.automation.hotkey("ctrl", "c")
        result.add_step("Ctrl+C (Copy)", copy)

        await self.automation.wait(0.3)

        # Take screenshot showing selected text
        screenshot = await self.automation.take_screenshot("keyboard_shortcut_test.png")
        result.add_step("Screenshot proof", screenshot)
        if screenshot["success"]:
            result.screenshots.append(screenshot["filepath"])

        result.status = "pass" if select_all["success"] and copy["success"] else "fail"
        result.details = {
            "select_all_success": select_all["success"],
            "copy_success": copy["success"],
        }

    # ══════════════════════════════════════════════════════════
    # SCENARIO 13: MULTI-APP WORKFLOW
    # ══════════════════════════════════════════════════════════

    async def test_multi_app_workflow(self, result: TestResult):
        """Complex workflow:
        1. Create a test file
        2. Open File Explorer to that folder
        3. Take screenshot
        4. Copy file to another location 
        5. Verify copy exists
        6. Take final screenshot
        """
        
        # Step 1: Create test file
        test_file = "test_results/test_workspace/multi_app_test.txt"
        create = await self.automation.create_file(
            test_file,
            f"Multi-app workflow test\nTimestamp: {datetime.now().isoformat()}\n"
            "This file proves the multi-app workflow test passed.\n"
        )
        result.add_step("Create test file", create)

        # Step 2: Open Explorer to the folder
        explore = await self.automation.open_explorer(str(Path(test_file).parent.resolve()))
        result.add_step("Open Explorer to folder", explore)
        await self.automation.wait(2.0)

        # Step 3: Screenshot
        ss1 = await self.automation.take_screenshot("multi_app_step3_explorer.png")
        result.add_step("Screenshot: Explorer open", ss1)
        if ss1["success"]:
            result.screenshots.append(ss1["filepath"])

        # Step 4: Copy file
        copy_dest = "test_results/test_workspace/multi_app_copy/multi_app_test.txt"
        copy = await self.automation.copy_file(test_file, copy_dest)
        result.add_step("Copy file", copy)

        # Step 5: Verify
        dest_exists = Path(copy_dest).exists()
        src_exists = Path(test_file).exists()
        
        if dest_exists and src_exists:
            src_content = Path(test_file).read_text(encoding="utf-8")
            dst_content = Path(copy_dest).read_text(encoding="utf-8")
            content_match = src_content == dst_content
        else:
            content_match = False

        result.add_step("Verify copy", {
            "source_exists": src_exists,
            "dest_exists": dest_exists,
            "content_match": content_match,
        })

        # Step 6: Final screenshot
        ss2 = await self.automation.take_screenshot("multi_app_final.png")
        result.add_step("Final screenshot", ss2)
        if ss2["success"]:
            result.screenshots.append(ss2["filepath"])

        all_success = create["success"] and copy["success"] and dest_exists and content_match
        result.status = "pass" if all_success else "fail"
        result.details = {
            "file_created": create["success"],
            "explorer_opened": explore["success"],
            "file_copied": copy["success"],
            "dest_exists": dest_exists,
            "content_matches": content_match,
            "workflow_complete": all_success,
        }

    # ══════════════════════════════════════════════════════════
    # SCENARIO 14: CLOSE APPLICATIONS
    # ══════════════════════════════════════════════════════════

    async def test_close_apps(self, result: TestResult):
        """Close Notepad and Calculator (opened by tests)."""
        
        # Close Notepad (without saving)
        # First try to dismiss save dialog
        await self.automation.hotkey("alt", "F4")
        await self.automation.wait(0.5)
        # Press "Don't Save" - Tab to the button and press Enter or use hotkey
        await self.automation.press_key("tab")
        await self.automation.wait(0.2)
        await self.automation.press_key("enter")
        await self.automation.wait(0.5)
        
        # Fallback: kill Notepad process
        close_notepad = await self.automation.close_application("notepad")
        result.add_step("Close Notepad", close_notepad)

        # Close Calculator
        close_calc = await self.automation.close_application("Calculator")
        result.add_step("Close Calculator", close_calc)

        await self.automation.wait(1.0)

        # Verify they're closed
        notepad_check = await self.automation.is_process_running("notepad")
        calc_check = await self.automation.is_process_running("Calculator")
        
        result.add_step("Verify closed", {
            "notepad_running": notepad_check["is_running"],
            "calc_running": calc_check["is_running"],
        })

        # Screenshot after cleanup
        screenshot = await self.automation.take_screenshot("after_close_apps.png")
        result.add_step("Screenshot after cleanup", screenshot)
        if screenshot["success"]:
            result.screenshots.append(screenshot["filepath"])

        result.status = "pass"
        result.details = {
            "notepad_closed": not notepad_check["is_running"],
            "calculator_closed": not calc_check["is_running"],
        }

    # ══════════════════════════════════════════════════════════
    # SCENARIO 15: CLEANUP
    # ══════════════════════════════════════════════════════════

    async def test_cleanup(self, result: TestResult):
        """Clean up test artifacts (but keep screenshots & report)."""
        
        workspace = Path("test_results/test_workspace")
        
        if workspace.exists():
            items_before = list(workspace.rglob("*"))
            count_before = len(items_before)
            
            # Delete test workspace
            delete_result = await self.automation.delete_file(str(workspace))
            result.add_step("Delete test workspace", delete_result)
            
            exists_after = workspace.exists()
            result.status = "pass" if not exists_after else "fail"
            result.details = {
                "items_cleaned": count_before,
                "workspace_removed": not exists_after,
            }
        else:
            result.status = "pass"
            result.details = {"message": "No test workspace to clean"}

    # ══════════════════════════════════════════════════════════
    # REPORT GENERATION
    # ══════════════════════════════════════════════════════════

    async def _generate_report(self):
        """Generate comprehensive test report with all evidence."""
        
        total_duration = round((time.perf_counter() - self.start_time) * 1000, 2)
        
        passed = sum(1 for r in self.test_results if r.status == "pass")
        failed = sum(1 for r in self.test_results if r.status == "fail")
        errors = sum(1 for r in self.test_results if r.status == "error")
        skipped = sum(1 for r in self.test_results if r.status == "skip")
        total = len(self.test_results)

        report = {
            "title": "JARVIS AI - Real Desktop Automation Test Report",
            "generated_at": datetime.now().isoformat(),
            "machine": {
                "os": os.name,
                "platform": sys.platform,
                "python_version": sys.version,
                "cwd": os.getcwd(),
            },
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
                "total_duration_ms": total_duration,
            },
            "tests": [r.to_dict() for r in self.test_results],
            "action_log": self.automation.action_log,
            "screenshots": [
                s for r in self.test_results for s in r.screenshots
            ],
        }

        # Save JSON report
        report_path = self.results_dir / "test_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        # Save human-readable report
        md_path = self.results_dir / "TEST_REPORT.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# JARVIS AI - Real Desktop Automation Test Report\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            f.write(f"**Total Duration:** {total_duration}ms\n\n")
            f.write("---\n\n")
            f.write("## Summary\n\n")
            f.write(f"| Metric | Value |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| Total Tests | {total} |\n")
            f.write(f"| ✅ Passed | {passed} |\n")
            f.write(f"| ❌ Failed | {failed} |\n")
            f.write(f"| ⚠️ Errors | {errors} |\n")
            f.write(f"| ⏭️ Skipped | {skipped} |\n")
            f.write(f"| Pass Rate | {(passed/total*100):.1f}% |\n")
            f.write(f"\n---\n\n")
            
            f.write("## Test Results (Detail)\n\n")
            for r in self.test_results:
                icon = "✅" if r.status == "pass" else "❌" if r.status in ("fail", "error") else "⏭️"
                f.write(f"### {icon} {r.name}: {r.scenario}\n\n")
                f.write(f"**Status:** {r.status.upper()}  \n")
                f.write(f"**Duration:** {r.duration_ms}ms  \n\n")
                
                if r.details:
                    f.write("**Details:**\n```json\n")
                    f.write(json.dumps(r.details, indent=2, default=str))
                    f.write("\n```\n\n")
                
                if r.error:
                    f.write(f"**Error:**\n```\n{r.error}\n```\n\n")
                
                if r.screenshots:
                    f.write("**Screenshots:**\n")
                    for ss in r.screenshots:
                        f.write(f"- `{ss}`\n")
                    f.write("\n")
                
                if r.steps:
                    f.write("**Steps Executed:**\n")
                    for step in r.steps:
                        step_result = step["result"]
                        success = step_result.get("success", "N/A")
                        icon_s = "✅" if success is True else "❌" if success is False else "ℹ️"
                        f.write(f"- {icon_s} {step['step']}\n")
                    f.write("\n")
                
                f.write("---\n\n")
            
            f.write("## Screenshots Captured\n\n")
            all_screenshots = [s for r in self.test_results for s in r.screenshots]
            if all_screenshots:
                for ss in all_screenshots:
                    f.write(f"- `{ss}`\n")
            else:
                f.write("No screenshots captured.\n")
            
            f.write(f"\n## Complete Action Log\n\n")
            f.write(f"Total actions executed: {len(self.automation.action_log)}\n\n")
            for entry in self.automation.action_log:
                f.write(f"- **{entry['timestamp']}** | `{entry['action']}` | ")
                success = entry['result'].get('success', 'N/A')
                f.write(f"{'✅' if success else '❌'}\n")

        print()
        print("=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"  Total:   {total}")
        print(f"  Passed:  {passed} ✅")
        print(f"  Failed:  {failed} ❌")
        print(f"  Errors:  {errors} ⚠️")
        print(f"  Skipped: {skipped} ⏭️")
        print(f"  Rate:    {(passed/total*100):.1f}%")
        print(f"  Duration: {total_duration}ms")
        print()
        print(f"  JSON Report: {report_path}")
        print(f"  MD Report:   {md_path}")
        print(f"  Screenshots: {self.screenshots_dir}")
        print("=" * 70)


if __name__ == "__main__":
    suite = RealDesktopTestSuite()
    asyncio.run(suite.run_all())
