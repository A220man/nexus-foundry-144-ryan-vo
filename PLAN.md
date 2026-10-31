# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

video-engine

## Roadmap

### skeleton — FastAPI + React skeleton with one workflow

Status: done

Acceptance:
- FastAPI app with health endpoint
- React + TypeScript + Vite frontend
- Docker compose with backend, frontend, Keycloak
- Basic video generation job workflow (create, poll, download)

Implementation: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/core/database.py`, `backend/app/core/security.py`, `backend/app/models/job.py`, `backend/app/models/user.py`, `backend/app/api/routes/health.py`, `backend/app/api/routes/jobs.py`, `backend/requirements.txt`, `backend/Dockerfile`, `backend/tests/test_health.py`, `backend/tests/test_jobs.py`, `frontend/package.json`, `frontend/vite.config.ts`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/types/index.ts`, `frontend/src/api/client.ts`, `frontend/src/hooks/useJobs.ts`, `frontend/src/components/JobCard.tsx`, `frontend/src/components/JobForm.tsx`, `frontend/src/components/JobList.tsx`, `frontend/src/pages/JobDetail.tsx`, `frontend/Dockerfile`, `frontend/nginx.conf`, `docker-compose.yaml`, `.env.example`, `.gitignore`, `README.md`, `CHANGELOG.md`, `LICENSE`, `pyproject.toml`, `portfolio.json`, `.github/workflows/ci.yml`

Tests: `backend/tests/test_health.py`, `backend/tests/test_jobs.py`, `frontend/src/__tests__/App.test.tsx`

### video-engine — Core video rendering engine

Status: in_progress

Acceptance:
- HTML-to-video rendering using headless browser
- Scene composition with timeline
- Export to MP4/WebM

Implementation: `backend/app/services/video_renderer.py`, `backend/requirements.txt`, `backend/Dockerfile`, `backend/app/api/routes/jobs.py`

### agent-api — Agent-friendly API for programmatic video generation

Status: planned

Acceptance:
- Structured input schema for video jobs
- Job status polling endpoint
- Webhook callback on completion

