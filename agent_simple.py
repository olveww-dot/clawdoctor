#!/usr/bin/env python3
"""
ClawDoctor Agent - 简化版 MVP
"""

import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

def check_gateway():
    """检查 Gateway 状态"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
             "--max-time", "3", "http://127.0.0.1:18789/"],
            capture_output=True, text=True
        )
        status_code = result.stdout.strip()
        return {"status": "running" if status_code == "200" else "error", "http_code": status_code}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_qqbot():
    """检查 QQ Bot 状态"""
    try:
        log_file = Path(f"/tmp/openclaw/openclaw-{datetime.now().strftime('%Y-%m-%d')}.log")
        if not log_file.exists():
            return {"status": "unknown"}
        
        result = subprocess.run(
            ["tail", "-50", str(log_file)],
            capture_output=True, text=True
        )
        logs = result.stdout
        
        errors = []
        if "WebSocket closed: 4009" in logs:
            errors.append("websocket_timeout")
        if "Gateway failed to start" in logs:
            errors.append("gateway_start_failed")
        
        return {"status": "error" if errors else "ok", "errors": errors}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def main():
    print("🦞 ClawDoctor Agent 启动...")
    print("按 Ctrl+C 停止\n")
    
    while True:
        timestamp = datetime.now().strftime("%H:%M:%S")
        gateway = check_gateway()
        qqbot = check_qqbot()
        
        status_icon = "✅" if gateway["status"] == "running" and qqbot["status"] == "ok" else "⚠️"
        
        print(f"[{timestamp}] {status_icon} Gateway: {gateway['status']} | QQ Bot: {qqbot['status']}")
        
        if qqbot.get("errors"):
            print(f"       错误: {qqbot['errors']}")
        
        # 保存到本地
        log_dir = Path("~/.clawdoctor/logs").expanduser()
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "gateway": gateway,
            "qqbot": qqbot
        }
        
        with open(log_file, "a") as f:
            f.write(json.dumps(report) + "\n")
        
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Agent 已停止")
