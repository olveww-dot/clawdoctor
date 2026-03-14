# ClawDoctor Skill

> OpenClaw Health Monitor & Fixer

## Description

ClawDoctor is a health monitoring and repair tool for OpenClaw. It provides real-time monitoring, one-click repair, security scanning, and a beautiful web dashboard.

## Features

- 🔍 Real-time monitoring (Gateway, skills, system resources)
- 🔧 One-click repair for common issues
- 🛡️ Security risk scanning
- 📊 Web dashboard with data visualization
- 🌐 Chinese & English support

## Installation

```bash
npx clawhub install clawdoctor
```

Or manually:

```bash
git clone https://github.com/olveww-dot/clawdoctor.git ~/.openclaw/skills/clawdoctor
```

## Usage

### CLI

```bash
# Check status
clawdoctor --status

# One-click fix
clawdoctor --fix

# Security scan
clawdoctor --scan
```

### Web Dashboard

```bash
# Start server
clawdoctor-server

# Open http://127.0.0.1:8080/dashboard.html
```

## Requirements

- Python 3.10+
- psutil
- OpenClaw installed

## Author

梁溪区佳妮电子商务工作室 EC & 小呆呆

📧 olveww@gmail.com

## License

MIT
