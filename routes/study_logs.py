from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database import crud

router = APIRouter(prefix="/study-groups", tags=["Study Groups"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new study group
@router.post("/")
def create_study_group(name: str, description: str, db: Session = Depends(get_db)):
    return crud.create_study_group(db, name, description)

# Join a group
@router.post("/{group_id}/join")
def join_group(group_id: int, user_id: int, db: Session = Depends(get_db)):
    return crud.join_group(db, group_id, user_id)

# Leave a group
@router.post("/{group_id}/leave")
def leave_group(group_id: int, user_id: int, db: Session = Depends(get_db)):
    return crud.leave_group(db, group_id, user_id)

# List all members of a group
@router.get("/{group_id}/members")
def list_group_members(group_id: int, db: Session = Depends(get_db)):
    return crud.list_group_members(db, group_id)

# List all groups a user belongs to
@router.get("/user/{user_id}")
def list_user_groups(user_id: int, db: Session = Depends(get_db)):
    return crud.list_user_groups(db, user_id)
