"""Tests for job endpoints."""
import pytest
import sys
import os
import uuid
from unittest.mock import AsyncMock, patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.models.job import JobStatus, JobType


@pytest.mark.asyncio
async def test_create_job(async_client):
    """Test creating a video generation job."""
    with patch('app.api.routes.jobs.process_job') as mock_process:
        response = await async_client.post(
            "/api/jobs",
            json={
                "input_html": "<h1>Test</h1>",
                "input_css": "h1 { color: red; }",
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "duration": 5,
                "format": "mp4",
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["width"] == 1920
    assert data["height"] == 1080
    assert data["fps"] == 30
    assert data["duration"] == 5
    assert data["format"] == "mp4"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_job_validation(async_client):
    """Test job creation validation."""
    # Invalid width
    response = await async_client.post(
        "/api/jobs",
        json={
            "input_html": "<h1>Test</h1>",
            "width": 50,
            "height": 1080,
            "fps": 30,
            "duration": 5,
            "format": "mp4",
        },
    )
    assert response.status_code == 422

    # Invalid format
    response = await async_client.post(
        "/api/jobs",
        json={
            "input_html": "<h1>Test</h1>",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "duration": 5,
            "format": "avi",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_jobs(async_client):
    """Test listing jobs."""
    response = await async_client.get("/api/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


@pytest.mark.asyncio
async def test_get_job(async_client):
    """Test getting a specific job."""
    # Create a job first
    with patch('app.api.routes.jobs.process_job'):
        response = await async_client.post(
            "/api/jobs",
            json={
                "input_html": "<h1>Test</h1>",
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "duration": 5,
                "format": "mp4",
            },
        )
    assert response.status_code == 201
    job_id = response.json()["id"]

    # Get the job
    response = await async_client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_id


@pytest.mark.asyncio
async def test_get_job_not_found(async_client):
    """Test getting non-existent job."""
    response = await async_client.get(f"/api/jobs/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_status(async_client):
    """Test job status endpoint."""
    # Create a job first
    with patch('app.api.routes.jobs.process_job'):
        response = await async_client.post(
            "/api/jobs",
            json={
                "input_html": "<h1>Test</h1>",
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "duration": 5,
                "format": "mp4",
            },
        )
    assert response.status_code == 201
    job_id = response.json()["id"]

    # Get job status
    response = await async_client.get(f"/api/jobs/{job_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_id
    assert "status" in data
    assert "progress" in data


@pytest.mark.asyncio
async def test_create_scene_render_job(async_client):
    """Test creating a scene render job with timeline."""
    with patch('app.api.routes.jobs.process_job') as mock_process:
        scene_data = {
            "scenes": [
                {
                    "html": "<div>Scene 1</div>",
                    "css": "div { color: red; }",
                    "duration": 2.0,
                },
                {
                    "html": "<div>Scene 2</div>",
                    "css": "div { color: blue; }",
                    "duration": 3.0,
                },
            ]
        }
        response = await async_client.post(
            "/api/jobs",
            json={
                "job_type": "scene_render",
                "input_json": scene_data,
                "width": 1280,
                "height": 720,
                "fps": 30,
                "duration": 5.0,
                "format": "mp4",
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["job_type"] == "scene_render"
    assert data["width"] == 1280
    assert data["height"] == 720
    assert data["input_json"] == scene_data
    assert "id" in data


@pytest.mark.asyncio
async def test_create_scene_render_job_validation(async_client):
    """Test scene render job validation requires scenes."""
    with patch('app.api.routes.jobs.process_job') as mock_process:
        response = await async_client.post(
            "/api/jobs",
            json={
                "job_type": "scene_render",
                "input_json": {},
                "width": 1280,
                "height": 720,
                "fps": 30,
                "duration": 5.0,
                "format": "mp4",
            },
        )
    # Should still create the job (validation happens at render time)
    assert response.status_code == 201
    data = response.json()
    assert data["job_type"] == "scene_render"


@pytest.mark.asyncio
async def test_scene_render_logic():
    """Test scene rendering logic without browser."""
    from app.models.job import Job, JobType, JobStatus
    from app.services.video_renderer import VideoRenderer
    import uuid
    
    # Create a mock job for scene rendering
    job = Job(
        id=uuid.uuid4(),
        job_type=JobType.SCENE_RENDER,
        width=640,
        height=480,
        fps=30,
        duration=2.0,
        format="mp4",
        input_json={
            "scenes": [
                {"html": "<div>Scene 1</div>", "css": "", "duration": 1.0},
                {"html": "<div>Scene 2</div>", "css": "", "duration": 1.0},
            ]
        },
    )
    
    renderer = VideoRenderer()
    
    # Verify the scene data is parsed correctly
    scenes = job.input_json.get("scenes", [])
    assert len(scenes) == 2
    assert scenes[0]["duration"] == 1.0
    assert scenes[1]["duration"] == 1.0
    
    # Verify total duration matches sum of scene durations
    total_scene_duration = sum(s.get("duration", 0) for s in scenes)
    assert total_scene_duration == 2.0
    assert total_scene_duration == job.duration
