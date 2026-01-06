"""
Authentication Schemas
"""
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """User registration request"""
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str


class Token(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response"""
    id: int
    username: str
    email: str
    is_active: bool
    role: str

    class Config:
        from_attributes = True

