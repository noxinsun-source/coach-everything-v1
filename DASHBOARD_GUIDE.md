# Coach Everything Dashboard - 快速启动指南

## 概述

Coach Everything Dashboard 是一个本地 Web 应用，用于可视化任务拆分、时间追踪和 AI 教练指导。

### 核心特性

- 🎨 三栏响应式布局（2:4:4 比例）
- ⏱️ 番茄钟计时器与时间追踪
- 📊 数据分析与可视化（甘特图、饼图、统计表）
- ⚙️ 完整设置面板（主题、语言、LLM 配置）
- 🔗 WebSocket 实时更新支持
- 📱 响应式设计（支持平板和手机）

## 前置条件

- Python 3.8+
- 现代浏览器（Chrome, Firefox, Safari, Edge）
- FastAPI 和依赖库已安装

## 快速启动

### 步骤 1: 安装依赖

```bash
cd /path/to/coach-everything

# 安装 Python 依赖
pip install -r requirements.txt

# 或使用 pyproject.toml
pip install -e .
```

### 步骤 2: 启动后端服务

```bash
python coach/dashboard_backend.py
```

您应该看到：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 步骤 3: 打开仪表板

在浏览器中打开：
```
http://127.0.0.1:8000/
```

## 使用指南

### 创建第一个项目

1. 启动后端服务
2. 打开仪表板
3. 使用 API 创建项目（或使用 CLI）：

```bash
# 使用 Coach CLI
python -m coach start --name "我的第一个项目" --domain "learning"
```

或通过 API：
```bash
curl -X POST http://127.0.0.1:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的第一个项目",
    "description": "项目描述",
    "domain": "learning",
    "vault_path": "/Users/me/Documents/Obsidian Vault"
  }'
```

### 界面导航

#### 顶部导航栏
- **左侧**: 应用标题 "🏃 Coach Everything"
- **中央**: 项目选择器（下拉菜单）
- **右侧**: 设置按钮和帮助按钮

#### 三栏布局

**左栏（20%）- 番茄钟与统计**
- 大显示的倒计时（25:00 或时间）
- 开始/暂停/重置按钮
- 今日完成的番茄钟数
- 累计耗时
- "查看统计"按钮展开详细分析

**中栏（60%）- 核心内容**
- 项目概览（名称、领域、进度条）
- 任务列表（支持筛选：全部/待办/进行中/已完成）
- Coach AI 指导建议
- 资源与技巧链接

**右栏（20%）- 工作区文件**
- Obsidian 工作区目录树
- 快速访问项目相关文件

### 番茄钟计时器

1. **开始工作**
   - 点击"开始"按钮或按 `Space`
   - 计时器开始 25 分钟倒计时
   - 状态显示"⏱️ 工作中..."

2. **完成工作周期**
   - 倒计时结束时自动进入休息模式
   - 显示休息时间（5 分钟或 15 分钟长休息）
   - 完成番茄钟数自动加 1

3. **暂停/重置**
   - 点击"暂停"可暂停计时
   - 点击"重置"可重新开始当前周期

### 任务管理

**任务状态**
- 待办（蓝色）：尚未开始
- 进行中（黄色）：正在进行中
- 已完成（绿色）：已完成

**任务信息**
- 标题和描述
- 估计耗时和实际耗时
- 所属阶段
- 完成度百分比

**筛选任务**
- 点击顶部的筛选按钮（全部/待办/进行中/已完成）
- 列表会实时更新

### 数据分析

1. **打开分析视图**
   - 点击左栏的"查看统计"按钮
   - 或按 `Ctrl+Shift+A`（Windows/Linux）或 `Cmd+Shift+A`（Mac）

2. **查看数据**
   - **甘特图**: ASCII 风格的任务时间线
   - **饼图**: 任务状态分布（已完成/进行中/待办）
   - **统计表**: 详细数据（总小时数、平均耗时、按时完成率等）

### 设置面板

**打开设置**
- 点击右上角的齿轮图标
- 或按 `Ctrl+S`（Windows/Linux）或 `Cmd+S`（Mac）

**主题设置**
- 切换深色/浅色模式

**显示设置**
- 调整字体大小（12-18px）

**语言设置**
- 中文或英文

**LLM 配置**
- 选择 LLM 提供商（Anthropic/OpenAI/自定义）
- 选择模型（Claude/GPT-4）

**MCP 配置**
- 查看 MCP 连接状态

### 面板展开

- 点击左栏顶部的"展开"按钮 → 番茄钟和统计占据整个屏幕
- 点击右栏顶部的"展开"按钮 → 文件浏览器占据整个屏幕
- 按 `Esc` 收起展开的面板

