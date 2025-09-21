# routes/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database import crud, models
from schemas.users import UserCreate, UserUpdate, UserResponse
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    existing = crud.get_user_by_matric_no(db, user.matric_no)
    if existing:
        raise HTTPException(status_code=400, detail="User with this matric_no already exists")
    created = crud.create_user(
        db,
        matric_no=user.matric_no,
        name=user.name,
        email=user.email,
        password=user.password,
        department=user.department,
        level=user.level
    )
    return created


@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """Get all users"""
    return crud.list_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a single user by ID"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    """Update user details"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
