from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from .database import Base


class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, nullable=True)  # deAPI request_id
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    model = Column(String, default="ZImageTurbo_INT8")
    
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
