# JARVIS AI — Real Desktop Automation Test Proof Document

**Generated:** 2026-02-24T23:34:32.803660
**Machine:** BROLY
**OS:** Windows (nt)
**Python:** 3.12.7
**Test Workspace:** `E:\jarvis_test_workspace`

---

## Summary

| Metric | Value |
|--------|-------|
| Total Scenarios | 12 |
| **PASSED** | **12** |
| **FAILED** | **0** |
| **ERRORS** | **0** |
| Pass Rate | 100.0% |
| Total Duration | 23441ms (23.4s) |
| Test Start | 2026-02-24T23:34:08.045783 |
| Test End | 2026-02-24T23:34:32.803660 |

---

## Detailed Results

### 1. Scenario 02: Take Screenshot [PASS]

- **Status:** PASS
- **Timestamp:** 2026-02-24T23:34:08.585877
- **Duration:** 539ms

**Proof Evidence:**

```json
{
  "filepath": "E:\\jarvis_test_workspace\\screenshots\\proof_02_screenshot.png",
  "file_exists": true,
  "file_size_bytes": 100662,
  "resolution": "1920x1080"
}
```

---

### 2. Scenario 03: Create File + Copy (E: drive) [PASS]

- **Status:** PASS
- **Timestamp:** 2026-02-24T23:34:08.605020
- **Duration:** 18ms

**Proof Evidence:**

```json
{
  "source_file": "E:\\jarvis_test_workspace\\source\\test_document.txt",
  "source_exists": true,
  "source_size": 384,
  "dest_file": "E:\\jarvis_test_workspace\\destination\\test_document.txt",
  "dest_exists": true,
  "dest_size": 384,
  "sizes_match": true,
  "content_matches": true
}
```

---

### 3. Scenario 04: Copy Folder (F: to E: drive) [PASS]

- **Status:** PASS
- **Timestamp:** 2026-02-24T23:34:08.626895
- **Duration:** 22ms

**Proof Evidence:**

```json
{
  "source_folder": "F:\\jarvis_test_source_folder",
  "source_file_count": 6,
  "source_dir_count": 2,
  "dest_folder": "E:\\jarvis_test_workspace\\copied_from_f",
  "dest_exists": true,
  "dest_file_count": 6,
  "dest_dir_count": 2,
  "file_counts_match": true
}
```

---

### 4. Scenario 05: List Directory (E: drive) [PASS]

- **Status:** PASS
- **Timestamp:** 2026-02-24T23:34:08.653364
- **Duration:** 23ms

**Proof Evidence:**

```json
{
  "path": "E:\\\\",
  "item_count": 63,
  "items_sample": [
    {
      "name": "!qhlogs.doc",
      "is_dir": false,
      "size_bytes": 22528,
      "modified": "2019-11-18T13:35:44"
    },
    {
      "name": "$RECYCLE.BIN",
      "is_dir": true,
      "size_bytes": 0,
      "modified": "2025-05-31T23:19:55.763581"
    },
    {
      "name": "1917.2019.1080p.BluRay.x264-WUTANG.srt",
      "is_dir": false,
      "size_bytes": 65370,
      "modified": "2020-12-03T13:55:11"
    },
    {
      "name": "1917.[2019].BRRip.XviD-BLiTZKRiEG.avi",
      "is_dir": false,
      "size_bytes": 1296654336,
      "modified": "2020-12-01T11:59:15"
    },
    {
      "name": "2021-01-28 09-45-25.mp4",
      "is_dir": false,
      "size_bytes": 218367644,
      "modified": "2021-01-28T10:53:52.201373"
    },
    {
      "name": "2021-01-28 11-05-54.mp4",
      "is_dir": false,
      "size_bytes": 357844700,
      "modified": "2021-01-28T13:14:50.717721"
    },
    {
      "name": "2021-01-28 14-16-04.mp4",
      "is_dir": false,
      "size_bytes": 274791488,
      "modified": "2021-01-28T15:47:52.421370"
    },
    {
      "name": "2021-01-28 16-06-44.mp4",
      "is_dir": false,
      "size_bytes": 272807404,
      "modified": "2021-01-28T17:37:34.490618"
    },
    {
      "name": "2021-01-29 09-38-42.mp4",
      "is_dir": false,
      "size_bytes": 294191132,
      "modified": "2021-01-29T11:02:35.326942"
    },
    {
      "name": "2021-01-29 11-12-50.mp4",
      "is_dir": false,
      "size_bytes": 396074597,
      "modified": "2021-01-29T13:22:45.353113"
    }
  ],
  "known_folders_found": [
    "bionic ai",
    "jarvis_test_workspace"
  ]
}
```

