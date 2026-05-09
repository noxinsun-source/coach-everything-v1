# Coach Everything 🚀

<div align="center">

**🌍 语言 | Language** 

[中文](#coach-everything-万能任务拆分和陪跑ai智能体) (默认) | [English](#coach-everything)

</div>

---

# Coach Everything - 万能任务拆分和陪跑AI智能体

**任务无限拆分 × 陪伴式学习与办公 × AI 实时陪跑**

一个为**任何人**、**任何任务**设计的通用AI系统。把模糊、令人不知所措的任务转化为清晰、可视化的微步骤。特别适合有拖延症、启动困难或执行力障碍的人。基于真实人类经验获得个性化指导，从此不再为"下一步具体要做什么"而困惑。

---

## 🎯 Coach Everything 是什么？

Coach Everything 是一个开源的 AI 陪跑系统，把模糊、令人不知所措的任务转化为清晰、可管理的微任务。

不同于通用的任务管理器或 AI 工具，Coach Everything：

- 🔍 **搜索真实人类经验** - 从 Reddit、论坛、博客、GitHub 找到已验证的策略
- 🧩 **逐步拆分任务** - 从粗糙大纲 → 详细步骤 → 1-2 小时微任务
- ✅ **需要你的批准** - 你在每个阶段控制路线图（大纲，然后是任务）
- 📁 **自动生成结构化工作空间** - 为你的项目创建 Obsidian vault 文件夹
- 🤖 **实时陪跑** - Coach Agent 监控进度并提供鼓励
- 💾 **本地保存知识** - 所有经验和学习都留在你的 vault；无信息泄露

**适用于：**
- 启动大型项目（脑子一片空白）
- 学习新技能（编程、设计、写作等）
- 求职过程
- 科研项目
- 副业和创业
- 任何复杂的多步骤任务

---

## 🚀 核心功能

### 1. 多维度搜索引擎
不是通用的谷歌搜索，而是：
- **人物身份维度**："有经验的开发者如何启动新项目？"
- **领域专特维度**："机器学习项目设置最佳实践"
- **时间维度**："最近的策略（2024-2026）vs 经典方法"
- **内容形式维度**："分步指南 vs 快速提示 vs 代码例子"

### 2. 逐步任务原子化
```
输入："我想学习机器学习"
    ↓
第1阶段（大纲）：批准粗略路线图
    - 基础知识
    - 动手项目
    - 高级话题
    ↓
第2阶段（详细步骤）：批准每个阶段的详细步骤
    - 下载推荐资源
    - 设置环境
    - 完成第一个练习
    ↓
第3阶段（微任务）：获得 1-2 小时的任务块和验证标准
    - 任务：安装 Anaconda 并创建虚拟环境
    - 验证：`conda --version` 显示成功
    - 时间估计：30 分钟
    - 下一个微任务：下载第一个教程 notebook
```

### 3. 基于经验的路由
不是通用的 AI 建议，而是：
- 做过这项任务的真实人类的策略
- 已验证的陷阱及如何避免
- 领域特定的最佳实践
- 针对不同学习风格的不同方法

### 4. 结构化工作空间生成
在 Obsidian 中自动创建项目文件夹：
```
项目名/
├── 📋 路线图.md            # 你批准的大纲
├── 📊 任务进度.md          # 微任务 + 完成状态
├── 📚 资源/                # 自动链接的最佳实践
├── 📝 笔记/                # 你的学习笔记
├── 📁 数据/                # 项目产物（代码、数据等）
└── 🤖 Coach 日志.md       # AI 陪跑反馈
```

### 5. 实时 Coach Agent
Coach 始终陪伴你：
- 监控每个微任务的进度
- 发送鼓励信息
- 检测你何时卡住并建议下一步
- 在需要时提出澄清问题
- 庆祝里程碑

### 6. 智能缓存和知识保存
- SQLite 缓存存储搜索结果、模板和经验
- 你的项目工作空间在 Obsidian 中（版本可控）
- 常见任务类型的可重用模板（学习、求职、科研等）

---

## 💻 安装

### 选项 1：Pip 安装（推荐用户）
```bash
pip install coach-everything
coach init
```

### 选项 2：Git Clone（推荐开发者）
```bash
git clone https://github.com/noxinsun-source/coach-everything-v1.git
cd coach-everything-v1
pip install -e .
coach init
```

---

## 🎬 快速开始

### 1. 启动新项目
```bash
coach start
```

按照提示操作：
```
欢迎使用 Coach Everything！🚀
你想学习/构建什么？
> 我想从零开始学 Python

很好！我在搜索已验证的策略...

找到 12 个相关指南来自有经验的学习者。
分析常见方法...完成！

这是你的路线图大纲：
1. 设置和基础（第 1 周）
   - 安装 Python 和 IDE
   - 学习基本语法和数据类型
   - 完成 5 个初学者练习
   
2. 核心概念（第 2-3 周）
   - 函数、类、错误处理
   - 处理文件和 API
   - 构建 2 个小项目

3. 高级话题（第 4+ 周）
   - OOP 设计模式
   - 测试和调试
   - 真实项目

这个路线图有意义吗？(yes/edit/show-sources)
> yes

✅ 路线图已批准！让我生成你的工作空间...
```

### 2. 获取详细步骤
```bash
coach expand
```

### 3. 追踪进度
```bash
coach status
```

显示：
- 当前微任务和验证标准
- 当前任务花费的时间
- 已完成的任务（带复选标记）
- 即将进行的微任务
- Coach 的鼓励信息

### 4. 获取陪跑
卡住时：
```bash
coach help
```

Coach Agent 回应：
```
你已经在这个任务上工作 45 分钟了。
要我进一步分解吗？或者你想看看有类似经历的人是怎么解决的？

常见解决方案：
1. 检查错误信息 - 在 Stack Overflow 上发布
2. 休息 10 分钟，然后重新阅读教程
3. 看你的资源/ 中的视频替代品

什么会最有帮助？
```

### 5. 切换任务
```bash
coach next
```

移动到下一个微任务并重置计时器。

---

## ⚙️ 配置

编辑 `~/.coach/config.yaml`：

```yaml
# 必需：你的 Obsidian vault 路径
obsidian_vault_path: /Users/yourname/Documents/Obsidian Vault

# 搜索配置
search:
  platforms:
    - reddit
    - github
    - forums
    - blogs
  include_papers: true
  recency_weight: 0.7

# 任务配置
task_atomization:
  default_micro_task_duration: 120  # 分钟
  require_approval: true
  include_verification_criteria: true

# Coach Agent 配置
coach_agent:
  personality: encouraging  # encouraging, formal, casual
  check_in_frequency: 60    # 分钟
  celebrate_milestones: true
```

---

## 📚 设计理念

### 1. **人类思考，AI 路由**
Coach 不决定什么对你最好。它**路由**你到解决过类似问题的人的经验。你来解读和决策。

### 2. **两层存储**
- **Obsidian（用户面向）**：你的项目工作空间、笔记、进度 - 完全版本可控
- **SQLite（系统缓存）**：搜索结果、模板、学到的模式 - 用于性能

### 3. **带批准的逐步精化**
永远不要自动生成大任务列表。逐步精化：
1. 大纲 → 你批准
2. 详细步骤 → 你批准
3. 微任务 → 你验证每一个

### 4. **具体性 > 通用性**
- 时间估计是 1-2 小时的任务块（不是"3 周"）
- 验证标准是可测试的（不是模糊的）
- 经验是领域特定的（不是通用建议）

### 5. **ADHD 友好**
- 始终清晰地了解"下一个微任务"
- 无分析瘫痪（经验预先筛选）
- 定期检查和鼓励
- 庆祝进度

---

## 🤝 贡献

欢迎贡献！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

**我们需要帮助的领域：**
- 新的搜索平台（Discord、专业论坛）
- 更多域的任务模板
- 与其他笔记应用的集成
- 移动应用进度追踪
- 基于视频教程的陪跑

---

## 📄 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

**简言之**：可自由地用于个人或商业项目。不提供任何担保。

---

## 🙏 致谢

### 贡献者

- **Noxinsun** ([@noxinsun-source](https://github.com/noxinsun-source)) - 产品愿景、设计、ADHD 专业知识
- **Claude Haiku** (Anthropic) - 架构、实现、文档

---

## 📞 支持

- 📖 **文档**：查看 `/docs` 文件夹
- 💬 **讨论**：在 GitHub 上开问题
- 🐛 **漏洞报告**：GitHub Issues
- 💡 **功能请求**：GitHub Discussions

---

**用❤️为那些执行力有困难的人制作**

---

# Coach Everything

**Infinite Task Breakdown × Companion Learning & Work × Real-time AI Coaching**

A universal AI system for **anyone**, **any task**. Break down vague, overwhelming tasks into clear, visualized micro-steps. Get personalized guidance based on real human experiences. Never feel stuck on "what to do next" again. Especially designed for people with procrastination, task initiation difficulties, or executive dysfunction challenges.

---

## What is Coach Everything?

Coach Everything is an open-source AI coaching system that transforms vague, overwhelming tasks into crystal-clear, bite-sized micro-steps. 

Unlike generic task managers or AI tools that just generate lists, Coach Everything:

- 🔍 **Searches real human experiences** - Finds proven strategies from Reddit, forums, blogs, and GitHub
- 🧩 **Progressively breaks down tasks** - Refines from rough outline → detailed steps → 1-2 hour micro-tasks
- ✅ **Requires your approval** - You control the roadmap at every stage (outline, then tasks)
- 📁 **Generates structured workspaces** - Auto-creates Obsidian vault folders and files for your project
- 🤖 **Provides real-time coaching** - The Coach Agent monitors progress and offers encouragement
- 💾 **Preserves knowledge locally** - All experiences and learnings stay in your vault; nothing leaves your machine

**Perfect for:**
- Starting large projects when your mind goes blank
- Learning new skills (programming, design, writing, etc.)
- Job hunting processes
- Research projects
- Side hustles and startups
- Any complex, multi-step task

---

## 🚀 Core Features

### 1. Multi-Dimensional Search Engine
Instead of generic Google results, Coach searches across:
- **Person identity**: "How do experienced developers start a new project?"
- **Domain specificity**: "Best practices in machine learning project setup"
- **Time period**: "Recent strategies (2024-2026) vs. classic methods"
- **Content format**: "Step-by-step guides vs. brief tips vs. code examples"

### 2. Progressive Task Atomization
```
Input: "I want to learn machine learning"
    ↓
Stage 1 (Outline): Approve the rough roadmap
    - Fundamentals
    - Hands-on projects
    - Advanced topics
    ↓
Stage 2 (Detailed Steps): Approve detailed steps for each phase
    - Download recommended resources
    - Set up environment
    - Complete first exercise
    ↓
Stage 3 (Micro-Tasks): Get 1-2 hour chunks with verification criteria
    - Task: Install Anaconda and create virtual environment
    - Verification: `conda --version` returns success
    - Time estimate: 30 minutes
    - Next micro-task: Download first tutorial notebook
```

### 3. Experience-Based Routing
Instead of generic AI advice, Coach finds and synthesizes:
- Real strategies from people who've done the task
- Proven pitfalls and how to avoid them
- Domain-specific best practices
- Different approaches for different learning styles

### 4. Structured Workspace Generation
Auto-creates your project folder in Obsidian:
```
Project Name/
├── 📋 Roadmap.md          # Your approved outline
├── 📊 Task Progress.md    # Micro-tasks + completion status
├── 📚 Resources/          # Auto-linked best practices
├── 📝 Notes/              # Your learning notes
├── 📁 Data/               # Project artifacts (code, data, etc.)
└── 🤖 Coach Log.md        # AI coaching feedback
```

### 5. Real-Time Coach Agent
The Coach stays with you:
- Monitors progress on each micro-task
- Sends encouragement messages
- Detects when you're stuck and suggests next steps
- Asks clarifying questions when needed
- Celebrates milestones

### 6. Smart Caching & Knowledge Preservation
- SQLite cache stores search results, templates, and experiences
- Your project workspace lives in Obsidian (version-controllable)
- Reusable templates for common task types (learning, job hunting, research, etc.)

---

## Installation

### Option 1: Pip Install (Recommended for Users)
```bash
pip install coach-everything
```

After installation, initialize Coach:
```bash
coach init
```

This creates:
- `~/.coach/` - Configuration and cache directory
- `~/.coach/cache.db` - SQLite cache for experiences and templates
- `~/.coach/config.yaml` - Your preferences

### Option 2: Git Clone (Recommended for Development)
```bash
git clone https://github.com/noxinsun-source/coach-everything-v1.git
cd coach-everything-v1
pip install -e .
```

After installation, initialize Coach:
```bash
coach init
```

---

## Quick Start

### 1. Start a New Project
```bash
coach start
```

Follow the interactive prompt:
```
Welcome to Coach Everything! 🚀
What task do you want to tackle?
> I want to learn Python from scratch

Great! I'm searching for proven strategies...

Found 12 relevant guides from experienced learners.
Analyzing common approaches... Done!

Here's your roadmap outline:
1. Setup & Fundamentals (Week 1)
   - Install Python and set up IDE
   - Learn basic syntax and data types
   - Complete 5 beginner exercises
   
2. Core Concepts (Week 2-3)
   - Functions, classes, error handling
   - Work with files and APIs
   - Build 2 small projects

3. Advanced Topics (Week 4+)
   - OOP design patterns
   - Testing and debugging
   - Real-world project

Does this roadmap make sense? (yes/edit/show-sources)
> yes

✅ Roadmap approved! Let me generate your workspace...
```

### 2. Get Detailed Steps
Once you approve the roadmap, Coach generates detailed steps:
```bash
coach expand
```

### 3. Track Progress
```bash
coach status
```

Shows:
- Current micro-task with verification criteria
- Time spent on current task
- Completed tasks (with checkmarks)
- Upcoming micro-tasks
- Coach's encouragement message

### 4. Get Coaching
When stuck:
```bash
coach help
```

The Coach Agent responds:
```
You've been working on this for 45 minutes. 
Want me to break it down further? Or would you like to see 
similar experiences from others who've hit this wall?

Common solutions:
1. Check the error message - post it to Stack Overflow
2. Take a 10-minute break, then re-read the tutorial
3. Watch the video alternative in your Resources/

What would help most?
```

### 5. Switch Tasks
```bash
coach next
```

Moves you to the next micro-task and resets the timer.

---

## Configuration

Coach stores your preferences in `~/.coach/config.yaml`:

```yaml
# Obsidian vault location (where workspaces are created)
obsidian_vault_path: /Users/you/Documents/Obsidian Vault

# Search preferences
search:
  platforms:
    - reddit        # r/learnprogramming, r/adhd, etc.
    - forums        # Stack Overflow, dev.to, etc.
    - blogs         # Medium, personal blogs, etc.
    - github        # Real project examples
  include_papers: true          # Include arXiv/OpenReview papers
  recency_weight: 0.7           # Prefer recent advice (0-1)
  
# Task atomization preferences
task_atomization:
  default_micro_task_duration: 120  # minutes (1-2 hours ideal)
  require_approval: true            # Need to approve each stage
  include_verification_criteria: true
  
# Coach Agent behavior
coach_agent:
  personality: encouraging           # encouraging, formal, casual
  check_in_frequency: 60            # minutes
  celebrate_milestones: true
  offer_help_threshold: 30          # Offer help after 30 min stuck
```

---

## Design Philosophy

### 1. **Humans Think, AI Routes**
The Coach doesn't decide what's best for you. It **routes** you to experiences from people who've solved similar problems. You interpret and decide.

### 2. **Two Layers of Storage**
- **Obsidian (User-facing)**: Your project workspace, notes, progress - fully version-controllable
- **SQLite (System cache)**: Search results, templates, learned patterns - for performance

### 3. **Progressive Refinement with Approval**
Never auto-generate huge task lists. Refine progressively:
1. Outline → you approve
2. Detailed steps → you approve
3. Micro-tasks → you verify each one

### 4. **Specificity > Generality**
- Time estimates are 1-2 hour chunks (not "3 weeks")
- Verification criteria are testable (not vague)
- Experiences are domain-specific (not generic advice)

### 5. **ADHD-Friendly**
- Clear "next micro-task" at all times
- No analysis paralysis (experiences pre-filtered)
- Regular check-ins and encouragement
- Celebration of progress

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas we need help with:**
- Additional search platforms (Discord, specialized forums)
- Task templates for more domains
- Integration with note-taking tools beyond Obsidian
- Mobile app for task progress tracking
- Video coaching (training the Coach Agent on video tutorials)

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

**In short**: Use Coach Everything freely for personal or commercial projects. No warranties provided.

---

## Support

- 📖 **Documentation**: See `/docs` folder
- 💬 **Discussion**: Open an issue on GitHub
- 🐛 **Bug Reports**: GitHub Issues
- 💡 **Feature Requests**: GitHub Discussions

---

## Contributors

- **Noxinsun** ([@noxinsun-source](https://github.com/noxinsun-source)) - Product vision, design, ADHD expertise
- **Claude Haiku** (Anthropic) - Architecture, implementation, documentation

---

**Made with ❤️ for people who struggle with executive function**
