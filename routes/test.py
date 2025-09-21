# routes/test.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google import genai
from dotenv import load_dotenv
import os
import json
import re

from auth.utils import get_current_user
from database.db import SessionLocal
from database import crud, models


load_dotenv()

router = APIRouter(prefix="/tests", tags=["Tests"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Select a Course for Test ----------
@router.get("/select-course/{user_id}")
def select_course(user_id: int, db: Session = Depends(get_db)):
    """Fetch all courses a user is enrolled in for test selection."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    courses = crud.list_courses(db)
    if not courses:
        raise HTTPException(status_code=404, detail="No courses available")

    return {
        "message": "Select a course to take a test",
        "courses": [
            {"id": c.id, "code": c.code, "title": c.title, "level": c.level}
            for c in courses
        ],
    }

# ----Generate Test--------
@router.post("/generate")
def generate_test(
    user_id: int,
    course_id: int,
    num_questions: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Get course
    course_record = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course_record:
        raise HTTPException(status_code=404, detail="Course not found")

    course = crud.get_course_by_code(db, course_record.code)

    # Setup Gemini model
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    Generate {num_questions} multiple-choice questions for the course {course.code} - {course.title}.
    Provide each question with 4 options (A, B, C, D) and the correct answer.
    Format as JSON list: 
    [{{"question": "...", "options": ["A", "B", "C", "D"], "answer": "A"}}]
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during content generation: {str(e)}")

    # Parse response safely
    cleaned_text = response.text.strip()
    cleaned_text = re.sub(r"^```(json)?|```$", "", cleaned_text, flags=re.MULTILINE).strip()
    try:
        questions = json.loads(cleaned_text)
        print(questions)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse Gemini output as JSON")

    # Extract correct answers
    try:
        correct_answers = [q["answer"] for q in questions]
    except KeyError:
        raise HTTPException(status_code=500, detail="Some questions are missing the 'answer' key.")

    # Save the test
    test = crud.create_test(
        db,
        user_id=user_id,
        course_id=course_id,
        questions=questions,
        correct_answers=correct_answers
    )

    return {
    "test_id": test.id,
    "course": course.code,
    "questions": questions
}

# ---------- Submit Answers ----------
@router.post("/submit")
def submit_test(test_id: int, student_answers: list[str], db: Session = Depends(get_db)):
    """Submit answers and calculate score."""
    test = crud.submit_test(db, test_id, student_answers)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return {"message": "Test submitted", "score": test.score, "answers": test.student_answers}

@router.get("/{test_id}/score")
def get_test_score(test_id: int, db: Session = Depends(get_db)):
    score_data = crud.get_test_score(db, test_id)
    if not score_data:
        raise HTTPException(status_code=404, detail="Test not found")
    return score_data


@router.get("/user/{user_id}/average-score")
def get_user_average_score(user_id: int, db: Session = Depends(get_db)):
    avg = crud.get_user_average_score(db, user_id)
    return {"user_id": user_id, "average_score": avg}