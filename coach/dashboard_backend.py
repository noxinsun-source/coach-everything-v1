"""
Coach Everything Dashboard Backend
FastAPI server for dashboard functionality
"""

from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import Column, String, DateTime, Integer, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os
import re
import shlex
import subprocess
import time
from pathlib import Path

DEFAULT_PROVIDER = "claude_code"
DEFAULT_MODEL = "sonnet"
DEFAULT_CLAUDE_CLI_COMMAND = "claude -p --model {model}"
CODEX_APP_CLI = Path("/Applications/Codex.app/Contents/Resources/codex")
DEFAULT_CODEX_CLI_COMMAND = (
    f"{CODEX_APP_CLI} exec --model {{model}} --sandbox read-only "
    "--ephemeral --ignore-user-config --ignore-rules --color never -"
    if CODEX_APP_CLI.exists()
    else (
        "codex exec --model {model} --sandbox read-only "
        "--ephemeral --ignore-user-config --ignore-rules --color never -"
    )
)
DEFAULT_WORKSPACE_ROOT = Path.home() / ".coach" / "workspaces"

# Initialize FastAPI
app = FastAPI(title="Coach Everything Dashboard", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_static_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(("/js/", "/css/")):
        response.headers["Cache-Control"] = "no-store"
    return response


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
    llm_provider = Column(String, default=DEFAULT_PROVIDER)
    llm_model = Column(String, default=DEFAULT_MODEL)
    llm_api_key = Column(String, nullable=True)
    llm_api_key_encrypted = Column(String, nullable=True)
    llm_base_url = Column(String, nullable=True)
    cli_claude_command = Column(String, nullable=True)
    cli_codex_command = Column(String, nullable=True)
    cli_timeout_seconds = Column(Integer, nullable=True)
    workspace_root = Column(String, nullable=True)


# Create tables
Base.metadata.create_all(bind=engine)


def _ensure_user_settings_schema():
    desired = {
        "llm_api_key_encrypted": "TEXT",
        "llm_base_url": "TEXT",
        "cli_claude_command": "TEXT",
        "cli_codex_command": "TEXT",
        "cli_timeout_seconds": "INTEGER",
        "workspace_root": "TEXT",
    }
    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(user_settings)")).fetchall()
        existing = {row[1] for row in rows}
        for col, col_type in desired.items():
            if col not in existing:
                conn.execute(text(f"ALTER TABLE user_settings ADD COLUMN {col} {col_type}"))


_ensure_user_settings_schema()


def _get_secret_key_path() -> Path:
    return db_dir / "llm_secret.key"


def _get_fernet():
    try:
        from cryptography.fernet import Fernet
    except Exception as e:
        raise RuntimeError("cryptography_not_installed") from e

    key_path = _get_secret_key_path()
    if not key_path.exists():
        key = Fernet.generate_key()
        key_path.write_bytes(key)
        try:
            os.chmod(key_path, 0o600)
        except Exception:
            pass
    return Fernet(key_path.read_bytes())


def _encrypt_optional(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    f = _get_fernet()
    return f.encrypt(value.encode("utf-8")).decode("utf-8")


def _decrypt_optional(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    f = _get_fernet()
    return f.decrypt(value.encode("utf-8")).decode("utf-8")


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
    vault_path: Optional[str] = None

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
    created_at: Optional[datetime] = None


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
    workspace_root: str
    workspace_files: List[dict] = []


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    provider: str
    model: Optional[str] = None
    mode: str = "task_breakdown"
    messages: List[ChatMessage]
    system_prompt: Optional[str] = None


class ChatResponse(BaseModel):
    provider: str
    model: Optional[str] = None
    message: ChatMessage


class ChatTaskSyncRequest(BaseModel):
    content: str
    project_id: Optional[str] = None
    project_name: Optional[str] = None


class ChatTaskSyncResponse(BaseModel):
    project: ProjectResponse
    tasks: List[TaskResponse]
    workspace_files: List[dict]
    created_count: int
    skipped_count: int


class WorkspaceUpdateRequest(BaseModel):
    vault_path: Optional[str] = None


class WorkspaceFolderCreateRequest(BaseModel):
    name: str


class WorkspaceResponse(BaseModel):
    project: ProjectResponse
    workspace_root: str
    workspace_files: List[dict]


class _SafeFormatDict(dict):
    def __missing__(self, key):
        return ""


def _build_system_prompt(mode: str, custom: Optional[str]) -> str:
    if mode == "coding":
        base = "你是一个专业的代码助手。回答要直接、可执行，并在需要时先问清关键信息。"
    elif mode == "research":
        base = "你是一个研究助理。先澄清目标，再给出结构化结论与可验证的引用/下一步。"
    elif mode == "custom":
        base = custom or ""
    else:
        base = (
            "你是一个任务拆分教练。目标是把用户的模糊目标拆成可执行的下一步，并在不确定时提出澄清问题。"
            "当你给出可同步的任务拆分时，优先使用 Markdown 标题、编号步骤、- [ ] 待办项、预计分钟数、链接和表格，"
            "这样前端可以把回答同步进任务面板。"
        )

    if custom and mode != "custom":
        return f"{base}\n\n补充要求：{custom}"
    return base


def _render_prompt(system_prompt: str, messages: List[ChatMessage]) -> str:
    parts = []
    if system_prompt:
        parts.append(f"SYSTEM: {system_prompt}".strip())
    for m in messages:
        role = (m.role or "").strip().upper()
        content = (m.content or "").strip()
        if not content:
            continue
        parts.append(f"{role}: {content}")
    parts.append("ASSISTANT:")
    return "\n\n".join(parts).strip() + "\n"


def _clean_markdown_text(value: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", value or "")
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"~~([^~]+)~~", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text.strip(" \t-—:：")


def _extract_minutes(text: str) -> int:
    hours = re.search(r"(\d+(?:\.\d+)?)\s*(?:小时|hour|hours|h)", text, re.IGNORECASE)
    if hours:
        return max(5, int(float(hours.group(1)) * 60))
    minutes = re.search(r"(\d+)\s*(?:分钟|minute|minutes|min|m)", text, re.IGNORECASE)
    if minutes:
        return max(5, int(minutes.group(1)))
    return 60


def _split_task_title_description(text: str) -> tuple[str, str]:
    cleaned = _clean_markdown_text(text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return "", ""

    for delimiter in ("：", ":", " - ", " — "):
        if delimiter in cleaned:
            title, description = cleaned.split(delimiter, 1)
            return title.strip()[:120], description.strip()

    return cleaned[:120], cleaned


def _parse_tasks_from_markdown(content: str) -> List[dict]:
    tasks = []
    phase = "对话拆分"
    seen = set()

    for raw_line in (content or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue

        heading_match = re.match(r"^#{1,6}\s+(.+)$", line)
        if heading_match:
            phase = _clean_markdown_text(heading_match.group(1))[:80] or phase
            continue

        if re.match(r"^\|.+\|$", line) and "---" not in line:
            cells = [_clean_markdown_text(cell) for cell in line.strip("|").split("|")]
            cells = [cell for cell in cells if cell]
            if not cells or any(cell in {"任务", "步骤", "事项", "时间", "负责人", "状态"} for cell in cells[:2]):
                continue
            title, description = _split_task_title_description(cells[0])
            if len(cells) > 1:
                description = " | ".join(cells[1:])
        else:
            item_match = re.match(r"^(?:[-*+]\s+(?:\[[ xX]\]\s*)?|\d+[.)、]\s+)(.+)$", line)
            if not item_match:
                continue
            title, description = _split_task_title_description(item_match.group(1))

        if not title:
            continue
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        tasks.append({
            "title": title,
            "description": description or title,
            "phase": phase,
            "estimated_minutes": _extract_minutes(line),
        })

    if not tasks:
        for line in (content or "").splitlines():
            cleaned = _clean_markdown_text(line)
            if cleaned:
                title, description = _split_task_title_description(cleaned)
                if title:
                    tasks.append({
                        "title": title,
                        "description": description or title,
                        "phase": phase,
                        "estimated_minutes": _extract_minutes(cleaned),
                    })
                break

    return tasks


def _safe_project_name(name: str) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff -]+", "", name or "").strip()
    cleaned = re.sub(r"\s+", "-", cleaned)
    return cleaned[:60] or "chat-task-plan"


def _workspace_root_path(settings: Optional[UserSettings] = None) -> Path:
    raw_root = settings.workspace_root if settings and settings.workspace_root else str(DEFAULT_WORKSPACE_ROOT)
    return Path(raw_root).expanduser()


def _workspace_path_for_project(
    project: Project,
    ensure: bool = True,
    workspace_root: Optional[Path] = None,
) -> Path:
    if project.vault_path:
        path = Path(project.vault_path).expanduser()
    else:
        path = (workspace_root or DEFAULT_WORKSPACE_ROOT) / _safe_project_name(project.name)
        if ensure:
            project.vault_path = str(path)
    if ensure:
        path.mkdir(parents=True, exist_ok=True)
    return path


def _workspace_files_for_project(project: Project, workspace_root: Optional[Path] = None) -> List[dict]:
    workspace = _workspace_path_for_project(project, ensure=False, workspace_root=workspace_root)
    if not workspace.exists() or not workspace.is_dir():
        return []
    files = []
    for path in sorted(workspace.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if path.name.startswith("."):
            continue
        files.append({
            "name": path.name,
            "path": str(path),
            "type": "folder" if path.is_dir() else "file",
        })
    return files


def _write_workspace_files(
    project: Project,
    tasks: List[TaskRecord],
    synced_content: str,
    workspace_root: Optional[Path] = None,
) -> List[dict]:
    workspace = _workspace_path_for_project(project, workspace_root=workspace_root)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    roadmap = [f"# {project.name} Roadmap", "", f"Generated: {now}", ""]
    for task in tasks:
        roadmap.append(f"- [{'x' if task.status == 'completed' else ' '}] **{task.title}** ({task.estimated_minutes} 分钟)")
        if task.description:
            roadmap.append(f"  - {task.description}")
    (workspace / "Roadmap.md").write_text("\n".join(roadmap).strip() + "\n", encoding="utf-8")

    progress = [
        f"# {project.name} Task Progress",
        "",
        "| 任务 | 阶段 | 状态 | 预计时间 | 创建时间 |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for task in tasks:
        progress.append(
            f"| {task.title} | {task.phase or '-'} | {task.status} | {task.estimated_minutes} 分钟 | {task.created_at:%Y-%m-%d %H:%M} |"
        )
    (workspace / "Task Progress.md").write_text("\n".join(progress).strip() + "\n", encoding="utf-8")

    log_path = workspace / "Coach Log.md"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"\n## Chat Sync {now}\n\n")
        f.write((synced_content or "").strip())
        f.write("\n")

    return _workspace_files_for_project(project, workspace_root=workspace_root)


def _workspace_response(project: Project, workspace_root: Path) -> WorkspaceResponse:
    project_response = ProjectResponse.from_orm(project)
    project_response.vault_path = str(_workspace_path_for_project(project, ensure=False, workspace_root=workspace_root))
    return WorkspaceResponse(
        project=project_response,
        workspace_root=str(workspace_root),
        workspace_files=_workspace_files_for_project(project, workspace_root=workspace_root),
    )


def _validate_workspace_directory(path_value: str) -> Path:
    path = Path(path_value).expanduser()
    if path.exists() and not path.is_dir():
        raise HTTPException(status_code=400, detail="Workspace path exists but is not a folder")
    return path


def _run_cli(command_template: str, model: Optional[str], prompt: str, timeout_seconds: int) -> str:
    template = (command_template or "").strip()
    if not template:
        raise RuntimeError("cli_command_not_configured")

    cmd_str = template.format_map(_SafeFormatDict(model=model or ""))
    argv = shlex.split(cmd_str)
    if not argv:
        raise RuntimeError("cli_command_not_configured")

    proc = subprocess.run(
        argv,
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_seconds,
        check=False,
    )
    if proc.returncode != 0:
        err = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"cli_failed:{proc.returncode}:{err[:800]}")

    out = (proc.stdout or b"").decode("utf-8", errors="replace").strip()
    return out


def _sse(event: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


def _iter_cli_stream(command_template: str, model: Optional[str], prompt: str, timeout_seconds: int):
    template = (command_template or "").strip()
    if not template:
        yield _sse("error", {"message": "CLI command not configured", "code": "cli_command_not_configured"})
        return

    cmd_str = template.format_map(_SafeFormatDict(model=model or ""))
    argv = shlex.split(cmd_str)
    if not argv:
        yield _sse("error", {"message": "CLI command not configured", "code": "cli_command_not_configured"})
        return

    yield _sse("status", {"message": "正在启动本地 CLI", "stage": "starting_cli"})

    try:
        proc = subprocess.Popen(
            argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
        )
    except FileNotFoundError:
        yield _sse("error", {"message": "CLI not found", "code": "cli_not_found"})
        return

    stdout_chunks = []
    stderr_chunks = []
    streams = {}
    if proc.stdout:
        os.set_blocking(proc.stdout.fileno(), False)
        streams[proc.stdout.fileno()] = "stdout"
    if proc.stderr:
        os.set_blocking(proc.stderr.fileno(), False)
        streams[proc.stderr.fileno()] = "stderr"

    if proc.stdin:
        try:
            proc.stdin.write(prompt.encode("utf-8"))
            proc.stdin.close()
        except BrokenPipeError:
            yield _sse("trace", {"message": "CLI closed stdin before receiving the full prompt", "source": "process"})

    started_at = time.monotonic()
    last_status_at = started_at
    yield _sse("status", {"message": "已发送请求，等待模型输出", "stage": "waiting"})

    while proc.poll() is None or streams:
        now = time.monotonic()
        if proc.poll() is None and now - started_at > timeout_seconds:
            proc.kill()
            yield _sse("error", {"message": f"CLI timeout after {timeout_seconds}s", "code": "cli_timeout"})
            return

        ready = []
        if streams:
            try:
                import select
                ready, _, _ = select.select(list(streams.keys()), [], [], 0.25)
            except OSError:
                ready = []
        else:
            time.sleep(0.1)

        for fd in ready:
            stream_name = streams.get(fd)
            try:
                chunk = os.read(fd, 4096)
            except BlockingIOError:
                continue

            if not chunk:
                streams.pop(fd, None)
                continue

            text = chunk.decode("utf-8", errors="replace")
            if stream_name == "stdout":
                stdout_chunks.append(text)
            else:
                stderr_chunks.append(text)
                for line in text.replace("\r", "\n").splitlines():
                    clean_line = line.strip()
                    if clean_line:
                        yield _sse("trace", {"message": clean_line, "source": "stderr"})

        if proc.poll() is None and now - last_status_at >= 3:
            elapsed = int(now - started_at)
            last_status_at = now
            yield _sse(
                "status",
                {"message": f"模型仍在运行中，已等待 {elapsed}s", "stage": "waiting", "elapsed_seconds": elapsed},
            )

    return_code = proc.returncode
    out = "".join(stdout_chunks).strip()
    err = "".join(stderr_chunks).strip()

    if return_code != 0:
        yield _sse(
            "error",
            {
                "message": f"CLI exited with code {return_code}: {err[-800:] or 'no stderr output'}",
                "code": "cli_failed",
                "return_code": return_code,
            },
        )
        return

    yield _sse("message", {"content": out})
    yield _sse("done", {"message": "模型回答完成"})


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
    settings = db.query(UserSettings).filter(UserSettings.id == "default").first()
    workspace_root = _workspace_root_path(settings)
    project_response = ProjectResponse.from_orm(project)
    project_response.vault_path = str(_workspace_path_for_project(project, ensure=False, workspace_root=workspace_root))

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
            completion_percent=(t.actual_minutes / t.estimated_minutes * 100) if t.estimated_minutes > 0 else 0,
            created_at=t.created_at,
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
        project=project_response,
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
        gantt_data=gantt_data,
        workspace_root=str(workspace_root),
        workspace_files=_workspace_files_for_project(project, workspace_root=workspace_root),
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


@app.patch("/api/projects/{project_id}/workspace", response_model=WorkspaceResponse)
async def update_project_workspace(project_id: str, req: WorkspaceUpdateRequest, db: Session = Depends(get_db)):
    """Set or initialize the local workspace folder for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    settings = db.query(UserSettings).filter(UserSettings.id == "default").first()
    workspace_root = _workspace_root_path(settings)
    path_value = (req.vault_path or "").strip()
    workspace = (
        _validate_workspace_directory(path_value)
        if path_value
        else _workspace_path_for_project(project, ensure=False, workspace_root=workspace_root)
    )
    workspace.mkdir(parents=True, exist_ok=True)
    project.vault_path = str(workspace)
    db.add(project)
    db.commit()
    db.refresh(project)
    return _workspace_response(project, workspace_root)


@app.post("/api/projects/{project_id}/workspace/folders", response_model=WorkspaceResponse)
async def create_workspace_folder(
    project_id: str,
    req: WorkspaceFolderCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a single folder inside the project's local workspace."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    folder_name = (req.name or "").strip()
    if not folder_name or folder_name in {".", ".."} or "/" in folder_name or "\\" in folder_name:
        raise HTTPException(status_code=400, detail="Folder name must be a single folder name")

    settings = db.query(UserSettings).filter(UserSettings.id == "default").first()
    workspace_root = _workspace_root_path(settings)
    workspace = _workspace_path_for_project(project, workspace_root=workspace_root)
    target = (workspace / folder_name).resolve()
    workspace_resolved = workspace.resolve()
    if target.parent != workspace_resolved:
        raise HTTPException(status_code=400, detail="Folder must be created inside the workspace")
    if target.exists() and not target.is_dir():
        raise HTTPException(status_code=400, detail="A file with that name already exists")
    target.mkdir(exist_ok=True)

    db.add(project)
    db.commit()
    db.refresh(project)
    return _workspace_response(project, workspace_root)


@app.post("/api/chat/sync-tasks", response_model=ChatTaskSyncResponse)
async def sync_chat_tasks(req: ChatTaskSyncRequest, db: Session = Depends(get_db)):
    """Turn an assistant task breakdown into persisted dashboard tasks and workspace files."""
    from uuid import uuid4

    settings = db.query(UserSettings).filter(UserSettings.id == "default").first()
    workspace_root = _workspace_root_path(settings)
    project = None
    if req.project_id:
        project = db.query(Project).filter(Project.id == req.project_id).first()

    if not project:
        base_name = (req.project_name or "").strip() or "对话任务拆分"
        project = Project(
            id=str(uuid4()),
            name=base_name[:80],
            description="从对话同步生成的任务拆分项目",
            domain="chat_task_breakdown",
            vault_path=str(workspace_root / _safe_project_name(base_name)),
            cache_path=f"{Path.home()}/.coach/{_safe_project_name(base_name)}.db",
        )
        db.add(project)
        db.flush()

    parsed_tasks = _parse_tasks_from_markdown(req.content)
    existing_titles = {
        (task.title or "").strip().lower()
        for task in db.query(TaskRecord).filter(TaskRecord.project_id == project.id).all()
    }

    created = []
    skipped_count = 0
    for parsed in parsed_tasks:
        title_key = parsed["title"].strip().lower()
        if not title_key or title_key in existing_titles:
            skipped_count += 1
            continue
        task = TaskRecord(
            id=str(uuid4()),
            project_id=project.id,
            title=parsed["title"],
            description=parsed["description"],
            phase=parsed["phase"],
            status="pending",
            estimated_minutes=parsed["estimated_minutes"],
            actual_minutes=0,
            verification_criteria=json.dumps({"source": "chat_sync"}, ensure_ascii=False),
        )
        db.add(task)
        created.append(task)
        existing_titles.add(title_key)

    db.commit()
    db.refresh(project)

    all_tasks = db.query(TaskRecord).filter(TaskRecord.project_id == project.id).all()
    workspace_files = _write_workspace_files(project, all_tasks, req.content, workspace_root=workspace_root)
    db.add(project)
    db.commit()

    task_responses = [
        TaskResponse(
            id=t.id,
            title=t.title,
            description=t.description,
            phase=t.phase,
            status=t.status,
            estimated_minutes=t.estimated_minutes,
            actual_minutes=t.actual_minutes,
            completion_percent=(t.actual_minutes / t.estimated_minutes * 100) if t.estimated_minutes > 0 else 0,
            created_at=t.created_at,
        )
        for t in all_tasks
    ]

    return ChatTaskSyncResponse(
        project=ProjectResponse.from_orm(project),
        tasks=task_responses,
        workspace_files=workspace_files,
        created_count=len(created),
        skipped_count=skipped_count,
    )


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
        db.refresh(settings)

    changed = False
    if not settings.llm_provider or (
        settings.llm_provider == "anthropic"
        and not (settings.llm_api_key_encrypted or settings.llm_api_key)
    ):
        settings.llm_provider = DEFAULT_PROVIDER
        changed = True
    if not settings.llm_model or settings.llm_model.startswith("claude-3-"):
        settings.llm_model = DEFAULT_MODEL
        changed = True
    if not settings.cli_claude_command or settings.cli_claude_command == "claude --model {model}":
        settings.cli_claude_command = DEFAULT_CLAUDE_CLI_COMMAND
        changed = True
    if (
        not settings.cli_codex_command
        or settings.cli_codex_command == "codex --model {model}"
        or "--ask-for-approval" in settings.cli_codex_command
        or "--ephemeral" not in settings.cli_codex_command
    ):
        settings.cli_codex_command = DEFAULT_CODEX_CLI_COMMAND
        changed = True
    if not settings.cli_timeout_seconds:
        settings.cli_timeout_seconds = 120
        changed = True
    if not settings.workspace_root:
        settings.workspace_root = str(DEFAULT_WORKSPACE_ROOT)
        changed = True
    if changed:
        db.add(settings)
        db.commit()

    has_key = bool(settings.llm_api_key_encrypted or settings.llm_api_key)
    return {
        "theme": settings.theme,
        "font_size": settings.font_size,
        "language": settings.language,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "llm_base_url": settings.llm_base_url,
        "has_llm_api_key": has_key,
        "cli_claude_command": settings.cli_claude_command,
        "cli_codex_command": settings.cli_codex_command,
        "cli_timeout_seconds": settings.cli_timeout_seconds,
        "workspace_root": settings.workspace_root or str(DEFAULT_WORKSPACE_ROOT),
    }


@app.post("/api/settings")
async def update_settings(settings_data: dict, db: Session = Depends(get_db)):
    """Update user settings"""
    settings = db.query(UserSettings).filter(UserSettings.id == "default").first()
    if not settings:
        settings = UserSettings(id="default")

    api_key_value = None
    if "llm_api_key" in settings_data:
        api_key_value = settings_data.get("llm_api_key")
        settings_data = dict(settings_data)
        settings_data.pop("llm_api_key", None)
    if "workspace_root" in settings_data:
        raw_root = (settings_data.get("workspace_root") or "").strip()
        if raw_root:
            workspace_root = _validate_workspace_directory(raw_root)
            workspace_root.mkdir(parents=True, exist_ok=True)
            settings_data["workspace_root"] = str(workspace_root)
        else:
            settings_data["workspace_root"] = str(DEFAULT_WORKSPACE_ROOT)

    for key, value in settings_data.items():
        if hasattr(settings, key):
            setattr(settings, key, value)

    if api_key_value is not None:
        try:
            if api_key_value:
                settings.llm_api_key_encrypted = _encrypt_optional(str(api_key_value))
                settings.llm_api_key = None
            else:
                settings.llm_api_key_encrypted = None
                settings.llm_api_key = None
        except RuntimeError as e:
            if str(e) == "cryptography_not_installed":
                raise HTTPException(status_code=500, detail="cryptography not installed")
            raise

    db.add(settings)
    db.commit()
    return {"status": "updated"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.id == "default").first()
    if not settings:
        settings = UserSettings(id="default")
        db.add(settings)
        db.commit()
        db.refresh(settings)

    provider = (req.provider or settings.llm_provider or "").strip()
    model = (req.model or settings.llm_model or "").strip() or None
    timeout_seconds = int(settings.cli_timeout_seconds or 120)

    system_prompt = _build_system_prompt(req.mode, req.system_prompt)
    prompt = _render_prompt(system_prompt, req.messages)

    try:
        if provider in ("claude_code", "claude"):
            out = _run_cli(settings.cli_claude_command or DEFAULT_CLAUDE_CLI_COMMAND, model, prompt, timeout_seconds)
        elif provider in ("codex", "codex_cli"):
            out = _run_cli(settings.cli_codex_command or DEFAULT_CODEX_CLI_COMMAND, model, prompt, timeout_seconds)
        elif provider == "mock":
            last_user = ""
            for m in reversed(req.messages):
                if m.role == "user":
                    last_user = m.content
                    break
            out = f"mock: {last_user}".strip()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
    except FileNotFoundError:
        raise HTTPException(status_code=424, detail=f"CLI not found for provider: {provider}")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="CLI timeout")
    except RuntimeError as e:
        msg = str(e)
        if msg == "cli_command_not_configured":
            raise HTTPException(status_code=400, detail="CLI command not configured")
        if msg.startswith("cli_failed:"):
            _, code, stderr = msg.split(":", 2)
            raise HTTPException(
                status_code=500,
                detail=f"{provider} CLI exited with code {code}: {stderr or 'no stderr output'}",
            )
        raise HTTPException(status_code=500, detail=msg)

    return ChatResponse(
        provider=provider,
        model=model,
        message=ChatMessage(role="assistant", content=out),
    )


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest, db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.id == "default").first()
    if not settings:
        settings = UserSettings(id="default")
        db.add(settings)
        db.commit()
        db.refresh(settings)

    provider = (req.provider or settings.llm_provider or "").strip()
    model = (req.model or settings.llm_model or "").strip() or None
    timeout_seconds = int(settings.cli_timeout_seconds or 120)
    system_prompt = _build_system_prompt(req.mode, req.system_prompt)
    prompt = _render_prompt(system_prompt, req.messages)

    if provider in ("claude_code", "claude"):
        command_template = settings.cli_claude_command or DEFAULT_CLAUDE_CLI_COMMAND
    elif provider in ("codex", "codex_cli"):
        command_template = settings.cli_codex_command or DEFAULT_CODEX_CLI_COMMAND
    elif provider == "mock":
        def mock_stream():
            yield _sse("status", {"message": "已连接 mock provider", "stage": "connected"})
            yield _sse("trace", {"message": "mock provider 正在生成回答", "source": "mock"})
            last_user = ""
            for m in reversed(req.messages):
                if m.role == "user":
                    last_user = m.content
                    break
            yield _sse("message", {"content": f"mock: {last_user}".strip()})
            yield _sse("done", {"message": "模型回答完成"})

        return StreamingResponse(mock_stream(), media_type="text/event-stream")
    else:
        def unknown_provider_stream():
            yield _sse("error", {"message": f"Unknown provider: {provider}", "code": "unknown_provider"})

        return StreamingResponse(unknown_provider_stream(), media_type="text/event-stream")

    def event_stream():
        yield _sse(
            "status",
            {"message": f"正在连接 {provider}", "stage": "connecting", "provider": provider, "model": model},
        )
        yield from _iter_cli_stream(command_template, model, prompt, timeout_seconds)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


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
