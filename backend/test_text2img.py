import asyncio
from app.services.deapi import get_deapi_client

async def test():
    client = get_deapi_client()
    print("Testing text2img API...")
    try:
        result = await client.generate_text2img(
            prompt='a beautiful sunset over the ocean',
            model='Flux_2_Klein_4B_BF16',
            width=512,
            height=512
        )
        print('Result:', result)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
