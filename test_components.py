import asyncio
import httpx

async def test_steps():
    """Test different workflows to understand which components are working"""
    
    tests = [
        ("Take a screenshot", "Screenshot"),
        ("Open notepad", "App Open"),
        ("Close notepad", "App Close"),
        ("Open calculator", "App Open 2"),
        ("Open edge", "Browser - Edge"),
        ("Open chrome", "Browser - Chrome"),
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for test_input, label in tests:
            try:
                # Create session
                session_resp = await client.post(
                    'http://localhost:9000/api/chats',
                    json={'name': f'Test {label}'}
                )
                session_id = session_resp.json()['id']
                
                # Send message
                msg_resp = await client.post(
                    f'http://localhost:9000/api/chats/{session_id}/messages',
                    json={'content': test_input, 'role': 'user'},
                    timeout=30.0
                )
                result = msg_resp.json()
                
                # Extract result
                content = result['content']
                status = "✓" if "Done" in content or "Completed" in content else "✗"
                print(f"{status} {label:20} | {test_input:30} | {content[:60]}...")
                
            except Exception as e:
                print(f"✗ {label:20} | {test_input:30} | ERROR: {str(e)[:40]}")

if __name__ == '__main__':
    asyncio.run(test_steps())
