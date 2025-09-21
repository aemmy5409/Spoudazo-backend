from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey, func, Boolean, JSON
from sqlalchemy.orm import relationship
from .db import Base

# ---------------- Association Tables ---------------- #
course_department_table = Table(
    "course_department",
    Base.metadata,
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
    Column("department_id", Integer, ForeignKey("departments.id"), primary_key=True)
)

group_members_table = Table(
    "group_members",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("study_groups.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
)

# ---------------- User ---------------- #
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    matric_no = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)
    department = Column(String, nullable=False)
    level = Column(String, nullable=False)
    is_google_user = Column(Boolean, default=False)
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tests = relationship("Test", back_populates="users")
    study_logs = relationship("StudyLog", back_populates="users")
    groups = relationship("StudyGroup", secondary=group_members_table, back_populates="members")


# ---------------- Department ---------------- #
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ---------------- Course ---------------- #
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    level = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    departments = relationship("Department", secondary=course_department_table, backref="courses")
    tests = relationship("Test", back_populates="courses")
    study_logs = relationship("StudyLog", back_populates="courses")


# ---------------- Test ---------------- #
class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

    # New fields
    questions = Column(JSON, nullable=True)  # List of generated questions
    correct_answers = Column(JSON, nullable=True)  # Correct answers from Gemini
    student_answers = Column(JSON, nullable=True)  # Answers submitted by student

    score = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="tests")
    courses = relationship("Course", back_populates="tests")

# ---------------- StudyLog ---------------- #
class StudyLog(Base):
    __tablename__ = "study_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    hours_studied = Column(Integer, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="study_logs")
    courses = relationship("Course", back_populates="study_logs")


# ---------------- Resource ---------------- #
class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    courses = relationship("Course", backref="resources")


# ---------------- StudyGroup ---------------- #
class StudyGroup(Base):
    __tablename__ = "study_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    members = relationship("User", secondary=group_members_table, back_populates="groups")


# ---------------- StudyTimetable ---------------- #
class StudyTimetable(Base):
    __tablename__ = "study_timetables"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    day_of_week = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)

    users = relationship("User", backref="timetables")
    courses = relationship("Course", backref="timetables")

class StudyHabit(Base):
    __tablename__ = "study_habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    preferred_time = Column(String, nullable=False)  # "morning", "afternoon", "night"
    hours_per_day = Column(Integer, nullable=False)
    difficult_courses = Column(String, nullable=True)  # comma-separated course codes
    break_minutes = Column(Integer, default=15)

    user = relationship("User", backref="study_habits")
