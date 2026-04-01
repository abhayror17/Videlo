import asyncio
import json
from app.services.deapi import DeAPIClient

async def test():
    client = DeAPIClient()
    
    # First, start a new generation
    result = await client.generate_text2img(
        prompt='A professional man, corporate headshot, studio lighting',
        model='Flux_2_Klein_4B_BF16',
        width=512,
        height=512
    )
    
    request_id = result['data']['request_id']
    print(f'Request ID: {request_id}')
    
    # Poll for completion
    for i in range(20):
        await asyncio.sleep(5)
        status = await client.get_request_status(request_id)
        data = status.get('data', {})
        print(f'Poll {i+1}: status={data.get("status")}, result_url={data.get("result_url")}')
        
        if data.get('status') == 'completed':
            print(f'COMPLETED! URL: {data["result_url"]}')
            break
        elif data.get('status') == 'failed':
            print(f'FAILED: {status}')
            break

asyncio.run(test())
