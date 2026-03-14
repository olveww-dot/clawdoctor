#!/usr/bin/env python3
"""
ClawDoctor 本地 HTTP 服务器
提供 Dashboard 静态文件和日志 API
"""

import json
import http.server
import socketserver
from pathlib import Path
from datetime import datetime
import os

PORT = 8080
LOG_DIR = Path.home() / ".clawdoctor" / "logs"

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def do_GET(self):
        # API: 获取日志数据
        if self.path.startswith('/api/logs'):
            self.send_json(self.get_logs())
            return
        
        # API: 获取最新状态
        if self.path == '/api/status':
            self.send_json(self.get_status())
            return
        
        # 静态文件: Dashboard
        if self.path == '/' or self.path == '/dashboard':
            self.path = '/dashboard.html'
        
        return super().do_GET()
    
    def get_logs(self):
        """读取日志文件"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            log_file = LOG_DIR / f"{today}.jsonl"
            
            if not log_file.exists():
                return {"error": "No logs found", "data": []}
            
            logs = []
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))
            
            return {"data": logs}
        except Exception as e:
            return {"error": str(e), "data": []}
    
    def get_status(self):
        """获取最新状态"""
        logs = self.get_logs()
        if logs.get("data"):
            latest = logs["data"][-1]
            return {
                "timestamp": latest.get("timestamp"),
                "gateway": latest.get("gateway", {}),
                "qqbot": latest.get("qqbot", {}),
                "system": latest.get("system", {})
            }
        return {"error": "No data"}
    
    def send_json(self, data):
        """发送 JSON 响应"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        """简化日志输出"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

def main():
    # 确保日志目录存在
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # 切换工作目录到项目目录
    os.chdir(Path(__file__).parent)
    
    print(f"🦞 ClawDoctor Server 启动...")
    print(f"📊 Dashboard: http://localhost:{PORT}")
    print(f"📡 API: http://localhost:{PORT}/api/logs")
    print(f"📝 日志目录: {LOG_DIR}")
    print(f"\n按 Ctrl+C 停止\n")
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server 已停止")

if __name__ == "__main__":
    main()
