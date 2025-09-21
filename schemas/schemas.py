from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# -------- Department --------
class DepartmentBase(BaseModel):
    name: str


class DepartmentResponse(DepartmentBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


# -------- Course --------
class CourseBase(BaseModel):
    code: str
    title: str
    level: str


class CourseCreate(CourseBase):
    department_ids: List[int] = []

# ---------------- TEST ----------------
class TestBase(BaseModel):
    user_id: int
    course_id: int
    score: int

class TestCreate(TestBase):
    pass

class TestOut(TestBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ---------------- STUDY LOG ----------------
class StudyLogBase(BaseModel):
    user_id: int
    course_id: int
    hours_studied: int

class StudyLogCreate(StudyLogBase):
    pass

class StudyLogOut(StudyLogBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True


# ---------------- DASHBOARD ----------------
class DashboardOut(BaseModel):
    average_score: Optional[float]
    best_course: Optional[str]
    weakest_course: Optional[str]
    total_study_hours: int
    course_stats: List[dict]


class CourseResponse(CourseBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    departments: List[DepartmentResponse] = []

    class Config:
        orm_mode = True


# -------- User --------
class UserBase(BaseModel):
    matric_no: str
    name: str
    email: str
    department: str
    level: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
