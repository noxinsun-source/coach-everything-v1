"""
Coach Everything Dashboard Backend
FastAPI server for dashboard functionality
"""

from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Column, String, DateTime, Integer, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

# Initialize FastAPI
app = FastAPI(title="Coach Everything Dashboard", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS)
static_dir = Path(__file__).parent / "dashboard_frontend"
if static_dir.exists():
    app.mount("/css", StaticFiles(directory=str(static_dir / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(static_dir / "js")), name="js")

# Database Setup
db_dir = Path.home() / ".coach"
db_dir.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{db_dir}/coach_dashboard.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class Project(Base):
    """Project model"""
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    domain = Column(String)  # learning, research, job_hunting, etc.
    created_at = Column(DateTime, default=datetime.now)
    vault_path = Column(String)  # Path to Obsidian folder
    cache_path = Column(String)  # Path to SQLite cache


class TaskRecord(Base):
    """Individual task record"""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    project_id = Column(String)
    title = Column(String)
    description = Column(String)
    phase = Column(String)
    status = Column(String)  # pending, in_progress, completed
    estimated_minutes = Column(Integer)
    actual_minutes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    verification_criteria = Column(String)  # JSON


class TimeLog(Base):
    """Time tracking log"""
    __tablename__ = "time_logs"

    id = Column(String, primary_key=True)
    task_id = Column(String)
    project_id = Column(String)
    pomodoros = Column(Integer, default=0)
    duration_minutes = Column(Integer)
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)


class CoachingNote(Base):
    """AI coaching notes and advice"""
    __tablename__ = "coaching_notes"

    id = Column(String, primary_key=True)
    project_id = Column(String)
    task_id = Column(String, nullable=True)
    note_type = Column(String)  # advice, encouragement, warning
    content = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class UserSettings(Base):
    """User settings"""
    __tablename__ = "user_settings"

    id = Column(String, primary_key=True, default="default")
    theme = Column(String, default="light")  # light, dark
    font_size = Column(Integer, default=14)
    language = Column(String, default="zh")  # zh, en
    llm_provider = Column(String, default="anthropic")
    llm_model = Column(String, default="claude-3-haiku-20240307")
    llm_api_key = Column(String, nullable=True)


# Create tables
Base.metadata.create_all(bind=engine)


# Pydantic Models
class ProjectCreate(BaseModel):
    """Create project request"""
    name: str
    description: str
    domain: str
    vault_path: str


class ProjectResponse(BaseModel):
    """Project response"""
    id: str
    name: str
    description: str
    domain: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """Task response"""
    id: str
    title: str
    description: str
    phase: str
    status: str
    estimated_minutes: int
    actual_minutes: int
    completion_percent: float = 0


class TimeStatsResponse(BaseModel):
    """Time statistics response"""
    total_hours: float
    average_duration: float
    pomodoros_count: int
    on_time_percent: float
    fastest_task: str
    slowest_task: str


class DashboardDataResponse(BaseModel):
    """Complete dashboard data"""
    project: ProjectResponse
    tasks: List[TaskResponse]
    time_stats: TimeStatsResponse
    recent_coaching_notes: List[dict]
    gantt_data: dict


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# API Routes

@app.get("/")
async def read_root():
    """Serve dashboard HTML"""
    dashboard_path = Path(__file__).parent / "dashboard_frontend" / "index.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path, media_type="text/html")
    return {"message": "Coach Everything Dashboard"}


@app.get("/index.html")
async def serve_index():
    """Serve dashboard HTML at /index.html"""
    dashboard_path = Path(__file__).parent / "dashboard_frontend" / "index.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Dashboard not found")


@app.get("/api/projects", response_model=List[ProjectResponse])
async def get_projects(db: Session = Depends(get_db)):
    """Get all projects"""
    projects = db.query(Project).all()
    return projects


