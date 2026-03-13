from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal, List, Union


# ============================================================
# TEXT-TO-IMAGE
# ============================================================

class Text2ImgRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    model: str = "Flux_2_Klein_4B_BF16"
    width: int = 1024
    height: int = 768
    guidance: float = 3.5
    steps: int = 4
    seed: int = -1
    loras: Optional[List[str]] = None


# ============================================================
# TEXT-TO-VIDEO
# ============================================================

class Txt2VideoRequest(BaseModel):
    prompt: str
    model: str = "Ltx2_3_22B_Dist_INT8"
    width: int = 512
    height: int = 512
    guidance: float = 3.5
    steps: int = 20
    frames: int = 24
    fps: int = 30
    seed: int = -1


# ============================================================
# IMAGE-TO-VIDEO
# ============================================================

class Img2VideoRequest(BaseModel):
    prompt: str
    model: str = "Ltx2_3_22B_Dist_INT8"
    width: int = 512
    height: int = 512
    guidance: float = 3.5
    steps: int = 20
    frames: int = 24
    fps: int = 30
    seed: int = -1


# ============================================================
# TEXT-TO-MUSIC
# ============================================================

class Txt2MusicRequest(BaseModel):
    caption: str = Field(..., min_length=10, max_length=300, description="Music description/caption")
    model: str = "AceStep_1_5_Turbo"
    duration: int = Field(60, ge=10, le=300, description="Duration in seconds")
    steps: int = Field(8, description="Inference steps")
    bpm: int = Field(120, ge=50, le=200, description="Beats per minute")
    guidance: Optional[float] = Field(None, description="Guidance scale (Base model only)")
    seed: int = -1


# ============================================================
# TEXT-TO-EMBEDDING
# ============================================================

class Txt2EmbeddingRequest(BaseModel):
    input: Union[str, List[str]] = Field(..., description="Text or list of texts to embed")
    model: str = "Bge_M3_FP16"


class EmbeddingResponse(BaseModel):
    request_id: Optional[str] = None
    embedding: Optional[List[float]] = None


# ============================================================
# VIDEO-TO-TEXT (URL Transcription)
# ============================================================

class Vid2TxtRequest(BaseModel):
    video_url: str = Field(..., description="Video URL (YouTube, X/Twitter, Twitch, Kick)")
    model: str = "WhisperLargeV3"
    include_ts: bool = True


# ============================================================
# AUDIO-TO-TEXT (X Spaces)
# ============================================================

class Aud2TxtRequest(BaseModel):
    audio_url: str = Field(..., description="X/Twitter Spaces URL")
    model: str = "WhisperLargeV3"
    include_ts: bool = True


# ============================================================
# TRANSCRIPTION RESPONSE
# ============================================================

class TranscriptionResponse(BaseModel):
    id: int
    uuid: Optional[str] = None
    source_type: str  # vid2txt, videofile2txt, audiofile2txt, aud2txt
    source_url: Optional[str] = None
    model: str
    include_ts: bool = True
    status: str
    progress: int = 0
    result_text: Optional[str] = None
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# IMAGE UPSCALE
# ============================================================

class ImgUpscaleRequest(BaseModel):
    model: str = "RealESRGAN_x4"


# ============================================================
# IMAGE BACKGROUND REMOVAL
# ============================================================

class ImgRmbgRequest(BaseModel):
    model: str = "Ben2"


# ============================================================
# VIDEO BACKGROUND REMOVAL
# ============================================================

class VidRmbgRequest(BaseModel):
    model: str = "RMBG-1.4"


# ============================================================
# PROMPT ENHANCEMENT
# ============================================================

class PromptEnhanceRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="Prompt to enhance")


class PromptEnhanceResponse(BaseModel):
    enhanced_prompt: str


# ============================================================
# GENERATION (Legacy/Combined)
# ============================================================

class GenerationCreate(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    generation_type: Literal[
        "text2img", "txt2video", "img2video", "img2img", "txt2audio", "img2txt",
        "txt2music", "txt2embedding", "vid2txt", "videofile2txt", "audiofile2txt",
        "aud2txt", "img-upscale", "img-rmbg", "vid-rmbg"
    ] = "text2img"
    model: str = "Flux_2_Klein_4B_BF16"
    width: int = 1024
    height: int = 768
    guidance: float = 3.5
    steps: int = 4
    seed: int = -1
    # Video-specific
    frames: Optional[int] = 24
    fps: Optional[int] = 30
    # Music-specific
    duration: Optional[int] = 60
    bpm: Optional[int] = 120
    # LoRA support
    loras: Optional[List[str]] = None


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
    credits_charged: Optional[int] = None
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


# ============================================================
# HEALTH & BALANCE
# ============================================================

class HealthResponse(BaseModel):
    status: str
    database: str


class BalanceResponse(BaseModel):
    balance: float
    currency: str


# ============================================================
# AI ADS GENERATOR
# ============================================================

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


# ============================================================
# CREDIT SYSTEM
# ============================================================

class CreditCheckRequest(BaseModel):
    """Request to estimate credits for a generation."""
    generation_type: str = Field(..., description="Type of generation: txt2img, txt2video, img2video, etc.")
    model: str = Field(..., description="Model slug/ID")
    width: Optional[int] = Field(None, description="Width in pixels")
    height: Optional[int] = Field(None, description="Height in pixels")
    frames: Optional[int] = Field(None, description="Number of frames (for video)")
    text_length: Optional[int] = Field(None, description="Text length (for TTS)")
    duration: Optional[int] = Field(None, description="Duration in seconds (for music/transcription)")


class CreditBreakdownResponse(BaseModel):
    """Detailed credit breakdown for display."""
    credits: int
    model: str
    model_name: str
    description: str
    parameters: dict


class CreditCheckResponse(BaseModel):
    """Response for credit check endpoint."""
    credits_required: int
    user_balance: int
    sufficient: bool
    breakdown: CreditBreakdownResponse


class UserCreditsResponse(BaseModel):
    """Response for user credits endpoint."""
    credits_balance: int
    total_credits_purchased: int
    total_credits_used: int


class CreditPackageResponse(BaseModel):
    """Credit package for purchase."""
    id: int
    name: str
    credits: int
    price_cents: int
    bonus_percent: int
    price_display: str  # e.g., "$1.00"

    class Config:
        from_attributes = True


class CreditPackagesListResponse(BaseModel):
    """List of available credit packages."""
    packages: list[CreditPackageResponse]
