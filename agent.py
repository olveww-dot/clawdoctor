#!/usr/bin/env python3
"""
ClawDoctor Agent - OpenClaw 健康监控 Agent
MVP 版本 - 本地监控 + 云端上报
"""

import json
import time
import subprocess
import psutil
import requests
from datetime import datetime
from pathlib import Path

# 配置
CONFIG = {
    "api_endpoint": "https://api.clawdoctor.io/v1/heartbeat",  # 云端 API（稍后部署）
    "check_interval": 60,  # 检查间隔（秒）
    "user_id": None,  # 用户 ID（注册后填充）
    "api_key": None,  # API Key（注册后填充）
}

class OpenClawMonitor:
    def __init__(self):
        self.gateway_pid = None
        self.last_status = {}
        
    def check_gateway(self):
        """检查 Gateway 状态"""
        try:
            # 检查端口 18789
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                 "--max-time", "3", "http://127.0.0.1:18789/"],
                capture_output=True, text=True
            )
            status_code = result.stdout.strip()
            
            # 检查进程
            gateway_process = None
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'openclaw-gateway' in ' '.join(proc.info['cmdline'] or []):
                        gateway_process = proc
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "status": "running" if status_code == "200" else "error",
                "http_code": status_code,
                "pid": gateway_process.pid if gateway_process else None,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def check_qqbot(self):
        """检查 QQ Bot 状态（通过日志）"""
        try:
            log_file = Path(f"/tmp/openclaw/openclaw-{datetime.now().strftime('%Y-%m-%d')}.log")
            if not log_file.exists():
                return {"status": "unknown", "error": "log file not found"}
            
            # 读取最后 100 行
            result = subprocess.run(
                ["tail", "-100", str(log_file)],
                capture_output=True, text=True
            )
            logs = result.stdout
            
            # 检查错误
            errors = []
            if "WebSocket closed: 4009" in logs:
                errors.append("websocket_timeout")
            if "Gateway failed to start" in logs:
                errors.append("gateway_start_failed")
            
            return {
                "status": "error" if errors else "ok",
                "errors": errors,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def check_system_resources(self):
        """检查系统资源"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available // 1024 // 1024,
                "disk_percent": disk.percent,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def auto_fix(self, issues):
        """自动修复常见问题"""
        fixes = []
        
        for issue in issues:
            if issue == "gateway_start_failed":
                try:
                    # 尝试重启 Gateway
                    subprocess.run(["pkill", "-f", "openclaw-gateway"], check=False)
                    time.sleep(2)
                    subprocess.run(
                        ["launchctl", "bootstrap", "gui/$UID", 
                         "~/Library/LaunchAgents/ai.openclaw.gateway.plist"],
                        check=False, shell=True
                    )
                    fixes.append("gateway_restarted")
                except Exception as e:
                    fixes.append(f"gateway_restart_failed: {e}")
        
        return fixes
    
    def run_check(self):
        """运行完整检查"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "gateway": self.check_gateway(),
            "qqbot": self.check_qqbot(),
            "system": self.check_system_resources(),
        }
        
        # 检查是否需要自动修复
        issues = []
        if report["gateway"]["status"] != "running":
            issues.append("gateway_start_failed")
        if report["qqbot"].get("errors"):
            issues.extend(report["qqbot"]["errors"])
        
        if issues:
            report["auto_fixes"] = self.auto_fix(issues)
        
        self.last_status = report
        return report
    
    def save_local(self, report):
        """保存到本地日志"""
        log_dir = Path("~/.clawdoctor/logs").expanduser()
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(report) + "\n")
    
    def send_to_cloud(self, report):
        """发送到云端（暂时保存到本地，等云端部署后再启用）"""
        # TODO: 部署云端后启用
        # if CONFIG["api_key"]:
        #     try:
        #         response = requests.post(
        #             CONFIG["api_endpoint"],
        #             json=report,
        #             headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
        #             timeout=10
        #         )
        #         return response.status_code == 200
        #     except Exception as e:
        #         print(f"Failed to send to cloud: {e}")
        #         return False
        return True

def main():
    """主循环"""
    print("🦞 ClawDoctor Agent 启动...")
    monitor = OpenClawMonitor()
    
    while True:
        try:
            # 运行检查
            report = monitor.run_check()
            
            # 保存本地
            monitor.save_local(report)
            
            # 发送到云端
            monitor.send_to_cloud(report)
            
            # 打印状态
            gateway_status = report["gateway"]["status"]
            qqbot_status = report["qqbot"]["status"]
            cpu = report["system"].get("cpu_percent", "N/A")
            memory = report["system"].get("memory_percent", "N/A")
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"Gateway: {gateway_status} | "
                  f"QQ Bot: {qqbot_status} | "
                  f"CPU: {cpu}% | "
                  f"Memory: {memory}%")
            
            # 如果有自动修复，打印出来
            if "auto_fixes" in report:
                print(f"  🔧 Auto fixes: {report['auto_fixes']}")
            
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
        
        # 等待下次检查
        time.sleep(CONFIG["check_interval"])

if __name__ == "__main__":
    main()