@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create new project"""
    from uuid import uuid4

    db_project = Project(
        id=str(uuid4()),
        name=project.name,
        description=project.description,
        domain=project.domain,
        vault_path=project.vault_path,
        cache_path=f"{Path.home()}/.coach/{project.name}.db"
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@app.get("/api/projects/{project_id}/dashboard", response_model=DashboardDataResponse)
async def get_project_dashboard(project_id: str, db: Session = Depends(get_db)):
    """Get complete dashboard data for a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tasks = db.query(TaskRecord).filter(TaskRecord.project_id == project_id).all()
    time_logs = db.query(TimeLog).filter(TimeLog.project_id == project_id).all()
    coaching_notes = db.query(CoachingNote).filter(
        CoachingNote.project_id == project_id
    ).order_by(CoachingNote.created_at.desc()).limit(5).all()

    # Calculate statistics
    total_minutes = sum(log.duration_minutes for log in time_logs)
    pomodoros = sum(log.pomodoros for log in time_logs)
    completed_tasks = [t for t in tasks if t.status == "completed"]
    on_time = len([t for t in completed_tasks if t.actual_minutes <= t.estimated_minutes])

    time_stats = TimeStatsResponse(
        total_hours=total_minutes / 60,
        average_duration=total_minutes / len(time_logs) if time_logs else 0,
        pomodoros_count=pomodoros,
        on_time_percent=(on_time / len(completed_tasks) * 100) if completed_tasks else 0,
        fastest_task=min(completed_tasks, key=lambda t: t.actual_minutes).title if completed_tasks else "",
        slowest_task=max(completed_tasks, key=lambda t: t.actual_minutes).title if completed_tasks else ""
    )

    task_responses = [
        TaskResponse(
            id=t.id,
            title=t.title,
            description=t.description,
            phase=t.phase,
            status=t.status,
            estimated_minutes=t.estimated_minutes,
            actual_minutes=t.actual_minutes,
            completion_percent=(t.actual_minutes / t.estimated_minutes * 100) if t.estimated_minutes > 0 else 0
        )
        for t in tasks
    ]

    gantt_data = {
        "tasks": [
            {
                "id": t.id,
                "name": t.title,
                "start": t.created_at.isoformat(),
                "end": (t.completed_at or datetime.now()).isoformat(),
                "duration": t.actual_minutes,
                "status": t.status
            }
            for t in tasks if t.actual_minutes > 0
        ]
    }

    return DashboardDataResponse(
        project=ProjectResponse.from_orm(project),
        tasks=task_responses,
        time_stats=time_stats,
        recent_coaching_notes=[
            {
                "type": note.note_type,
                "content": note.content,
                "created_at": note.created_at.isoformat()
            }
            for note in coaching_notes
        ],
        gantt_data=gantt_data
    )


@app.post("/api/projects/{project_id}/tasks")
async def create_task(project_id: str, task_data: dict, db: Session = Depends(get_db)):
    """Create a new task for project"""
    from uuid import uuid4

    db_task = TaskRecord(
        id=str(uuid4()),
        project_id=project_id,
        title=task_data.get("title"),
        description=task_data.get("description"),
        phase=task_data.get("phase"),
        status="pending",
        estimated_minutes=task_data.get("estimated_minutes", 120),
        verification_criteria=json.dumps(task_data.get("verification_criteria", {}))
    )
    db.add(db_task)
    db.commit()
    return {"id": db_task.id, "status": "created"}


@app.post("/api/time-logs")
async def log_time(log_data: dict, db: Session = Depends(get_db)):
    """Log time spent on a task"""
    from uuid import uuid4

    db_log = TimeLog(
        id=str(uuid4()),
        task_id=log_data.get("task_id"),
        project_id=log_data.get("project_id"),
        duration_minutes=log_data.get("duration_minutes"),
        pomodoros=log_data.get("pomodoros", 0),
        start_time=datetime.fromisoformat(log_data.get("start_time", datetime.now().isoformat())),
        end_time=datetime.fromisoformat(log_data.get("end_time", datetime.now().isoformat()))
    )

    # Update task actual time
    task = db.query(TaskRecord).filter(TaskRecord.id == log_data.get("task_id")).first()
    if task:
        task.actual_minutes = log_data.get("duration_minutes")
        if log_data.get("completed"):
            task.status = "completed"
            task.completed_at = datetime.now()

    db.add(db_log)
    db.commit()
    return {"id": db_log.id, "status": "logged"}


@app.get("/api/settings")
async def get_settings(db: Session = Depends(get_db)):
    """Get user settings"""
    settings = db.query(UserSettings).filter(UserSettings.id == "default").first()
    if not settings:
        settings = UserSettings(id="default")
        db.add(settings)
        db.commit()
    return {
        "theme": settings.theme,
        "font_size": settings.font_size,
        "language": settings.language,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model
    }


@app.post("/api/settings")
async def update_settings(settings_data: dict, db: Session = Depends(get_db)):
    """Update user settings"""
    settings = db.query(UserSettings).filter(UserSettings.id == "default").first()
    if not settings:
        settings = UserSettings(id="default")

    for key, value in settings_data.items():
        if hasattr(settings, key):
            setattr(settings, key, value)

    db.add(settings)
    db.commit()
    return {"status": "updated"}


@app.websocket("/ws/pomodoro/{project_id}")
async def websocket_pomodoro(websocket: WebSocket, project_id: str):
    """WebSocket for real-time Pomodoro updates"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Handle pomodoro timer events
            event = json.loads(data)
            # Broadcast to other clients
            await websocket.send_json({
                "type": event.get("type"),
                "data": event.get("data")
            })
    except Exception as e:
        print(f"WebSocket error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
