#!/usr/bin/env python3
"""Quick workflow verification"""
import requests
import json

BASE_URL = 'http://localhost:9000'

print('\n📋 Fetching all workflows...\n')
response = requests.get(f'{BASE_URL}/api/workflows', timeout=10)
workflows = response.json()

if isinstance(workflows, list):
    print(f'✅ Found {len(workflows)} workflows in database\n')
    for w in workflows:
        print(f'  📧 Workflow: {w.get("name", "Unknown")}')
        print(f'     ID: {w.get("id", "N/A")}')
        print(f'     Type: {w.get("trigger_type", "N/A")}')
        print(f'     Status: {w.get("is_active", "Unknown")}')
        if w.get("created_at"):
            print(f'     Created: {str(w.get("created_at"))[:19]}')
        print()
else:
    print('Unexpected response format')
    print(workflows)
