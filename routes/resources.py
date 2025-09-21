from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from auth.utils import get_current_user
from database.db import SessionLocal
from database import crud, models

router = APIRouter(prefix="/resources", tags=["Resources"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---- Create Resource ----
@router.post("/")
def create_resource(title: str, url: str, type: str, course_id: int | None = None, db: Session = Depends(get_db)):
    return crud.create_resource(db, title, url, type, course_id)


# ---- Upload PDF ----
@router.post("/upload_pdf/")
def upload_pdf(course_id: int, title: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    return crud.upload_pdf_resource(db, file, course_id, title)


# ---- List Resources ----
@router.get("/")
def list_resources(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.list_resources(db)



# ---- Delete Resource ----
@router.delete("/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    success = crud.delete_resource(db, resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": "Resource deleted successfully"}


# ---- Generate AI Resources for Weak Courses ----
@router.post("/generate_ai_resources/{user_id}")
def generate_ai_resources(user_id: int, db: Session = Depends(get_db)):
    resources = crud.generate_ai_resources_for_weak_courses(db, user_id)
    return {"generated_resources": resources}
