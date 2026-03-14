#!/usr/bin/env python3
"""
ClawDoctor - OpenClaw Health Monitor & Fixer
Core Features: Real-time Monitor, One-click Fix, Security Scan
"""

import json
import time
import subprocess
import psutil
import socket
import os
from datetime import datetime
from pathlib import Path
import logging

# Config
DATA_DIR = Path.home() / ".clawdoctor"
DATA_DIR.mkdir(exist_ok=True)

# Logging
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
    """OpenClaw Status Monitor"""
    
    def __init__(self):
        self.status = {
            "gateway": {"status": "unknown", "pid": None, "port": 18789},
            "skills": {"total": 0, "errors": []},
            "system": {"cpu": 0, "memory": 0, "disk": 0}
        }
    
    def check_gateway(self):
        """Check Gateway Status"""
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                 "--max-time", "3", "http://127.0.0.1:18789/"],
                capture_output=True, text=True
            )
            http_status = result.stdout.strip()
            
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
            logger.error(f"Gateway check failed: {e}")
            self.status["gateway"] = {"status": "error", "error": str(e)}
            return self.status["gateway"]
    
    def check_skills(self):
        """Check Skills"""
        try:
            skills_dir = Path.home() / ".openclaw" / "skills"
            if skills_dir.exists():
                total = len([d for d in skills_dir.iterdir() if d.is_dir()])
            else:
                total = 0
            self.status["skills"] = {"total": total, "errors": []}
            return self.status["skills"]
        except Exception as e:
            logger.error(f"Skills check failed: {e}")
            self.status["skills"] = {"total": 0, "errors": [str(e)]}
            return self.status["skills"]
    
    def check_system(self):
        """Check System Resources"""
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
            logger.error(f"System check failed: {e}")
            return {"cpu": 0, "memory": 0, "disk": 0, "error": str(e)}
    
    def full_check(self):
        """Full Check"""
        self.check_gateway()
        self.check_skills()
        self.check_system()
        return self.status


