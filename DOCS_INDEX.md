# Coach Everything 文档索引

完整的文档导航和快速链接指南。

## 🚀 快速开始

**新用户从这里开始：**

1. **[QUICK_START.md](QUICK_START.md)** ⭐ - 5 分钟快速上手
   - 安装步骤
   - 启动仪表板
   - 创建第一个项目
   - 基本用法

## 📚 完整文档

### 用户指南

- **[README.md](README.md)** - 项目主页
  - Coach Everything 是什么
  - 核心功能概述
  - 系统架构说明
  - 安装选项

- **[DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)** - 仪表板完整指南
  - Dashboard 概述和特性
  - 前置条件和启动步骤
  - 完整的使用指南
  - 快捷键参考
  - API 使用示例
  - 故障排除

- **[DASHBOARD_SETUP.md](DASHBOARD_SETUP.md)** - 详细设置和配置
  - 系统架构图
  - 安装步骤（包括虚拟环境）
  - 配置文件说明
  - 数据管理和备份
  - 常见问题解答
  - 性能优化
  - 生产部署指南
  - 日志和调试

### 技术文档

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 完整系统架构
  - 系统架构总览
  - 前端架构详解
  - 后端架构详解
  - 数据流说明
  - 实时更新（WebSocket）
  - 性能考虑
  - 错误处理
  - 扩展指南
  - 测试架构
  - 部署架构

- **[coach/dashboard_frontend/README.md](coach/dashboard_frontend/README.md)** - 前端开发指南
  - 功能特性
  - 文件结构
  - 技术栈
  - API 对接详情
  - 响应数据结构
  - 开发指南
  - 浏览器兼容性
  - 故障排除

## 🔧 工具和脚本

- **[test_dashboard.py](test_dashboard.py)** - 测试套件
  - 验证后端连接
  - 检查前端文件
  - 测试所有 API 端点
  - 数据库完整性检查
  
  运行方式：
  ```bash
  python test_dashboard.py
  ```

## 📁 代码结构

```
coach-everything/
├── README.md                          # 主要文档
├── QUICK_START.md                     # 快速开始 ⭐
├── DASHBOARD_GUIDE.md                 # Dashboard 用户指南
├── DASHBOARD_SETUP.md                 # 详细设置指南
├── ARCHITECTURE.md                    # 系统架构文档
├── DOCS_INDEX.md                      # 本文件
├── test_dashboard.py                  # 测试脚本
├── requirements.txt                   # Python 依赖
├── setup.py                           # 包配置
├── pyproject.toml                     # 项目配置
│
├── coach/                             # 主要代码包
│   ├── __init__.py
│   ├── main.py                        # CLI 工具
│   ├── agent.py                       # Coach Agent
│   ├── config.py                      # 配置管理
│   ├── llm_manager.py                 # LLM 提供商管理
│   ├── timer_and_analytics.py         # 计时器和分析
│   ├── dashboard_backend.py           # FastAPI 后端
│   │
│   ├── dashboard_frontend/            # Web Dashboard
│   │   ├── index.html                 # 主 HTML
│   │   ├── README.md                  # 前端文档
│   │   ├── css/
│   │   │   └── styles.css             # 样式表
│   │   └── js/
│   │       ├── app.js                 # 应用初始化
│   │       ├── api.js                 # API 客户端
│   │       └── ui.js                  # UI 控制器
│   │
│   ├── models/                        # 数据模型
│   │   ├── task.py
│   │   ├── roadmap.py
│   │   └── workspace.py
│   │
│   ├── engines/                       # 核心引擎
│   │   ├── search_engine.py
│   │   ├── task_atomizer.py
│   │   └── workspace_generator.py
│   │
│   ├── storage/                       # 数据存储
│   │   ├── cache_manager.py
│   │   └── preference_manager.py
│   │
│   └── feedback/                      # 反馈系统
│
├── examples/                          # 示例代码
├── docs/                              # 其他文档
├── .github/                           # GitHub 工作流
└── .gitignore
```

## 🎓 学习路径

### 对于用户

```
1. 阅读 QUICK_START.md (5分钟)
   ↓
2. 按照步骤安装和启动 (5分钟)
   ↓
3. 创建第一个项目 (2分钟)
   ↓
4. 查看 DASHBOARD_GUIDE.md 学习完整功能 (10分钟)
   ↓
5. 开始使用仪表板进行任务管理
   ↓
6. 需要帮助时参考 DASHBOARD_SETUP.md 的故障排除部分
```

### 对于开发者

```
1. 阅读 README.md 了解项目 (10分钟)
   ↓
2. 阅读 ARCHITECTURE.md 理解系统设计 (20分钟)
   ↓
3. 查看 DASHBOARD_SETUP.md 的开发模式部分 (5分钟)
   ↓
4. 运行 test_dashboard.py 验证环境 (2分钟)
   ↓
5. 查看前端文档：coach/dashboard_frontend/README.md (10分钟)
   ↓
6. 开始修改代码
```

## 📖 按用途查找文档

### "我想快速上手"
→ [QUICK_START.md](QUICK_START.md)

### "我想了解完整功能"
→ [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)

### "我想配置和优化"
→ [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md)

### "我想理解系统架构"
→ [ARCHITECTURE.md](ARCHITECTURE.md)

### "我想修改前端代码"
→ [coach/dashboard_frontend/README.md](coach/dashboard_frontend/README.md)

### "我想修改后端代码"
→ 查看 [coach/dashboard_backend.py](coach/dashboard_backend.py) 的注释

### "我想部署到生产环境"
→ [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md) 的生产部署部分

### "出现问题，我需要帮助"
→ [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md) 的故障排除部分

### "我想验证安装是否正确"
→ 运行 `python test_dashboard.py`

## 📝 文档维护

文档最后更新时间：**2026-05-09**

### 当您修改代码时，请更新相应文档：

| 修改范围 | 相关文档 |
|---------|---------|
| 前端 HTML/CSS/JS | `coach/dashboard_frontend/README.md` + `ARCHITECTURE.md` |
| 后端 API | `ARCHITECTURE.md` + `DASHBOARD_GUIDE.md` |
| 数据库模型 | `ARCHITECTURE.md` |
| 配置选项 | `DASHBOARD_SETUP.md` |
| 依赖包 | `requirements.txt` + `setup.py` |

## 🔗 外部链接

- **GitHub**: https://github.com/noxinsun/coach-everything
- **问题反馈**: https://github.com/noxinsun/coach-everything/issues
- **讨论区**: https://github.com/noxinsun/coach-everything/discussions

## 📞 获取帮助

1. **查阅文档**: 先查看本索引和相关文档
2. **运行测试**: 执行 `python test_dashboard.py` 检查问题
3. **查看日志**: 检查后端和浏览器的日志输出
4. **提问**: 在 GitHub Issues 中提问

---

**快速链接**
- ⭐ [快速开始](QUICK_START.md)
- 📖 [Dashboard 指南](DASHBOARD_GUIDE.md)
- 🏗️ [系统架构](ARCHITECTURE.md)
- 🔧 [设置指南](DASHBOARD_SETUP.md)
