"""Tests for job endpoints."""
import pytest
from httpx import AsyncClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.main import app
from app.models.job import JobStatus, JobType


@pytest.mark.asyncio
async def test_create_job():
    """Test creating a video generation job."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/jobs",
            json={
                "job_type": "html_to_video",
                "input_html": "<html><body>Hello</body></html>",
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "duration": 5,
                "format": "mp4",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"
        assert data["job_type"] == "html_to_video"
        assert data["width"] == 1920
        assert data["height"] == 1080


@pytest.mark.asyncio
async def test_create_job_validation():
    """Test job creation validation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Invalid width
        response = await client.post(
            "/api/jobs",
            json={
                "job_type": "html_to_video",
                "width": 50,  # Too small
            },
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_jobs():
    """Test listing jobs."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data


@pytest.mark.asyncio
async def test_get_job():
    """Test getting a specific job."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a job first
        create_response = await client.post(
            "/api/jobs",
            json={"job_type": "html_to_video", "input_html": "<html>Test</html>"},
        )
        job_id = create_response.json()["id"]

        # Get the job
        response = await client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id


@pytest.mark.asyncio
async def test_get_job_not_found():
    """Test getting non-existent job."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        import uuid
        fake_id = uuid.uuid4()
        response = await client.get(f"/api/jobs/{fake_id}")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_status():
    """Test job status endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        create_response = await client.post(
            "/api/jobs",
            json={"job_type": "html_to_video", "input_html": "<html>Test</html>"},
        )
        job_id = create_response.json()["id"]

        response = await client.get(f"/api/jobs/{job_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert "status" in data
        assert "progress" in data
