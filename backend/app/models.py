from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Boolean, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """User model with credit balance tracking."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    credits_balance = Column(Integer, default=0)
    total_credits_purchased = Column(Integer, default=0)
    total_credits_used = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    credit_transactions = relationship("CreditTransaction", back_populates="user")
    generations = relationship("Generation", back_populates="user")


class CreditTransaction(Base):
    """Model for tracking all credit transactions."""
    __tablename__ = "credit_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # positive for purchases/bonus, negative for usage
    balance_after = Column(Integer, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # 'purchase', 'generation', 'refund', 'bonus', 'signup'
    description = Column(Text, nullable=True)
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)  # Link to generation if applicable
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="credit_transactions")


class CreditPackage(Base):
    """Model for credit purchase packages."""
    __tablename__ = "credit_packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)
    price_cents = Column(Integer, nullable=False)
    bonus_percent = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


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
    
    # Credit tracking
    credits_charged = Column(Integer, nullable=True)  # Credits deducted for this generation
    
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100 progress percentage
    remote_url = Column(String, nullable=True)  # Result URL
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
    """Model for AI Ads Generator pipeline - tracks the full ad creation workflow."""
    __tablename__ = "ad_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    
    # User input
    user_prompt = Column(Text, nullable=False)
    brand_name = Column(String, nullable=True)
    brand_description = Column(Text, nullable=True)
    
    # Pipeline status
    current_step = Column(String, default="init")  # init, enhancing, script, image, video, qa, completed, failed
    
    # Step 1: Prompt Enhancement
    enhanced_prompt = Column(Text, nullable=True)
    enhancement_status = Column(String, default="pending")  # pending, processing, completed, failed
    
    # Step 2: Script Generation
    script = Column(Text, nullable=True)
    script_status = Column(String, default="pending")  # pending, processing, completed, failed
    script_feedback = Column(Text, nullable=True)
    script_request_id = Column(String, nullable=True)  # For tracking LLM request
    
    # Step 3: Image Generation
    image_url = Column(String, nullable=True)
    image_status = Column(String, default="pending")  # pending, processing, completed, failed
    image_feedback = Column(Text, nullable=True)
    image_request_id = Column(String, nullable=True)  # deAPI request_id
    image_generation_id = Column(Integer, nullable=True)  # Link to Generation model
    
    # Step 4: Video Generation
    video_url = Column(String, nullable=True)
    video_status = Column(String, default="pending")  # pending, processing, completed, failed
    video_feedback = Column(Text, nullable=True)
    video_request_id = Column(String, nullable=True)  # deAPI request_id
    video_generation_id = Column(Integer, nullable=True)  # Link to Generation model
    
    # QA Results
    qa_status = Column(String, default="pending")  # pending, processing, approved, rejected
    qa_feedback = Column(Text, nullable=True)
    qa_details = Column(Text, nullable=True)  # JSON string with detailed QA results
    qa_iterations = Column(Integer, default=0)  # Number of QA iterations
    
    # Overall status
    overall_status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


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
