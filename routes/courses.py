from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database import crud
from schemas import schemas

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.CourseResponse)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    db_course = crud.get_course_by_code(db, course.code)
    if db_course:
        raise HTTPException(status_code=400, detail="Course already exists")

    return crud.create_course(
        db,
        code=course.code,
        title=course.title,
        level=course.level,
        department_ids=course.department_ids
    )


@router.get("/", response_model=list[schemas.CourseResponse])
def list_courses(db: Session = Depends(get_db)):
    return crud.list_courses(db)

@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    success = crud.delete_course(db, course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted successfully"}

