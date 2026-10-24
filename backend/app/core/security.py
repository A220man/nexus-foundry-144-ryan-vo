"""Security utilities for OIDC/JWT authentication."""
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from app.core.config import get_settings


@dataclass
class TokenData:
    """Decoded token data."""
    sub: str
    iss: str
    aud: str
    exp: int
    iat: int
    email: Optional[str] = None
    preferred_username: Optional[str] = None
    name: Optional[str] = None
    roles: list[str] = None

    def __post_init__(self):
        if self.roles is None:
            self.roles = []


class SecurityManager:
    """Manages OIDC/JWT token validation."""

    def __init__(self):
        self.settings = get_settings()
        self._jwks_cache: Optional[dict] = None
        self._jwks_fetched_at: Optional[datetime] = None

    def _get_jwks_url(self) -> str:
        """Get JWKS URL from OIDC discovery or Keycloak config."""
        issuer = self.settings.oidc_issuer_url or f"{self.settings.keycloak_url}/realms/{self.settings.keycloak_realm}"
        return f"{issuer}/protocol/openid-connect/certs"

    async def get_jwks(self) -> dict:
        """Fetch JWKS from Keycloak (cached for 1 hour)."""
        import httpx
        now = datetime.utcnow()
        if (
            self._jwks_cache
            and self._jwks_fetched_at
            and (now - self._jwks_fetched_at).total_seconds() < 3600
        ):
            return self._jwks_cache

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self._get_jwks_url())
            response.raise_for_status()
            self._jwks_cache = response.json()
            self._jwks_fetched_at = now
            return self._jwks_cache

    def _get_signing_key(self, jwks: dict, kid: str) -> str:
        """Extract signing key from JWKS."""
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        raise ValueError(f"Signing key not found for kid: {kid}")

    async def validate_token(self, token: str) -> TokenData:
        """Validate OIDC access token."""
        try:
            # Decode header to get key ID
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            if not kid:
                raise ValueError("Token missing kid header")

            # Get JWKS and signing key
            jwks = await self.get_jwks()
            key = self._get_signing_key(jwks, kid)

            # Validate token
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self.settings.keycloak_client_id,
                issuer=self.settings.oidc_issuer_url or f"{self.settings.keycloak_url}/realms/{self.settings.keycloak_realm}",
            )
            return TokenData(**payload)

        except JWTError as e:
            raise ValueError(f"Invalid OIDC token: {e}")
        except Exception as e:
            raise ValueError(f"Token validation failed: {e}")


security_manager = SecurityManager()
