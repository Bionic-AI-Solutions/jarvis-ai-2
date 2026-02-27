import asyncio
import httpx

async def test_complex():
    """Test complex workflows using Chrome"""
    
    tests = [
        ("Open chrome and navigate to google.com", "Chrome + Google"),
        ("Open chrome and go to github.com", "Chrome + GitHub"),
        ("Open chrome and visit google.com then search for python", "Chrome + Search"),
    ]
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        for test_input, label in tests:
            print(f"\n{label}")
            print(f"  Request: {test_input}")
            
            try:
                # Create session
                session_resp = await client.post(
                    'http://localhost:9000/api/chats',
                    json={'name': f'Test {label}'}
                )
                session_id = session_resp.json()['id']
                
                # Send message with longer timeout
                msg_resp = await client.post(
                    f'http://localhost:9000/api/chats/{session_id}/messages',
                    json={'content': test_input, 'role': 'user'},
                    timeout=90.0
                )
                result = msg_resp.json()
                
                # Extract result
                content = result['content']
                print(f"  Response: {content[:120]}...")
                
            except asyncio.TimeoutError:
                print(f"  ERROR: Timeout after 90s")
            except Exception as e:
                print(f"  ERROR: {str(e)[:80]}")

if __name__ == '__main__':
    asyncio.run(test_complex())
