"""Video generation job endpoints."""
import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.database import get_db_session
from app.models.job import Job, JobStatus, JobType

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


# Job response model - defined first since it's used by multiple endpoints
class JobResponse(BaseModel):
    """Response model for job data."""
    id: uuid.UUID
    job_type: JobType
    status: JobStatus
    input_html: Optional[str]
    input_css: Optional[str]
    input_json: Optional[dict]
    width: int
    height: int
    fps: int
    duration: float
    format: str
    output_path: Optional[str]
    output_url: Optional[str]
    file_size: Optional[int]
    error_message: Optional[str]
    progress: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Agent-friendly structured input schema for programmatic video generation
# This schema is designed for agent/LLM consumption and programmatic API use
class AgentJobCreate(BaseModel):
    """Minimal structured input for agent-created video jobs.
    
    Agents can use this schema to create video generation jobs with
    clearly defined, validated fields. All fields have defaults and
    validation constraints suitable for automated workflows.
    """
    job_type: JobType = Field(default=JobType.HTML_TO_VIDEO, description="Type of video generation job")
    input_html: Optional[str] = Field(default=None, description="HTML content for video generation")
    input_css: Optional[str] = Field(default=None, description="CSS styling for video generation")
    input_json: Optional[dict] = Field(default=None, description="JSON data for template rendering")
    width: int = Field(default=1920, ge=100, le=7680, description="Video width in pixels")
    height: int = Field(default=1080, ge=100, le=4320, description="Video height in pixels")
    fps: int = Field(default=30, ge=1, le=120, description="Frames per second")
    duration: float = Field(default=10.0, ge=0.1, le=3600.0, description="Video duration in seconds")
    format: str = Field(default="mp4", pattern="^(mp4|webm)$", description="Output video format")
    webhook_url: Optional[str] = Field(default=None, description="Callback URL on job completion")
    
    model_config = {
        "json_schema_extra": {
            "description": "Agent-friendly schema for programmatic video job creation"
        }
    }


# Agent API endpoint for programmatic video job creation
@router.post("/agent", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_agent_job(
    job_data: AgentJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
) -> JobResponse:
    """Create a video generation job using the agent-friendly API.
    
    This endpoint provides a structured, validated input schema designed
    for programmatic use by agents and LLMs. All fields have validation
    constraints and sensible defaults.
    
    Args:
        job_data: Structured input following the AgentJobCreate schema
        background_tasks: FastAPI background tasks dependency
        db: Database session dependency
    
    Returns:
        JobResponse with the created job details
    """
    # Use the job_type directly since it's already a JobType enum
    job_type_enum = job_data.job_type
    
    job = Job(
        job_type=job_type_enum,
        input_html=job_data.input_html,
        input_css=job_data.input_css,
        input_json=job_data.input_json,
        width=job_data.width,
        height=job_data.height,
        fps=job_data.fps,
        duration=job_data.duration,
        format=job_data.format,
        status=JobStatus.PENDING,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Queue background processing
    background_tasks.add_task(process_job, job.id)
    
    return JobResponse.model_validate(job)


# Standard job creation model (for web UI form submissions)
class JobCreate(BaseModel):
    """Request model for creating a video generation job."""
    job_type: JobType = JobType.HTML_TO_VIDEO
    input_html: Optional[str] = None
    input_css: Optional[str] = None
    input_json: Optional[dict] = None
    width: int = Field(default=1920, ge=100, le=7680)
    height: int = Field(default=1080, ge=100, le=4320)
    fps: int = Field(default=30, ge=1, le=120)
    duration: float = Field(default=10.0, ge=0.1, le=3600.0)
    format: str = Field(default="mp4", pattern="^(mp4|webm)$")
    webhook_url: Optional[str] = None


# Standard job list response
class JobListResponse(BaseModel):
    """Response model for paginated job list."""
    jobs: List[JobResponse]
    total: int
    page: int
    page_size: int


async def process_job(job_id: uuid.UUID) -> None:
    """Background async task to process a video generation job."""
    from app.core.database import get_session_factory
    from app.services.video_renderer import video_renderer
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return

        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        job.progress = 10
        db.commit()

        # Render video using the video rendering service
        import asyncio
        output_path = await video_renderer.render_job(job)
        job.progress = 90
        db.commit()

        job.output_path = output_path
        job.output_url = f"/api/jobs/{job_id}/download"
        job.file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.progress = 100
        db.commit()
        # Trigger webhook callback if webhook_url is set
        if job.webhook_url:
            await trigger_job_webhook(job.id, job.webhook_url, "completed")

    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()
        # Trigger webhook callback on failure if webhook_url is set
        if job.webhook_url:
            await trigger_job_webhook(job.id, job.webhook_url, "failed")
    finally:
        db.close()


async def trigger_job_webhook(job_id: uuid.UUID, webhook_url: str, status: str) -> None:
    """Trigger a webhook callback for a job status change."""
    import httpx
    
    payload = {
        "job_id": str(job_id),
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Support both HTTP and HTTPS webhooks
            if webhook_url.startswith("http://") or webhook_url.startswith("https://"):
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
            else:
                # Assume it's a URL we can post to directly
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
    except httpx.HTTPError as e:
        # Log webhook failure but don't fail the job
        print(f"Webhook delivery failed for job {job_id}: {e}")
    except Exception as e:
        print(f"Unexpected webhook error for job {job_id}: {e}")


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
) -> JobResponse:
    """Create a new video generation job."""
    job = Job(
        job_type=job_data.job_type,
        input_html=job_data.input_html,
        input_css=job_data.input_css,
        input_json=job_data.input_json,
        width=job_data.width,
        height=job_data.height,
        fps=job_data.fps,
        duration=job_data.duration,
        format=job_data.format,
        status=JobStatus.PENDING,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Queue background processing
    background_tasks.add_task(process_job, job.id)

    return JobResponse.model_validate(job)


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[JobStatus] = None,
    job_type_filter: Optional[JobType] = None,
    db: Session = Depends(get_db_session),
) -> JobListResponse:
    """List video generation jobs with pagination and filtering."""
    query = db.query(Job)

    if status_filter:
        query = query.filter(Job.status == status_filter)
    if job_type_filter:
        query = query.filter(Job.job_type == job_type_filter)

    total = query.count()
    jobs = query.order_by(Job.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return JobListResponse(
        jobs=[JobResponse.model_validate(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: uuid.UUID, db: Session = Depends(get_db_session)) -> JobResponse:
    """Get a specific job by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job)


@router.get("/{job_id}/status")
async def get_job_status(job_id: uuid.UUID, db: Session = Depends(get_db_session)) -> dict:
    """Get job status (lightweight endpoint for polling)."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "status": job.status,
        "progress": job.progress,
        "error_message": job.error_message,
    }


@router.get("/{job_id}/download")
async def download_job(job_id: uuid.UUID, db: Session = Depends(get_db_session)) -> dict:
    """Get download URL for completed job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job not completed")

    if not job.output_path:
        raise HTTPException(status_code=404, detail="Output file not found")

    return {
        "url": job.output_url,
        "filename": f"{job_id}.{job.format}",
        "size": job.file_size,
    }


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_job(job_id: uuid.UUID, db: Session = Depends(get_db_session)) -> None:
    """Cancel a pending or queued job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status not in [JobStatus.PENDING, JobStatus.QUEUED]:
        raise HTTPException(status_code=400, detail="Cannot cancel job in current state")

    job.status = JobStatus.CANCELLED
    job.completed_at = datetime.utcnow()
    db.commit()
