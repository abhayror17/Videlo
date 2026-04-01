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
# TEXT-TO-AUDIO / TTS
# ============================================================

class Txt2AudioRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=10001, description="Text to convert to speech")
    model: str = Field("Kokoro", description="TTS model: Kokoro, Chatterbox, Qwen3_TTS_12Hz_1_7B_CustomVoice, Qwen3_TTS_12Hz_1_7B_Base, Qwen3_TTS_12Hz_1_7B_VoiceDesign")
    voice: Optional[str] = Field(None, description="Voice ID (model-specific)")
    lang: str = Field("en-us", description="Language code")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Speech speed")
    format: str = Field("mp3", description="Output format: mp3, flac, wav")
    sample_rate: int = Field(24000, description="Sample rate in Hz")
    mode: str = Field("custom_voice", description="Mode: custom_voice, voice_clone, voice_design")
    ref_audio: Optional[str] = Field(None, description="Reference audio URL for voice cloning")
    ref_text: Optional[str] = Field(None, description="Reference text for voice cloning")
    instruct: Optional[str] = Field(None, description="Voice design instructions")


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
# VIDEO REPLACE (WAN 2.2 ANIMATE)
# ============================================================

class VideoReplaceRequest(BaseModel):
    """Request for video character replacement using WAN 2.2 Animate."""
    prompt: Optional[str] = Field(None, description="Optional text prompt to guide the replacement")
    model: str = Field("Wan_2_2_14B_Animate_Replace", description="WAN 2.2 Animate model slug")
    width: Optional[int] = Field(None, description="Output video width (uses input if omitted)")
    height: Optional[int] = Field(None, description="Output video height (uses input if omitted)")
    steps: int = Field(4, ge=1, le=50, description="Number of inference steps")
    seed: int = Field(-1, description="Random seed (-1 for random)")


# ============================================================
# PROMPT ENHANCEMENT
# ============================================================

class PromptEnhanceRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="Prompt to enhance")


class PromptEnhanceResponse(BaseModel):
    enhanced_prompt: str


# ============================================================
# NANOBANANA IMAGE GENERATION
# ============================================================

class NanoBananaRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="Text prompt for image generation")
    model: str = Field("nano-banana-2", description="Model: nano-banana-2 or nano-banana-pro")
    aspect_ratio: str = Field("1:1", description="Aspect ratio: 1:1, 16:9, 9:16, 3:4, 4:3")
    reference_images: Optional[List[str]] = Field(None, description="Reference image URLs for image-to-image")


class NanoBananaResponse(BaseModel):
    task_id: str
    status: str
    image_urls: List[str] = []
    error: Optional[str] = None


# ============================================================
# GENERATION (Legacy/Combined)
# ============================================================

