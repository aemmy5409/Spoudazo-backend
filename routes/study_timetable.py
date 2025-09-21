from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database import crud
from utils.parser import parse_timetable
from utils.timetable_generator import generate_personalized_timetable

router = APIRouter(prefix="/study-timetable", tags=["Study Timetable"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/generate")
async def generate_timetable(
    user_id: int,
    file: UploadFile = File(...),
    preferred_time: str = Form(...),
    hours_per_day: int = Form(...),
    difficult_courses: str = Form(""),
    break_minutes: int = Form(15),
    db: Session = Depends(get_db)
):
    try:
        contents = await file.read()
        school_timetable = parse_timetable(contents, file.filename)

        habits = crud.save_study_habits(
            db, user_id, preferred_time, hours_per_day, difficult_courses, break_minutes
        )

        personalized = generate_personalized_timetable(school_timetable, habits)

        crud.save_timetable_from_parsed_data(db, user_id, personalized)

        # save as resource
        timetable_url = f"/resources/timetable/{user_id}.json"  # fake path for now
        crud.create_resource(db, None, f"Timetable for User {user_id}", timetable_url)

        return {"message": "Personalized timetable created", "timetable": personalized}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate timetable: {e}")
