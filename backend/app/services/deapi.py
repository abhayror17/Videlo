import aiohttp
import json
import socket
import asyncio
from typing import Optional, List, Union
from ..config import get_settings

settings = get_settings()


class DeAPIClient:
    def __init__(self, custom_api_key: Optional[str] = None):
        self.base_url = settings.deapi_base_url
        # Use custom API key if provided (BYOK), otherwise use server default
        self.api_key = custom_api_key or settings.deapi_api_key
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
    
    # ============================================================
    # TEXT-TO-IMAGE
    # ============================================================
    
    async def generate_text2img(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 768,
        model: str = "Flux_2_Klein_4B_BF16",
        guidance: float = 3.5,
        steps: int = 4,
        seed: int = -1,
        negative_prompt: Optional[str] = None,
        loras: Optional[List[str]] = None
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
        
        if loras:
            payload["loras"] = loras
        
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
        model: str = "Ltx2_3_22B_Dist_INT8",
        frames: int = 97,
        seed: int = -1,
        fps: int = 24
    ) -> dict:
        """
        Submit text-to-video generation request to deAPI.
        
        Note: Ltx2_3_22B_Dist_INT8 does NOT support steps or guidance.
        
        Args:
            prompt: Text prompt for video generation
            width: Output width (min 512, max 1024)
            height: Output height (min 512, max 1024)
            model: Model slug (default: Ltx2_3_22B_Dist_INT8)
            frames: Number of frames (min 49, max 241)
            seed: Random seed (-1 for random)
            fps: Frames per second (fixed at 24)
        """
        payload = {
            "prompt": prompt,
            "model": model,
            "width": max(512, width),
            "height": max(512, height),
            "frames": max(49, frames),
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
                if response.status != 200:
                    error_text = await response.text()
                    print(f"[txt2video] error response: {error_text}")
                    response.raise_for_status()
                return await response.json()
    
    async def generate_img2video(
        self,
        first_frame_image: bytes,
        prompt: str,
        width: int = 512,
        height: int = 512,
        model: str = "Ltx2_3_22B_Dist_INT8",
        frames: int = 97,
        seed: int = -1,
        fps: int = 24,
        last_frame_image: Optional[bytes] = None
    ) -> dict:
        """
        Submit image-to-video generation request to deAPI.
        
        Note: Ltx2_3_22B_Dist_INT8 does NOT support steps or guidance.
        
        Args:
            first_frame_image: Image bytes for first frame (required)
            prompt: Motion prompt for video generation
            width: Output width (min 512, max 1024)
            height: Output height (min 512, max 1024)
            model: Model slug (default: Ltx2_3_22B_Dist_INT8)
            frames: Number of frames (min 49, max 241)
            seed: Random seed (-1 for random)
            fps: Frames per second (fixed at 24)
            last_frame_image: Optional last frame image bytes
        """
        # Build multipart form data - NO steps or guidance for LTX-2.3
        data = aiohttp.FormData()
        data.add_field('first_frame_image', first_frame_image, filename='first_frame.png', content_type='image/png')
        data.add_field('prompt', prompt)
        data.add_field('model', model)
        data.add_field('width', str(width))
        data.add_field('height', str(height))
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
                if response.status != 200:
                    error_text = await response.text()
                    print(f"[img2video] error response: {error_text}")
                    response.raise_for_status()
                return await response.json()
    
    async def generate_img2img(
        self,
        image: bytes,
        prompt: str,
        model: str = "QwenImageEdit_Plus_NF4",
        guidance: float = 3.5,
        steps: int = 20,
        seed: int = -1,
        negative_prompt: Optional[str] = None,
        loras: Optional[List[str]] = None,
        image_filename: str = "image.png"
    ) -> dict:
        """Submit image-to-image transformation request to deAPI."""
        # Build multipart form data
        data = aiohttp.FormData()
        data.add_field('image', image, filename=image_filename, content_type='image/png')
        data.add_field('prompt', prompt)
        data.add_field('model', model)
        data.add_field('guidance', str(guidance))
        data.add_field('steps', str(steps))
        data.add_field('seed', str(seed))
        
        if negative_prompt:
            data.add_field('negative_prompt', negative_prompt)
        
        if loras:
            data.add_field('loras', json.dumps(loras))
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/img2img",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def generate_txt2audio(
        self,
        text: str,
        model: str = "Kokoro",
        voice: str = "af_sky",
        lang: str = "en-us",
        speed: float = 1.0,
        format: str = "flac",
        sample_rate: int = 24000,
        mode: str = "custom_voice",
        ref_audio: Optional[bytes] = None,
        ref_text: Optional[str] = None,
        instruct: Optional[str] = None
    ) -> dict:
        """Submit text-to-speech generation request to deAPI."""
        # Build multipart form data
        data = aiohttp.FormData()
        data.add_field('text', text)
        data.add_field('model', model)
        data.add_field('lang', lang)
        data.add_field('speed', str(speed))
        data.add_field('format', format)
        data.add_field('sample_rate', str(sample_rate))
        data.add_field('mode', mode)
        
        if mode == "custom_voice":
            data.add_field('voice', voice)
        elif mode == "voice_clone" and ref_audio:
            data.add_field('ref_audio', ref_audio, filename='ref_audio.mp3', content_type='audio/mpeg')
            if ref_text:
                data.add_field('ref_text', ref_text)
        elif mode == "voice_design" and instruct:
            data.add_field('instruct', instruct)
        else:
            data.add_field('voice', voice)  # Default fallback
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/txt2audio",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def generate_img2txt(
        self,
        image: bytes,
        model: str = "Nanonets_Ocr_S_F16",
        language: Optional[str] = None,
        format: str = "text",
        image_filename: str = "image.png",
        return_result_in_response: bool = True
    ) -> dict:
        """Submit image-to-text (OCR) request to deAPI."""
        # Build multipart form data
        data = aiohttp.FormData()
        data.add_field('image', image, filename=image_filename, content_type='image/png')
        data.add_field('model', model)
        data.add_field('format', format)
        data.add_field('return_result_in_response', 'true')
        
        if language:
            data.add_field('language', language)
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/img2txt",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # IMAGE BACKGROUND REMOVAL
    # ============================================================
    
    async def remove_image_background(
        self,
        image: bytes,
        model: str = "Ben2",
        image_filename: str = "image.png"
    ) -> dict:
        """Remove background from image using deAPI."""
        data = aiohttp.FormData()
        data.add_field('image', image, filename=image_filename, content_type='image/png')
        data.add_field('model', model)
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/img-rmbg",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # VIDEO-TO-TEXT (URL)
    # ============================================================
    
    async def generate_vid2txt(
        self,
        video_url: str,
        model: str = "WhisperLargeV3",
        include_ts: bool = True
    ) -> dict:
        """Transcribe video from URL (YouTube, X, Twitch, Kick)."""
        payload = {
            "video_url": video_url,
            "model": model,
            "include_ts": include_ts
        }
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=300)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/vid2txt",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # VIDEO-TO-TEXT (FILE UPLOAD)
    # ============================================================
    
    async def generate_videofile2txt(
        self,
        video: bytes,
        model: str = "WhisperLargeV3",
        include_ts: bool = True,
        video_filename: str = "video.mp4"
    ) -> dict:
        """Transcribe video file."""
        data = aiohttp.FormData()
        data.add_field('video', video, filename=video_filename, content_type='video/mp4')
        data.add_field('model', model)
        data.add_field('include_ts', 'true' if include_ts else 'false')
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=300)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/videofile2txt",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # TEXT-TO-MUSIC
    # ============================================================
    
    async def generate_txt2music(
        self,
        caption: str,
        model: str = "AceStep_1_5_Turbo",
        duration: int = 60,
        steps: int = 8,
        bpm: int = 120,
        guidance: Optional[float] = None,
        seed: int = -1
    ) -> dict:
        """Submit text-to-music generation request to deAPI."""
        payload = {
            "caption": caption,
            "model": model,
            "duration": duration,
            "inference_steps": steps,
            "bpm": bpm,
            "seed": seed
        }
        
        if guidance:
            payload["guidance"] = guidance
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/txt2music",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # AUDIO-TO-VIDEO (LTX-2.3 for AI Avatar Animation)
    # ============================================================
    
    async def generate_aud2video(
        self,
        image_url: str,
        audio_url: str,
        prompt: str = "",
        model: str = "Ltx2_3_22B_Dist_INT8",
        width: int = 512,
        height: int = 512,
        frames: int = 97,
        seed: int = -1,
        fps: int = 24
    ) -> dict:
        """
        Submit audio-to-video generation request to deAPI.
        
        This is the key endpoint for AI Avatar animation:
        - Takes a portrait image URL and audio URL
        - LTX-2.3 generates lip-synced animation with natural head movements
        - Returns a complete talking avatar video
        
        Args:
            image_url: URL to the portrait image (downloaded and uploaded as binary)
            audio_url: URL to the audio file (downloaded and uploaded as binary)
            prompt: Motion prompt for animation direction
            model: LTX-2.3 model variant (default: Ltx2_3_22B_Dist_INT8)
            width: Output video width (min 512, max 1024)
            height: Output video height (min 512, max 1024)
            frames: Number of frames to generate (min 49, max 241)
            seed: Random seed (-1 for random)
            fps: Frames per second (fixed at 24)
            
        Returns:
            dict with request_id and status
        """
        # Fetch both image and audio files from URLs (API requires binary uploads)
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            timeout=aiohttp.ClientTimeout(total=60)
        ) as fetch_session:
            # Fetch image
            async with fetch_session.get(image_url) as img_response:
                img_response.raise_for_status()
                image_data = await img_response.read()
                # Detect content type from response or extension
                image_content_type = img_response.headers.get('Content-Type', 'image/png')
                if image_url.lower().endswith('.jpg') or image_url.lower().endswith('.jpeg'):
                    image_filename = 'portrait.jpg'
                elif image_url.lower().endswith('.webp'):
                    image_filename = 'portrait.webp'
                else:
                    image_filename = 'portrait.png'
            
            # Fetch audio
            async with fetch_session.get(audio_url) as audio_response:
                audio_response.raise_for_status()
                audio_data = await audio_response.read()
                # Detect content type from response or extension
                audio_content_type = audio_response.headers.get('Content-Type', 'audio/mpeg')
                if audio_url.lower().endswith('.wav'):
                    audio_filename = 'speech.wav'
                elif audio_url.lower().endswith('.flac'):
                    audio_filename = 'speech.flac'
                else:
                    audio_filename = 'speech.mp3'
        
        # Build multipart form data - both files as binary uploads
        # Note: Ltx2_3_22B_Dist_INT8 doesn't support steps/guidance
        data = aiohttp.FormData()
        data.add_field('audio', audio_data, filename=audio_filename, content_type=audio_content_type)
        data.add_field('first_frame_image', image_data, filename=image_filename, content_type=image_content_type)
        data.add_field('prompt', prompt)
        data.add_field('model', model)
        data.add_field('width', str(width))
        data.add_field('height', str(height))
        data.add_field('frames', str(frames))
        data.add_field('seed', str(seed))
        data.add_field('fps', str(fps))
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/aud2video",
                data=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"[Avatar] aud2video error response: {error_text}")
                    response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # TEXT-TO-EMBEDDING
    # ============================================================
    
    async def generate_txt2embedding(
        self,
        input_text: Union[str, List[str]],
        model: str = "Bge_M3_FP16",
        return_result_in_response: bool = True
    ) -> dict:
        """Submit text-to-embedding request to deAPI."""
        payload = {
            "input": input_text,
            "model": model,
            "return_result_in_response": return_result_in_response
        }
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/txt2embedding",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # VIDEO-TO-TEXT (URL Transcription)
    # ============================================================
    
    async def generate_vid2txt(
        self,
        video_url: str,
        model: str = "WhisperLargeV3",
        include_ts: bool = True
    ) -> dict:
        """Transcribe video from URL (YouTube, X/Twitter, Twitch, Kick)."""
        payload = {
            "video_url": video_url,
            "model": model,
            "include_ts": include_ts
        }
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/vid2txt",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # VIDEO FILE TRANSCRIPTION
    # ============================================================
    
    async def generate_videofile2txt(
        self,
        video: bytes,
        model: str = "WhisperLargeV3",
        include_ts: bool = True,
        video_filename: str = "video.mp4"
    ) -> dict:
        """Transcribe uploaded video file."""
        data = aiohttp.FormData()
        data.add_field('video', video, filename=video_filename, content_type='video/mp4')
        data.add_field('model', model)
        data.add_field('include_ts', str(include_ts).lower())
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/videofile2txt",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # AUDIO FILE TRANSCRIPTION
    # ============================================================
    
    async def generate_audiofile2txt(
        self,
        audio: bytes,
        model: str = "WhisperLargeV3",
        include_ts: bool = True,
        audio_filename: str = "audio.mp3"
    ) -> dict:
        """Transcribe uploaded audio file."""
        data = aiohttp.FormData()
        data.add_field('audio', audio, filename=audio_filename, content_type='audio/mpeg')
        data.add_field('model', model)
        data.add_field('include_ts', str(include_ts).lower())
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/audiofile2txt",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # X SPACES TRANSCRIPTION
    # ============================================================
    
    async def generate_aud2txt(
        self,
        audio_url: str,
        model: str = "WhisperLargeV3",
        include_ts: bool = True
    ) -> dict:
        """Transcribe X/Twitter Spaces from URL."""
        payload = {
            "audio_url": audio_url,
            "model": model,
            "include_ts": include_ts
        }
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/aud2txt",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # IMAGE UPSCALE
    # ============================================================
    
    async def generate_img_upscale(
        self,
        image: bytes,
        model: str = "RealESRGAN_x4",
        image_filename: str = "image.png"
    ) -> dict:
        """Upscale image using RealESRGAN x4."""
        data = aiohttp.FormData()
        data.add_field('image', image, filename=image_filename, content_type='image/png')
        data.add_field('model', model)
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/img-upscale",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # IMAGE BACKGROUND REMOVAL
    # ============================================================
    
    async def generate_img_rmbg(
        self,
        image: bytes,
        model: str = "Ben2",
        image_filename: str = "image.png"
    ) -> dict:
        """Remove background from image."""
        data = aiohttp.FormData()
        data.add_field('image', image, filename=image_filename, content_type='image/png')
        data.add_field('model', model)
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/img-rmbg",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # VIDEO BACKGROUND REMOVAL
    # ============================================================
    
    async def generate_vid_rmbg(
        self,
        video: bytes,
        model: str = "RMBG-1.4",
        video_filename: str = "video.mp4"
    ) -> dict:
        """Remove background from video."""
        data = aiohttp.FormData()
        data.add_field('video', video, filename=video_filename, content_type='video/mp4')
        data.add_field('model', model)
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/vid-rmbg",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # VIDEO REPLACE (WAN 2.2 ANIMATE)
    # ============================================================
    
    async def generate_video_replace(
        self,
        video: bytes,
        character_image: bytes,
        prompt: str = "",
        model: str = "Wan_2_2_14B_Animate_Replace",
        width: Optional[int] = None,
        height: Optional[int] = None,
        steps: int = 4,
        seed: int = -1,
        video_filename: str = "video.mp4",
        image_filename: str = "character.png"
    ) -> dict:
        """
        Submit video-replace request to deAPI using WAN 2.2 Animate.
        
        Replaces a person in a video with a character from a reference image.
        The model copies body movements, facial expressions, and scene lighting.
        
        Args:
            video: Video file bytes (MP4, MPEG, MOV, AVI, WMV, OGG)
            character_image: Character reference image bytes (JPG, PNG, WebP)
            prompt: Optional text prompt to guide the replacement
            model: WAN 2.2 Animate model slug (default: Wan_2_2_14B_Animate_Replace)
            width: Output video width (optional, uses input video width if omitted)
            height: Output video height (optional, uses input video height if omitted)
            steps: Number of inference steps (default: 4)
            seed: Random seed (-1 for random)
            video_filename: Name for the video file
            image_filename: Name for the character image file
            
        Returns:
            dict with request_id and status
        """
        # Build multipart form data
        data = aiohttp.FormData()
        data.add_field('video', video, filename=video_filename, content_type='video/mp4')
        data.add_field('character_image', character_image, filename=image_filename, content_type='image/png')
        data.add_field('model', model)
        data.add_field('steps', str(steps))
        data.add_field('seed', str(seed))
        
        if prompt:
            data.add_field('prompt', prompt)
        
        if width:
            data.add_field('width', str(width))
        
        if height:
            data.add_field('height', str(height))
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes for video processing
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/video-replace",
                data=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"[video-replace] error response: {error_text}")
                    response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # PROMPT ENHANCEMENT
    # ============================================================
    
    async def enhance_prompt_image(
        self,
        prompt: str
    ) -> dict:
        """Enhance a prompt for image generation."""
        payload = {"prompt": prompt}
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/prompt/image",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def enhance_prompt_video(
        self,
        prompt: str
    ) -> dict:
        """Enhance a prompt for video generation."""
        payload = {"prompt": prompt}
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/prompt/video",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def enhance_prompt_image2image(
        self,
        prompt: str,
        image: bytes,
        image_filename: str = "image.png"
    ) -> dict:
        """Enhance a prompt for image-to-image transformation."""
        data = aiohttp.FormData()
        data.add_field('prompt', prompt)
        data.add_field('image', image, filename=image_filename, content_type='image/png')
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/prompt/image2image",
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def enhance_prompt_speech(
        self,
        prompt: str
    ) -> dict:
        """Enhance a prompt for speech generation."""
        payload = {"prompt": prompt}
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.post(
                f"{self.base_url}/api/v1/client/prompt/speech",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def get_sample_prompts(self) -> dict:
        """Get sample prompts for inspiration."""
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.get(
                f"{self.base_url}/api/v1/client/prompts/samples"
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
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
    
    # ============================================================
    # URL-BASED HELPER METHODS (for UGC Ads)
    # ============================================================
    
    async def submit_text2img(
        self,
        prompt: str,
        model: str = "Flux_2_Klein_4B_BF16",
        width: int = 1024,
        height: int = 768,
        guidance: float = 3.5,
        steps: int = 4,
        seed: int = -1
    ) -> dict:
        """
        Submit text-to-image and return result directly.
        Convenience wrapper for UGC ads that returns the URL directly.
        """
        result = await self.generate_text2img(
            prompt=prompt,
            model=model,
            width=width,
            height=height,
            guidance=guidance,
            steps=steps,
            seed=seed
        )
        
        # Extract URL from response
        data = result.get("data", result)
        return {
            "url": data.get("url") or data.get("image_url") or result.get("url"),
            "request_id": result.get("request_id"),
            "status": "completed"
        }
    
    async def submit_img2video(
        self,
        image_url: str,
        prompt: str,
        model: str = "Ltx2_3_22B_Dist_INT8",
        width: int = 768,
        height: int = 768,
        frames: int = 120,
        seed: int = -1
    ) -> dict:
        """
        Submit image-to-video from URL and return result directly.
        Downloads image from URL and uploads to deAPI.
        
        Args:
            image_url: URL to the source image
            prompt: Motion prompt for video generation
            model: Video model (default: Ltx2_3_22B_Dist_INT8)
            width: Output width
            height: Output height
            frames: Number of frames (min 49, max 241)
            seed: Random seed
            
        Returns:
            dict with url and status
        """
        # Download image from URL
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            async with session.get(image_url) as response:
                response.raise_for_status()
                image_data = await response.read()
                
                # Detect content type
                content_type = response.headers.get('Content-Type', 'image/png')
                if 'jpeg' in content_type or 'jpg' in image_url.lower():
                    filename = 'image.jpg'
                else:
                    filename = 'image.png'
        
        # Generate video from image bytes
        result = await self.generate_img2video(
            first_frame_image=image_data,
            prompt=prompt,
            model=model,
            width=width,
            height=height,
            frames=frames,
            seed=seed
        )
        
        # Extract URL from response
        data = result.get("data", result)
        return {
            "url": data.get("url") or data.get("video_url") or result.get("url"),
            "request_id": result.get("request_id"),
            "status": "completed"
        }


# Singleton client (for default server key)
_client: Optional[DeAPIClient] = None


def get_deapi_client(custom_api_key: Optional[str] = None) -> DeAPIClient:
    """
    Get deAPI client. If custom_api_key is provided, creates a new client with that key (BYOK).
    Otherwise returns the singleton client with server's default key.
    """
    if custom_api_key:
        # Create a new client with custom key (BYOK mode)
        return DeAPIClient(custom_api_key=custom_api_key)
    
    # Use singleton client with server default key
    global _client
    if _client is None:
        _client = DeAPIClient()
    return _client