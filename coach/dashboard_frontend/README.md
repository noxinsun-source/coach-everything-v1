# Coach Everything Dashboard Frontend

本文件夹包含 Coach Everything 的 Web 仪表板前端。

## 功能特性

### 📊 三栏布局（2:4:4 比例）

- **左侧栏（20%）**: 番茄钟计时器与快速统计
  - 25分钟工作计时
  - 番茄钟历史记录
  - 快速统计显示
  - 可展开至全屏查看详细分析

- **中间栏（60%）**: 项目与任务管理
  - 项目概览信息
  - 任务列表（支持筛选）
  - AI Coach 指导意见
  - 资源与技巧链接

- **右侧栏（20%）**: 工作区文件浏览
  - Obsidian 工作区文件树
  - 快速访问任务相关文件
  - 可展开至全屏

### ⏱️ 番茄钟计时器

- 25分钟工作周期
- 5分钟短休息（每4个番茄钟后15分钟长休息）
- 实时显示与通知
- WebSocket 实时更新支持

### 📈 数据分析与可视化

- 甘特图显示任务进度
- 饼图展示任务分布
- 详细统计表格
- 时间趋势分析
- 按时完成率计算

### ⚙️ 设置面板

- **主题设置**: 深色/浅色模式
- **显示设置**: 字体大小调整（12-18px）
- **语言设置**: 中文/英文切换
- **LLM 配置**: 选择 LLM 提供商与模型
- **MCP 配置**: MCP 状态监控

### 🎯 项目管理

- 项目选择器（下拉菜单）
- 多项目支持
- 项目进度跟踪
- 任务状态管理（待办/进行中/已完成）

## 文件结构

```
dashboard_frontend/
├── index.html           # 主 HTML 文件
├── css/
│   └── styles.css      # 全部样式表（响应式设计）
├── js/
│   ├── app.js          # 应用入口与初始化
│   ├── api.js          # API 客户端
│   └── ui.js           # UI 控制器与事件处理
└── README.md           # 本文件
```

## 技术栈

- **前端框架**: 原生 HTML5 + CSS3 + JavaScript (ES6+)
- **图表库**: Chart.js（饼图与数据可视化）
- **API 通信**: Fetch API
- **WebSocket**: 实时计时器更新
- **响应式设计**: CSS Grid + Flexbox
- **主题支持**: CSS 变量 + Dark Mode

## 快速开始

### 1. 启动后端服务

```bash
cd /path/to/coach-everything
python coach/dashboard_backend.py
```

后端将运行在 `http://127.0.0.1:8000`

### 2. 打开仪表板

在浏览器中访问：
```
http://127.0.0.1:8000/
```

### 3. 选择或创建项目

使用顶部的项目选择器选择一个项目开始使用。

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+S` / `Cmd+S` | 打开设置 |
| `Ctrl+Shift+A` / `Cmd+Shift+A` | 显示分析 |
| `Space` | 开始/暂停计时器 |
| `Esc` | 关闭模态框或收起面板 |

## API 对接

### 主要端点

#### 项目管理
- `GET /api/projects` - 获取所有项目
- `POST /api/projects` - 创建新项目
- `GET /api/projects/{project_id}/dashboard` - 获取项目仪表板数据

#### 任务管理
- `POST /api/projects/{project_id}/tasks` - 创建任务
- `PATCH /api/tasks/{task_id}` - 更新任务

#### 时间追踪
- `POST /api/time-logs` - 记录时间
- `GET /api/projects/{project_id}/time-logs` - 获取时间日志

#### 设置
- `GET /api/settings` - 获取用户设置
- `POST /api/settings` - 更新用户设置

#### WebSocket
- `WS /ws/pomodoro/{project_id}` - 实时番茄钟更新

### 响应数据结构

#### DashboardDataResponse
```json
{
  "project": {
    "id": "uuid",
    "name": "项目名",
    "description": "描述",
    "domain": "学习|研究|求职|创业",
    "created_at": "2026-05-09T00:00:00"
  },
  "tasks": [
    {
      "id": "uuid",
      "title": "任务标题",
      "description": "任务描述",
      "phase": "阶段",
      "status": "pending|in_progress|completed",
      "estimated_minutes": 120,
      "actual_minutes": 95,
      "completion_percent": 79.17
    }
  ],
  "time_stats": {
    "total_hours": 12.5,
    "average_duration": 95.0,
    "pomodoros_count": 15,
    "on_time_percent": 73.33,
    "fastest_task": "任务名",
    "slowest_task": "任务名"
  },
  "recent_coaching_notes": [
    {
      "type": "advice|encouragement|warning",
      "content": "建议或指导内容",
      "created_at": "2026-05-09T00:00:00"
    }
  ],
  "gantt_data": {
    "tasks": [
      {
        "id": "uuid",
        "name": "任务名",
        "start": "2026-05-09T10:00:00",
        "end": "2026-05-09T11:35:00",
        "duration": 95,
        "status": "completed"
      }
    ]
  }
}
```

## 开发指南

### 添加新功能

1. **UI 更新**: 在 `index.html` 中添加新的 HTML 元素
2. **样式**: 在 `css/styles.css` 中添加 CSS 规则
3. **事件处理**: 在 `js/ui.js` 中添加事件监听器和处理函数
4. **API 调用**: 在 `js/api.js` 中添加新的 API 方法

### 添加新的 API 端点

在 `js/api.js` 中的 `CoachAPI` 类添加方法：

```javascript
async getNewData(param) {
    return this.request('/api/endpoint', {
        method: 'GET',
        // or POST, PATCH, DELETE
    });
}
```

### 调试

在浏览器控制台访问：
```javascript
// 查看全局对象
window.CoachApp.api     // API 客户端
window.CoachApp.ui      // UI 控制器

// 测试 API
await api.getProjects();
```

## 浏览器兼容性

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 性能优化

- 使用 CSS Grid 和 Flexbox 实现高效布局
- 防止重复 DOM 更新
- WebSocket 用于实时更新而非轮询
- 本地 localStorage 存储用户偏好设置

## 故障排除

### "API 后端不可访问"警告

**解决方案**:
```bash
# 确保后端服务正在运行
python coach/dashboard_backend.py

# 检查是否监听 127.0.0.1:8000
lsof -i :8000
```

### 计时器不工作

1. 检查浏览器控制台是否有错误
2. 确保 WebSocket 连接正常
3. 清除浏览器缓存

### 样式未正确加载

- 清除浏览器缓存
- 检查 CSS 文件路径
- 在浏览器开发工具中检查网络标签

## 贡献指南

欢迎提交改进建议和 bug 报告！

## 许可证

MIT License - 与主项目相同
