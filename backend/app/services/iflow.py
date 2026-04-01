import aiohttp
import socket
from typing import Optional, List, Dict
from ..config import get_settings

settings = get_settings()


class iFlowClient:
    """iFlow API Client for AI Assistant and text generation capabilities."""
    
    def __init__(self, custom_api_key: Optional[str] = None):
        self.base_url = settings.iflow_base_url
        # Use custom API key if provided (BYOK), otherwise use server default
        self.api_key = custom_api_key or settings.iflow_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _create_connector(self) -> aiohttp.TCPConnector:
        """Create an aiohttp connector forced to IPv4."""
        return aiohttp.TCPConnector(
            family=socket.AF_INET,  # Force IPv4
            ssl=False,
            limit=10
        )
    
    # ============================================================
    # CHAT COMPLETIONS (AI Assistant)
    # ============================================================
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "kimi-k2",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> dict:
        """
        Send a chat completion request to iFlow API.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model to use (kimi-k2, gpt-4o, gpt-4o-mini, claude-3-sonnet, claude-3-haiku)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
        
        Returns:
            API response dict
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def simple_chat(
        self,
        user_message: str,
        system_prompt: str = "You are a helpful AI assistant.",
        model: str = "kimi-k2",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Simple chat interface that returns just the response text.
        
        Args:
            user_message: The user's message
            system_prompt: System instructions for the AI
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            The AI's response text
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        result = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract the response content
        choices = result.get("choices", [])
        if choices and len(choices) > 0:
            return choices[0].get("message", {}).get("content", "")
        
        return ""
    
    # ============================================================
    # TEXT COMPLETIONS
    # ============================================================
    
    async def text_completion(
        self,
        prompt: str,
        model: str = "kimi-k2",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> dict:
        """
        Send a text completion request to iFlow API.
        
        Args:
            prompt: The prompt text
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            API response dict
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as session:
            async with session.post(
                f"{self.base_url}/completions",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # EMBEDDINGS
    # ============================================================
    
    async def create_embedding(
        self,
        input_text: str,
        model: str = "text-embedding-3-small"
    ) -> dict:
        """
        Create embeddings for the input text.
        
        Args:
            input_text: Text to embed
            model: Embedding model to use
        
        Returns:
            API response dict with embedding vector
        """
        payload = {
            "model": model,
            "input": input_text
        }
        
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            async with session.post(
                f"{self.base_url}/embeddings",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    # ============================================================
    # MODELS LIST
    # ============================================================
    
    async def list_models(self) -> dict:
        """
        List available models from iFlow API.
        
        Returns:
            API response dict with available models
        """
        async with aiohttp.ClientSession(
            connector=self._create_connector(),
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.get(
                f"{self.base_url}/models"
            ) as response:
                response.raise_for_status()
                return await response.json()


# Singleton client (for default server key)
_client: Optional[iFlowClient] = None


def get_iflow_client(custom_api_key: Optional[str] = None) -> iFlowClient:
    """
    Get iFlow client. If custom_api_key is provided, creates a new client with that key (BYOK).
    Otherwise returns the singleton client with server's default key.
    """
    if custom_api_key:
        # Create a new client with custom key (BYOK mode)
        return iFlowClient(custom_api_key=custom_api_key)
    
    # Use singleton client with server default key
    global _client
    if _client is None:
        _client = iFlowClient()
    return _client
