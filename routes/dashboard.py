# routes/dashboard.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth.utils import get_current_user
from database.db import SessionLocal
from database import crud, models

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_main_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user_id = current_user.id

    test_trend = (
        db.query(models.Test.course_id, models.Test.score, models.Test.created_at)
        .filter(models.Test.user_id == user_id)
        .order_by(models.Test.created_at.asc())
        .all()
    )
    test_trend_named = [
        {"course": f"{c.code} - {c.title}" if (c := db.query(models.Course).get(cid)) else f"Course {cid}",
         "score": score, "date": created_at}
        for cid, score, created_at in test_trend
    ]

    study_trend = (
        db.query(func.date(models.StudyLog.date), func.sum(models.StudyLog.hours_studied))
        .filter(models.StudyLog.user_id == user_id)
        .group_by(func.date(models.StudyLog.date))
        .order_by(func.date(models.StudyLog.date).asc())
        .all()
    )
    study_trend_named = [{"date": str(date), "hours": hrs} for date, hrs in study_trend]

    return {
        "user": {"name": current_user.name, "level": current_user.level},
        "progress_trend": test_trend_named,
        "study_hours_trend": study_trend_named,
        "quick_actions": [
            {"name": "Take Test", "route": "/tests"},
            {"name": "Generate Timetable", "route": "/study-timetable/generate"},
            {"name": "PDF Summarizer", "route": "/pdf/summarize"},
            {"name": "Watch Videos", "route": "/resources/videos"},
            {"name": "Chatbot", "route": "/chatbot"},
        ],
    }

