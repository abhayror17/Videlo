from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from .database import Base


class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, nullable=True)  # deAPI request_id
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    model = Column(String, default="Flux_2_Klein_4B_BF16")
    
    # Generation type: text2img, img2video
    generation_type = Column(String, default="text2img")
    
    # Image dimensions
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # Video-specific fields
    frames = Column(Integer, nullable=True)
    fps = Column(Integer, nullable=True)
    
    # Generation parameters
    guidance = Column(Float, nullable=True)
    steps = Column(Integer, nullable=True)
    seed = Column(Integer, nullable=True)
    
    status = Column(String, default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100 progress percentage
    remote_url = Column(String, nullable=True)  # Result URL
    thumbnail_url = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
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
