# Coach Everything Dashboard - 详细设置指南

## 什么是 Dashboard？

Coach Everything Dashboard 是一个本地 Web 应用，提供：

- 📊 实时任务进度与时间追踪
- ⏱️ 番茄钟计时器与统计
- 📈 数据可视化（甘特图、饼图）
- ⚙️ 完整的设置和配置界面
- 🔗 与 Obsidian 工作区的集成

## 架构概述

```
┌─────────────────────────────────────────────┐
│         浏览器 (Web Dashboard)              │
│  ┌──────────┬──────────┬──────────────────┐ │
│  │左栏(20%)│中栏(60%)│右栏(20%)         │ │
│  │番茄钟   │任务拆分 │工作区文件       │ │
│  └──────────┴──────────┴──────────────────┘ │
└──────────────────────────────────────────────┘
                      ↕️ HTTP/WebSocket
┌──────────────────────────────────────────────┐
│    FastAPI 后端 (127.0.0.1:8000)            │
│  ┌────────────────────────────────────────┐ │
│  │        SQLite 数据库                   │ │
│  │  ~/.coach/coach_dashboard.db           │ │
│  └────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

## 系统要求

- **Python**: 3.8 或更高版本
- **浏览器**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **操作系统**: macOS, Linux, Windows
- **网络**: 本地网络（不需要互联网连接）

## 安装步骤

### 1. 克隆项目（如果还没有）

```bash
git clone https://github.com/noxinsun/coach-everything.git
cd coach-everything
```

### 2. 创建虚拟环境（推荐）

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

或者使用 `pyproject.toml`：

```bash
pip install -e .
```

### 4. 初始化配置

```bash
mkdir -p ~/.coach
```

配置文件将在首次运行时自动创建。

## 启动 Dashboard

### 方法 1: 直接运行（开发模式）

```bash
python coach/dashboard_backend.py
```

输出应该显示：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 方法 2: 使用 uvicorn 运行（生产模式）

```bash
python -m uvicorn coach.dashboard_backend:app --host 127.0.0.1 --port 8000
```

### 方法 3: 后台运行（macOS/Linux）

```bash
nohup python coach/dashboard_backend.py > dashboard.log 2>&1 &
```

## 访问 Dashboard

1. 打开浏览器
2. 访问: `http://127.0.0.1:8000/`
3. 您应该看到 Coach Everything Dashboard 界面

## 创建第一个项目

### 使用 CLI 创建

```bash
python -m coach start --name "我的第一个项目" --domain "learning"
```

### 使用 API 创建

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

### 在 Dashboard 中

1. 后端启动后，CLI 或 API 创建的项目会自动显示
2. 在顶部的项目选择器中选择项目
3. 仪表板会加载项目数据

## 验证安装

### 运行测试套件

```bash
python test_dashboard.py
```

这将测试：
- ✅ 后端连接
- ✅ 前端文件服务
- ✅ 数据库完整性
- ✅ API 端点
- ✅ 项目/任务/时间日志 CRUD 操作
- ✅ 设置管理

## 配置文件

配置文件位置：`~/.coach/config.yaml`

### 首次创建的默认配置

```yaml
llm:
  provider: anthropic
  model_name: claude-3-haiku-20240307
  api_key: null
  base_url: null

obsidian_vault_path: /Users/me/Documents/Obsidian Vault
cache_dir: /Users/me/.coach

search:
  platforms:
    - reddit
    - forums
    - blogs
    - github
  include_papers: true
  recency_weight: 0.7
  max_results_per_platform: 10

task_atomization:
  default_micro_task_duration: 120
  require_approval: true
  include_verification_criteria: true
  refinement_levels: 3

coach_agent:
  personality: encouraging
  check_in_frequency: 60
  celebrate_milestones: true
  offer_help_threshold: 30
```

### 配置 LLM API 密钥

编辑 `~/.coach/config.yaml`：

```yaml
llm:
  provider: anthropic
  model_name: claude-3-haiku-20240307
  api_key: sk_xxxxxxxxxxxxx  # 在这里添加您的 API 密钥
```

或者在 Dashboard 设置面板中配置（不保存到文件）。

## 数据管理

### 数据存储位置

```
~/.coach/
├── coach_dashboard.db      # 主数据库（项目、任务、时间日志）
├── config.yaml             # 用户配置
└── [project-name].db       # 项目级别的缓存数据库
```

### 备份数据

