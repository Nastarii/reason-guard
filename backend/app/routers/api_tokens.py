from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import hashlib

from app.database import get_db
from app.models.user import User
from app.models.api_token import ApiToken, generate_token
from app.schemas.api_token import (
    ApiTokenCreate,
    ApiTokenResponse,
    ApiTokenCreatedResponse,
    ApiTokenUpdate,
)
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api-tokens", tags=["API Tokens"])


def hash_token(token: str) -> str:
    """Hash a token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


@router.get("", response_model=List[ApiTokenResponse])
async def list_tokens(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos os tokens do usuário."""
    tokens = (
        db.query(ApiToken)
        .filter(ApiToken.user_id == current_user.id)
        .order_by(ApiToken.created_at.desc())
        .all()
    )
    return tokens


@router.post("", response_model=ApiTokenCreatedResponse)
async def create_token(
    token_data: ApiTokenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria um novo token de API."""
    # Generate the token
    raw_token = generate_token()
    token_hash = hash_token(raw_token)
    token_prefix = raw_token[:10]

    # Create the token record
    db_token = ApiToken(
        user_id=current_user.id,
        name=token_data.name,
        token_hash=token_hash,
        token_prefix=token_prefix,
        description=token_data.description,
        expires_at=token_data.expires_at,
    )

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return ApiTokenCreatedResponse(
        id=db_token.id,
        name=db_token.name,
        token=raw_token,
        token_prefix=token_prefix,
        description=db_token.description,
        expires_at=db_token.expires_at,
        created_at=db_token.created_at,
    )


@router.get("/{token_id}", response_model=ApiTokenResponse)
async def get_token(
    token_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtém detalhes de um token específico."""
    token = (
        db.query(ApiToken)
        .filter(ApiToken.id == token_id, ApiToken.user_id == current_user.id)
        .first()
    )

    if not token:
        raise HTTPException(status_code=404, detail="Token não encontrado")

    return token


@router.patch("/{token_id}", response_model=ApiTokenResponse)
async def update_token(
    token_id: str,
    token_data: ApiTokenUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualiza um token existente."""
    token = (
        db.query(ApiToken)
        .filter(ApiToken.id == token_id, ApiToken.user_id == current_user.id)
        .first()
    )

    if not token:
        raise HTTPException(status_code=404, detail="Token não encontrado")

    update_data = token_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(token, key, value)

    db.commit()
    db.refresh(token)

    return token


@router.delete("/{token_id}")
async def delete_token(
    token_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove um token."""
    token = (
        db.query(ApiToken)
        .filter(ApiToken.id == token_id, ApiToken.user_id == current_user.id)
        .first()
    )

    if not token:
        raise HTTPException(status_code=404, detail="Token não encontrado")

    db.delete(token)
    db.commit()

    return {"message": "Token removido com sucesso"}


@router.post("/{token_id}/revoke", response_model=ApiTokenResponse)
async def revoke_token(
    token_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revoga (desativa) um token."""
    token = (
        db.query(ApiToken)
        .filter(ApiToken.id == token_id, ApiToken.user_id == current_user.id)
        .first()
    )

    if not token:
        raise HTTPException(status_code=404, detail="Token não encontrado")

    token.is_active = False
    db.commit()
    db.refresh(token)

    return token
