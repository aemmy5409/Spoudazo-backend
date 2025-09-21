# schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from pydantic import ConfigDict


class UserBase(BaseModel):
    matric_no: Optional[str] = None
    name: str
    email: EmailStr
    department: Optional[str] = None
    level: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    matric_no: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    level: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_google_user: bool

    model_config = ConfigDict(from_attributes=True)
