# Coach Everything - 5 分钟快速开始

## 系统要求

- Python 3.8+
- 现代浏览器（Chrome, Firefox, Safari, Edge）

## 安装（1 分钟）

```bash
# 克隆项目
git clone https://github.com/noxinsun/coach-everything.git
cd coach-everything

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 启动（1 分钟）

### 终端 1: 启动后端

```bash
python coach/dashboard_backend.py
```

您应该看到：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 终端 2: 打开仪表板

```bash
# 在浏览器中打开
open http://127.0.0.1:8000/

# 或手动访问
http://127.0.0.1:8000/
```

## 创建第一个项目（1 分钟）

### 方法 A: 使用 CLI

```bash
python -m coach start --name "我的第一个项目" --domain "learning"
```

### 方法 B: 使用 API

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

## 在仪表板中使用（2 分钟）

1. **选择项目**
   - 在顶部下拉菜单选择您的项目
   - 仪表板会加载项目数据

2. **开始番茄钟**
   - 点击左栏的"开始"按钮
   - 或按 `Space` 键开始 25 分钟计时
   - 完成后自动进入 5 分钟休息

3. **查看任务**
   - 中栏显示所有任务
   - 点击任务卡片可选择
   - 使用筛选按钮过滤状态

4. **打开分析**
   - 点击"查看统计"按钮
   - 查看甘特图和饼图
   - 查看详细的统计数据

5. **调整设置**
   - 右上角点击齿轮图标
   - 调整主题、语言、字体大小
   - 配置 LLM 提供商

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Space` | 开始/暂停计时器 |
| `Ctrl+S` | 打开设置 |
| `Ctrl+Shift+A` | 显示分析 |
| `Esc` | 关闭弹窗 |

## 验证安装

```bash
# 运行测试套件
python test_dashboard.py
```

应该看到所有绿色的 ✅ 标记。

## 故障排除

### 无法访问 Dashboard

```bash
# 检查后端是否运行
lsof -i :8000

# 如果占用，改用其他端口
python -m uvicorn coach.dashboard_backend:app --port 8001
```

### 项目不显示

```bash
# 确保项目已创建
python -m coach start --name "项目名" --domain "learning"

# 或刷新浏览器
```

### WebSocket 错误

- 清除浏览器缓存（Ctrl+Shift+Delete）
- 硬刷新（Ctrl+F5）
- 检查防火墙规则

## 下一步

1. 📖 阅读 [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) - 完整使用指南
2. 🔧 阅读 [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md) - 详细设置说明
3. 🏗️ 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) - 系统架构文档
4. 👨‍💻 修改代码：
   - 前端: `coach/dashboard_frontend/`
   - 后端: `coach/dashboard_backend.py`

## 生产环境

对于生产部署，参考 [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md) 的生产部署部分。

---

祝您使用愉快！🚀

有问题？查看完整文档或提出 Issue。
