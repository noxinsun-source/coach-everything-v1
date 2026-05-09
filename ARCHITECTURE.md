# Coach Everything Dashboard - 完整架构文档

## 系统架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│                   (Web Dashboard UI)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  index.html + CSS + JavaScript                         │ │
│  │  - 响应式三栏布局 (2:4:4)                             │ │
│  │  - 番茄钟计时器与统计                                │ │
│  │  - 任务管理与进度追踪                                │ │
│  │  - 设置和配置面板                                    │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────┬───────────────────┘
                                           ↕️
                                   HTTP/WebSocket
                                           ↓
┌──────────────────────────────────────────────────────────────┐
│              API Layer (FastAPI Backend)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  REST Endpoints & WebSocket                           │ │
│  │  - /api/projects                                      │ │
│  │  - /api/projects/{id}/dashboard                      │ │
│  │  - /api/projects/{id}/tasks                          │ │
│  │  - /api/time-logs                                    │ │
│  │  - /api/settings                                     │ │
│  │  - /ws/pomodoro/{project_id}                         │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────┬───────────────────┘
                                           ↕️
                                        ORM
                                           ↓
┌──────────────────────────────────────────────────────────────┐
│            Data Layer (SQLAlchemy + SQLite)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Database: ~/.coach/coach_dashboard.db               │ │
│  │                                                       │ │
│  │  Tables:                                              │ │
│  │  - projects (id, name, domain, vault_path)          │ │
│  │  - tasks (id, project_id, title, status, time)     │ │
│  │  - time_logs (id, task_id, duration, pomodoros)    │ │
│  │  - coaching_notes (id, content, type)               │ │
│  │  - user_settings (theme, language, llm_config)     │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## 前端架构（Frontend）

### 文件结构

```
coach/dashboard_frontend/
├── index.html           # 单页应用主文件
├── css/
│   └── styles.css      # 全部样式（~1100 行，包括响应式设计）
├── js/
│   ├── app.js          # 应用初始化和全局设置
│   ├── api.js          # API 客户端和 HTTP 通信
│   └── ui.js           # UI 控制器和事件处理
└── README.md           # 前端开发指南
```

### 核心类和模块

#### `js/api.js` - API 客户端

```javascript
class CoachAPI {
    // 项目管理
    getProjects()                          // GET /api/projects
    createProject(data)                    // POST /api/projects
    getProjectDashboard(projectId)         // GET /api/projects/{id}/dashboard

    // 任务管理
    createTask(projectId, taskData)        // POST /api/projects/{id}/tasks
    updateTask(taskId, updates)            // PATCH /api/tasks/{id}

    // 时间追踪
    logTime(logData)                       // POST /api/time-logs
    getTimeLogs(projectId)                 // GET /api/projects/{id}/time-logs

    // 设置管理
    getSettings()                          // GET /api/settings
    updateSettings(data)                   // POST /api/settings

    // WebSocket
    connectPomodoroWebSocket(projectId)    // WS /ws/pomodoro/{projectId}
    sendPomodoroEvent(ws, event)
}
```

#### `js/ui.js` - UI 控制器

```javascript
class DashboardUI {
    // 项目管理
    loadProjects()                         // 加载并显示项目列表
    loadProject(projectId)                 // 加载特定项目的完整数据
    populateProjectSelector(projects)      // 填充项目下拉菜单

    // 渲染方法
    renderTasks(tasks)                     // 渲染任务列表
    renderCoachingNotes(notes)             // 渲染 AI 教练笔记
    renderFileTree(project)                // 渲染工作区文件树
    renderGanttChart(ganttData)            // 渲染甘特图
    renderPieChart(tasks)                  // 渲染饼图

    // 计时器管理
    startTimer()                           // 开始计时
    pauseTimer()                           // 暂停计时
    resetTimer()                           // 重置计时
    completeTimerPhase()                   // 完成一个阶段（工作或休息）
    updateTimerDisplay()                   // 更新显示的时间

    // 面板控制
    toggleLeftPanelExpand()                // 展开/收起左栏
    toggleRightPanelExpand()               // 展开/收起右栏

    // 分析和统计
    showAnalytics()                        // 显示分析模态框
    closeAnalytics()                       // 关闭分析模态框

    // 设置管理
    showSettings()                         // 显示设置模态框
    saveSettings()                         // 保存设置
    loadSettings()                         // 加载用户设置
    toggleTheme(isDark)                    // 切换深色/浅色模式
    changeFontSize(size)                   // 改变字体大小

    // 工具方法
    filterTasks(filter)                    // 按状态筛选任务
    showNotification(message, type)        // 显示通知
}
```

