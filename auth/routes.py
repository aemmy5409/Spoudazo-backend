from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm  import Session
from database.db import SessionLocal
from database import models
from . import schemas
from .schemas import UserResponse
from auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_reset_token,
    verify_reset_token,
)
from utils.email_service import send_reset_email
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Auth"])

# --- DB Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- Normal Signup --------
@router.post("/signup", response_model=UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        matric_no=user.matric_no,
        password=hashed_pw,
        department=user.department,
        level=user.level,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# -------- Normal Login --------
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Note: form_data.username is what user enters in "username" field (use matric_no if you want)
    user = db.query(models.User).filter(models.User.matric_no == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}



# -------- Google Login --------
@router.post("/google-login")
def google_login(request: schemas.GoogleLoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()

    if not user:
        # create account with null matric_no
        user = models.User(
            name=request.name,
            email=request.email,
            is_google_user=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"requires_matric": True, "message": "Please provide matric number", "user_id": user.id}

    if not user.matric_no:
        return {"requires_matric": True, "message": "Please provide matric number", "user_id": user.id}

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}


# --- Matric Update for Google Users ---
@router.patch("/add-matric/{user_id}")
def add_matric(user_id: int, update: schemas.MatricUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or not user.is_google_user:
        raise HTTPException(status_code=404, detail="User not found or not a Google user")

    if user.matric_no:
        raise HTTPException(status_code=400, detail="Matric already set")

    user.matric_no = update.matric_no
    user.department = update.department
    user.level = update.level
    db.commit()
    return {"message": "Matric info updated successfully"}


# -------- Forgot Password --------
@router.post("/forgot-password")
def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_reset_token(user.email)
    email_sent = send_reset_email(user.email, reset_token)

    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send reset email")

    return {"message": "Password reset link sent to your email"}


# -------- Reset Password --------
@router.post("/reset-password")
def reset_password(request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    email = verify_reset_token(request.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(request.new_password)
    db.commit()

    return {"message": "Password reset successfully"}
