"""User models for authentication and authorization."""
import enum
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


# Association table for user roles (many-to-many)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", PG_UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("role", Enum(UserRole), primary_key=True),
)


class User(Base):
    """User model with OIDC integration."""

    __tablename__ = "users"
    __allow_unmapped__ = True

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # OIDC identifiers
    subject: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, index=True)
    issuer: Mapped[str] = mapped_column(String(512), nullable=False)

    # Profile
    email: Mapped[Optional[str]] = mapped_column(String(256), unique=True, nullable=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(128), unique=True, nullable=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    jobs = relationship("Job", back_populates="user", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

    def has_role(self, role: UserRole) -> bool:
        """Check if user has a specific role."""
        # This would need a query to the user_roles table in real implementation
        return self.is_superuser

    def is_operator_or_admin(self) -> bool:
        """Check if user is operator or admin."""
        return self.is_superuser
