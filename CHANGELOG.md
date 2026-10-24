# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-24

### Added
- Initial FastAPI backend with health endpoints
- Job management API (create, list, get, status, download, cancel)
- SQLite/PostgreSQL database with SQLAlchemy models
- OIDC authentication with Keycloak integration
- React + TypeScript + Vite frontend
- Job dashboard with filtering and pagination
- Job creation form with validation
- Job detail page with live status polling
- Docker Compose with backend, frontend, PostgreSQL, Keycloak
- Comprehensive test suite (backend + frontend)
- CI/CD pipeline configuration

### Security
- OIDC authorization code flow with PKCE
- Role-based access control (viewer/operator/admin)
- HttpOnly cookies with CSRF protection
- No hardcoded secrets or demo mode in production

## [Unreleased]

### Planned
- Headless browser video rendering engine
- Scene composition with timeline editor
- Webhook callbacks for job completion
- Template library for common video formats
- GPU-accelerated rendering support
