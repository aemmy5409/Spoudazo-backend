import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database import crud, models
import os

router = APIRouter(prefix="/generate-test", tags=["AI Test Generator"])

# Setup Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{course_id}/user/{user_id}")
def generate_test(course_id: int, user_id: int, num_questions: int = 10, db: Session = Depends(get_db)):
    # Get course
    course = crud.get_course_by_code(db, db.query(models.Course).filter(models.Course.id == course_id).first().code)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Ask Gemini to generate MCQs
    model = genai.GenerativeModel("gemini-1.5-pro")
    prompt = f"""
    Generate {num_questions} multiple-choice questions for the course {course.code} - {course.title}.
    Provide each question with 4 options (A, B, C, D) and the correct answer.
    Format as JSON list: 
    [{{"question": "...", "options": ["A", "B", "C", "D"], "answer": "A"}}]
    """
    response = model.generate_content(prompt)
    try:
        questions = eval(response.text)  # quick parse (could replace with json.loads)
    except:
        raise HTTPException(status_code=500, detail="Failed to parse Gemini output")

    # Save placeholder test result (score = 0 until user answers)
    test = crud.create_test(db, user_id=user_id, course_id=course_id, score=0)

    return {
        "test_id": test.id,
        "course": course.code,
        "questions": questions
    }
