from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    name: Optional[str] = None
    email: EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str | None = "user"


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str
