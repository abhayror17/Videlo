"""
Nano Banana Prompt API Client
For image generation using nanobananaprompt.club
"""
import aiohttp
import socket
import json
import base64
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class NanoBananaModel(str, Enum):
    NANO_BANANA_2 = "nano-banana-2"
    NANO_BANANA_PRO = "nano-banana-pro"


class AspectRatio(str, Enum):
    SQUARE = "1:1"
    LANDSCAPE_16_9 = "16:9"
    PORTRAIT_9_16 = "9:16"
    PORTRAIT_3_4 = "3:4"
    LANDSCAPE_4_3 = "4:3"


@dataclass
class GenerationResult:
    success: bool
    task_id: Optional[str] = None
    status: Optional[str] = None
    image_urls: List[str] = None
    error: Optional[str] = None
    guest_usage_used: int = 0
    guest_usage_remaining: int = 3

    def __post_init__(self):
        if self.image_urls is None:
            self.image_urls = []


class NanoBananaClient:
    """Client for Nano Banana Prompt image generation API."""
    
    BASE_URL = "https://nanobananaprompt.club"
    UGUU_URL = "https://uguu.se/upload"
    MAX_IMAGES = 9
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=120)
    
    def _create_connector(self) -> aiohttp.TCPConnector:
        """Create an aiohttp connector forced to IPv4."""
        return aiohttp.TCPConnector(
            family=socket.AF_INET,
            ssl=False,
            limit=10
        )
    
    async def upload_to_uguu(self, image_data: str) -> Optional[str]:
        """
        Upload a base64 image to uguu.se temporary file host.
        
        Args:
            image_data: Base64 encoded image (with or without data URI prefix)
        
        Returns:
            URL of uploaded image or None on failure
        """
        try:
            # Handle data URI
            if image_data.startswith('data:'):
                # Extract base64 part
                header, base64_part = image_data.split(',', 1)
                # Extract mime type for extension
                mime = header.split(':')[1].split(';')[0]
                ext = mime.split('/')[-1] if '/' in mime else 'png'
                ext = 'jpg' if ext == 'jpeg' else ext
            else:
                base64_part = image_data
                ext = 'png'
            
            # Decode base64
            image_bytes = base64.b64decode(base64_part)
            
            # Check size
            if len(image_bytes) > self.MAX_IMAGE_SIZE:
                print(f"[NanoBanana] Image too large: {len(image_bytes)} bytes")
                return None
            
            # Upload to uguu.se
            async with aiohttp.ClientSession(
                connector=self._create_connector(),
                timeout=aiohttp.ClientTimeout(total=60)
            ) as session:
                # Create multipart form
                form = aiohttp.FormData()
                form.add_field(
                    'files[]',
                    image_bytes,
                    filename=f'image.{ext}',
                    content_type=f'image/{ext}'
                )
                
                async with session.post(self.UGUU_URL, data=form) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success') and data.get('files'):
                            url = data['files'][0].get('url')
                            print(f"[NanoBanana] Uploaded to uguu.se: {url}")
                            return url
                    else:
                        text = await response.text()
                        print(f"[NanoBanana] Upload failed: {response.status} - {text}")
                        return None
                        
        except Exception as e:
            print(f"[NanoBanana] Upload error: {e}")
            return None
    
    async def upload_images(self, images: List[str]) -> List[str]:
        """
        Upload multiple base64 images to uguu.se.
        
        Args:
            images: List of base64 encoded images (up to 9)
        
        Returns:
            List of uploaded URLs
        """
        import asyncio
        
        if not images:
            return []
        
        # Limit to MAX_IMAGES
        images = images[:self.MAX_IMAGES]
        
        # Upload in parallel
        tasks = [self.upload_to_uguu(img) for img in images]
        results = await asyncio.gather(*tasks)
        
        # Filter out failures
        urls = [url for url in results if url]
        return urls
    
    async def generate_image(
        self,
        prompt: str,
        model: NanoBananaModel = NanoBananaModel.NANO_BANANA_2,
        aspect_ratio: AspectRatio = AspectRatio.SQUARE,
        reference_images: Optional[List[str]] = None,
        bypass_guest_limit: bool = True
    ) -> GenerationResult:
        """
        Generate an image from a prompt.
        
        Args:
            prompt: The text prompt describing the image
            model: Model to use (nano-banana-2 or nano-banana-pro)
            aspect_ratio: Output aspect ratio
            reference_images: Optional list of reference images (URLs or base64 data URIs)
            bypass_guest_limit: Set to True to bypass 3-generation guest limit
        
        Returns:
            GenerationResult with task_id and status
        """
        # Upload base64 images to uguu.se if needed
        uploaded_urls = []
        if reference_images:
            for img in reference_images:
                if img.startswith('data:'):
                    # It's base64, upload it
                    url = await self.upload_to_uguu(img)
                    if url:
                        uploaded_urls.append(url)
                    else:
                        return GenerationResult(
                            success=False,
                            error="Failed to upload reference image"
                        )
                else:
                    # It's already a URL
                    uploaded_urls.append(img)
        
        scene = "image-to-image" if uploaded_urls else "text-to-image"
        
        payload = {
            "mediaType": "image",
            "scene": scene,
            "provider": "kie",
            "model": model.value,
            "prompt": prompt,
            "options": {
                "aspect_ratio": aspect_ratio.value
            }
        }
        
        if uploaded_urls:
            payload["options"]["image_input"] = uploaded_urls
        
        cookies = {}
        if bypass_guest_limit:
            cookies["nbp_guest_image_generations_used"] = "0"
        
        try:
            async with aiohttp.ClientSession(
                connector=self._create_connector(),
                timeout=self.timeout,
                cookies=cookies
            ) as session:
                async with session.post(
                    f"{self.BASE_URL}/api/ai/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    data = await response.json()
                    
                    print(f"[NanoBanana] Generate response: {json.dumps(data, indent=2)}")
                    
                    if data.get("code") != 0:
                        return GenerationResult(
                            success=False,
                            error=data.get("message", "Generation failed")
                        )
                    
                    result_data = data.get("data", {})
                    return GenerationResult(
                        success=True,
                        task_id=result_data.get("id"),
                        status=result_data.get("status"),
                        guest_usage_used=result_data.get("guestUsageUsed", 0),
                        guest_usage_remaining=result_data.get("guestUsageRemaining", 3)
                    )
                    
        except Exception as e:
            print(f"[NanoBanana] Generate error: {e}")
            return GenerationResult(
                success=False,
                error=str(e)
            )
    
    async def query_task(
        self,
        task_id: str,
        prompt: str = "",
        bypass_guest_limit: bool = True
    ) -> GenerationResult:
        """
        Query the status of a generation task.
        
        Args:
            task_id: The task ID returned from generate_image
            prompt: The original prompt (required by API)
            bypass_guest_limit: Set to True to bypass guest limit
        
        Returns:
            GenerationResult with status and image URLs if complete
        """
        cookies = {}
        if bypass_guest_limit:
            cookies["nbp_guest_image_generations_used"] = "0"
        
        try:
            async with aiohttp.ClientSession(
                connector=self._create_connector(),
                timeout=self.timeout,
                cookies=cookies
            ) as session:
                async with session.post(
                    f"{self.BASE_URL}/api/ai/query",
                    json={"taskId": task_id, "prompt": prompt},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    data = await response.json()
                    
                    print(f"[NanoBanana] Query response: {json.dumps(data, indent=2)}")
                    
                    if data.get("code") != 0:
                        return GenerationResult(
                            success=False,
                            error=data.get("message", "Query failed")
                        )
                    
                    result_data = data.get("data", {})
                    status = result_data.get("status")
                    
                    # Parse image URLs from nested JSON structure
                    image_urls = []
                    
                    # Parse taskResult JSON string
                    task_result = result_data.get("taskResult", "{}")
                    if isinstance(task_result, str):
                        try:
                            task_result = json.loads(task_result)
                        except:
                            task_result = {}
                    
                    # Parse resultJson from taskResult
                    result_json = task_result.get("resultJson", "")
                    if result_json:
                        try:
                            result_obj = json.loads(result_json)
                            # Get resultUrls array
                            urls = result_obj.get("resultUrls", [])
                            if urls:
                                image_urls = urls if isinstance(urls, list) else [urls]
                        except:
                            pass
                    
                    # Fallback: check other fields
                    if not image_urls:
                        if result_data.get("output_images"):
                            output_images = result_data["output_images"]
                            image_urls = output_images if isinstance(output_images, list) else [output_images]
                        elif result_data.get("output"):
                            output = result_data["output"]
                            image_urls = output if isinstance(output, list) else [output]
                    
                    print(f"[NanoBanana] Status: {status}, Images: {image_urls}")
                    
                    return GenerationResult(
                        success=True,
                        task_id=task_id,
                        status=status,
                        image_urls=image_urls
                    )
                    
        except Exception as e:
            print(f"[NanoBanana] Query error: {e}")
            return GenerationResult(
                success=False,
                error=str(e)
            )
    
    async def generate_and_wait(
        self,
        prompt: str,
        model: NanoBananaModel = NanoBananaModel.NANO_BANANA_2,
        aspect_ratio: AspectRatio = AspectRatio.SQUARE,
        reference_images: Optional[List[str]] = None,
        max_wait_seconds: int = 120,
        poll_interval: int = 5
    ) -> GenerationResult:
        """
        Generate an image and wait for completion.
        
        Args:
            prompt: The text prompt
            model: Model to use
            aspect_ratio: Output aspect ratio
            reference_images: Optional reference images for img2img
            max_wait_seconds: Maximum time to wait for completion
            poll_interval: Seconds between status checks
        
        Returns:
            GenerationResult with final status and image URLs
        """
        import asyncio
        
        # Start generation
        result = await self.generate_image(
            prompt=prompt,
            model=model,
            aspect_ratio=aspect_ratio,
            reference_images=reference_images
        )
        
        if not result.success:
            return result
        
        task_id = result.task_id
        elapsed = 0
        
        # Poll for completion
        while elapsed < max_wait_seconds:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            
            result = await self.query_task(task_id, prompt)
            
            if not result.success:
                return result
            
            if result.status == "success":
                return result
            
            if result.status == "failed":
                return GenerationResult(
                    success=False,
                    error="Generation failed"
                )
        
        return GenerationResult(
            success=False,
            error="Generation timed out"
        )


# Singleton client
_client: Optional[NanoBananaClient] = None


def get_nanobanana_client() -> NanoBananaClient:
    """Get the NanoBanana client singleton."""
    global _client
    if _client is None:
        _client = NanoBananaClient()
    return _client
