from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chatbot.routes import router as chatbot_router
from pdfsummarizer.routes import router as pdf_router
from routes import performance, users, courses, department, dashboard, test, resources, study_group, study_timetable
from auth import routes
app = FastAPI(
    title="📚 Spoudazo API",
    description="Smarter Learning for Smarter Students",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",      # React dev server
    "http://localhost:5173",      # Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # List of allowed origins
    allow_credentials=True,             # Allow cookies and auth headers
    allow_methods=["*"],                # Allow all HTTP methods
    allow_headers=["*"],                # Allow all headers
)

# Include routes
app.include_router(routes.router)
app.include_router(performance.router, prefix="/performance", tags=["Performance"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(test.router)
app.include_router(resources.router, prefix="/resources", tags=["Resources"])
app.include_router(study_group.router, prefix="/study-groups", tags=["Study Groups"])
app.include_router(study_timetable.router, prefix="/study-timetable", tags=["Study Timetable"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(department.router, prefix="/departments", tags=["Departments"])
app.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(pdf_router, tags=["PDF Summarizer"])

@app.get("/")
async def root():
    return {"message": "Welcome to Spoudazo API 🚀"}
