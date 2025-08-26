from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional


class UserBase(BaseModel):
    name: Optional[str] = None
    email: EmailStr


class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)
    role: str | None = "user"

    @validator("password")
    def validate_password_strength(cls, v):
        if " " in v:
            raise ValueError("Password cannot contain spaces")
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: constr(min_length=3, max_length=50) | None = None
    email: EmailStr | None = None
    role: str | None = None
    password: constr(min_length=8) | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str
