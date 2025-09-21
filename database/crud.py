from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from pydantic import EmailStr
from . import models

# ---------- USERS ----------
def create_user(db: Session, matric_no: str, name: str, email: EmailStr, password: str, department: str, level: str):
    user = models.User(
        matric_no=matric_no,
        name=name,
        email=email,
        password=password,
        department=department,
        level=level
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_matric_no(db: Session, matric_no: str):
    return db.query(models.User).filter(models.User.matric_no == matric_no).first()

def list_users(db: Session):
    return db.query(models.User).all()

def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False


# ---------- DEPARTMENTS ----------
def create_department(db: Session, name: str):
    dept = models.Department(name=name)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept

def get_department_by_name(db: Session, name: str):
    return db.query(models.Department).filter(models.Department.name == name).first()

def list_departments(db: Session):
    return db.query(models.Department).all()

def delete_department(db: Session, dept_id: int):
    dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if dept:
        db.delete(dept)
        db.commit()
        return True
    return False


# ---------- COURSES ----------
def create_course(db: Session, code: str, title: str, level: str, department_ids: list[int]):
    course = models.Course(code=code, title=title, level=level)
    if department_ids:
        course.departments = db.query(models.Department).filter(models.Department.id.in_(department_ids)).all()
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

def get_course_by_code(db: Session, code: str):
    return db.query(models.Course).filter(models.Course.code == code).first()

def list_courses(db: Session):
    return db.query(models.Course).all()

def delete_course(db: Session, course_id: int):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if course:
        db.delete(course)
        db.commit()
        return True
    return False


# ---------- TESTS ----------
def create_test(db: Session, user_id: int, course_id: int, questions: list, correct_answers: list):
    test = models.Test(
        user_id=user_id,
        course_id=course_id,
        questions=questions,
        correct_answers=correct_answers,
        student_answers=None,
        score=None
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return test
# In crud.py

def get_test_score(db: Session, test_id: int):
    """Return a test score by test_id"""
    test = db.query(models.Test).filter(models.Test.id == test_id).first()
    return {"test_id": test.id, "score": test.score} if test else None


def get_user_average_score(db: Session, user_id: int):
    """Return the average score of all tests for a given user"""
    avg_score = (
        db.query(func.avg(models.Test.score))
        .filter(models.Test.user_id == user_id)
        .scalar()
    )
    return round(avg_score, 2) if avg_score else 0


def submit_test(db: Session, test_id: int, student_answers: list):
    test = db.query(models.Test).filter(models.Test.id == test_id).first()
    if not test:
        return None

    test.student_answers = student_answers

    # Auto-calculate score
    correct = 0
    for i, ans in enumerate(student_answers):
        if i < len(test.correct_answers) and ans == test.correct_answers[i]:
            correct += 1
    test.score = int((correct / len(test.correct_answers)) * 100) if test.correct_answers else 0

    db.commit()
    db.refresh(test)
    return test

def list_tests(db: Session, user_id: int):
    return db.query(models.Test).filter(models.Test.user_id == user_id).all()

def get_course_tests(db: Session, user_id: int, course_id: int):
    return db.query(models.Test).filter(models.Test.user_id == user_id, models.Test.course_id == course_id).all()

def delete_test(db: Session, test_id: int):
    test = db.query(models.Test).filter(models.Test.id == test_id).first()
    if test:
        db.delete(test)
        db.commit()
    return test

def delete_all_tests_for_user(db: Session, user_id: int):
    tests = db.query(models.Test).filter(models.Test.user_id == user_id).all()
    for t in tests:
        db.delete(t)
    db.commit()
    return len(tests)


# ---------- STUDY LOG ----------
def create_study_log(db: Session, user_id: int, course_id: int, hours_studied: int):
    study_log = models.StudyLog(user_id=user_id, course_id=course_id, hours_studied=hours_studied)
    db.add(study_log)
    db.commit()
    db.refresh(study_log)
    return study_log

def get_study_logs_by_user(db: Session, user_id: int):
    return db.query(models.StudyLog).filter(models.StudyLog.user_id == user_id).all()

def get_weekly_study_hours(db: Session, user_id: int):
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    results = (
        db.query(models.StudyLog.course_id, func.sum(models.StudyLog.hours_studied).label("total_hours"))
        .filter(models.StudyLog.user_id == user_id, models.StudyLog.date >= one_week_ago)
        .group_by(models.StudyLog.course_id)
        .all()
    )
    return results

def get_average_scores_by_course(db: Session, user_id: int):
    results = (
        db.query(models.Test.course_id, func.avg(models.Test.score).label("avg_score"))
        .filter(models.Test.user_id == user_id)
        .group_by(models.Test.course_id)
        .all()
    )
    return results

def delete_study_log(db: Session, log_id: int):
    log = db.query(models.StudyLog).filter(models.StudyLog.id == log_id).first()
    if log:
        db.delete(log)
        db.commit()
        return True
    return False


# ---------- RESOURCES ----------
import os
import requests
UPLOAD_FOLDER = "uploads/resources"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
def create_resource(db: Session, title: str, url: str, type: str, course_id: int | None = None):
    resource = models.Resource(
        course_id=course_id,
        title=title,
        url=url,
        type=type
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def list_resources(db: Session, course_id: int | None = None):
    query = db.query(models.Resource)
    if course_id:
        query = query.filter(models.Resource.course_id == course_id)
    return query.all()


def delete_resource(db: Session, resource_id: int):
    resource = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if resource:
        db.delete(resource)
        db.commit()
        return True
    return False


def upload_pdf_resource(db: Session, file, course_id: int, title: str):
    """Save PDF locally and store as resource"""
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(filepath, "wb") as f:
        f.write(file.file.read())

    resource = models.Resource(
        course_id=course_id,
        title=title,
        url=filepath,  # stored as file path
        type="pdf"
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)


def generate_ai_resources_for_weak_courses(db: Session, user_id: int):
    # Find weak courses
    weak_courses = (
        db.query(models.Course)
        .join(models.Test)
        .filter(models.Test.user_id == user_id)
        .group_by(models.Course.id)
        .having(func.avg(models.Test.score) < 50)
        .all()
    )

    resources = []
    for course in weak_courses:
        # Generate YouTube video suggestions (mock, but you can integrate Gemini/YouTube API later)
        youtube_links = [
            f"https://www.youtube.com/results?search_query={course.title}+lecture",
            f"https://www.youtube.com/results?search_query={course.code}+tutorial"
        ]

        for link in youtube_links:
            res = create_resource(db, f"YouTube: {course.title}", link, "video", course.id)
            resources.append(res)

        # Add sample open-source textbook link
        textbook_link = f"https://example.com/{course.code}_textbook.pdf"
        res = create_resource(db, f"Textbook: {course.title}", textbook_link, "pdf", course.id)
        resources.append(res)

    return resources

# ---------- STUDY GROUPS ----------
def create_study_group(db: Session, name: str, description: str):
    group = models.StudyGroup(name=name, description=description)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group

def join_group(db: Session, group_id: int, user_id: int):
    group = db.query(models.StudyGroup).filter(models.StudyGroup.id == group_id).first()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not group or not user:
        return None
    group.members.append(user)
    db.commit()
    return group

def leave_group(db: Session, group_id: int, user_id: int):
    group = db.query(models.StudyGroup).filter(models.StudyGroup.id == group_id).first()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if group and user and user in group.members:
        group.members.remove(user)
        db.commit()
    return group

def list_group_members(db: Session, group_id: int):
    group = db.query(models.StudyGroup).filter(models.StudyGroup.id == group_id).first()
    return group.members if group else []

def list_user_groups(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user.groups if user else []


# ---------- STUDY HABITS ----------
def save_study_habits(db, user_id: int, preferred_time: str, hours_per_day: int, difficult_courses: str, break_minutes: int):
    habits = models.StudyHabit(
        user_id=user_id,
        preferred_time=preferred_time,
        hours_per_day=hours_per_day,
        difficult_courses=difficult_courses,
        break_minutes=break_minutes
    )
    db.add(habits)
    db.commit()
    db.refresh(habits)
    return habits

def get_study_habits(db, user_id: int):
    return db.query(models.StudyHabit).filter(models.StudyHabit.user_id == user_id).first()


# ---------- STUDY TIMETABLE ----------
def save_timetable_from_parsed_data(db, user_id: int, timetable_data: dict):
    entries = []
    for day, slots in timetable_data.items():
        for slot in slots:
            entry = models.StudyTimetable(
                user_id=user_id,
                course_id=None,  # can be mapped later if course codes are known
                day_of_week=day,
                start_time=slot["start"],
                end_time=slot["end"]
            )
            db.add(entry)
            entries.append({
                "day": day,
                "start": slot["start"],
                "end": slot["end"],
                "course": slot.get("course", "")
            })
    db.commit()
    return entries

def get_user_timetable(db, user_id: int):
    return db.query(models.StudyTimetable).filter(models.StudyTimetable.user_id == user_id).all()

def delete_user_timetable(db, user_id: int):
    timetable = db.query(models.StudyTimetable).filter(models.StudyTimetable.user_id == user_id).all()
    count = len(timetable)
    for entry in timetable:
        db.delete(entry)
    db.commit()
    return count

def generate_personalized_timetable(school_timetable, habits):
    personalized = {}
    for day, slots in school_timetable.items():
        personalized[day] = []
        total_study_hours = habits.hours_per_day
        break_minutes = habits.break_minutes

        for slot in slots:
            if total_study_hours > 0:
                study_session = {
                    "course": slot["course"],
                    "start": slot["end"],
                    "end": f"{int(slot['end'].split(':')[0]) + 1}:00",
                    "type": "study"
                }
                personalized[day].append(study_session)
                total_study_hours -= 1

        if habits.difficult_courses:
            difficult_list = habits.difficult_courses.split(",")
            for course in difficult_list:
                if total_study_hours > 0:
                    personalized[day].append({
                        "course": course.strip(),
                        "start": habits.preferred_time,
                        "end": "Flexible",
                        "type": "extra study"
                    })
                    total_study_hours -= 1
    return personalized


# ---------- DASHBOARD ----------
def get_dashboard_data(db: Session, user_id: int):
    study_data = (
        db.query(models.StudyLog.course_id, func.sum(models.StudyLog.hours_studied).label("total_hours"))
        .filter(models.StudyLog.user_id == user_id)
        .group_by(models.StudyLog.course_id)
        .all()
    )

    test_data = (
        db.query(models.Test.course_id, func.avg(models.Test.score).label("avg_score"))
        .filter(models.Test.user_id == user_id)
        .group_by(models.Test.course_id)
        .all()
    )

    return {"study_data": study_data, "test_data": test_data}
