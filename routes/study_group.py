from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database import crud

router = APIRouter(prefix="/study-groups", tags=["Study Groups"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a study group
@router.post("/")
def create_group(name: str, description: str, db: Session = Depends(get_db)):
    return crud.create_study_group(db, name, description)

# Join a study group
@router.post("/{group_id}/join/{user_id}")
def join_group(group_id: int, user_id: int, db: Session = Depends(get_db)):
    group = crud.join_group(db, group_id, user_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group or User not found")
    return {"message": f"User {user_id} joined group {group_id}"}

# Leave a study group
@router.post("/{group_id}/leave/{user_id}")
def leave_group(group_id: int, user_id: int, db: Session = Depends(get_db)):
    group = crud.leave_group(db, group_id, user_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group or User not found")
    return {"message": f"User {user_id} left group {group_id}"}

# List group members
@router.get("/{group_id}/members")
def list_members(group_id: int, db: Session = Depends(get_db)):
    members = crud.list_group_members(db, group_id)
    return {"group_id": group_id, "members": [m.name for m in members]}

# List groups of a user
@router.get("/user/{user_id}")
def list_user_groups(user_id: int, db: Session = Depends(get_db)):
    groups = crud.list_user_groups(db, user_id)
    return {"user_id": user_id, "groups": [g.name for g in groups]}
