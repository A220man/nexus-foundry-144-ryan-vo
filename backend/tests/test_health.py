"""Tests for health endpoints."""
import pytest
from httpx import AsyncClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test basic health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_readiness_check():
    """Test readiness check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
