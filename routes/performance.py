# routes/performance.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth.utils import get_current_user
from database.db import SessionLocal
from database import crud, models
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from fastapi.responses import FileResponse

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- AI Insights -------- #
def generate_ai_insights(avg_scores, weekly_study, db: Session):
    insights = []
    if not avg_scores and not weekly_study:
        return ["No data yet. Start logging tests and study sessions!"]

    score_map = {cid: avg for cid, avg in avg_scores}
    study_map = {cid: hrs for cid, hrs in weekly_study}

    for cid, avg in score_map.items():
        course = db.query(models.Course).filter(models.Course.id == cid).first()
        cname = f"{course.code} - {course.title}" if course else f"Course {cid}"
        hours = study_map.get(cid, 0)

        if avg is None:
            # Optionally, add a note for no score yet, or just skip
            insights.append(f"ℹ️ {cname}: No average score available yet.")
            continue

        if avg < 50:
            insights.append(f"⚠️ {cname}: Low average ({round(avg,2)}). Increase study time by {hours+2} hrs/week.")
        elif hours > 5 and avg < 60:
            insights.append(f"📘 {cname}: You study {hours} hrs but avg is {round(avg,2)}. Try group study or videos.")
        elif avg >= 70:
            insights.append(f"✅ {cname}: Great job! Avg {round(avg,2)}. Keep it up!")


    for cid, hrs in study_map.items():
        if cid not in score_map:
            course = db.query(models.Course).filter(models.Course.id == cid).first()
            cname = f"{course.code} - {course.title}" if course else f"Course {cid}"
            insights.append(f"📌 {cname}: {hrs} hrs studied but no test results yet.")

    return insights


# -------- Trend Data -------- #
def get_trend_data(db: Session, user_id: int):
    """Return test progress and study logs trend over time"""

    # Progress trend: test scores over time
    test_trend = (
        db.query(models.Test.course_id, models.Test.score, models.Test.created_at)
        .filter(models.Test.user_id == user_id)
        .order_by(models.Test.created_at.asc())
        .all()
    )
    test_trend_named = [
        {
            "course": f"{c.code} - {c.title}" if (c := db.query(models.Course).get(cid)) else f"Course {cid}",
            "score": score,
            "date": created_at
        }
        for cid, score, created_at in test_trend
    ]

    # Study hours trend (per day)
    study_trend = (
        db.query(func.date(models.StudyLog.date), func.sum(models.StudyLog.hours_studied))
        .filter(models.StudyLog.user_id == user_id)
        .group_by(func.date(models.StudyLog.date))
        .order_by(func.date(models.StudyLog.date).asc())
        .all()
    )
    study_trend_named = [{"date": str(date), "hours": hrs} for date, hrs in study_trend]

    return {"test_trend": test_trend_named, "study_trend": study_trend_named}


