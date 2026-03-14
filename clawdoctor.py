#!/usr/bin/env python3
"""
ClawDoctor - OpenClaw 健康监控与修复系统
核心功能：
1. 实时监控（OpenClaw + 系统资源）
2. 一键修复（独立运行，外部守护）
3. 安全监测（公网暴露 + 技能安全）
"""

import json
import time
import subprocess
import psutil
import socket
import requests
import sqlite3
from datetime import datetime
from pathlib import Path
from threading import Thread
import logging

# 配置
CONFIG_FILE = Path.home() / ".clawdoctor" / "config.json"
DATA_DIR = Path.home() / ".clawdoctor"
DATA_DIR.mkdir(exist_ok=True)

# 日志设置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(DATA_DIR / "clawdoctor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ClawDoctor")


class OpenClawMonitor:
    """OpenClaw 状态监控"""
    
    def __init__(self):
        self.status = {
            "gateway": {"status": "unknown", "pid": None, "port": 18789},
            "qqbot": {"status": "unknown", "connected": False},
            "skills": {"total": 0, "errors": []},
            "system": {"cpu": 0, "memory": 0, "disk": 0}
        }
    
    def check_gateway(self):
        """检查 Gateway 状态"""
        try:
            # 检查端口
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 "--max-time", "3", "http://127.0.0.1:18789/"],
                capture_output=True, text=True
            )
            http_status = result.stdout.strip()
            
            # 查找进程
            pid = None
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'openclaw-gateway' in cmdline:
                        pid = proc.info['pid']
                        break
                except:
                    continue
            
            self.status["gateway"] = {
                "status": "running" if http_status == "200" else "error",
                "pid": pid,
                "port": 18789,
                "http_status": http_status
            }
            
            return self.status["gateway"]
            
        except Exception as e:
            logger.error(f"Gateway 检查失败: {e}")
            self.status["gateway"] = {"status": "error", "error": str(e)}
            return self.status["gateway"]
    
    def check_qqbot(self):
        """检查 QQ Bot WebSocket 连接"""
        try:
            # 检查 QQ Bot 进程
            pid = None
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'qqbot' in cmdline.lower() or 'onebot' in cmdline.lower():
                        pid = proc.info['pid']
                        break
                except:
                    continue
            
            # 检查 WebSocket 连接（通过日志）
            log_file = Path.home() / ".openclaw" / "logs" / "gateway.log"
            ws_connected = False
            if log_file.exists():
                # 检查最近5分钟是否有 WebSocket 连接记录
                recent_logs = subprocess.run(
                    ["tail", "-100", str(log_file)],
                    capture_output=True, text=True
                )
                if "qqbot" in recent_logs.stdout.lower() and "connected" in recent_logs.stdout.lower():
                    ws_connected = True
            
            self.status["qqbot"] = {
                "status": "running" if pid else "stopped",
                "pid": pid,
                "connected": ws_connected
            }
            
            return self.status["qqbot"]
            
        except Exception as e:
            logger.error(f"QQ Bot 检查失败: {e}")
            self.status["qqbot"] = {"status": "error", "error": str(e)}
            return self.status["qqbot"]
    
    def check_skills(self):
        """检查技能状态"""
        try:
            skills_dir = Path.home() / ".openclaw" / "skills"
            total = 0
            errors = []
            
            if skills_dir.exists():
                total = len([d for d in skills_dir.iterdir() if d.is_dir()])
            
            # 检查技能加载错误（通过日志）
            log_file = Path.home() / ".openclaw" / "logs" / "gateway.log"
            if log_file.exists():
                result = subprocess.run(
                    ["grep", "-i", "skill.*error", str(log_file)],
                    capture_output=True, text=True
                )
                if result.stdout:
                    errors = result.stdout.strip().split("\n")[-5:]  # 最近5条
            
            self.status["skills"] = {
                "total": total,
                "errors": errors
            }
            
            return self.status["skills"]
            
        except Exception as e:
            logger.error(f"技能检查失败: {e}")
            self.status["skills"] = {"total": 0, "errors": [str(e)]}
            return self.status["skills"]
    
    def check_system(self):
        """检查系统资源"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            self.status["system"] = {
                "cpu": cpu,
                "memory": memory,
                "disk": disk,
                "timestamp": datetime.now().isoformat()
            }
            
            return self.status["system"]
            
        except Exception as e:
            logger.error(f"系统检查失败: {e}")
            return {"cpu": 0, "memory": 0, "disk": 0, "error": str(e)}
    
    def full_check(self):
        """完整检查"""
        self.check_gateway()
        self.check_qqbot()
        self.check_skills()
        self.check_system()
        return self.status


class OpenClawFixer:
    """OpenClaw 修复工具（独立运行）"""
    
    def __init__(self):
        self.fix_log = []
    
    def fix_gateway(self):
        """修复 Gateway"""
        logger.info("开始修复 Gateway...")
        fixes = []
        
        try:
            # 1. 停止现有 Gateway
            subprocess.run(["openclaw", "gateway", "stop"], capture_output=True)
            time.sleep(2)
            fixes.append("停止现有 Gateway")
            
            # 2. 清理僵尸进程
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'openclaw' in proc.info['name'].lower():
                        proc.terminate()
                        fixes.append(f"终止僵尸进程 PID:{proc.info['pid']}")
                except:
                    pass
            
            time.sleep(1)
            
            # 3. 重新启动 Gateway
            result = subprocess.run(
                ["openclaw", "gateway", "start"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                fixes.append("Gateway 启动成功")
                logger.info("Gateway 修复完成")
            else:
                fixes.append(f"Gateway 启动失败: {result.stderr}")
                logger.error(f"Gateway 启动失败: {result.stderr}")
            
            self.fix_log.extend(fixes)
            return fixes
            
        except Exception as e:
            error_msg = f"Gateway 修复失败: {e}"
            logger.error(error_msg)
            self.fix_log.append(error_msg)
            return [error_msg]
    
    def fix_qqbot(self):
        """修复 QQ Bot"""
        logger.info("开始修复 QQ Bot...")
        fixes = []
        
        try:
            # 1. 检查 QQ Bot 配置
            config_file = Path.home() / ".openclaw" / "openclaw.json"
            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)
                    if 'channels' in config and 'qqbot' in config['channels']:
                        fixes.append("QQ Bot 配置存在")
                    else:
                        fixes.append("警告: QQ Bot 配置缺失")
            
            # 2. 重启 Gateway（QQ Bot 依赖 Gateway）
            gateway_fixes = self.fix_gateway()
            fixes.extend(gateway_fixes)
            
            self.fix_log.extend(fixes)
            return fixes
            
        except Exception as e:
            error_msg = f"QQ Bot 修复失败: {e}"
            logger.error(error_msg)
            self.fix_log.append(error_msg)
            return [error_msg]
    
    def fix_all(self):
        """一键修复所有问题"""
        logger.info("开始一键修复...")
        all_fixes = {
            "timestamp": datetime.now().isoformat(),
            "gateway": self.fix_gateway(),
            "qqbot": self.fix_qqbot()
        }
        logger.info("一键修复完成")
        return all_fixes


class SecurityScanner:
    """安全扫描器"""
    
    def __init__(self):
        self.risks = []
    
    def check_public_exposure(self):
        """检查 Gateway 是否暴露在公网"""
        risks = []
        
        try:
            # 检查 Gateway 绑定地址
            result = subprocess.run(
                ["openclaw", "gateway", "status"],
                capture_output=True, text=True
            )
            
            if "0.0.0.0" in result.stdout or "public" in result.stdout.lower():
                risks.append({
                    "level": "high",
                    "type": "public_exposure",
                    "message": "Gateway 可能暴露在公网，存在安全风险"
                })
            
            # 检查端口是否可从外网访问
            try:
                # 获取本机 IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                
                # 简单检查（实际应该用更复杂的方法）
                if not local_ip.startswith("192.168.") and not local_ip.startswith("10."):
                    risks.append({
                        "level": "medium",
                        "type": "network_config",
                        "message": f"检测到公网 IP: {local_ip}，请确认 Gateway 未暴露"
                    })
            except:
                pass
            
        except Exception as e:
            logger.error(f"公网暴露检查失败: {e}")
        
        return risks
    
    def check_skill_security(self):
        """检查技能安全性"""
        risks = []
        
        try:
            skills_dir = Path.home() / ".openclaw" / "skills"
            if not skills_dir.exists():
                return risks
            
            for skill_dir in skills_dir.iterdir():
                if not skill_dir.is_dir():
                    continue
                
                skill_name = skill_dir.name
                skill_md = skill_dir / "SKILL.md"
                
                if skill_md.exists():
                    content = skill_md.read_text().lower()
                    
                    # 检查危险关键词
                    dangerous_patterns = [
                        "curl", "wget", "rm -rf", "eval(", "exec(",
                        "subprocess", "os.system", "__import__"
                    ]
                    
                    for pattern in dangerous_patterns:
                        if pattern in content:
                            risks.append({
                                "level": "medium",
                                "type": "suspicious_skill",
                                "skill": skill_name,
                                "message": f"技能 '{skill_name}' 包含潜在危险代码: {pattern}"
                            })
                            break
            
        except Exception as e:
            logger.error(f"技能安全检查失败: {e}")
        
        return risks
    
    def full_scan(self):
        """完整安全扫描"""
        logger.info("开始安全扫描...")
        
        all_risks = []
        all_risks.extend(self.check_public_exposure())
        all_risks.extend(self.check_skill_security())
        
        self.risks = all_risks
        
        logger.info(f"安全扫描完成，发现 {len(all_risks)} 个风险")
        return all_risks


class ClawDoctor:
    """ClawDoctor 主类"""
    
    def __init__(self):
        self.monitor = OpenClawMonitor()
        self.fixer = OpenClawFixer()
        self.scanner = SecurityScanner()
        self.running = False
    
    def start_monitoring(self, interval=60):
        """启动监控"""
        self.running = True
        logger.info(f"ClawDoctor 监控启动，检查间隔: {interval}秒")
        
        while self.running:
            try:
                status = self.monitor.full_check()
                logger.info(f"状态检查完成: Gateway={status['gateway']['status']}, "
                          f"QQBot={status['qqbot']['status']}")
                
                # 检查是否需要自动修复
                if status['gateway']['status'] != 'running':
                    logger.warning("Gateway 异常，尝试自动修复...")
                    self.fixer.fix_gateway()
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
                time.sleep(interval)
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        logger.info("ClawDoctor 监控停止")
    
    def one_click_fix(self):
        """一键修复"""
        return self.fixer.fix_all()
    
    def security_audit(self):
        """安全审计"""
        return self.scanner.full_scan()
    
    def get_status(self):
        """获取当前状态"""
        return self.monitor.full_check()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ClawDoctor - OpenClaw 健康监控")
    parser.add_argument("--monitor", action="store_true", help="启动持续监控")
    parser.add_argument("--fix", action="store_true", help="一键修复")
    parser.add_argument("--scan", action="store_true", help="安全扫描")
    parser.add_argument("--status", action="store_true", help="查看状态")
    parser.add_argument("--interval", type=int, default=60, help="监控间隔(秒)")
    
    args = parser.parse_args()
    
    doctor = ClawDoctor()
    
    if args.monitor:
        try:
            doctor.start_monitoring(args.interval)
        except KeyboardInterrupt:
            doctor.stop_monitoring()
    
    elif args.fix:
        result = doctor.one_click_fix()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.scan:
        risks = doctor.security_audit()
        print(json.dumps(risks, indent=2, ensure_ascii=False))
    
    elif args.status:
        status = doctor.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
