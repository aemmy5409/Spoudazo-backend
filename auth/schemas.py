from pydantic import BaseModel, EmailStr
from typing import Optional
from pydantic import ConfigDict


# ----------- Shared ----------- #
class UserBase(BaseModel):
    name: str
    email: EmailStr
    matric_no: Optional[str] = None
    department: Optional[str] = None
    level: Optional[str] = None


# ----------- Create User ----------- #
class UserCreate(UserBase):
    password: str


# ----------- Response Schema ----------- #
class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # ✅ replaces orm_mode=True


# ----------- Login ----------- #
class LoginRequest(BaseModel):
    matric_no: str
    password: str


# ----------- Google Login ----------- #
class GoogleLoginRequest(BaseModel):
    name: str
    email: EmailStr


class MatricUpdate(BaseModel):
    matric_no: str
    department: str
    level: str


# ----------- Password Reset ----------- #
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