class OpenClawFixer:
    """OpenClaw Fixer"""
    
    def __init__(self):
        self.fix_log = []
    
    def fix_gateway(self):
        """Fix Gateway"""
        logger.info("Fixing Gateway...")
        fixes = []
        try:
            # Check port usage
            for conn in psutil.net_connections():
                if conn.laddr.port == 18789:
                    try:
                        p = psutil.Process(conn.pid)
                        p.terminate()
                        fixes.append(f"Killed process using port 18789 (PID:{conn.pid})")
                        time.sleep(1)
                    except:
                        pass
            
            # Stop existing Gateway
            subprocess.run(["openclaw", "gateway", "stop"], capture_output=True)
            time.sleep(2)
            fixes.append("Stopped existing Gateway")
            
            # Kill zombie processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'openclaw-gateway' in cmdline:
                        proc.terminate()
                        fixes.append(f"Killed zombie process PID:{proc.info['pid']}")
                except:
                    pass
            
            time.sleep(1)
            
            # Restart Gateway
            result = subprocess.run(
                ["openclaw", "gateway", "start"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                fixes.append("Gateway started successfully")
                logger.info("Gateway fix completed")
            else:
                fixes.append(f"Gateway start failed: {result.stderr}")
                logger.error(f"Gateway start failed: {result.stderr}")
            
            self.fix_log.extend(fixes)
            return fixes
        except Exception as e:
            error_msg = f"Gateway fix failed: {e}"
            logger.error(error_msg)
            self.fix_log.append(error_msg)
            return [error_msg]
    
    def fix_config(self):
        """Fix Config"""
        logger.info("Fixing config...")
        fixes = []
        try:
            config_file = Path.home() / ".openclaw" / "openclaw.json"
            if not config_file.exists():
                fixes.append("Config file not found")
                return fixes
            
            # Backup
            backup_file = config_file.with_suffix('.json.backup')
            import shutil
            shutil.copy2(config_file, backup_file)
            fixes.append(f"Config backed up to {backup_file}")
            
            # Check JSON
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                fixes.append("Config format OK")
            except json.JSONDecodeError as e:
                fixes.append(f"JSON error: {e}")
                return fixes
            
            # Add missing configs
            if 'gateway' not in config:
                config['gateway'] = {'mode': 'local'}
                fixes.append("Added missing gateway config")
            
            if 'models' not in config:
                config['models'] = {'mode': 'merge', 'providers': {}}
                fixes.append("Added missing models config")
            
            # Save
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            fixes.append("Config saved")
            
            self.fix_log.extend(fixes)
            return fixes
        except Exception as e:
            error_msg = f"Config fix failed: {e}"
            logger.error(error_msg)
            self.fix_log.append(error_msg)
            return [error_msg]
    
    def fix_logs(self):
        """Fix Logs"""
        logger.info("Fixing logs...")
        fixes = []
        try:
            log_dirs = [
                Path.home() / ".openclaw" / "logs",
                Path("/tmp") / "openclaw",
                DATA_DIR
            ]
            
            total_freed = 0
            for log_dir in log_dirs:
                if not log_dir.exists():
                    continue
                for log_file in log_dir.glob("*.log"):
                    size = log_file.stat().st_size
                    if size > 100 * 1024 * 1024:
                        log_file.unlink()
                        total_freed += size
                        fixes.append(f"Deleted large log: {log_file.name} ({size/1024/1024:.1f}MB)")
            
            if total_freed > 0:
                fixes.append(f"Total freed: {total_freed/1024/1024:.1f}MB")
            else:
                fixes.append("Logs OK")
            
            self.fix_log.extend(fixes)
            return fixes
        except Exception as e:
            error_msg = f"Logs fix failed: {e}"
            logger.error(error_msg)
            self.fix_log.append(error_msg)
            return [error_msg]
    
    def fix_all(self):
        """One-click Fix All"""
        logger.info("Starting one-click fix...")
        all_fixes = {
            "timestamp": datetime.now().isoformat(),
            "gateway": self.fix_gateway(),
            "config": self.fix_config(),
            "logs": self.fix_logs()
        }
        logger.info("One-click fix completed")
        return all_fixes


class SecurityScanner:
    """Security Scanner"""
    
    def __init__(self):
        self.risks = []
    
    def check_public_exposure(self):
        """Check Public Exposure"""
        risks = []
        try:
            result = subprocess.run(
                ["openclaw", "gateway", "status"],
                capture_output=True, text=True
            )
            if "0.0.0.0" in result.stdout:
                risks.append({
                    "level": "high",
                    "type": "public_exposure",
                    "message": "Gateway exposed to public network"
                })
        except Exception as e:
            logger.error(f"Public exposure check failed: {e}")
        return risks
    
    def full_scan(self):
        """Full Security Scan"""
        logger.info("Starting security scan...")
        all_risks = []
        all_risks.extend(self.check_public_exposure())
        self.risks = all_risks
        logger.info(f"Security scan completed, found {len(all_risks)} risks")
        return all_risks


class ClawDoctor:
    """ClawDoctor Main Class"""
    
    def __init__(self):
        self.monitor = OpenClawMonitor()
        self.fixer = OpenClawFixer()
        self.scanner = SecurityScanner()
    
    def one_click_fix(self):
        """One-click Fix"""
        return self.fixer.fix_all()
    
    def security_audit(self):
        """Security Audit"""
        return self.scanner.full_scan()
    
    def get_status(self):
        """Get Current Status"""
        return self.monitor.full_check()


def main():
    """Main Function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ClawDoctor - OpenClaw Health Monitor")
    parser.add_argument("--fix", action="store_true", help="One-click fix")
    parser.add_argument("--scan", action="store_true", help="Security scan")
    parser.add_argument("--status", action="store_true", help="Show status")
    
    args = parser.parse_args()
    
    doctor = ClawDoctor()
    
    if args.fix:
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
