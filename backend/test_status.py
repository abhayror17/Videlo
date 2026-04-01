import asyncio
from app.services.deapi import get_deapi_client

async def test():
    client = get_deapi_client()
    # Check status of the last request
    result = await client.get_request_status('7358b8c4-2ab1-466f-981e-8aad437a0d58')
    print('Status result:', result)

asyncio.run(test())
