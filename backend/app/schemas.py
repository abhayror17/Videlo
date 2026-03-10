from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


class Text2ImgRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    model: str = "Flux_2_Klein_4B_BF16"
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
    model: str = "Flux_2_Klein_4B_BF16"
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


# AI Ads Generator Schemas
class AdCampaignCreate(BaseModel):
    user_prompt: str = Field(..., min_length=10, description="User's ad concept/idea")
    brand_name: Optional[str] = Field(None, description="Brand name for the ad")
    brand_description: Optional[str] = Field(None, description="Brief brand description")


class AdCampaignResponse(BaseModel):
    id: int
    user_prompt: str
    brand_name: Optional[str] = None
    brand_description: Optional[str] = None
    
    # Pipeline status
    current_step: str = "init"
    
    # Enhancement
    enhanced_prompt: Optional[str] = None
    enhancement_status: str = "pending"
    
    # Script
    script: Optional[str] = None
    script_status: str = "pending"
    script_feedback: Optional[str] = None
    
    # Image
    image_url: Optional[str] = None
    image_status: str = "pending"
    image_feedback: Optional[str] = None
    
    # Video
    video_url: Optional[str] = None
    video_status: str = "pending"
    video_feedback: Optional[str] = None
    
    # QA
    qa_status: str = "pending"
    qa_feedback: Optional[str] = None
    qa_details: Optional[str] = None
    qa_iterations: int = 0
    
    # Overall
    overall_status: str = "pending"
    error_message: Optional[str] = None
    
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdCampaignListResponse(BaseModel):
    items: list[AdCampaignResponse]
    total: int
    page: int
    pages: int


class RedoRequest(BaseModel):
    step: Literal["script", "image", "video"] = Field(..., description="Which step to redo")
    feedback: Optional[str] = Field(None, description="Additional feedback for the redo")
