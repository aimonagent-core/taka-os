# File: app/schemas/auth.py
# Purpose: Authentication-related Pydantic schemas
# Dependencies: pydantic, email-validator

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str | None = None
    tenant_name: str | None = None


class UserLogin(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str
    mfa_code: str | None = None


class TokenResponse(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    mfa_required: bool = False
    mfa_token: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: str | None
    role: str
    is_active: bool
    tenant_id: str
    mfa_enabled: bool
    created_at: datetime


class InvitationCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    role: str


class InvitationAccept(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    token: str
    password: str = Field(..., min_length=8)
    full_name: str | None = None