## 快捷键参考

| 快捷键 | 功能 |
|--------|------|
| `Space` | 开始/暂停计时器 |
| `Ctrl+S` / `Cmd+S` | 打开设置 |
| `Ctrl+Shift+A` / `Cmd+Shift+A` | 显示分析 |
| `Esc` | 关闭模态框或收起面板 |

## API 示例

### 获取所有项目

```bash
curl http://127.0.0.1:8000/api/projects
```

响应：
```json
[
  {
    "id": "uuid-1234",
    "name": "我的第一个项目",
    "description": "项目描述",
    "domain": "learning",
    "created_at": "2026-05-09T10:00:00"
  }
]
```

### 获取项目仪表板数据

```bash
curl http://127.0.0.1:8000/api/projects/uuid-1234/dashboard
```

### 创建任务

```bash
curl -X POST http://127.0.0.1:8000/api/projects/uuid-1234/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "完成项目计划",
    "description": "详细描述任务",
    "phase": "规划",
    "estimated_minutes": 120,
    "verification_criteria": {
      "description": "计划文档已完成",
      "commands": ["cat plan.md"]
    }
  }'
```

### 记录时间

```bash
curl -X POST http://127.0.0.1:8000/api/time-logs \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task-uuid",
    "project_id": "project-uuid",
    "duration_minutes": 25,
    "pomodoros": 1,
    "start_time": "2026-05-09T10:00:00",
    "end_time": "2026-05-09T10:25:00",
    "completed": false
  }'
```

## 数据存储

所有数据存储在本地 SQLite 数据库中：

```
~/.coach/coach_dashboard.db
```

表结构：
- `projects` - 项目信息
- `tasks` - 任务记录
- `time_logs` - 时间记录
- `coaching_notes` - AI 教练笔记
- `user_settings` - 用户设置

## 故障排除

### 问题 1: "API 后端不可访问"

**原因**: 后端服务未运行

**解决方案**:
```bash
# 在新的终端窗口运行
python coach/dashboard_backend.py

# 检查是否监听 8000 端口
lsof -i :8000
```

### 问题 2: 加载项目时出错

**原因**: 项目数据格式不正确或数据库损坏

**解决方案**:
```bash
# 重置数据库（谨慎！这会删除所有数据）
rm ~/.coach/coach_dashboard.db

# 重新启动后端
python coach/dashboard_backend.py
```

### 问题 3: WebSocket 连接失败

**原因**: 防火墙或代理阻止 WebSocket

**解决方案**:
- 检查防火墙规则
- 尝试在浏览器控制台检查连接错误
- 刷新页面重新连接

### 问题 4: 样式未正确加载

**原因**: CSS 文件路径不正确

**解决方案**:
- 清除浏览器缓存
- 按 `Ctrl+F5`（Windows/Linux）或 `Cmd+Shift+R`（Mac）强制刷新
- 检查浏览器开发工具的网络标签

## 开发模式

### 启用自动重载

```bash
python coach/dashboard_backend.py
```

后端已配置为在代码改变时自动重载（`reload=True`）

### 浏览器调试

打开浏览器开发工具（F12）：

1. **Console** 标签：查看日志和错误
2. **Network** 标签：查看 API 调用
3. **Application** 标签：查看本地存储和 WebSocket

### 在控制台测试 API

```javascript
// 获取所有项目
await api.getProjects()

// 获取特定项目的仪表板
await api.getProjectDashboard('project-uuid')

// 更新设置
await api.updateSettings({ theme: 'dark' })
```

## 生产部署

对于生产环境，建议：

1. **使用生产服务器**
   ```bash
   python -m uvicorn coach.dashboard_backend:app --host 0.0.0.0 --port 8000
   ```

2. **启用 HTTPS**
   - 配置反向代理（nginx/Caddy）
   - 使用 SSL 证书

3. **数据备份**
   ```bash
   cp ~/.coach/coach_dashboard.db ~/.coach/coach_dashboard.db.backup
   ```

4. **性能优化**
   - 增加 SQLite 缓存
   - 使用连接池
   - 启用 GZIP 压缩

## 更多信息

- 完整 API 文档: `coach/dashboard_backend.py`
- 前端代码: `coach/dashboard_frontend/`
- CLI 工具: `coach/main.py`
- 配置文件: `~/.coach/config.yaml`

## 问题反馈

如果遇到问题，请检查：
1. 后端是否运行
2. 浏览器控制台是否有错误
3. 网络连接是否正常
4. 数据库文件是否存在且可访问

---

祝您使用愉快！🚀