```bash
# 完整备份
cp -r ~/.coach ~/.coach.backup-$(date +%Y%m%d)

# 仅备份数据库
cp ~/.coach/coach_dashboard.db ~/.coach/coach_dashboard.db.backup
```

### 恢复数据

```bash
# 从备份恢复
cp ~/.coach.backup-20260509/coach_dashboard.db ~/.coach/coach_dashboard.db
```

### 重置数据库（谨慎！）

```bash
# 删除数据库（下次启动时将创建新的）
rm ~/.coach/coach_dashboard.db

# 重启后端
python coach/dashboard_backend.py
```

## 常见问题

### Q1: 后端启动失败

**错误**: `Address already in use`

**解决方案**:
```bash
# 找到占用 8000 端口的进程
lsof -i :8000

# 杀死该进程
kill -9 <PID>

# 或改用其他端口
python -m uvicorn coach.dashboard_backend:app --port 8001
```

### Q2: 无法访问 Dashboard

**错误**: `ERR_CONNECTION_REFUSED`

**解决方案**:
1. 确认后端正在运行: `lsof -i :8000`
2. 检查防火墙规则
3. 尝试 `http://localhost:8000` 而不是 `127.0.0.1`

### Q3: 数据没有保存

**检查**:
1. 检查数据库文件是否存在: `ls -la ~/.coach/coach_dashboard.db`
2. 检查文件权限: `chmod 644 ~/.coach/coach_dashboard.db`
3. 查看错误日志: 后端控制台输出

### Q4: WebSocket 连接失败

**症状**: 计时器更新不及时

**解决方案**:
1. 检查浏览器控制台是否有错误（F12）
2. 尝试刷新页面
3. 检查代理或防火墙是否阻止 WebSocket

### Q5: 字体大小/主题改变后没有效果

**解决方案**:
1. 清除浏览器缓存: Ctrl+Shift+Delete（Windows）或 Cmd+Shift+Delete（Mac）
2. 硬刷新: Ctrl+F5（Windows）或 Cmd+Shift+R（Mac）

## 性能优化

### 对于大量任务（1000+ 任务）

1. **启用数据库索引**
   ```bash
   sqlite3 ~/.coach/coach_dashboard.db "CREATE INDEX idx_project_id ON tasks(project_id);"
   ```

2. **分页加载任务**
   - 修改后端在 API 中实现分页

3. **增加 SQLite 缓存**
   ```python
   # 在 dashboard_backend.py 中
   engine = create_engine(
       DATABASE_URL,
       connect_args={"check_same_thread": False},
       pool_pre_ping=True,
       echo_pool=True
   )
   ```

### 对于慢速网络

1. **启用 gzip 压缩**
   ```python
   from fastapi.middleware.gzip import GZIPMiddleware
   app.add_middleware(GZIPMiddleware, minimum_size=1000)
   ```

2. **优化静态文件**
   - 缩小 CSS/JS
   - 使用 CDN 托管 Chart.js

## 生产部署

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 使用 Docker（可选）

创建 `Dockerfile`：
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "coach/dashboard_backend.py"]
```

构建和运行：
```bash
docker build -t coach-everything .
docker run -p 8000:8000 -v ~/.coach:/root/.coach coach-everything
```

## 日志和调试

### 查看后端日志

```bash
# 运行时查看（在前台运行）
python coach/dashboard_backend.py

# 后台运行时查看
tail -f dashboard.log
```

### 启用调试模式

编辑 `coach/dashboard_backend.py`：
```python
# 改为
app = FastAPI(
    title="Coach Everything Dashboard",
    version="1.0.0",
    debug=True  # 添加此行
)
```

### 浏览器开发工具

1. 打开 F12
2. **Console** 标签: JavaScript 错误和日志
3. **Network** 标签: API 请求/响应
4. **Storage** 标签: 本地数据和 Cookies

## 下一步

1. 📖 阅读 [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) 了解如何使用
2. 🔧 查看 [coach/dashboard_frontend/README.md](coach/dashboard_frontend/README.md) 了解前端详情
3. 🛠️ 修改 [coach/dashboard_backend.py](coach/dashboard_backend.py) 自定义后端

## 获取帮助

- 查看 GitHub Issues: https://github.com/noxinsun/coach-everything/issues
- 查看主要 README: [README.md](README.md)
- 检查测试套件: `python test_dashboard.py`

---

祝您使用愉快！🚀

如有任何问题，欢迎提出 Issue 或 Pull Request。
