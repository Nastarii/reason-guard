from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ApiTokenCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    expires_at: Optional[datetime] = None


class ApiTokenResponse(BaseModel):
    id: UUID
    name: str
    token_prefix: str
    description: Optional[str]
    is_active: bool
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ApiTokenCreatedResponse(BaseModel):
    id: UUID
    name: str
    token: str
    token_prefix: str
    description: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime
    message: str = "Guarde este token com segurança. Ele não será exibido novamente."

    class Config:
        from_attributes = True


class ApiTokenUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
