from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default=ProjectStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    scenes = relationship("Scene", back_populates="project", cascade="all, delete-orphan")
    output_video_path = Column(String(500), nullable=True)


class Scene(Base):
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    order = Column(Integer, default=0)
    prompt = Column(Text, nullable=False)
    reference_image_path = Column(String(500), nullable=True)
    audio_path = Column(String(500), nullable=True)
    generated_image_url = Column(String(500), nullable=True)
    generated_video_url = Column(String(500), nullable=True)
    video_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="scenes")
