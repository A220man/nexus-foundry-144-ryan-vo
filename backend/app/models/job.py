"""Video generation job models."""
import enum
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, Enum, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base


class JobType(str, enum.Enum):
    """Type of video generation job."""
    HTML_TO_VIDEO = "html_to_video"
    SCENE_RENDER = "scene_render"
    TEMPLATE_RENDER = "template_render"


class JobStatus(str, enum.Enum):
    """Status of a video generation job."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(Base):
    """Video generation job model."""

    __tablename__ = "jobs"
    __allow_unmapped__ = True

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type: Mapped[JobType] = mapped_column(Enum(JobType), nullable=False, default=JobType.HTML_TO_VIDEO)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), nullable=False, default=JobStatus.PENDING)

    # Input data
    input_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    input_css: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    input_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Render options
    width: Mapped[int] = mapped_column(Integer, default=1920)
    height: Mapped[int] = mapped_column(Integer, default=1080)
    fps: Mapped[int] = mapped_column(Integer, default=30)
    duration: Mapped[float] = mapped_column(Integer, default=10)
    format: Mapped[str] = mapped_column(String(20), default="mp4")

    # Output
    output_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    output_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Metadata
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="jobs")

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, type={self.job_type}, status={self.status})>"
