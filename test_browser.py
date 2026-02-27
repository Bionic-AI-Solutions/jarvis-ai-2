import asyncio
import httpx

async def test_browser():
    """Test explicit browser navigation"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Create session
        session_resp = await client.post(
            'http://localhost:9000/api/chats',
            json={'name': 'Browser Test'}
        )
        session_id = session_resp.json()['id']
        print(f'Session: {session_id}')
        
        # Test with explicit browser
        msg_resp = await client.post(
            f'http://localhost:9000/api/chats/{session_id}/messages',
            json={
                'content': 'Open firefox and navigate to gmail.com then draft an email to john@example.com',
                'role': 'user'
            }
        )
        result = msg_resp.json()
        print(f'\n→ Request: Open firefox and navigate to gmail.com then draft an email')
        print(f'← Response: {result["content"]}')

async def test_simple_app():
    """Test simple app opening"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        session_resp = await client.post(
            'http://localhost:9000/api/chats',
            json={'name': 'App Test'}
        )
        session_id = session_resp.json()['id']
        
        msg_resp = await client.post(
            f'http://localhost:9000/api/chats/{session_id}/messages',
            json={'content': 'Open notepad', 'role': 'user'}
        )
        result = msg_resp.json()
        print(f'\n→ Request: Open notepad')
        print(f'← Response: {result["content"]}')

if __name__ == '__main__':
    asyncio.run(test_browser())
    asyncio.run(test_simple_app())