---

### 5. Scenario 06: Open File Explorer (E: drive) [PASS]

- **Status:** PASS
- **Timestamp:** 2026-02-24T23:34:13.007470
- **Duration:** 4353ms

**Proof Evidence:**

```json
{
  "explorer_opened": true,
  "explorer_running": true,
  "screenshot": "E:\\jarvis_test_workspace\\screenshots\\proof_06_explorer_opened.png"
}
```

---

### 6. Scenario 07: RAG Agent Parse + Execute [PASS]

- **Status:** PASS
- **Timestamp:** 2026-02-24T23:34:19.698328
- **Duration:** 5382ms

**Proof Evidence:**

```json
{
  "commands_tested": 4,
  "sub_results": [
    {
      "command": "open notepad",
      "parsed": true,
      "steps": 1,
      "confidence": 0.95,
      "executed": true,
      "steps_succeeded": 1,
      "steps_total": 1
    },
    {
      "command": "take a screenshot",
      "parsed": true,
      "steps": 1,
      "confidence": 0.99,
      "executed": true,
      "steps_succeeded": 1,
      "steps_total": 1
    },
    {
      "command": "create file E:\\jarvis_test_workspace\\rag_test_output.txt with content Hello from JARVIS AI RAG Agent",
      "parsed": true,
      "steps": 1,
      "confidence": 0.93,
      "executed": true,
      "steps_succeeded": 1,
      "steps_total": 1
    },
    {
      "command": "list E:\\jarvis_test_workspace",
      "parsed": true,
      "steps": 1,
      "confidence": 0.88,
      "executed": true,
      "steps_succeeded": 1,
      "steps_total": 1
    }
  ]
}
```

---

### 7. Scenario 08: End-to-End Complex Workflow [PASS]

- **Status:** PASS
- **Timestamp:** 2026-02-24T23:34:19.916946
- **Duration:** 218ms

**Proof Evidence:**

```json
{
  "files_created": 3,
  "directory_listed": true,
  "screenshot_taken": true,
  "screenshot_path": "E:\\jarvis_test_workspace\\screenshots\\proof_08_e2e.png",
  "folder_copied": true,
  "source_file_count": 3,
  "dest_file_count": 3,
  "counts_match": true,
  "content_integrity": true
}
```

---

### 8. Scenario 09: Move File [PASS]

- **Status:** PASS
- **Timestamp:** 2026-02-24T23:34:19.919944
- **Duration:** 3ms

**Proof Evidence:**

```json
{
  "source": "E:\\jarvis_test_workspace\\move_source\\moveme.txt",
  "destination": "E:\\jarvis_test_workspace\\move_dest\\moveme.txt",
  "source_removed": true,
  "dest_exists": true,
  "source_size": 1900,
  "dest_size": 1900,
  "size_preserved": true
}
```

---

### 9. Scenario 10: Delete File [PASS]

- **Status:** PASS
- **Timestamp:** 2026-02-24T23:34:19.921944
- **Duration:** 2ms

**Proof Evidence:**

```json
{
  "filepath": "E:\\jarvis_test_workspace\\delete_me.txt",
  "existed_before_delete": true,
  "exists_after_delete": false,
  "successfully_deleted": true
}
```

---

### 10. Scenario 11: Process Check [PASS]

- **Status:** PASS
- **Timestamp:** 2026-02-24T23:34:22.605729
- **Duration:** 2683ms

**Proof Evidence:**

```json
{
  "processes_checked": {
    "explorer": {
      "running": true,
      "instances": 3
    },
    "chrome": {
      "running": true,
      "instances": 27
    },
    "python": {
      "running": true,
      "instances": 3
    },
    "svchost": {
      "running": true,
      "instances": 91
    }
  }
}
```

---

### 11. Scenario 12: Open + Close Application (Notepad) [PASS]

