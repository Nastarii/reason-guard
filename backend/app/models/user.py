from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_user_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reasoning_traces = relationship("ReasoningTrace", back_populates="user")
    path_analyses = relationship("PathAnalysis", back_populates="user")
    logic_graphs = relationship("LogicGraph", back_populates="user")
    consistency_checks = relationship("ConsistencyCheck", back_populates="user")
    audit_reports = relationship("AuditReport", back_populates="user")
    api_tokens = relationship("ApiToken", back_populates="user", cascade="all, delete-orphan")
