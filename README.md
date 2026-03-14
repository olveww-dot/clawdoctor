# 🦞 ClawDoctor

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Health%20Monitor-blue?style=for-the-badge" alt="OpenClaw">
  <img src="https://img.shields.io/badge/Python-3.10%2B-green?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

<p align="center">
  <b>OpenClaw Health Monitor & Fixer</b><br>
  <b>OpenClaw 健康监控与修复工具</b>
</p>

<p align="center">
  🔍 实时监控 · 🔧 一键修复 · 🛡️ 安全扫描 · 📊 数据可视化 · 🌐 中英文支持
</p>

---

## 📸 截图 | Screenshots

> 启动服务后访问：`http://127.0.0.1:8080/dashboard.html`

**功能预览：**
- 🔍 完整检查 - 一键检测所有组件状态
- 🔧 一键修复 - 自动修复常见问题
- 🛡️ 安全扫描 - 检测潜在安全风险
- 📊 实时监控 - CPU/内存/磁盘可视化
- 🌐 中英文切换 - 支持双语界面

---

## ✨ 功能特性 | Features

| 功能 | 中文 | English |
|------|------|---------|
| 🔍 **实时监控** | 监控 Gateway、技能、系统资源 | Monitor Gateway, skills, system resources |
| 🔧 **一键修复** | 自动修复常见问题 | Auto-fix common issues |
| 🛡️ **安全扫描** | 检测安全风险 | Security risk detection |
| 📊 **数据可视化** | 图表展示资源趋势 | Visualize resource trends |
| 🌐 **多语言** | 支持中英文界面 | Chinese & English support |

---

## 🚀 快速开始 | Quick Start

### 方式一：ClawHub 安装（推荐）| Install via ClawHub (Recommended)

```bash
npx clawhub install clawdoctor
```

### 方式二：手动安装 | Manual Installation

```bash
# 克隆仓库 | Clone repository
git clone https://github.com/olveww-dot/clawdoctor.git
cd clawdoctor

# 运行安装脚本 | Run install script
./install.sh

# 或手动安装 | Or install manually
pip3 install psutil
```

### 使用 | Usage

```bash
# 查看状态 | Check status
python3 clawdoctor_simple.py --status

# 一键修复 | One-click fix
python3 clawdoctor_simple.py --fix

# 安全扫描 | Security scan
python3 clawdoctor_simple.py --scan

# 启动 Web 服务 | Start web server
python3 server_simple.py
```

---

## 🛠️ 技术栈 | Tech Stack

- **Backend**: Python 3.10+, HTTP Server
- **Frontend**: HTML5, Tailwind CSS, Chart.js
- **Monitoring**: psutil for system metrics
- **i18n**: JavaScript i18n for Chinese/English

---

## 📁 项目结构 | Project Structure

```
clawdoctor/
├── clawdoctor_simple.py    # 核心监控与修复模块
├── server_simple.py        # Web API 服务器
├── dashboard.html          # Web 监控界面
├── SKILL.md               # ClawHub 技能描述
├── package.json           # 技能配置
├── install.sh             # 安装脚本
└── README.md              # 项目说明
```

---

## 🤝 贡献 | Contributing

欢迎提交 Issue 和 PR！

Welcome to submit issues and PRs!

---

## 👨‍💻 作者 | Author

<p align="center">
  <b>梁溪区佳妮电子商务工作室 EC & 小呆呆</b><br>
  <b>Liangxi Jiani E-commerce Studio EC & Xiaodaidai</b><br><br>
  📧 <a href="mailto:olveww@gmail.com">olveww@gmail.com</a>
</p>

---

## 📄 许可证 | License

MIT License © 2026 ClawDoctor

---

<p align="center">
  Made with ❤️ for OpenClaw users
</p>