- **Status:** PASS
- **Timestamp:** 2026-02-24T23:34:28.921967
- **Duration:** 6316ms

**Proof Evidence:**

```json
{
  "opened": true,
  "pid": 6488,
  "running_after_open": true,
  "closed": true,
  "running_after_close": false,
  "lifecycle_complete": true
}
```

---

### 12. Scenario 01: Open Chrome [PASS]

- **Status:** PASS
- **Timestamp:** 2026-02-24T23:34:32.802660
- **Duration:** 3881ms

**Proof Evidence:**

```json
{
  "pid": 16000,
  "exe_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "chrome_running": true,
  "chrome_instances": 28,
  "screenshot": "E:\\jarvis_test_workspace\\screenshots\\proof_01_chrome_opened.png",
  "screenshot_size": 127594
}
```

---

## Screenshots Captured

- `proof_01_chrome_opened.png` (127,594 bytes)
- `proof_02_screenshot.png` (100,662 bytes)
- `proof_06_explorer_opened.png` (126,609 bytes)
- `proof_08_e2e.png` (129,692 bytes)
- `proof_12_notepad_open.png` (127,993 bytes)

## Desktop Automation Audit Trail

Total actions logged: 35

```json
[
  {
    "timestamp": "2026-02-24T23:34:19.701328",
    "action": "create_file",
    "parameters": {
      "filepath": "E:\\jarvis_test_workspace\\e2e_test\\notes.md",
      "content_length": 61
    },
    "result": {
      "success": true,
      "filepath": "E:\\jarvis_test_workspace\\e2e_test\\notes.md",
      "size_bytes": 65,
      "content_length": 61,
      "duration_ms": 0.93
    }
  },
  {
    "timestamp": "2026-02-24T23:34:19.702327",
    "action": "list_directory",
    "parameters": {
      "path": "E:\\jarvis_test_workspace\\e2e_test"
    },
    "result": {
      "success": true,
      "path": "E:\\jarvis_test_workspace\\e2e_test",
      "item_count": 3,
      "items": [
        {
          "name": "data.csv",
          "is_dir": false,
          "size_bytes": 56,
          "modified": "2026-02-24T23:34:19.700329"
        },
        {
          "name": "notes.md",
          "is_dir": false,
          "size_bytes": 65,
          "modified": "2026-02-24T23:34:19.701329"
        },
        {
          "name": "report.txt",
          "is_dir": false,
          "size_bytes": 57,
          "modified": "2026-02-24T23:34:19.699329"
        }
      ],
      "duration_ms": 0.84
    }
  },
  {
    "timestamp": "2026-02-24T23:34:19.873950",
    "action": "take_screenshot",
    "parameters": {
      "filename": "proof_08_e2e.png"
    },
    "result": {
      "success": true,
      "filepath": "E:\\jarvis_test_workspace\\screenshots\\proof_08_e2e.png",
      "filename": "proof_08_e2e.png",
      "width": 1920,
      "height": 1080,
      "file_size_bytes": 129692,
      "duration_ms": 170.42
    }
  },
  {
    "timestamp": "2026-02-24T23:34:19.878949",
    "action": "copy_folder",
    "parameters": {
      "source": "E:\\jarvis_test_workspace\\e2e_test",
      "destination": "E:\\jarvis_test_workspace\\e2e_copy"
    },
    "result": {
      "success": true,
      "source": "E:\\jarvis_test_workspace\\e2e_test",
      "destination": "E:\\jarvis_test_workspace\\e2e_copy",
      "source_file_count": 3,
      "destination_file_count": 3,
      "duration_ms": 4.64
    }
  },
  {
    "timestamp": "2026-02-24T23:34:19.917945",
    "action": "create_file",
    "parameters": {
      "filepath": "E:\\jarvis_test_workspace\\move_source\\moveme.txt",
      "content_length": 1850
    },
    "result": {
      "success": true,
      "filepath": "E:\\jarvis_test_workspace\\move_source\\moveme.txt",
      "size_bytes": 1900,
      "content_length": 1850,
      "duration_ms": 0.94
    }
  },
  {
    "timestamp": "2026-02-24T23:34:19.918945",
    "action": "move_file",
    "parameters": {
      "source": "E:\\jarvis_test_workspace\\move_source\\moveme.txt",
      "destination": "E:\\jarvis_test_workspace\\move_dest\\moveme.txt"
    },
    "result": {
      "success": true,
      "source": "E:\\jarvis_test_workspace\\move_source\\moveme.txt",
      "destination": "E:\\jarvis_test_workspace\\move_dest\\moveme.txt",
      "source_removed": true,
      "destination_exists": true,
      "duration_ms": 0.94
    }
  },
  {
    "timestamp": "2026-02-24T23:34:19.920945",
    "action": "create_file",
    "parameters": {
      "filepath": "E:\\jarvis_test_workspace\\delete_me.txt",
      "content_length": 27
    },
    "result": {
      "success": true,
      "filepath": "E:\\jarvis_test_workspace\\delete_me.txt",
      "size_bytes": 28,
      "content_length": 27,
      "duration_ms": 0.75
    }
  },
  {
    "timestamp": "2026-02-24T23:34:19.921944",
    "action": "delete_file",
    "parameters": {
      "filepath": "E:\\jarvis_test_workspace\\delete_me.txt"
    },
    "result": {
      "success": true,
      "filepath": "E:\\jarvis_test_workspace\\delete_me.txt",
      "deleted": true,
      "duration_ms": 0.45
    }
  },
  {
    "timestamp": "2026-02-24T23:34:20.601357",
    "action": "is_process_running",
    "parameters": {
      "process_name": "explorer"
    },
    "result": {
      "success": true,
      "process_name": "explorer",
      "is_running": true,
      "instances": [
        {
          "pid": 4368,
          "name": "explorer.exe"
        },
        {
          "pid": 10276,
          "name": "explorer.exe"
        },
        {
          "pid": 13600,
          "name": "explorer.exe"
        }
      ],
      "instance_count": 3,
      "duration_ms": 678.3
    }
  },
  {
    "timestamp": "2026-02-24T23:34:21.263346",
    "action": "is_process_running",
    "parameters": {
      "process_name": "chrome"
    },
    "result": {
      "success": true,
      "process_name": "chrome",
      "is_running": true,
      "instances": [
        {
          "pid": 1732,
          "name": "chrome.exe"
        },
        {
          "pid": 1752,
          "name": "chrome.exe"
        },
        {
          "pid": 1896,
          "name": "chrome.exe"
        },
        {
          "pid": 2036,
          "name": "chrome.exe"
        },
        {
          "pid": 2608,
          "name": "chrome.exe"
        },
        {
          "pid": 2680,
          "name": "chrome.exe"
        },
        {
          "pid": 2720,
          "name": "chrome.exe"
        },
        {
          "pid": 3040,
          "name": "chrome.exe"
        },
        {
          "pid": 6880,
          "name": "chrome.exe"
        },
        {
          "pid": 7344,
          "name": "chrome.exe"
        },
        {
          "pid": 8596,
          "name": "chrome.exe"
        },
        {
          "pid": 9424,
          "name": "chrome.exe"
        },
        {
          "pid": 9724,
          "name": "chrome.exe"
        },
        {
          "pid": 10912,
          "name": "chrome.exe"
        },
        {
          "pid": 11980,
          "name": "chrome.exe"
        },
        {
          "pid": 13320,
          "name": "chrome.exe"
        },
        {
          "pid": 13484,
          "name": "chrome.exe"
        },
        {
          "pid": 14556,
          "name": "chrome.exe"
        },
        {
          "pid": 14800,
          "name": "chrome.exe"
        },
        {
          "pid": 14952,
          "name": "chrome.exe"
        },
        {
          "pid": 15000,
          "name": "chrome.exe"
        },
        {
          "pid": 16612,
          "name": "chrome.exe"
        },
        {
          "pid": 16676,
          "name": "chrome.exe"
        },
        {
          "pid": 17548,
          "name": "chrome.exe"
        },
        {
          "pid": 18672,
          "name": "chrome.exe"
        },
        {
          "pid": 18736,
          "name": "chrome.exe"
        },
        {
          "pid": 19592,
          "name": "chrome.exe"
        }
      ],
      "instance_count": 27,
      "duration_ms": 662.36
    }
  },
  {
    "timestamp": "2026-02-24T23:34:21.937647",
    "action": "is_process_running",
    "parameters": {
      "process_name": "python"
    },
    "result": {
      "success": true,
      "process_name": "python",
      "is_running": true,
      "instances": [
        {
          "pid": 6372,
          "name": "python.exe"
        },
        {
          "pid": 7540,
          "name": "python.exe"
        },
        {
          "pid": 15896,
          "name": "python.exe"
        }
      ],
      "instance_count": 3,
      "duration_ms": 673.39
    }
  },
  {
    "timestamp": "2026-02-24T23:34:22.605729",
    "action": "is_process_running",
    "parameters": {
      "process_name": "svchost"
    },
    "result": {
      "success": true,
      "process_name": "svchost",
      "is_running": true,
      "instances": [
        {
          "pid": 1352,
          "name": "svchost.exe"
        },
        {
          "pid": 1480,
          "name": "svchost.exe"
        },
        {
          "pid": 1644,
          "name": "svchost.exe"
        },
        {
          "pid": 1692,
          "name": "svchost.exe"
        },
        {
          "pid": 1768,
          "name": "svchost.exe"
        },
        {
          "pid": 1860,
          "name": "svchost.exe"
        },
        {
          "pid": 1928,
          "name": "svchost.exe"
        },
        {
          "pid": 1944,
          "name": "svchost.exe"
        },
        {
          "pid": 1964,
          "name": "svchost.exe"
        },
        {
          "pid": 2056,
          "name": "svchost.exe"
        },
        {
          "pid": 2064,
          "name": "svchost.exe"
        },
        {
          "pid": 2208,
          "name": "svchost.exe"
        },
        {
          "pid": 2244,
          "name": "svchost.exe"
        },
        {
          "pid": 2284,
          "name": "svchost.exe"
        },
        {
          "pid": 2320,
          "name": "svchost.exe"
        },
        {
          "pid": 2380,
          "name": "svchost.exe"
        },
        {
          "pid": 2428,
          "name": "svchost.exe"
        },
        {
          "pid": 2628,
          "name": "svchost.exe"
        },
        {
          "pid": 2636,
          "name": "svchost.exe"
        },
        {
          "pid": 2668,
          "name": "svchost.exe"
        },
        {
          "pid": 2852,
          "name": "svchost.exe"
        },
        {
          "pid": 2880,
          "name": "svchost.exe"
        },
        {
          "pid": 2992,
          "name": "svchost.exe"
        },
        {
          "pid": 3088,
          "name": "svchost.exe"
        },
        {
          "pid": 3280,
          "name": "svchost.exe"
        },
        {
          "pid": 3392,
          "name": "svchost.exe"
        },
        {
          "pid": 3400,
          "name": "svchost.exe"
        },
        {
          "pid": 3464,
          "name": "svchost.exe"
        },
        {
          "pid": 3472,
          "name": "svchost.exe"
        },
        {
          "pid": 3480,
          "name": "svchost.exe"
        },
        {
          "pid": 3628,
          "name": "svchost.exe"
        },
        {
          "pid": 3676,
          "name": "svchost.exe"
        },
        {
          "pid": 3712,
          "name": "svchost.exe"
        },
        {
          "pid": 3744,
          "name": "svchost.exe"
        },
        {
          "pid": 3752,
          "name": "svchost.exe"
        },
        {
          "pid": 4028,
          "name": "svchost.exe"
        },
        {
          "pid": 4252,
          "name": "svchost.exe"
        },
        {
          "pid": 4840,
          "name": "svchost.exe"
        },
        {
          "pid": 4936,
          "name": "svchost.exe"
        },
        {
          "pid": 5004,
          "name": "svchost.exe"
        },
        {
          "pid": 5036,
          "name": "svchost.exe"
        },
        {
          "pid": 5164,
          "name": "svchost.exe"
        },
        {
          "pid": 5172,
          "name": "svchost.exe"
        },
        {
          "pid": 5196,
          "name": "svchost.exe"
        },
        {
          "pid": 5304,
          "name": "svchost.exe"
        },
        {
          "pid": 5364,
          "name": "svchost.exe"
        },
        {
          "pid": 5408,
          "name": "svchost.exe"
        },
        {
          "pid": 5444,
          "name": "svchost.exe"
        },
        {
          "pid": 5524,
          "name": "svchost.exe"
        },
        {
          "pid": 5552,
          "name": "svchost.exe"
        },
        {
          "pid": 5788,
          "name": "svchost.exe"
        },
        {
          "pid": 5800,
          "name": "svchost.exe"
        },
        {
          "pid": 5892,
          "name": "svchost.exe"
        },
        {
          "pid": 5908,
          "name": "svchost.exe"
        },
        {
          "pid": 5956,
          "name": "svchost.exe"
        },
        {
          "pid": 5968,
          "name": "svchost.exe"
        },
        {
          "pid": 6044,
          "name": "svchost.exe"
        },
        {
          "pid": 6052,
          "name": "svchost.exe"
        },
        {
          "pid": 7368,
          "name": "svchost.exe"
        },
        {
          "pid": 9060,
          "name": "svchost.exe"
        },
        {
          "pid": 9088,
          "name": "svchost.exe"
        },
        {
          "pid": 9228,
          "name": "svchost.exe"
        },
        {
          "pid": 9252,
          "name": "svchost.exe"
        },
        {
          "pid": 9336,
          "name": "svchost.exe"
        },
        {
          "pid": 9388,
          "name": "svchost.exe"
        },
        {
          "pid": 9400,
          "name": "svchost.exe"
        },
        {
          "pid": 9552,
          "name": "svchost.exe"
        },
        {
          "pid": 9716,
          "name": "svchost.exe"
        },
        {
          "pid": 9732,
          "name": "svchost.exe"
        },
        {
          "pid": 10064,
          "name": "svchost.exe"
        },
        {
          "pid": 10528,
          "name": "svchost.exe"
        },
        {
          "pid": 10596,
          "name": "svchost.exe"
        },
        {
          "pid": 10732,
          "name": "svchost.exe"
        },
        {
          "pid": 10900,
          "name": "svchost.exe"
        },
        {
          "pid": 11100,
          "name": "svchost.exe"
        },
        {
          "pid": 11160,
          "name": "svchost.exe"
        },
        {
          "pid": 11340,
          "name": "svchost.exe"
        },
        {
          "pid": 11760,
          "name": "svchost.exe"
        },
        {
          "pid": 11864,
          "name": "svchost.exe"
        },
        {
          "pid": 12528,
          "name": "svchost.exe"
        },
        {
          "pid": 13224,
          "name": "svchost.exe"
        },
        {
          "pid": 14200,
          "name": "svchost.exe"
        },
        {
          "pid": 14500,
          "name": "svchost.exe"
        },
        {
          "pid": 16992,
          "name": "svchost.exe"
        },
        {
          "pid": 17368,
          "name": "svchost.exe"
        },
        {
          "pid": 17912,
          "name": "svchost.exe"
        },
        {
          "pid": 17992,
          "name": "svchost.exe"
        },
        {
          "pid": 18032,
          "name": "svchost.exe"
        },
        {
          "pid": 18232,
          "name": "svchost.exe"
        },
        {
          "pid": 19908,
          "name": "svchost.exe"
        },
        {
          "pid": 20772,
          "name": "svchost.exe"
        }
      ],
      "instance_count": 91,
      "duration_ms": 668.02
    }
  },
  {
    "timestamp": "2026-02-24T23:34:23.657346",
    "action": "open_application",
    "parameters": {
      "app_name": "notepad",
      "args": null
    },
    "result": {
      "success": true,
      "pid": 6488,
      "exe_path": "notepad.exe",
      "duration_ms": 1050.74
    }
  },
  {
    "timestamp": "2026-02-24T23:34:25.826452",
    "action": "is_process_running",
    "parameters": {
      "process_name": "notepad"
    },
    "result": {
      "success": true,
      "process_name": "notepad",
      "is_running": true,
      "instances": [
        {
          "pid": 6684,
          "name": "Notepad.exe"
        }
      ],
      "instance_count": 1,
      "duration_ms": 663.9
    }
  },
  {
    "timestamp": "2026-02-24T23:34:25.998959",
    "action": "take_screenshot",
    "parameters": {
      "filename": "proof_12_notepad_open.png"
    },
    "result": {
      "success": true,
      "filepath": "E:\\jarvis_test_workspace\\screenshots\\proof_12_notepad_open.png",
      "filename": "proof_12_notepad_open.png",
      "width": 1920,
      "height": 1080,
      "file_size_bytes": 127993,
      "duration_ms": 171.95
    }
  },
  {
    "timestamp": "2026-02-24T23:34:26.711452",
    "action": "close_application",
    "parameters": {
      "process_name": "notepad"
    },
    "result": {
      "success": true,
      "process_name": "notepad",
      "terminated_count": 1,
      "errors": null,
      "duration_ms": 711.79
    }
  },
  {
    "timestamp": "2026-02-24T23:34:28.921967",
    "action": "is_process_running",
    "parameters": {
      "process_name": "notepad"
    },
    "result": {
      "success": true,
      "process_name": "notepad",
      "is_running": false,
      "instances": [],
      "instance_count": 0,
      "duration_ms": 705.23
    }
  },
  {
    "timestamp": "2026-02-24T23:34:29.935510",
    "action": "open_application",
    "parameters": {
      "app_name": "chrome",
      "args": null
    },
    "result": {
      "success": true,
      "pid": 16000,
      "exe_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
      "duration_ms": 1012.46
    }
  },
  {
    "timestamp": "2026-02-24T23:34:32.625947",
    "action": "is_process_running",
    "parameters": {
      "process_name": "chrome"
    },
    "result": {
      "success": true,
      "process_name": "chrome",
      "is_running": true,
      "instances": [
        {
          "pid": 1732,
          "name": "chrome.exe"
        },
        {
          "pid": 1752,
          "name": "chrome.exe"
        },
        {
          "pid": 1896,
          "name": "chrome.exe"
        },
        {
          "pid": 2036,
          "name": "chrome.exe"
        },
        {
          "pid": 2608,
          "name": "chrome.exe"
        },
        {
          "pid": 2680,
          "name": "chrome.exe"
        },
        {
          "pid": 2720,
          "name": "chrome.exe"
        },
        {
          "pid": 3040,
          "name": "chrome.exe"
        },
        {
          "pid": 4448,
          "name": "chrome.exe"
        },
        {
          "pid": 6512,
          "name": "chrome.exe"
        },
        {
          "pid": 6880,
          "name": "chrome.exe"
        },
        {
          "pid": 7344,
          "name": "chrome.exe"
        },
        {
          "pid": 8596,
          "name": "chrome.exe"
        },
        {
          "pid": 9424,
          "name": "chrome.exe"
        },
        {
          "pid": 9724,
          "name": "chrome.exe"
        },
        {
          "pid": 10912,
          "name": "chrome.exe"
        },
        {
          "pid": 11980,
          "name": "chrome.exe"
        },
        {
          "pid": 13320,
          "name": "chrome.exe"
        },
        {
          "pid": 13484,
          "name": "chrome.exe"
        },
        {
          "pid": 14556,
          "name": "chrome.exe"
        },
        {
          "pid": 14800,
          "name": "chrome.exe"
        },
        {
          "pid": 14952,
          "name": "chrome.exe"
        },
        {
          "pid": 15000,
          "name": "chrome.exe"
        },
        {
          "pid": 16612,
          "name": "chrome.exe"
        },
        {
          "pid": 16676,
          "name": "chrome.exe"
        },
        {
          "pid": 17548,
          "name": "chrome.exe"
        },
        {
          "pid": 18672,
          "name": "chrome.exe"
        },
        {
          "pid": 19592,
          "name": "chrome.exe"
        }
      ],
      "instance_count": 28,
      "duration_ms": 685.41
    }
  },
  {
    "timestamp": "2026-02-24T23:34:32.802660",
    "action": "take_screenshot",
    "parameters": {
      "filename": "proof_01_chrome_opened.png"
    },
    "result": {
      "success": true,
      "filepath": "E:\\jarvis_test_workspace\\screenshots\\proof_01_chrome_opened.png",
      "filename": "proof_01_chrome_opened.png",
      "width": 1920,
      "height": 1080,
      "file_size_bytes": 127594,
      "duration_ms": 175.85
    }
  }
]
```

---

*This document was auto-generated by JARVIS AI Test Suite. All tests executed REAL desktop actions — no mocks, no fakes.*