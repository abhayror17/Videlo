import aiohttp
import json
import socket
import asyncio
from typing import Optional
from ..config import get_settings

settings = get_settings()


class DeAPIClient:
    def __init__(self):
        self.base_url = settings.deapi_base_url
        self.api_key = settings.deapi_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

    def _create_connector(self) -> aiohttp.TCPConnector:
        """Create an aiohttp connector forced to IPv4."""
        return aiohttp.TCPConnector(
            family=socket.AF_INET,  # Force IPv4
            ssl=False,
            limit=10
        )
    
    async def generate_text2img(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 768,
        model: str = "ZImageTurbo_INT8",
        guidance: float = 3.5,
        steps: int = 4,
        seed: int = -1,
        negative_prompt: Optional[str] = None
    ) -> dict:
        """Submit text-to-image generation request to deAPI."""
        payload = {
            "prompt": prompt,
            "model": model,
            "width": width,
            "height": height,
            "guidance": guidance,
            "steps": steps,
            "seed": seed
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/txt2img",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def generate_txt2video(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        model: str = "Ltx2_19B_Dist_FP8",
        guidance: float = 3.5,
        steps: int = 20,
        frames: int = 24,
        seed: int = -1,
        fps: int = 30
    ) -> dict:
        """Submit text-to-video generation request to deAPI."""
        payload = {
            "prompt": prompt,
            "model": model,
            "width": width,
            "height": height,
            "guidance": guidance,
            "steps": steps,
            "frames": frames,
            "seed": seed,
            "fps": fps
        }
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/txt2video",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def generate_img2video(
        self,
        first_frame_image: bytes,
        prompt: str,
        width: int = 512,
        height: int = 512,
        model: str = "Ltx2_19B_Dist_FP8",
        guidance: float = 3.5,
        steps: int = 20,
        frames: int = 24,
        seed: int = -1,
        fps: int = 30,
        last_frame_image: Optional[bytes] = None
    ) -> dict:
        """Submit image-to-video generation request to deAPI."""
        # Build multipart form data
        data = aiohttp.FormData()
        data.add_field('first_frame_image', first_frame_image, filename='first_frame.png', content_type='image/png')
        data.add_field('prompt', prompt)
        data.add_field('model', model)
        data.add_field('width', str(width))
        data.add_field('height', str(height))
        data.add_field('guidance', str(guidance))
        data.add_field('steps', str(steps))
        data.add_field('frames', str(frames))
        data.add_field('seed', str(seed))
        data.add_field('fps', str(fps))
        
        if last_frame_image:
            data.add_field('last_frame_image', last_frame_image, filename='last_frame.png', content_type='image/png')
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/img2video",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def get_request_status(self, request_id: str) -> dict:
        """Get the status of a request."""
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.get(
                f"{self.base_url}/api/v1/client/request-status/{request_id}"
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def check_balance(self) -> dict:
        """Check account balance."""
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.get(
                f"{self.base_url}/api/v1/client/balance"
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def list_models(self, inference_type: Optional[str] = None) -> dict:
        """List available models."""
        params = {}
        if inference_type:
            params["filter[inference_types]"] = inference_type
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.get(
                f"{self.base_url}/api/v1/client/models",
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()


# Singleton client
_client: Optional[DeAPIClient] = None


def get_deapi_client() -> DeAPIClient:
    global _client
    if _client is None:
        _client = DeAPIClient()
    return _client