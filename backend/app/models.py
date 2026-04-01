from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Boolean, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """User model aligned with the SQLite migration-backed users table."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    credits_balance = Column(Integer, default=0)
    total_credits_purchased = Column(Integer, default=0)
    total_credits_used = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    generations = relationship("Generation", back_populates="user")


class Generation(Base):
    """Model for image/video/audio generation results."""
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, nullable=True)  # deAPI request_id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Link to user
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    model = Column(String, default="Flux_2_Klein_4B_BF16")
    
    # Generation type: text2img, img2video, txt2video, img2img, txt2audio, img2txt,
    # txt2music, txt2embedding, img-upscale, img-rmbg, vid-rmbg
    generation_type = Column(String, default="text2img")
    
    # Image dimensions
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # Video-specific fields
    frames = Column(Integer, nullable=True)
    fps = Column(Integer, nullable=True)
    
    # Music-specific fields
    duration = Column(Integer, nullable=True)  # Duration in seconds
    bpm = Column(Integer, nullable=True)  # Beats per minute
    
    # Generation parameters
    guidance = Column(Float, nullable=True)
    steps = Column(Integer, nullable=True)
    seed = Column(Integer, nullable=True)
    
    # LoRA support (stored as JSON array)
    loras = Column(JSON, nullable=True)
    
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100 progress percentage
    remote_url = Column(String, nullable=True)  # Original deAPI URL (may expire)
    local_path = Column(String, nullable=True)  # Local stored file path (permanent)
    thumbnail_url = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="generations")


class Transcription(Base):
    """Model for audio/video transcription results."""
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, nullable=True)  # deAPI request_id
    
    # Source type: vid2txt, videofile2txt, audiofile2txt, aud2txt
    source_type = Column(String, nullable=False)
    
    # Source URL (for vid2txt, aud2txt)
    source_url = Column(String, nullable=True)
    
    # Original filename (for file uploads)
    source_filename = Column(String, nullable=True)
    
    # Model used
    model = Column(String, default="WhisperLargeV3")
    
    # Whether to include timestamps
    include_ts = Column(Integer, default=1)
    
    # Status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)
    
    # Result
    result_text = Column(Text, nullable=True)  # Transcribed text
    result_url = Column(String, nullable=True)  # URL to result file
    
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class AdCampaign(Base):
    """
    Model for AI Ads Generator - Agentic Multi-Phase Workflow.
    
    Supports conversational ad creation through 10 phases:
    1. UNDERSTAND & ASK - Ask clarification questions
    2. BUILD CONTEXT - Convert to structured JSON
    3. GENERATE AD STRATEGY - Create ad angles
    4. SCRIPT GENERATION - Generate UGC scripts
    5. AVATAR GENERATION - Create UGC characters
    6. STORYBOARD ENGINE - Break into scenes
    7. IMAGE PROMPT GENERATION - Scene image prompts
    8. VIDEO PROMPT GENERATION - Scene video prompts
    9. BATCH OUTPUT - Return structured output
    10. ITERATION MODE - Modify outputs
    """
    __tablename__ = "ad_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    
    # User input
    user_prompt = Column(Text, nullable=False)
    
    # Current workflow phase
    current_phase = Column(Integer, default=1)  # 1-10
    phase_status = Column(String, default="pending")  # pending, processing, completed, failed
    
    # Phase 1: Clarification questions asked
    clarification_questions = Column(JSON, nullable=True)  # List of questions asked
    user_answers = Column(JSON, nullable=True)  # User's answers
    
    # Phase 2: Structured context
    context = Column(JSON, nullable=True)  # {brand, product, target_audience, platform, hooks, tone, ad_angles, avatar_preferences, constraints}
    
    # Phase 3: Ad strategy/angles
    ad_angles = Column(JSON, nullable=True)  # List of {hook_idea, emotional_trigger, why_convert}
    
    # Phase 4-8: Scripts, Avatars, Storyboards, Prompts (stored in related tables)
    
    # Batch settings
    num_scripts = Column(Integer, default=5)
    num_avatars = Column(Integer, default=3)
    
    # Generation status tracking
    scripts_status = Column(String, default="pending")
    avatars_status = Column(String, default="pending")
    storyboards_status = Column(String, default="pending")
    image_prompts_status = Column(String, default="pending")
    video_prompts_status = Column(String, default="pending")
    
    # Iteration mode
    iteration_count = Column(Integer, default=0)
    last_iteration_command = Column(Text, nullable=True)
    
    # Overall status
    overall_status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    avatars = relationship("AdAvatar", back_populates="campaign", cascade="all, delete-orphan")
    scripts = relationship("AdScript", back_populates="campaign", cascade="all, delete-orphan")
    storyboards = relationship("AdStoryboard", back_populates="campaign", cascade="all, delete-orphan")
    conversations = relationship("AdConversation", back_populates="campaign", cascade="all, delete-orphan")


class AdAvatar(Base):
    """UGC character/avatar for ad campaigns."""
    __tablename__ = "ad_avatars"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    region = Column(String(50), nullable=True)  # e.g., "India", "US", "Europe"
    
    # Physical appearance (locked for consistency)
    appearance = Column(Text, nullable=True)  # Detailed physical description
    outfit_style = Column(Text, nullable=True)
    personality_vibe = Column(Text, nullable=True)  # e.g., "friendly, approachable, confident"
    
    # Consistency lock
    appearance_locked = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaign = relationship("AdCampaign", back_populates="avatars")


class AdScript(Base):
    """UGC-style ad script."""
    __tablename__ = "ad_scripts"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id"), nullable=False)
    
    script_id = Column(Integer, nullable=False)  # 1-N within campaign
    
    # Script content
    hook = Column(Text, nullable=False)  # Opening hook
    cta = Column(Text, nullable=True)  # Call to action
    framework = Column(String(50), nullable=True)  # PAS, Testimonial, Before/After, Curiosity
    
    # Full script as JSON
    scenes = Column(JSON, nullable=False)  # [{scene: 1, dialogue: "", visual: "", duration: ""}]
    
    # Assigned avatar
    avatar_id = Column(Integer, ForeignKey("ad_avatars.id"), nullable=True)
    
    # Generation metadata
    ad_angle_ref = Column(Integer, nullable=True)  # Reference to ad angle used
    
    # Iteration tracking
    version = Column(Integer, default=1)
    iteration_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("AdCampaign", back_populates="scripts")
    avatar = relationship("AdAvatar")
    storyboard = relationship("AdStoryboard", back_populates="script", uselist=False)


class AdStoryboard(Base):
    """Storyboard for a script with scene breakdowns."""
    __tablename__ = "ad_storyboards"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id"), nullable=False)
    script_id = Column(Integer, ForeignKey("ad_scripts.id"), nullable=False)
    
    # Scene breakdowns
    scenes = Column(JSON, nullable=False)  # [{scene_num, visual_direction, camera_angle, lighting, emotion, environment}]
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("AdCampaign", back_populates="storyboards")
    script = relationship("AdScript", back_populates="storyboard")
    scene_prompts = relationship("AdScenePrompt", back_populates="storyboard", cascade="all, delete-orphan")


class AdScenePrompt(Base):
    """Image and video prompts for each scene."""
    __tablename__ = "ad_scene_prompts"

    id = Column(Integer, primary_key=True, index=True)
    storyboard_id = Column(Integer, ForeignKey("ad_storyboards.id"), nullable=False)
    
    scene_num = Column(Integer, nullable=False)
    
    # Image prompt (Phase 7)
    image_prompt = Column(Text, nullable=True)
    image_generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)
    image_url = Column(String, nullable=True)
    image_status = Column(String, default="pending")
    
    # Video prompt (Phase 8)
    video_prompt = Column(Text, nullable=True)
    video_generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)
    video_url = Column(String, nullable=True)
    video_status = Column(String, default="pending")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    storyboard = relationship("AdStoryboard", back_populates="scene_prompts")


class AdConversation(Base):
    """Track the conversational flow for the ad campaign."""
    __tablename__ = "ad_conversations"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("ad_campaigns.id"), nullable=False)
    
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    phase = Column(Integer, nullable=True)  # Which phase this message belongs to
    content = Column(Text, nullable=False)
    
    # Metadata
    message_type = Column(String(50), nullable=True)  # "question", "answer", "iteration", "result"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaign = relationship("AdCampaign", back_populates="conversations")


class Workflow(Base):
    """Model for saving user workflows/node graphs."""
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Graph data stored as JSON
    nodes = Column(JSON, nullable=False, default=list)
    edges = Column(JSON, nullable=False, default=list)
    
    # Metadata
    node_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AiAvatarProject(Base):
    """
    Model for AI Video Avatar Pipeline.
    
    3-Step Pipeline:
    1. Generate Portrait (txt2img - FLUX-2 Klein)
    2. Generate Voice (txt2audio - Kokoro/Chatterbox)
    3. Animate (aud2video - LTX-2.3)
    """
    __tablename__ = "ai_avatar_projects"

    id = Column(Integer, primary_key=True, index=True)
    
    # User inputs
    name = Column(String(100), nullable=True)  # Project name
    portrait_prompt = Column(Text, nullable=False)  # Prompt for portrait generation
    speech_text = Column(Text, nullable=False)  # Text to convert to speech
    motion_prompt = Column(Text, nullable=True)  # Animation direction prompt
    
    # Voice settings
    voice_model = Column(String(50), default="Kokoro")  # Kokoro, Chatterbox
    voice_id = Column(String(50), default="af_sky")  # Voice ID
    voice_speed = Column(Float, default=1.0)
    voice_lang = Column(String(20), default="en-us")
    
    # Portrait settings
    portrait_model = Column(String(50), default="Flux_2_Klein_4B_BF16")
    portrait_width = Column(Integer, default=512)
    portrait_height = Column(Integer, default=512)
    
    # Animation settings
    animation_model = Column(String(50), default="Ltx2_3_22B_Dist_INT8")
    animation_frames = Column(Integer, default=97)  # min 49, max 241
    animation_fps = Column(Integer, default=24)  # fixed at 24 for LTX-2.3
    
    # Generation results with deAPI request_ids
    portrait_request_id = Column(String, nullable=True)  # deAPI request_id for portrait
    portrait_url = Column(String, nullable=True)  # Generated portrait URL
    portrait_generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)
    portrait_status = Column(String, default="pending")
    
    audio_request_id = Column(String, nullable=True)  # deAPI request_id for audio
    audio_url = Column(String, nullable=True)  # Generated audio URL
    audio_generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)
    audio_status = Column(String, default="pending")
    
    video_request_id = Column(String, nullable=True)  # deAPI request_id for video
    video_url = Column(String, nullable=True)  # Final animated video URL
    video_generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)
    video_status = Column(String, default="pending")
    
    # Current step (1=portrait, 2=audio, 3=video)
    current_step = Column(Integer, default=1)
    overall_status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


# ==============================================================================
# UGC AI ADS CREATOR - NEW MODELS
# ==============================================================================

class UgcAdStory(Base):
    """
    Model for UGC AI Ads Creator - Complete ad story with scenes and shots.
    
    This model stores the generated story structure including characters,
    product info, scenes, and shots that form a complete UGC ad.
    """
    __tablename__ = "ugc_ad_stories"

    id = Column(Integer, primary_key=True, index=True)
    
    # Story metadata
    title = Column(String(255), nullable=False)
    story_id = Column(String(100), unique=True, index=True, nullable=False)
    target_platform = Column(String(50), default="Instagram")
    total_duration_sec = Column(Integer, default=15)
    
    # Story content
    hook = Column(Text, nullable=False)
    cta = Column(Text, nullable=False)
    setting_description = Column(Text, nullable=True)
    
    # Characters (stored as JSON array)
    characters = Column(JSON, nullable=False, default=list)
    
    # Product info
    product_name = Column(String(255), nullable=False)
    product_category = Column(String(100), nullable=True)
    product_description = Column(Text, nullable=True)
    product_key_features = Column(JSON, nullable=True, default=list)
    product_visual_description = Column(Text, nullable=True)
    
    # Reference images
    character_reference_url = Column(String, nullable=True)
    product_reference_url = Column(String, nullable=True)
    
    # Inspiration prompts used
    inspiration_prompts = Column(JSON, nullable=True, default=list)
    
    # Status
    status = Column(String(50), default="draft")  # draft, generating, images_ready, videos_ready, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    scenes = relationship("UgcScene", back_populates="story", cascade="all, delete-orphan", order_by="UgcScene.scene_num")


class UgcScene(Base):
    """
    Model for a scene within a UGC ad story.
    Each scene contains multiple shots (5-second segments).
    """
    __tablename__ = "ugc_scenes"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("ugc_ad_stories.id"), nullable=False, index=True)
    
    # Scene metadata
    scene_num = Column(Integer, nullable=False)
    scene_name = Column(String(255), nullable=False)
    setting = Column(Text, nullable=True)
    mood = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    story = relationship("UgcAdStory", back_populates="scenes")
    shots = relationship("UgcShot", back_populates="scene", cascade="all, delete-orphan", order_by="UgcShot.shot_num")


class UgcShot(Base):
    """
    Model for a shot within a UGC scene.
    Each shot represents a 5-second video segment with first/last frames.
    """
    __tablename__ = "ugc_shots"

    id = Column(Integer, primary_key=True, index=True)
    scene_id = Column(Integer, ForeignKey("ugc_scenes.id"), nullable=False, index=True)
    
    # Shot metadata
    shot_num = Column(Integer, nullable=False)
    duration_sec = Column(Integer, default=5)
    
    # Content
    frame_description = Column(Text, nullable=False)  # For image generation
    action = Column(Text, nullable=True)
    dialogue = Column(Text, nullable=True)
    camera_angle = Column(String(100), nullable=True)
    lighting = Column(String(100), nullable=True)
    audio_notes = Column(Text, nullable=True)
    
    # Image generation (first frame)
    first_frame_prompt = Column(Text, nullable=True)
    first_frame_generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)
    first_frame_url = Column(String, nullable=True)
    first_frame_status = Column(String, default="pending")  # pending, processing, completed, failed
    
    # Image generation (last frame - optional, for transitions)
    last_frame_prompt = Column(Text, nullable=True)
    last_frame_generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)
    last_frame_url = Column(String, nullable=True)
    last_frame_status = Column(String, default="pending")
    
    # Video generation
    video_prompt = Column(Text, nullable=True)
    video_generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)
    video_url = Column(String, nullable=True)
    video_status = Column(String, default="pending")
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    scene = relationship("UgcScene", back_populates="shots")