class GenerationCreate(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    generation_type: Literal[
        "text2img", "txt2video", "img2video", "img2img", "txt2audio", "img2txt",
        "txt2music", "txt2embedding", "vid2txt", "videofile2txt", "audiofile2txt",
        "aud2txt", "img-upscale", "img-rmbg", "vid-rmbg", "video-replace"
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
    status: str
    progress: int = 0
    remote_url: Optional[str] = None
    local_path: Optional[str] = None
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
# AI ADS GENERATOR - MULTI-PHASE WORKFLOW
# ============================================================

# Phase 1: Clarification Questions
class ClarificationQuestion(BaseModel):
    id: str
    question: str
    type: Literal["text", "select", "multiselect"] = "text"
    options: Optional[List[str]] = None


class ClarificationQuestionsResponse(BaseModel):
    campaign_id: int
    phase: int = 1
    questions: List[ClarificationQuestion]


class ClarificationAnswer(BaseModel):
    question_id: str
    answer: Union[str, List[str]]


class ClarificationAnswersRequest(BaseModel):
    answers: List[ClarificationAnswer]


# Phase 2: Structured Context
class AvatarPreferences(BaseModel):
    gender: Optional[str] = None
    age_range: Optional[str] = None
    persona: Optional[str] = None


class AdContext(BaseModel):
    brand: str = ""
    product: str = ""
    target_audience: str = ""
    platform: str = ""
    hooks: List[str] = []
    tone: str = ""
    ad_angles: List[str] = []
    avatar_preferences: Optional[AvatarPreferences] = None
    constraints: List[str] = []


# Phase 3: Ad Strategy/Angles
class AdAngle(BaseModel):
    id: int
    hook_idea: str
    emotional_trigger: str
    why_convert: str


class AdStrategyResponse(BaseModel):
    campaign_id: int
    phase: int = 3
    angles: List[AdAngle]


# Phase 4: Script Generation
class ScriptScene(BaseModel):
    scene: int
    dialogue: str
    visual: str
    duration: str


class AdScriptData(BaseModel):
    id: int
    hook: str
    scenes: List[ScriptScene]
    cta: str


class ScriptsGenerateRequest(BaseModel):
    num_scripts: int = Field(5, ge=1, le=20, description="Number of scripts to generate")


class ScriptsResponse(BaseModel):
    campaign_id: int
    phase: int = 4
    scripts: List[AdScriptData]


# Phase 5: Avatar Generation
class AdAvatarData(BaseModel):
    id: int
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    region: Optional[str] = None
    appearance: str
    outfit_style: str
    personality_vibe: str


class AvatarsResponse(BaseModel):
    campaign_id: int
    phase: int = 5
    avatars: List[AdAvatarData]


# Phase 6: Storyboard
class StoryboardScene(BaseModel):
    scene_num: int
    visual_direction: str
    camera_angle: str
    lighting: str
    emotion: str
    environment: str


class StoryboardResponse(BaseModel):
    campaign_id: int
    script_id: int
    phase: int = 6
    scenes: List[StoryboardScene]


# Phase 7-8: Image/Video Prompts
class ScenePromptData(BaseModel):
    id: int
    scene_num: int
    image_prompt: Optional[str] = None
    video_prompt: Optional[str] = None
    image_generation_id: Optional[int] = None
    video_generation_id: Optional[int] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    image_status: str = "pending"
    video_status: str = "pending"


class StoryboardDetailData(BaseModel):
    id: int
    script_id: int
    scenes: List[dict]
    scene_prompts: List[ScenePromptData] = []


class PromptsResponse(BaseModel):
    campaign_id: int
    script_id: int
    phase: int = 7  # or 8
    scenes: List[ScenePromptData]


# Phase 9: Batch Output
class BatchOutputResponse(BaseModel):
    campaign_id: int
    phase: int = 9
    context: AdContext
    avatars: List[AdAvatarData]
    scripts: List[AdScriptData]
    storyboards: List[dict]
    image_prompts: List[dict]
    video_prompts: List[dict]


# Phase 10: Iteration Mode
class IterationRequest(BaseModel):
    command: str = Field(..., description="Iteration command, e.g., 'make it funnier', 'change avatar', 'target gym audience'")
    target: Optional[str] = Field(None, description="Target to modify: 'scripts', 'avatars', 'hooks', 'all'")


class IterationResponse(BaseModel):
    campaign_id: int
    iteration_count: int
    changes_made: str
    updated_data: dict


# Campaign Creation & Management
class AdCampaignCreate(BaseModel):
    user_prompt: str = Field(..., min_length=5, description="User's ad concept/idea")
    brand_name: Optional[str] = Field(None, description="Brand name for the ad")
    brand_description: Optional[str] = Field(None, description="Brief brand description")


class AdCampaignResponse(BaseModel):
    id: int
    user_prompt: str
    
    # Current workflow phase
    current_phase: int = 1
    phase_status: str = "pending"
    
    # Clarification questions
    clarification_questions: Optional[List[dict]] = None
    user_answers: Optional[List[dict]] = None
    
    # Structured context
    context: Optional[dict] = None
    
    # Ad strategy
    ad_angles: Optional[List[dict]] = None
    
    # Generation settings
    num_scripts: int = 5
    num_avatars: int = 3
    
    # Status tracking
    scripts_status: str = "pending"
    avatars_status: str = "pending"
    storyboards_status: str = "pending"
    image_prompts_status: str = "pending"
    video_prompts_status: str = "pending"
    
    # Iteration
    iteration_count: int = 0
    last_iteration_command: Optional[str] = None
    
    # Overall
    overall_status: str = "pending"
    error_message: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdCampaignListResponse(BaseModel):
    items: List[AdCampaignResponse]
    total: int
    page: int
    pages: int


class AdCampaignDetailResponse(AdCampaignResponse):
    """Full campaign details with all related data."""
    avatars: List[AdAvatarData] = []
    scripts: List[dict] = []
    storyboards: List[StoryboardDetailData] = []


# Legacy support (deprecated - will be removed)
class RedoRequest(BaseModel):
    step: Literal["script", "image", "video"] = Field(..., description="Which step to redo")
    feedback: Optional[str] = Field(None, description="Additional feedback for the redo")


# ============================================================
# AI VIDEO AVATAR PIPELINE
# ============================================================

class AiAvatarCreate(BaseModel):
    """Create a new AI Avatar project."""
    name: Optional[str] = Field(None, description="Project name")
    portrait_prompt: str = Field(..., min_length=5, description="Prompt for portrait generation")
    speech_text: str = Field(..., min_length=3, description="Text to convert to speech")
    motion_prompt: Optional[str] = Field(None, description="Animation direction prompt")
    
    # Voice settings
    voice_model: str = Field("Kokoro", description="TTS model: Kokoro, Chatterbox")
    voice_id: str = Field("af_sky", description="Voice ID")
    voice_speed: float = Field(1.0, ge=0.5, le=2.0, description="Speech speed")
    voice_lang: str = Field("en-us", description="Language code")
    
    # Portrait settings
    portrait_model: str = Field("Flux_2_Klein_4B_BF16", description="Image generation model")
    portrait_width: int = Field(512, description="Portrait width")
    portrait_height: int = Field(512, description="Portrait height")
    
    # Animation settings
    animation_model: str = Field("Ltx2_3_22B_Dist_INT8", description="Animation model")
    animation_frames: int = Field(24, description="Number of frames")
    animation_fps: int = Field(30, description="Frames per second")


class AiAvatarResponse(BaseModel):
    """Response for AI Avatar project."""
    id: int
    name: Optional[str] = None
    portrait_prompt: str
    speech_text: str
    motion_prompt: Optional[str] = None
    
    # Voice settings
    voice_model: str = "Kokoro"
    voice_id: str = "af_sky"
    voice_speed: float = 1.0
    voice_lang: str = "en-us"
    
    # Portrait settings
    portrait_model: str = "Flux_2_Klein_4B_BF16"
    portrait_width: int = 512
    portrait_height: int = 512
    
    # Animation settings
    animation_model: str = "Ltx2_3_22B_Dist_INT8"
    animation_frames: int = 24
    animation_fps: int = 30
    
    # Generation results
    portrait_url: Optional[str] = None
    portrait_status: str = "pending"
    audio_url: Optional[str] = None
    audio_status: str = "pending"
    video_url: Optional[str] = None
    video_status: str = "pending"
    
    # Status
    current_step: int = 1
    overall_status: str = "pending"
    error_message: Optional[str] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AiAvatarListResponse(BaseModel):
    """List of AI Avatar projects."""
    items: List[AiAvatarResponse]
    total: int
    page: int
    pages: int


class AiAvatarStepRequest(BaseModel):
    """Request to run a specific step."""
    step: Literal["portrait", "audio", "video", "all"] = Field(..., description="Which step to run")


class AiAvatarRegenerateRequest(BaseModel):
    """Request to regenerate with modified parameters."""
    portrait_prompt: Optional[str] = None
    speech_text: Optional[str] = None
    motion_prompt: Optional[str] = None
    voice_id: Optional[str] = None
    voice_speed: Optional[float] = None


# ============================================================
# UGC AI ADS CREATOR
# ============================================================

class PromptMatchData(BaseModel):
    """A matched prompt from the library."""
    id: str
    prompt: str
    title: str
    tags: List[str] = []
    model: str = "youmind"
    image_url: Optional[str] = None
    relevance_score: float = 0.0
    match_reason: str = ""


class PromptSearchRequest(BaseModel):
    """Request to search for matching prompts."""
    query: str = Field(..., min_length=2, description="Search query")
    product_type: Optional[str] = Field(None, description="Product type filter")
    category: Optional[str] = Field(None, description="Category filter")
    mood: Optional[str] = Field(None, description="Mood/style filter")
    limit: int = Field(5, ge=1, le=20, description="Max results")


class PromptSearchResponse(BaseModel):
    """Response with matched prompts."""
    query: str
    detected_category: Optional[str] = None
    detected_mood: Optional[str] = None
    matches: List[PromptMatchData]
    total: int


class UgcCharacterData(BaseModel):
    """Character data for UGC story."""
    name: str
    role: str = "protagonist"
    age: int = 25
    gender: str = "female"
    appearance: str = ""
    outfit: str = ""
    personality: str = ""


class UgcProductData(BaseModel):
    """Product data for UGC story."""
    name: str
    category: str = ""
    description: str = ""
    key_features: List[str] = []
    visual_description: str = ""


class UgcShotData(BaseModel):
    """Shot data for UGC scene."""
    id: Optional[int] = None
    shot_num: int
    duration_sec: int = 5
    frame_description: str
    action: Optional[str] = None
    dialogue: Optional[str] = None
    camera_angle: Optional[str] = None
    lighting: Optional[str] = None
    audio_notes: Optional[str] = None
    first_frame_prompt: Optional[str] = None
    first_frame_url: Optional[str] = None
    first_frame_status: str = "pending"
    last_frame_prompt: Optional[str] = None
    last_frame_url: Optional[str] = None
    last_frame_status: str = "pending"
    video_prompt: Optional[str] = None
    video_url: Optional[str] = None
    video_status: str = "pending"
    error_message: Optional[str] = None


class UgcSceneData(BaseModel):
    """Scene data for UGC story."""
    id: Optional[int] = None
    scene_num: int
    scene_name: str
    setting: Optional[str] = None
    mood: Optional[str] = None
    shots: List[UgcShotData] = []


class UgcStoryCreate(BaseModel):
    """Request to create a new UGC ad story."""
    product_name: str = Field(..., min_length=2, description="Product name")
    product_description: str = Field(..., min_length=5, description="Product description")
    product_category: Optional[str] = Field(None, description="Product category")
    character_name: Optional[str] = Field(None, description="Main character name")
    character_description: Optional[str] = Field(None, description="Character description")
    character_reference_url: Optional[str] = Field(None, description="Character reference image URL")
    product_reference_url: Optional[str] = Field(None, description="Product reference image URL")
    target_audience: Optional[str] = Field(None, description="Target audience")
    platform: str = Field("Instagram", description="Target platform")
    ad_goal: str = Field("product_awareness", description="Advertising goal")
    tone: str = Field("authentic", description="Ad tone")
    setting_preference: Optional[str] = Field(None, description="Preferred setting")
    total_duration_sec: int = Field(15, ge=5, le=60, description="Total duration in seconds")


class UgcStoryResponse(BaseModel):
    """Response for a UGC ad story."""
    id: int
    story_id: str
    title: str
    target_platform: str
    total_duration_sec: int
    hook: str
    cta: str
    setting_description: Optional[str] = None
    characters: List[dict] = []
    product_name: str
    product_category: Optional[str] = None
    product_description: Optional[str] = None
    product_key_features: List[str] = []
    product_visual_description: Optional[str] = None
    character_reference_url: Optional[str] = None
    product_reference_url: Optional[str] = None
    inspiration_prompts: List[dict] = []
    status: str = "draft"
    error_message: Optional[str] = None
    scenes: List[UgcSceneData] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UgcStoryListResponse(BaseModel):
    """List of UGC ad stories."""
    items: List[UgcStoryResponse]
    total: int
    page: int
    pages: int


class UgcStoryGenerateRequest(BaseModel):
    """Request to generate images/videos for a story."""
    generate_images: bool = Field(True, description="Generate shot images")
    generate_videos: bool = Field(True, description="Generate shot videos")
    model: str = Field("Flux_2_Klein_4B_BF16", description="Image generation model")
    video_model: str = Field("Ltx2_3_22B_Dist_INT8", description="Video generation model")
    aspect_ratio: str = Field("16:9", description="Image aspect ratio")


class UgcShotRegenerateRequest(BaseModel):
    """Request to regenerate a specific shot."""
    shot_id: int
    regenerate_image: bool = Field(True, description="Regenerate first frame image")
    regenerate_video: bool = Field(True, description="Regenerate video")
    custom_prompt: Optional[str] = Field(None, description="Custom prompt override")


class UgcShotRegenerateResponse(BaseModel):
    """Response for shot regeneration."""
    shot_id: int
    first_frame_status: str
    video_status: str
    first_frame_url: Optional[str] = None
    video_url: Optional[str] = None