#### `js/app.js` - 应用初始化

```javascript
// 初始化过程
document.addEventListener('DOMContentLoaded', () => {
    addAnimationStyles()                   // 添加动画样式
    initializeDashboard()                  // 初始化仪表板
})

// 设置
function applySystemTheme()                // 应用系统主题偏好
function setupKeyboardShortcuts()          // 设置快捷键
function checkAPIConnection()              // 检查 API 连接
```

### UI 组件布局

#### 三栏布局（2:4:4 比例）

```
┌──────────────────────────────────────────────────────────────┐
│                      导航栏                                    │
├────────────────────────────────────────────────────────────┤
│       │                                        │              │
│ 左栏  │              中栏（核心内容）        │   右栏       │
│ 20%  │                  60%                 │   20%        │
│       │                                        │              │
│ ─── │ ─────────────────────────────────── │ ─────        │
│ 番茄 │ 项目概览                            │ 工作区      │
│ 钟   │ • 项目名                            │ • 📋 路线   │
│      │ • 进度条                            │ • 📊 任务   │
│      │                                        │ • 🤖 日志   │
│ ─── │ ─────────────────────────────────── │ ─────        │
│      │ 任务列表                            │              │
│ 统计 │ • 筛选按钮                         │              │
│      │ • 任务卡片                         │              │
│      │   - 标题/描述                      │              │
│      │   - 状态/耗时                      │              │
│      │   - 进度                            │              │
│      │                                        │              │
│ ─── │ ─────────────────────────────────── │ ─────        │
│      │ Coach 指导                         │              │
│      │ • 建议                              │              │
│      │ • 鼓励                              │              │
│      │ • 警告                              │              │
│      │                                        │              │
│      │ 资源与技巧                         │              │
│      │ • 链接列表                         │              │
│      │                                        │              │
└──────────────────────────────────────────────────────────────┘
```

### CSS 架构

- **CSS 变量系统**: 用于主题和响应式设计
- **Grid + Flexbox**: 响应式布局
- **动画**: 过渡和关键帧动画
- **深色模式**: `body.dark-mode` 类

```css
:root {
    --color-primary: #6366f1
    --color-bg-light: #f9fafb
    --sidebar-width: 260px
    /* ... 更多变量 ... */
}

body.dark-mode {
    --color-bg-light: #1f2937
    --color-text-dark: #f3f4f6
    /* ... 覆盖变量 ... */
}
```

## 后端架构（Backend）

### 文件结构

```
coach/
├── dashboard_backend.py        # FastAPI 应用主文件
├── __init__.py                 # 包初始化
├── agent.py                    # Coach Agent 核心
├── config.py                   # 配置管理
├── llm_manager.py              # LLM 提供商管理
├── timer_and_analytics.py      # 计时器与分析
├── main.py                     # CLI 工具
├── models/                     # 数据模型
│   ├── task.py
│   ├── roadmap.py
│   └── workspace.py
├── engines/                    # 核心引擎
│   ├── search_engine.py
│   ├── task_atomizer.py
│   └── workspace_generator.py
├── storage/                    # 数据存储
│   ├── cache_manager.py
│   └── preference_manager.py
├── feedback/                   # 反馈系统
└── dashboard_frontend/         # Web UI
    ├── index.html
    ├── css/
    └── js/
```

### FastAPI 应用（dashboard_backend.py）

