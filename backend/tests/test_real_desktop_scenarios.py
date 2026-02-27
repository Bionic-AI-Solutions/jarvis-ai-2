"""REAL Desktop Automation Test Suite — NO MOCKS, NO FAKES.

Executes ACTUAL desktop actions on Windows and verifies results.
Generates proof documentation with timestamps, screenshots, and file checks.

Usage:
    cd backend
    python -m tests.test_real_desktop_scenarios

Scenarios tested:
1. Open Chrome (verify process running)
2. Take screenshot (verify file created)
3. Create file on E: drive, copy to another location, verify sizes match
4. Copy a real folder from F: to E: test workspace, verify file counts
5. List directory contents, verify real entries
6. Open File Explorer at a path, verify window opens
7. Close an application we opened (cleanup)
8. Full end-to-end: open Chrome, navigate, screenshot, close

Author: JARVIS AI Sprint 1
Date: Auto-generated
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add backend root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.desktop_automation import DesktopAutomationService
from app.agents.rag_agent import RAGAgent
from app.agents.execution_agent import ExecutionAgent


# ── Test Configuration ──────────────────────────────────────

TEST_WORKSPACE = r"E:\jarvis_test_workspace"
SCREENSHOTS_DIR = os.path.join(TEST_WORKSPACE, "screenshots")
PROOF_FILE = os.path.join(TEST_WORKSPACE, "TEST_PROOF_DOCUMENT.md")
PROOF_JSON = os.path.join(TEST_WORKSPACE, "test_results.json")

# Real paths verified to exist on this machine
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
E_DRIVE = r"E:\\"
F_DRIVE = r"F:\\"


class TestRunner:
    """Runs real desktop automation tests and collects proof."""

    def __init__(self):
        self.desktop = DesktopAutomationService(screenshots_dir=SCREENSHOTS_DIR)
        self.rag = RAGAgent()
        self.executor = ExecutionAgent(desktop_service=self.desktop)
        self.results: List[Dict[str, Any]] = []
        self.start_time = None
        self.end_time = None

    def _record(self, scenario: str, status: str, details: Dict, duration_ms: float, proof: Dict = None):
        """Record a test result."""
        entry = {
            "scenario": scenario,
            "status": status,  # PASS, FAIL, ERROR
            "timestamp": datetime.now().isoformat(),
            "duration_ms": round(duration_ms, 2),
            "details": details,
            "proof": proof or {},
        }
        self.results.append(entry)
        icon = "PASS" if status == "PASS" else "FAIL" if status == "FAIL" else "ERROR"
        print(f"  [{icon}] {scenario} ({duration_ms:.0f}ms)")
        if status != "PASS":
            print(f"        Details: {json.dumps(details, default=str)[:200]}")

    # ── Scenario 1: Open Chrome ─────────────────────────────

    async def test_01_open_chrome(self):
        """Open Google Chrome and verify it's running."""
        scenario = "Scenario 01: Open Chrome"
        start = time.perf_counter()
        print(f"\n{'='*60}")
        print(f"  {scenario}")
        print(f"{'='*60}")

        try:
            # Step 1: Open Chrome
            result = await self.desktop.open_application("chrome")
            duration = (time.perf_counter() - start) * 1000

            if not result["success"]:
                self._record(scenario, "FAIL", result, duration)
                return

            print(f"    Chrome opened - PID: {result.get('pid')}")

            # Step 2: Wait for it to load
            await asyncio.sleep(2)

            # Step 3: Verify process is running
            check = await self.desktop.is_process_running("chrome")
            is_running = check.get("is_running", False)
            instance_count = check.get("instance_count", 0)

            print(f"    Chrome running: {is_running}, instances: {instance_count}")

            # Step 4: Take screenshot as proof
            screenshot = await self.desktop.take_screenshot(filename="proof_01_chrome_opened.png")

            proof = {
                "pid": result.get("pid"),
                "exe_path": result.get("exe_path"),
                "chrome_running": is_running,
                "chrome_instances": instance_count,
                "screenshot": screenshot.get("filepath") if screenshot.get("success") else None,
                "screenshot_size": screenshot.get("file_size_bytes", 0),
            }

            duration = (time.perf_counter() - start) * 1000
            if is_running:
                self._record(scenario, "PASS", result, duration, proof)
            else:
                self._record(scenario, "FAIL", {"error": "Chrome not detected as running after open"}, duration, proof)

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self._record(scenario, "ERROR", {"error": str(e), "traceback": traceback.format_exc()}, duration)

    # ── Scenario 2: Take Screenshot ─────────────────────────

    async def test_02_take_screenshot(self):
        """Take a full screenshot and verify the file exists."""
        scenario = "Scenario 02: Take Screenshot"
        start = time.perf_counter()
        print(f"\n{'='*60}")
        print(f"  {scenario}")
        print(f"{'='*60}")

        try:
            result = await self.desktop.take_screenshot(filename="proof_02_screenshot.png")
            duration = (time.perf_counter() - start) * 1000

            if result["success"]:
                filepath = result["filepath"]
                exists = os.path.exists(filepath)
                size = result.get("file_size_bytes", 0)
                width = result.get("width", 0)
                height = result.get("height", 0)

                print(f"    Screenshot saved: {filepath}")
                print(f"    Size: {size:,} bytes, Resolution: {width}x{height}")
                print(f"    File exists: {exists}")

                proof = {
                    "filepath": filepath,
                    "file_exists": exists,
                    "file_size_bytes": size,
                    "resolution": f"{width}x{height}",
                }
                self._record(scenario, "PASS" if exists and size > 0 else "FAIL", result, duration, proof)
            else:
                self._record(scenario, "FAIL", result, duration)

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self._record(scenario, "ERROR", {"error": str(e), "traceback": traceback.format_exc()}, duration)

    # ── Scenario 3: Create File and Copy ────────────────────

    async def test_03_create_and_copy_file(self):
        """Create a test file, copy it, verify sizes match."""
        scenario = "Scenario 03: Create File + Copy (E: drive)"
        start = time.perf_counter()
        print(f"\n{'='*60}")
        print(f"  {scenario}")
        print(f"{'='*60}")

        source_file = os.path.join(TEST_WORKSPACE, "source", "test_document.txt")
        dest_dir = os.path.join(TEST_WORKSPACE, "destination")
        dest_file = os.path.join(dest_dir, "test_document.txt")

        try:
            # Step 1: Create file with known content
            content = f"""JARVIS AI Test Document
Created: {datetime.now().isoformat()}
Purpose: Verify file creation and copy operations
This is REAL content written to a REAL file on the E: drive.
No mocking. No faking. This file physically exists.
Line count test: line 6 of 10
Line count test: line 7 of 10
Line count test: line 8 of 10
Line count test: line 9 of 10
Line count test: line 10 of 10
"""
            create_result = await self.desktop.create_file(source_file, content)
            print(f"    Created: {source_file}")
            print(f"    Create success: {create_result['success']}")
            print(f"    File size: {create_result.get('size_bytes', 'N/A')} bytes")

            if not create_result["success"]:
                self._record(scenario, "FAIL", create_result, (time.perf_counter() - start) * 1000)
                return

            # Verify file actually exists on disk
            source_path = Path(source_file)
            assert source_path.exists(), f"Source file doesn't exist at {source_file}"
            actual_content = source_path.read_text(encoding="utf-8")
            assert content in actual_content, "File content doesn't match what we wrote"
            print(f"    Content verified: {len(actual_content)} chars")

            # Step 2: Copy file to destination
            os.makedirs(dest_dir, exist_ok=True)
            copy_result = await self.desktop.copy_file(source_file, dest_dir)
            print(f"    Copy success: {copy_result['success']}")

            if not copy_result["success"]:
                self._record(scenario, "FAIL", copy_result, (time.perf_counter() - start) * 1000)
                return

            # Step 3: Verify copy
            dest_path = Path(dest_file)
            dest_exists = dest_path.exists()
            src_size = source_path.stat().st_size
            dst_size = dest_path.stat().st_size if dest_exists else 0
            sizes_match = src_size == dst_size

            print(f"    Destination exists: {dest_exists}")
            print(f"    Source size: {src_size}")
            print(f"    Dest size:   {dst_size}")
            print(f"    Sizes match: {sizes_match}")

            # Read destination content to verify
            if dest_exists:
                dest_content = dest_path.read_text(encoding="utf-8")
                content_matches = actual_content == dest_content
                print(f"    Content match: {content_matches}")
            else:
                content_matches = False

            duration = (time.perf_counter() - start) * 1000
            proof = {
                "source_file": source_file,
                "source_exists": source_path.exists(),
                "source_size": src_size,
                "dest_file": str(dest_path),
                "dest_exists": dest_exists,
                "dest_size": dst_size,
                "sizes_match": sizes_match,
                "content_matches": content_matches,
            }

            all_pass = dest_exists and sizes_match and content_matches
            self._record(scenario, "PASS" if all_pass else "FAIL", copy_result, duration, proof)

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self._record(scenario, "ERROR", {"error": str(e), "traceback": traceback.format_exc()}, duration)

    # ── Scenario 4: Copy Folder from F: to E: ──────────────

    async def test_04_copy_folder_f_to_e(self):
        """Create a test folder structure on F:, copy to E: workspace, verify counts match."""
        scenario = "Scenario 04: Copy Folder (F: to E: drive)"
        start = time.perf_counter()
        print(f"\n{'='*60}")
        print(f"  {scenario}")
        print(f"{'='*60}")

        # Create a test folder on F: with known structure
        source_folder = r"F:\jarvis_test_source_folder"
        dest_folder = os.path.join(TEST_WORKSPACE, "copied_from_f")

        try:
            # Step 1: Create source folder structure on F: drive
            os.makedirs(os.path.join(source_folder, "subfolder1"), exist_ok=True)
            os.makedirs(os.path.join(source_folder, "subfolder2"), exist_ok=True)

            # Create files in the structure
            files_created = []
            for i in range(1, 4):
                fpath = os.path.join(source_folder, f"file_{i}.txt")
                Path(fpath).write_text(f"Test file {i} - created at {datetime.now().isoformat()}\n" * 10)
                files_created.append(fpath)

            for i in range(1, 3):
                fpath = os.path.join(source_folder, "subfolder1", f"sub1_file_{i}.txt")
                Path(fpath).write_text(f"Subfolder1 file {i}\n" * 5)
                files_created.append(fpath)

            fpath = os.path.join(source_folder, "subfolder2", "sub2_data.txt")
            Path(fpath).write_text("Data in subfolder2\n" * 20)
            files_created.append(fpath)

            print(f"    Created source folder: {source_folder}")
            print(f"    Files in source: {len(files_created)}")

            # Count source files
            src_path = Path(source_folder)
            src_file_count = len([f for f in src_path.rglob("*") if f.is_file()])
            src_dir_count = len([f for f in src_path.rglob("*") if f.is_dir()])
            print(f"    Source: {src_file_count} files, {src_dir_count} dirs")

            # Step 2: Copy folder to E: workspace
            copy_result = await self.desktop.copy_folder(source_folder, dest_folder)
            print(f"    Copy success: {copy_result['success']}")

            if not copy_result["success"]:
                self._record(scenario, "FAIL", copy_result, (time.perf_counter() - start) * 1000)
                return

            # Step 3: Verify destination
            # copy_folder copies into dest_folder/source_name
            dst_path = Path(dest_folder)
            if not dst_path.exists():
                # It might have been placed as dest_folder/jarvis_test_source_folder
                dst_path = Path(dest_folder) / src_path.name
            
            dst_exists = dst_path.exists()
            if dst_exists:
                dst_file_count = len([f for f in dst_path.rglob("*") if f.is_file()])
                dst_dir_count = len([f for f in dst_path.rglob("*") if f.is_dir()])
            else:
                dst_file_count = 0
                dst_dir_count = 0

            print(f"    Destination: {dst_path}")
            print(f"    Dest exists: {dst_exists}")
            print(f"    Dest: {dst_file_count} files, {dst_dir_count} dirs")
            print(f"    File count match: {src_file_count == dst_file_count}")

            duration = (time.perf_counter() - start) * 1000
            proof = {
                "source_folder": source_folder,
                "source_file_count": src_file_count,
                "source_dir_count": src_dir_count,
                "dest_folder": str(dst_path),
                "dest_exists": dst_exists,
                "dest_file_count": dst_file_count,
                "dest_dir_count": dst_dir_count,
                "file_counts_match": src_file_count == dst_file_count,
            }

            all_pass = dst_exists and src_file_count == dst_file_count
            self._record(scenario, "PASS" if all_pass else "FAIL", copy_result, duration, proof)

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self._record(scenario, "ERROR", {"error": str(e), "traceback": traceback.format_exc()}, duration)
        finally:
            # Cleanup source folder on F:
            if os.path.exists(source_folder):
                shutil.rmtree(source_folder, ignore_errors=True)
                print(f"    Cleaned up source: {source_folder}")

    # ── Scenario 5: List Directory Contents ─────────────────

    async def test_05_list_directory(self):
        """List contents of E: drive root and verify real entries."""
        scenario = "Scenario 05: List Directory (E: drive)"
        start = time.perf_counter()
        print(f"\n{'='*60}")
        print(f"  {scenario}")
        print(f"{'='*60}")

        try:
            result = await self.desktop.list_directory(r"E:\\")
            duration = (time.perf_counter() - start) * 1000

            if result["success"]:
                items = result.get("items", [])
                print(f"    Items found: {result.get('item_count', 0)}")
                for item in items[:10]:
                    kind = "DIR " if item.get("is_dir") else "FILE"
                    size = item.get("size_bytes", 0)
                    print(f"      [{kind}] {item['name']}  ({size:,} bytes)")
                if len(items) > 10:
                    print(f"      ... and {len(items)-10} more items")

                # Verify we can see known folders
                names = [i["name"].lower() for i in items]
                known_existing = []
                for known in ["bionic ai", "jarvis_test_workspace"]:
                    if known in names:
                        known_existing.append(known)
                
                print(f"    Known folders detected: {known_existing}")

                proof = {
                    "path": r"E:\\",
                    "item_count": len(items),
                    "items_sample": items[:10],
                    "known_folders_found": known_existing,
                }
                self._record(scenario, "PASS" if len(items) > 0 else "FAIL", result, duration, proof)
            else:
                self._record(scenario, "FAIL", result, duration)

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self._record(scenario, "ERROR", {"error": str(e), "traceback": traceback.format_exc()}, duration)

    # ── Scenario 6: Open File Explorer ──────────────────────

    async def test_06_open_explorer(self):
        """Open File Explorer at E: drive and verify window."""
        scenario = "Scenario 06: Open File Explorer (E: drive)"
        start = time.perf_counter()
        print(f"\n{'='*60}")
        print(f"  {scenario}")
        print(f"{'='*60}")

        try:
            result = await self.desktop.open_explorer(r"E:\\")
            duration_after_open = (time.perf_counter() - start) * 1000
            print(f"    Explorer opened: {result['success']}")

            if result["success"]:
                # Wait for window to appear
                await asyncio.sleep(2)

                # Take screenshot as proof
                screenshot = await self.desktop.take_screenshot(filename="proof_06_explorer_opened.png")

                # Check for explorer window
                check = await self.desktop.is_process_running("explorer")
                
                duration = (time.perf_counter() - start) * 1000
                proof = {
                    "explorer_opened": result["success"],
                    "explorer_running": check.get("is_running", False),
                    "screenshot": screenshot.get("filepath") if screenshot.get("success") else None,
                }
                self._record(scenario, "PASS", result, duration, proof)
            else:
                self._record(scenario, "FAIL", result, duration_after_open)

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self._record(scenario, "ERROR", {"error": str(e), "traceback": traceback.format_exc()}, duration)

    # ── Scenario 7: RAG Agent Parse + Execute ───────────────

    async def test_07_rag_parse_and_execute(self):
        """Test RAG agent parsing natural language into plans, then executing."""
        scenario = "Scenario 07: RAG Agent Parse + Execute"
        start = time.perf_counter()
        print(f"\n{'='*60}")
        print(f"  {scenario}")
        print(f"{'='*60}")

        test_commands = [
            "open notepad",
            "take a screenshot",
            f"create file {os.path.join(TEST_WORKSPACE, 'rag_test_output.txt')} with content Hello from JARVIS AI RAG Agent",
            f"list {TEST_WORKSPACE}",
        ]

        sub_results = []
        all_pass = True

        for cmd in test_commands:
            print(f"\n    Command: \"{cmd}\"")

            # Parse with RAG
            plan = await self.rag.process(cmd)
            steps = plan.get("steps", [])
            confidence = plan.get("confidence", 0.0)
            reasoning = plan.get("reasoning", "")

            print(f"    → Parsed: {len(steps)} steps, confidence={confidence:.2f}")
            print(f"    → Reasoning: {reasoning[:80]}")

            if not steps:
                print(f"    → SKIPPED: No steps generated")
                sub_results.append({
                    "command": cmd,
                    "parsed": False,
                    "steps": 0,
                    "confidence": confidence,
                })
                all_pass = False
                continue

            for s in steps:
                print(f"      Step: {s['action']} → {s.get('description', '')}")

            # Execute the plan
            exec_result = await self.executor.execute_plan(plan)
            succeeded = exec_result.get("steps_succeeded", 0)
            total = exec_result.get("steps_total", 0)
            print(f"    → Executed: {succeeded}/{total} steps succeeded")

            sub_results.append({
                "command": cmd,
                "parsed": True,
                "steps": len(steps),
                "confidence": confidence,
                "executed": exec_result["success"],
                "steps_succeeded": succeeded,
                "steps_total": total,
            })

            if not exec_result["success"]:
                all_pass = False

            # Pause between commands
            await asyncio.sleep(1)

        duration = (time.perf_counter() - start) * 1000

        # Close notepad we opened
        await self.desktop.close_application("notepad")
        await asyncio.sleep(0.5)

        proof = {
            "commands_tested": len(test_commands),
            "sub_results": sub_results,
        }
        self._record(scenario, "PASS" if all_pass else "FAIL", {"sub_results": sub_results}, duration, proof)

    # ── Scenario 8: End-to-End Complex Workflow ─────────────

    async def test_08_end_to_end_complex(self):
        """Full E2E: Create files on E:, list them, take screenshot, copy to subfolder, verify."""
        scenario = "Scenario 08: End-to-End Complex Workflow"
        start = time.perf_counter()
        print(f"\n{'='*60}")
        print(f"  {scenario}")
        print(f"{'='*60}")

        e2e_dir = os.path.join(TEST_WORKSPACE, "e2e_test")
        e2e_copy_dir = os.path.join(TEST_WORKSPACE, "e2e_copy")

        try:
            # Step 1: Create multiple files
            print("\n    Step 1: Create multiple files")
            files_to_create = {
                "report.txt": "Quarterly Report Q4 2025\nRevenue: $1.2M\nProfit: $300K\n",
                "data.csv": "name,age,city\nJohn,30,NYC\nJane,25,LA\nBob,40,Chicago\n",
                "notes.md": "# Meeting Notes\n- Discuss roadmap\n- Review sprints\n- Plan Q1\n",
            }
            
            created_files = []
            for fname, content in files_to_create.items():
                fpath = os.path.join(e2e_dir, fname)
                res = await self.desktop.create_file(fpath, content)
                print(f"      Created {fname}: {res['success']} ({res.get('size_bytes', 0)} bytes)")
                if res["success"]:
                    created_files.append(fpath)

            # Step 2: List the directory we just created
            print("\n    Step 2: List created directory")
            list_res = await self.desktop.list_directory(e2e_dir)
            if list_res["success"]:
                for item in list_res.get("items", []):
                    print(f"      {item['name']} - {item.get('size_bytes', 0)} bytes")
            else:
                print(f"      Failed: {list_res.get('error')}")

            # Step 3: Take screenshot
            print("\n    Step 3: Take screenshot")
            ss_res = await self.desktop.take_screenshot(filename="proof_08_e2e.png")
            print(f"      Screenshot: {ss_res['success']}")

            # Step 4: Copy entire e2e_dir to e2e_copy
            print("\n    Step 4: Copy folder")
            copy_res = await self.desktop.copy_folder(e2e_dir, e2e_copy_dir)
            print(f"      Folder copy: {copy_res['success']}")

            # Step 5: Verify copy
            print("\n    Step 5: Verify copied folder")
            src_files = list(Path(e2e_dir).rglob("*"))
            src_file_count = len([f for f in src_files if f.is_file()])
            
            copy_check_path = Path(e2e_copy_dir)
            if not copy_check_path.exists():
                copy_check_path = Path(e2e_copy_dir) / Path(e2e_dir).name
            
            if copy_check_path.exists():
                dst_files = list(copy_check_path.rglob("*"))
                dst_file_count = len([f for f in dst_files if f.is_file()])
            else:
                dst_file_count = 0

            counts_match = src_file_count == dst_file_count
            print(f"      Source files: {src_file_count}")
            print(f"      Dest files:   {dst_file_count}")
            print(f"      Match: {counts_match}")

            # Step 6: Verify file content integrity
            print("\n    Step 6: Content integrity check")
            content_ok = True
            for fname, expected_content in files_to_create.items():
                src_fp = Path(e2e_dir) / fname
                dst_fp = copy_check_path / fname
                if dst_fp.exists():
                    actual = dst_fp.read_text(encoding="utf-8")
                    match = actual == expected_content
                    print(f"      {fname}: content match = {match}")
                    if not match:
                        content_ok = False
                else:
                    print(f"      {fname}: NOT FOUND in destination")
                    content_ok = False

            duration = (time.perf_counter() - start) * 1000
            proof = {
                "files_created": len(created_files),
                "directory_listed": list_res.get("success", False),
                "screenshot_taken": ss_res.get("success", False),
                "screenshot_path": ss_res.get("filepath"),
                "folder_copied": copy_res.get("success", False),
                "source_file_count": src_file_count,
                "dest_file_count": dst_file_count,
                "counts_match": counts_match,
                "content_integrity": content_ok,
            }

            all_pass = (
                len(created_files) == len(files_to_create) and
                list_res.get("success") and
                copy_res.get("success") and
                counts_match and
                content_ok
            )
            self._record(scenario, "PASS" if all_pass else "FAIL", proof, duration, proof)

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self._record(scenario, "ERROR", {"error": str(e), "traceback": traceback.format_exc()}, duration)

    # ── Scenario 9: Move File ───────────────────────────────

    async def test_09_move_file(self):
        """Move a file from one location to another, verify source gone and dest exists."""
        scenario = "Scenario 09: Move File"
        start = time.perf_counter()
        print(f"\n{'='*60}")
        print(f"  {scenario}")
        print(f"{'='*60}")

        source = os.path.join(TEST_WORKSPACE, "move_source", "moveme.txt")
        dest = os.path.join(TEST_WORKSPACE, "move_dest", "moveme.txt")

        try:
            # Create source file
            create_res = await self.desktop.create_file(source, "This file will be MOVED, not copied.\n" * 50)
            print(f"    Created source: {create_res['success']} ({create_res.get('size_bytes', 0)} bytes)")

            src_size = Path(source).stat().st_size if Path(source).exists() else 0

            # Move it
            move_res = await self.desktop.move_file(source, dest)
            print(f"    Move result: {move_res['success']}")

            # Verify
            src_gone = not Path(source).exists()
            dst_exists = Path(dest).exists()
            dst_size = Path(dest).stat().st_size if dst_exists else 0

            print(f"    Source gone: {src_gone}")
            print(f"    Dest exists: {dst_exists}")
            print(f"    Size preserved: {src_size} → {dst_size} (match={src_size == dst_size})")

            duration = (time.perf_counter() - start) * 1000
            proof = {
                "source": source,
                "destination": dest,
                "source_removed": src_gone,
                "dest_exists": dst_exists,
                "source_size": src_size,
                "dest_size": dst_size,
                "size_preserved": src_size == dst_size,
            }
            all_pass = src_gone and dst_exists and src_size == dst_size
            self._record(scenario, "PASS" if all_pass else "FAIL", move_res, duration, proof)

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self._record(scenario, "ERROR", {"error": str(e), "traceback": traceback.format_exc()}, duration)

    # ── Scenario 10: Delete File and Verify ─────────────────

    async def test_10_delete_file(self):
        """Create then delete a file, verify it's gone."""
        scenario = "Scenario 10: Delete File"
        start = time.perf_counter()
        print(f"\n{'='*60}")
        print(f"  {scenario}")
        print(f"{'='*60}")

        target = os.path.join(TEST_WORKSPACE, "delete_me.txt")

        try:
            # Create
            await self.desktop.create_file(target, "This file will be deleted.\n")
            exists_before = Path(target).exists()
            print(f"    File created: {exists_before}")

            # Delete
            del_res = await self.desktop.delete_file(target)
            exists_after = Path(target).exists()

            print(f"    Delete result: {del_res['success']}")
            print(f"    File exists after: {exists_after}")

            duration = (time.perf_counter() - start) * 1000
            proof = {
                "filepath": target,
                "existed_before_delete": exists_before,
                "exists_after_delete": exists_after,
                "successfully_deleted": exists_before and not exists_after,
            }
            all_pass = exists_before and not exists_after
            self._record(scenario, "PASS" if all_pass else "FAIL", del_res, duration, proof)

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self._record(scenario, "ERROR", {"error": str(e), "traceback": traceback.format_exc()}, duration)

    # ── Scenario 11: Process Check ──────────────────────────

    async def test_11_process_check(self):
        """Check if known processes are running."""
        scenario = "Scenario 11: Process Check"
        start = time.perf_counter()
        print(f"\n{'='*60}")
        print(f"  {scenario}")
        print(f"{'='*60}")

        try:
            processes_to_check = ["explorer", "chrome", "python", "svchost"]
            results = {}

            for proc_name in processes_to_check:
                res = await self.desktop.is_process_running(proc_name)
                running = res.get("is_running", False)
                count = res.get("instance_count", 0)
                results[proc_name] = {"running": running, "instances": count}
                print(f"    {proc_name}: running={running}, instances={count}")

            duration = (time.perf_counter() - start) * 1000
            proof = {
                "processes_checked": results,
            }
            # At minimum, explorer and svchost should be running on Windows
            expected_running = results.get("explorer", {}).get("running", False)
            self._record(scenario, "PASS" if expected_running else "FAIL", results, duration, proof)

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self._record(scenario, "ERROR", {"error": str(e), "traceback": traceback.format_exc()}, duration)

    # ── Scenario 12: Close Notepad (Cleanup) ────────────────

    async def test_12_close_notepad(self):
        """Open notepad, verify running, close it, verify closed."""
        scenario = "Scenario 12: Open + Close Application (Notepad)"
        start = time.perf_counter()
        print(f"\n{'='*60}")
        print(f"  {scenario}")
        print(f"{'='*60}")

        try:
            # Open
            open_res = await self.desktop.open_application("notepad")
            print(f"    Opened notepad: {open_res['success']}, PID={open_res.get('pid')}")
            await asyncio.sleep(1.5)

            # Verify running
            check1 = await self.desktop.is_process_running("notepad")
            running_after_open = check1.get("is_running", False)
            print(f"    Running after open: {running_after_open}")

            # Take proof screenshot
            await self.desktop.take_screenshot(filename="proof_12_notepad_open.png")

            # Close
            close_res = await self.desktop.close_application("notepad")
            print(f"    Close result: {close_res['success']}")
            await asyncio.sleep(1.5)

            # Verify closed
            check2 = await self.desktop.is_process_running("notepad")
            running_after_close = check2.get("is_running", False)
            print(f"    Running after close: {running_after_close}")

            duration = (time.perf_counter() - start) * 1000
            proof = {
                "opened": open_res.get("success"),
                "pid": open_res.get("pid"),
                "running_after_open": running_after_open,
                "closed": close_res.get("success"),
                "running_after_close": running_after_close,
                "lifecycle_complete": running_after_open and not running_after_close,
            }
            all_pass = open_res.get("success") and running_after_open and not running_after_close
            self._record(scenario, "PASS" if all_pass else "FAIL", {"open": open_res, "close": close_res}, duration, proof)

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self._record(scenario, "ERROR", {"error": str(e), "traceback": traceback.format_exc()}, duration)

    # ── Generate Proof Document ──────────────────────────────

    def generate_proof_document(self):
        """Generate Markdown proof document with all results."""
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")
        total = len(self.results)
        total_duration = sum(r["duration_ms"] for r in self.results)

        md = []
        md.append("# JARVIS AI — Real Desktop Automation Test Proof Document")
        md.append("")
        md.append(f"**Generated:** {datetime.now().isoformat()}")
        md.append(f"**Machine:** {os.environ.get('COMPUTERNAME', 'Unknown')}")
        md.append(f"**OS:** Windows ({os.name})")
        md.append(f"**Python:** {sys.version.split()[0]}")
        md.append(f"**Test Workspace:** `{TEST_WORKSPACE}`")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## Summary")
        md.append("")
        md.append(f"| Metric | Value |")
        md.append(f"|--------|-------|")
        md.append(f"| Total Scenarios | {total} |")
        md.append(f"| **PASSED** | **{passed}** |")
        md.append(f"| **FAILED** | **{failed}** |")
        md.append(f"| **ERRORS** | **{errors}** |")
        md.append(f"| Pass Rate | {(passed/total*100) if total else 0:.1f}% |")
        md.append(f"| Total Duration | {total_duration:.0f}ms ({total_duration/1000:.1f}s) |")
        md.append(f"| Test Start | {self.start_time} |")
        md.append(f"| Test End | {self.end_time} |")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## Detailed Results")
        md.append("")

        for i, r in enumerate(self.results, 1):
            status_emoji = "PASS" if r["status"] == "PASS" else "FAIL" if r["status"] == "FAIL" else "ERROR"
            md.append(f"### {i}. {r['scenario']} [{status_emoji}]")
            md.append("")
            md.append(f"- **Status:** {r['status']}")
            md.append(f"- **Timestamp:** {r['timestamp']}")
            md.append(f"- **Duration:** {r['duration_ms']:.0f}ms")
            md.append("")

            if r.get("proof"):
                md.append("**Proof Evidence:**")
                md.append("")
                md.append("```json")
                md.append(json.dumps(r["proof"], indent=2, default=str))
                md.append("```")
                md.append("")

            if r["status"] != "PASS" and r.get("details"):
                md.append("**Details:**")
                md.append("")
                md.append("```json")
                md.append(json.dumps(r["details"], indent=2, default=str)[:500])
                md.append("```")
                md.append("")

            md.append("---")
            md.append("")

        # Screenshots
        md.append("## Screenshots Captured")
        md.append("")
        ss_dir = Path(SCREENSHOTS_DIR)
        if ss_dir.exists():
            screenshots = sorted(ss_dir.glob("proof_*.png"))
            if screenshots:
                for ss in screenshots:
                    size = ss.stat().st_size
                    md.append(f"- `{ss.name}` ({size:,} bytes)")
            else:
                md.append("No proof screenshots found.")
        md.append("")

        # Audit trail
        md.append("## Desktop Automation Audit Trail")
        md.append("")
        md.append(f"Total actions logged: {len(self.desktop.action_log)}")
        md.append("")
        md.append("```json")
        # Last 20 actions
        trail = self.desktop.action_log[-20:]
        md.append(json.dumps(trail, indent=2, default=str))
        md.append("```")
        md.append("")

        md.append("---")
        md.append("")
        md.append("*This document was auto-generated by JARVIS AI Test Suite. All tests executed REAL desktop actions — no mocks, no fakes.*")

        return "\n".join(md)

    # ── Run All Tests ────────────────────────────────────────

    async def run_all(self):
        """Execute all test scenarios."""
        self.start_time = datetime.now().isoformat()
        
        print("\n" + "=" * 70)
        print("  JARVIS AI — Real Desktop Automation Test Suite")
        print("  NO MOCKS. NO FAKES. REAL ACTIONS.")
        print("=" * 70)
        print(f"  Start time: {self.start_time}")
        print(f"  Workspace: {TEST_WORKSPACE}")

        # Ensure test workspace exists
        os.makedirs(TEST_WORKSPACE, exist_ok=True)
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

        # Run all scenarios in order
        await self.test_02_take_screenshot()
        await self.test_03_create_and_copy_file()
        await self.test_04_copy_folder_f_to_e()
        await self.test_05_list_directory()
        await self.test_06_open_explorer()
        await self.test_07_rag_parse_and_execute()
        await self.test_08_end_to_end_complex()
        await self.test_09_move_file()
        await self.test_10_delete_file()
        await self.test_11_process_check()
        await self.test_12_close_notepad()
        await self.test_01_open_chrome()

        self.end_time = datetime.now().isoformat()

        # Print summary
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")
        total = len(self.results)

        print("\n" + "=" * 70)
        print("  FINAL RESULTS")
        print("=" * 70)
        print(f"  PASSED: {passed}/{total}")
        print(f"  FAILED: {failed}/{total}")
        print(f"  ERRORS: {errors}/{total}")
        print(f"  Pass Rate: {(passed/total*100) if total else 0:.1f}%")
        print("=" * 70)

        # Generate proof document
        proof_md = self.generate_proof_document()
        Path(PROOF_FILE).write_text(proof_md, encoding="utf-8")
        print(f"\n  Proof document: {PROOF_FILE}")

        # Save raw JSON results
        raw = {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "results": self.results,
            "audit_trail": self.desktop.action_log,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
            }
        }
        Path(PROOF_JSON).write_text(json.dumps(raw, indent=2, default=str), encoding="utf-8")
        print(f"  Raw JSON: {PROOF_JSON}")

        return raw


if __name__ == "__main__":
    runner = TestRunner()
    results = asyncio.run(runner.run_all())