# -------- Main Performance Endpoint -------- #
@router.get("/{user_id}")
def get_performance(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user_id = current_user.id
    tests = crud.list_tests(db, user_id)
    study_logs = crud.get_study_logs_by_user(db, user_id)

    if not tests and not study_logs:
        raise HTTPException(status_code=404, detail="No performance data found")

    avg_scores = crud.get_average_scores_by_course(db, user_id)
    weekly_study = crud.get_weekly_study_hours(db, user_id)

    # Calculate overall average score
    overall_avg = (
        db.query(func.avg(models.Test.score))
        .filter(models.Test.user_id == user_id)
        .scalar()
    )
    overall_avg = round(overall_avg, 2) if overall_avg else 0

    weak_courses = sorted([entry for entry in avg_scores if entry[1] is not None], key=lambda x: x[1])[:3]

    insights = generate_ai_insights(avg_scores, weekly_study, db)
    trends = get_trend_data(db, user_id)

    # Named data (replace course_id with course code/title)
    avg_scores_named = [
        (db.query(models.Course).get(cid).code, round(avg, 2)) for cid, avg in avg_scores
    ]
    weekly_study_named = [
        (db.query(models.Course).get(cid).code, hrs) for cid, hrs in weekly_study
    ]
    weak_courses_named = [
        {"course": db.query(models.Course).get(cid).code, "avg_score": round(avg, 2)} for cid, avg in weak_courses
    ]

    return {
        "average_score": overall_avg,
        "avg_scores": avg_scores_named,
        "weekly_study": weekly_study_named,
        "weak_courses": weak_courses_named,
        "ai_insights": insights,
        "trends": trends,
    }


# -------- Download Report (PDF) -------- #
@router.get("/{user_id}/download")
def download_report(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    avg_scores = crud.get_average_scores_by_course(db, user_id)
    weekly_study = crud.get_weekly_study_hours(db, user_id)

    overall_avg = (
        db.query(func.avg(models.Test.score))
        .filter(models.Test.user_id == user_id)
        .scalar()
    )
    overall_avg = round(overall_avg, 2) if overall_avg else 0

    insights = generate_ai_insights(avg_scores, weekly_study, db)

    file_path = f"performance_report_{user_id}.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Performance Report for {user.name}", styles['Title']))
    elements.append(Spacer(1, 20))

    # Overall Average
    elements.append(Paragraph(f"Overall Average Score: {overall_avg}", styles['Heading2']))
    elements.append(Spacer(1, 10))

    # Avg scores per course
    elements.append(Paragraph("Average Scores Per Course:", styles['Heading2']))
    score_data = [["Course", "Average Score"]]
    for cid, avg in avg_scores:
        c = db.query(models.Course).get(cid)
        cname = f"{c.code} - {c.title}" if c else f"Course {cid}"
        score_data.append([cname, round(avg, 2)])
    elements.append(Table(score_data))
    elements.append(Spacer(1, 20))

    # Weekly study hours
    elements.append(Paragraph("Weekly Study Hours:", styles['Heading2']))
    study_data = [["Course", "Total Hours"]]
    for cid, hrs in weekly_study:
        c = db.query(models.Course).get(cid)
        cname = f"{c.code} - {c.title}" if c else f"Course {cid}"
        study_data.append([cname, hrs])
    elements.append(Table(study_data))
    elements.append(Spacer(1, 20))

    # Weak courses with scores
    elements.append(Paragraph("Weak Courses (Lowest Scores):", styles['Heading2']))
    weak_courses = sorted(avg_scores, key=lambda x: x[1])[:3]
    for cid, score in weak_courses:
        c = db.query(models.Course).get(cid)
        cname = f"{c.code} - {c.title}" if c else f"Course {cid}"
        elements.append(Paragraph(f"{cname} - Avg Score: {round(score, 2)}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # AI Insights
    elements.append(Paragraph("AI Insights:", styles['Heading2']))
    for insight in insights:
        elements.append(Paragraph(insight, styles['Normal']))

    doc.build(elements)
    return FileResponse(path=file_path, filename=file_path, media_type="application/pdf")
# Add this at the bottom of performance.py

@router.get("/{user_id}/trend-data")
def get_user_trend_data(user_id: int, db: Session = Depends(get_db)):
    """
    Returns only the data needed for plotting charts:
    - Test scores trend (date vs score)
    - Study hours trend (date vs hours)
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # --- Test Scores Trend ---
    test_trend = (
        db.query(models.Test.course_id, models.Test.score, models.Test.created_at)
        .filter(models.Test.user_id == user_id)
        .order_by(models.Test.created_at.asc())
        .all()
    )
    test_trend_named = [
        {
            "course": f"{c.code}" if (c := db.query(models.Course).get(cid)) else f"Course {cid}",
            "score": score,
            "date": created_at.strftime("%Y-%m-%d")
        }
        for cid, score, created_at in test_trend
    ]

    # --- Study Hours Trend ---
    study_trend = (
        db.query(func.date(models.StudyLog.date), func.sum(models.StudyLog.hours_studied))
        .filter(models.StudyLog.user_id == user_id)
        .group_by(func.date(models.StudyLog.date))
        .order_by(func.date(models.StudyLog.date).asc())
        .all()
    )
    study_trend_named = [{"date": str(date), "hours": hrs} for date, hrs in study_trend]

    return {
        "test_trend": test_trend_named,
        "study_trend": study_trend_named
    }
