from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


class Text2ImgRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    model: str = "ZImageTurbo_INT8"
    width: int = 1024
    height: int = 768
    guidance: float = 3.5
    steps: int = 4
    seed: int = -1


class Txt2VideoRequest(BaseModel):
    prompt: str
    model: str = "Ltx2_19B_Dist_FP8"
    width: int = 512
    height: int = 512
    guidance: float = 3.5
    steps: int = 20
    frames: int = 24
    fps: int = 30
    seed: int = -1


class Img2VideoRequest(BaseModel):
    prompt: str
    model: str = "Ltx2_19B_Dist_FP8"
    width: int = 512
    height: int = 512
    guidance: float = 3.5
    steps: int = 20
    frames: int = 24
    fps: int = 30
    seed: int = -1


class GenerationCreate(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    generation_type: Literal["text2img", "txt2video", "img2video"] = "text2img"
    model: str = "ZImageTurbo_INT8"
    width: int = 1024
    height: int = 768
    guidance: float = 3.5
    steps: int = 4
    seed: int = -1
    # Video-specific
    frames: Optional[int] = 24
    fps: Optional[int] = 30


class GenerationResponse(BaseModel):
    id: int
    uuid: Optional[str] = None
    prompt: str
    negative_prompt: Optional[str] = None
    model: str
    generation_type: str = "text2img"
    width: Optional[int] = None
    height: Optional[int] = None
    frames: Optional[int] = None
    fps: Optional[int] = None
    guidance: Optional[float] = None
    steps: Optional[int] = None
    seed: Optional[int] = None
    status: str
    progress: int = 0
    remote_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GenerationListResponse(BaseModel):
    items: list[GenerationResponse]
    total: int
    page: int
    pages: int


class HealthResponse(BaseModel):
    status: str
    database: str


class BalanceResponse(BaseModel):
    balance: float
    currency: str