#### 数据库模型（SQLAlchemy ORM）

```python
class Project(Base):
    """项目"""
    id: String (PK)
    name: String (unique)
    description: String
    domain: String (learning/research/job_hunting/startup)
    created_at: DateTime
    vault_path: String (Obsidian 路径)
    cache_path: String (SQLite 缓存路径)

class TaskRecord(Base):
    """任务记录"""
    id: String (PK)
    project_id: String (FK)
    title: String
    description: String
    phase: String
    status: String (pending/in_progress/completed)
    estimated_minutes: Integer
    actual_minutes: Integer
    created_at: DateTime
    completed_at: DateTime (nullable)
    verification_criteria: JSON String

class TimeLog(Base):
    """时间日志"""
    id: String (PK)
    task_id: String (FK)
    project_id: String (FK)
    pomodoros: Integer
    duration_minutes: Integer
    start_time: DateTime
    end_time: DateTime (nullable)

class CoachingNote(Base):
    """教练笔记"""
    id: String (PK)
    project_id: String (FK)
    task_id: String (FK, nullable)
    note_type: String (advice/encouragement/warning)
    content: String
    created_at: DateTime

class UserSettings(Base):
    """用户设置"""
    id: String (PK)
    theme: String (light/dark)
    font_size: Integer
    language: String (zh/en)
    llm_provider: String
    llm_model: String
    llm_api_key: String (nullable)
```

#### API 端点

```python
# 项目管理
GET    /api/projects                      # 获取所有项目
POST   /api/projects                      # 创建项目
GET    /api/projects/{project_id}/dashboard  # 获取仪表板数据

# 任务管理
POST   /api/projects/{project_id}/tasks   # 创建任务
PATCH  /api/tasks/{task_id}               # 更新任务

# 时间追踪
POST   /api/time-logs                     # 记录时间
GET    /api/projects/{project_id}/time-logs  # 获取时间日志

# 设置管理
GET    /api/settings                      # 获取设置
POST   /api/settings                      # 保存设置

# WebSocket
WS     /ws/pomodoro/{project_id}          # 番茄钟实时更新
```

#### 响应模型（Pydantic）

```python
class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    domain: str
    created_at: datetime

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    phase: str
    status: str
    estimated_minutes: int
    actual_minutes: int
    completion_percent: float

class TimeStatsResponse(BaseModel):
    total_hours: float
    average_duration: float
    pomodoros_count: int
    on_time_percent: float
    fastest_task: str
    slowest_task: str

class DashboardDataResponse(BaseModel):
    project: ProjectResponse
    tasks: List[TaskResponse]
    time_stats: TimeStatsResponse
    recent_coaching_notes: List[dict]
    gantt_data: dict
```

### 数据流（Data Flow）

#### 加载项目流程

```
1. 用户在项目选择器中选择项目
   ↓
2. 前端调用 api.getProjectDashboard(projectId)
   ↓
3. FastAPI 处理 GET /api/projects/{project_id}/dashboard
   ↓
4. 后端查询数据库：
   - 获取项目信息
   - 获取所有任务
   - 获取时间日志
   - 获取最近的教练笔记
   ↓
5. 后端计算统计数据：
   - 总小时数
   - 平均耗时
   - 番茄钟数
   - 按时完成率
   - 最快/最慢任务
   ↓
6. 生成甘特图数据
   ↓
7. 返回 DashboardDataResponse（JSON）
   ↓
8. 前端使用数据更新 UI：
   - renderTasks()
   - renderCoachingNotes()
   - updateStats()
   - connectPomodoroWebSocket()
```

#### 记录时间流程

```
1. 用户完成一个番茄钟周期
   ↓
2. 前端调用 api.logTime(timeData)
   ↓
3. FastAPI 处理 POST /api/time-logs
   ↓
4. 后端：
   - 创建 TimeLog 记录
   - 更新对应 TaskRecord 的 actual_minutes
   - 更新任务状态（如果已完成）
   ↓
5. 通过 WebSocket 广播更新到所有连接的客户端
   ↓
6. 前端接收更新，刷新 UI
```

