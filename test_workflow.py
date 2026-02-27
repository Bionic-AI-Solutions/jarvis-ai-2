import asyncio
import httpx
import json

async def test_screenshot():
    """Test screenshot workflow through agent pipeline"""
    print("Testing screenshot workflow...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Create a session
            session_resp = await client.post(
                'http://localhost:9000/api/chats',
                json={'name': 'Screenshot Test', 'description': 'Test screenshot workflow'}
            )
            session_id = session_resp.json()['id']
            print(f'✓ Created session: {session_id}')
            
            # Test: Take a screenshot
            print("\n→ Sending: 'Take a screenshot and tell me what you see'")
            msg_resp = await client.post(
                f'http://localhost:9000/api/chats/{session_id}/messages',
                json={'content': 'Take a screenshot and tell me what you see', 'role': 'user'}
            )
            result = msg_resp.json()
            print(f'✓ Response: {result["content"]}')
            
        except Exception as e:
            print(f"✗ Error: {e}")

async def test_gmail():
    """Test Gmail workflow"""
    print("\n\nTesting Gmail workflow...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Create a session
            session_resp = await client.post(
                'http://localhost:9000/api/chats',
                json={'name': 'Gmail Test', 'description': 'Test Gmail workflow'}
            )
            session_id = session_resp.json()['id']
            print(f'✓ Created session: {session_id}')
            
            # Test: Open Gmail
            print("\n→ Sending: 'Open Gmail and draft an email to john@example.com saying hello world'")
            msg_resp = await client.post(
                f'http://localhost:9000/api/chats/{session_id}/messages',
                json={'content': 'Open Gmail and draft an email to john@example.com saying hello world', 'role': 'user'}
            )
            result = msg_resp.json()
            print(f'✓ Response: {result["content"]}')
            
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == '__main__':
    asyncio.run(test_screenshot())
    asyncio.run(test_gmail())
