#!/usr/bin/env python3
"""
ClawDoctor Agent V2 - 带自动修复功能
"""

import json
import time
import subprocess
import psutil
from datetime import datetime
from pathlib import Path

# 配置
CONFIG = {
    "check_interval": 60,
    "max_restart_attempts": 3,
    "restart_cooldown": 300,
}

class AutoFixer:
    def __init__(self):
        self.restart_attempts = 0
        self.last_restart_time = None
    
    def can_restart(self):
        if self.last_restart_time is None:
            return True
        elapsed = (datetime.now() - self.last_restart_time).total_seconds()
        if elapsed < CONFIG["restart_cooldown"]:
            print(f"       ⏱️ 冷却中... 还需 {int(CONFIG['restart_cooldown'] - elapsed)} 秒")
            return False
        if self.restart_attempts >= CONFIG["max_restart_attempts"]:
            print(f"       ⚠️ 已达到最大重启次数")
            return False
        return True
    
    def restart_gateway(self):
        try:
            print("       🔧 正在自动修复: 重启 Gateway...")
            subprocess.run(["pkill", "-f", "openclaw-gateway"], capture_output=True, check=False)
            time.sleep(2)
            subprocess.run(["launchctl", "start", "ai.openclaw.gateway"], capture_output=True)
            time.sleep(3)
            
            # 验证
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 "--max-time", "3", "http://127.0.0.1:18789/"],
                capture_output=True, text=True
            )
            
            if result.stdout.strip() == "200":
                self.restart_attempts += 1
                self.last_restart_time = datetime.now()
                print("       ✅ Gateway 重启成功!")
                return True
            else:
                print("       ❌ Gateway 重启失败")
                return False
        except Exception as e:
            print(f"       ❌ 重启出错: {e}")
            return False
    
    def fix(self, gateway_status):
        fixes = []
        if gateway_status["status"] != "running":
            if self.can_restart():
                if self.restart_gateway():
                    fixes.append({"action": "gateway_restarted", "status": "success"})
                else:
                    fixes.append({"action": "gateway_restart", "status": "failed"})
            else:
                fixes.append({"action": "restart_skipped", "reason": "cooldown_or_max_attempts"})
        return fixes

def check_gateway():
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
    try:
        log_file = Path(f"/tmp/openclaw/openclaw-{datetime.now().strftime('%Y-%m-%d')}.log")
        if not log_file.exists():
            return {"status": "unknown", "errors": []}
        result = subprocess.run(["tail", "-50", str(log_file)], capture_output=True, text=True)
        logs = result.stdout
        errors = []
        if "WebSocket closed: 4009" in logs:
            errors.append("websocket_timeout")
        return {"status": "error" if errors else "ok", "errors": errors}
    except Exception as e:
        return {"status": "error", "error": str(e), "errors": [str(e)]}

def check_system():
    """检查系统资源"""
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": round(cpu, 1),
            "memory_percent": round(memory.percent, 1),
            "memory_available_mb": memory.available // 1024 // 1024,
            "disk_percent": round(disk.percent, 1)
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    print("🦞 ClawDoctor Agent V2 启动...")
    print("✨ 自动修复已启用")
    print("按 Ctrl+C 停止\n")
    
    fixer = AutoFixer()
    
    while True:
        timestamp = datetime.now().strftime("%H:%M:%S")
        gateway = check_gateway()
        qqbot = check_qqbot()
        system = check_system()
        
        # 自动修复
        fixes = []
        if gateway["status"] != "running":
            fixes = fixer.fix(gateway)
            if any(f.get("status") == "success" for f in fixes):
                # 修复成功，重新检查
                time.sleep(2)
                gateway = check_gateway()
        
        # 显示状态
        status_icon = "✅" if gateway["status"] == "running" and qqbot["status"] == "ok" else "⚠️"
        cpu = system.get("cpu_percent", "--")
        mem = system.get("memory_percent", "--")
        print(f"[{timestamp}] {status_icon} Gateway: {gateway['status']} | QQ Bot: {qqbot['status']} | CPU: {cpu}% | Mem: {mem}%")
        
        if fixes:
            for fix in fixes:
                print(f"       🔧 {fix['action']}: {fix.get('status', fix.get('reason', ''))}")
        
        if qqbot.get("errors"):
            print(f"       错误: {qqbot['errors']}")
        
        # 保存日志
        log_dir = Path("~/.clawdoctor/logs").expanduser()
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "gateway": gateway,
            "qqbot": qqbot,
            "system": system,
            "fixes": fixes
        }
        
        with open(log_file, "a") as f:
            f.write(json.dumps(report) + "\n")
        
        time.sleep(CONFIG["check_interval"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Agent 已停止")
