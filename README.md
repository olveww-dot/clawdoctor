# 🦞 ClawDoctor

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Health%20Monitor-blue?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJjdXJyZW50Q29sb3IiIHN0cm9rZS13aWR0aD0iMiI+PHBhdGggZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6Ii8+PHBhdGggZD0iTTEyIDZ2MTJtLTYtNmgxMiIvPjwvc3ZnPg==&logoColor=white" alt="OpenClaw">
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

### 安装 | Installation

```bash
# 克隆仓库 | Clone repository
git clone https://github.com/olveww-dot/clawdoctor.git
cd clawdoctor

# 安装依赖 | Install dependencies
pip3 install psutil

# 启动服务 | Start server
python3 server_simple.py
```

### 使用 | Usage

```bash
# 查看状态 | Check status
python3 clawdoctor_simple.py --status

# 一键修复 | One-click fix
python3 clawdoctor_simple.py --fix

# 安全扫描 | Security scan
python3 clawdoctor_simple.py --scan
```

### Web 界面 | Web Dashboard

启动服务后访问 | Visit after starting server:
```
http://127.0.0.1:8080/dashboard.html
```

---

## 📸 截图 | Screenshots

<p align="center">
  <img src="https://via.placeholder.com/800x400/1f2937/ffffff?text=ClawDoctor+Dashboard" alt="Dashboard" width="80%">
</p>

---

## 🛠️ 技术栈 | Tech Stack

- **Backend**: Python 3.10+, Flask-like HTTP server
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
