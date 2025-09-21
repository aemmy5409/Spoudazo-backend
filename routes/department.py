from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database import crud
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- SCHEMAS ----------
class DepartmentCreate(BaseModel):
    name: str

# ---------- ROUTES ----------
@router.post("/")
def create_department(dept: DepartmentCreate, db: Session = Depends(get_db)):
    existing = crud.get_department_by_name(db, dept.name)
    if existing:
        raise HTTPException(status_code=400, detail="Department already exists")
    return crud.create_department(db, dept.name)

@router.get("/")
def list_departments(db: Session = Depends(get_db)):
    return crud.list_departments(db)

@router.delete("/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    success = crud.delete_department(db, dept_id)
    if not success:
        raise HTTPException(status_code=404, detail="Department not found")
    return {"message": "Department deleted successfully"}