## 集成点

### 1. 与 CLI 的集成

```
CLI (coach/main.py)
    ↓
CoachAgent
    ↓
创建项目/任务
    ↓
保存到 SQLite
    ↓
Dashboard 自动显示
```

### 2. 与 Obsidian 的集成

```
Dashboard 显示 vault_path
    ↓
通过右栏文件树浏览工作区
    ↓
显示相关文件：
    - 📋 Roadmap.md
    - 📊 Task Progress.md
    - 🤖 Coach Log.md
```

### 3. 与 LLM 的集成

```
用户在设置中配置 LLM
    ↓
保存到 user_settings 表
    ↓
前端可能直接调用 LLM API（客户端）
或
后端调用 LLM 生成教练笔记（通过 CoachingNote）
```

## 实时更新（WebSocket）

### 番茄钟 WebSocket 协议

```
连接: WS http://127.0.0.1:8000/ws/pomodoro/{project_id}

消息格式：
{
    "type": "timer_event",  // timer_start, timer_pause, timer_complete, etc.
    "data": {
        "pomodoro": 1,
        "phase": "work",  // work or break
        "remaining": 1500,  // 秒
        "timestamp": "2026-05-09T10:00:00"
    }
}

服务器广播：
{
    "type": "timer_event",
    "data": { ... }  // 相同格式
}
```

## 性能考虑

### 数据库优化

```python
# 索引
CREATE INDEX idx_project_id ON tasks(project_id)
CREATE INDEX idx_task_id ON time_logs(task_id)
CREATE INDEX idx_created_at ON time_logs(created_at)

# 查询优化
- 使用关系加载避免 N+1 查询
- 分页加载大量任务
- 缓存计算的统计数据
```

### 前端优化

```javascript
// 防止不必要的 DOM 更新
- 检查数据是否改变才更新
- 使用事件委托
- 虚拟化长列表

// 网络优化
- 合并 API 请求
- 使用 WebSocket 减少轮询
- gzip 压缩响应
```

## 错误处理

### 后端错误处理

```python
try:
    # 业务逻辑
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
except SQLAlchemyError:
    raise HTTPException(status_code=500, detail="Database error")
```

### 前端错误处理

```javascript
try {
    const data = await api.getProjects()
} catch (error) {
    console.error('Failed:', error)
    ui.showNotification('操作失败', 'error')
}

// WebSocket 错误
ws.onerror = (error) => {
    console.error('WebSocket error:', error)
    // 自动重连逻辑
}
```

## 扩展点

### 添加新的 API 端点

1. 在后端添加 SQLAlchemy 模型
2. 创建 Pydantic 响应模型
3. 添加 FastAPI 路由
4. 在前端 `api.js` 中添加客户端方法
5. 在 `ui.js` 中添加 UI 逻辑

### 添加新的 UI 组件

1. 在 `index.html` 中添加 HTML
2. 在 `styles.css` 中添加样式
3. 在 `ui.js` 中添加事件处理

## 测试架构

```
test_dashboard.py
├── checkAPIConnection()      # 检查后端可达性
├── testFrontendFiles()       # 检查文件服务
├── testCreateProject()       # 创建项目
├── testGetProjects()         # 获取项目列表
├── testGetDashboard()        # 获取仪表板数据
├── testCreateTask()          # 创建任务
├── testLogTime()             # 记录时间
├── testSettings()            # 设置管理
└── testDatabaseIntegrity()   # 数据库完整性
```

## 部署架构

### 开发环境

```
python coach/dashboard_backend.py
→ 127.0.0.1:8000
→ 自动重载（reload=True）
```

### 生产环境

```
Nginx (reverse proxy)
    ↓
Uvicorn (production ASGI server)
    ↓
FastAPI app
    ↓
SQLite (or PostgreSQL)
```

---

本文档涵盖了 Coach Everything Dashboard 的完整架构。更多详情请参考各个组件的 README 文件。
