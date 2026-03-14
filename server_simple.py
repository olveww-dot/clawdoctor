#!/usr/bin/env python3
"""
ClawDoctor Simple API Server
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import threading
import time
import sys

sys.path.insert(0, str(Path(__file__).parent))
from clawdoctor_simple import ClawDoctor, OpenClawMonitor, OpenClawFixer, SecurityScanner

doctor = ClawDoctor()
monitor = OpenClawMonitor()
fixer = OpenClawFixer()
scanner = SecurityScanner()

logs_data = []
max_logs = 100


class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        path = self.path
        
        if path == '/api/status':
            result = monitor.full_check()
            self.wfile.write(json.dumps(result).encode())
        elif path == '/api/logs':
            self.wfile.write(json.dumps({'data': logs_data}).encode())
        elif path == '/api/check':
            result = monitor.full_check()
            add_log(result)
            self.wfile.write(json.dumps(result).encode())
        elif path == '/api/scan':
            result = scanner.full_scan()
            self.wfile.write(json.dumps({'risks': result}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        path = self.path
        
        if path == '/api/fix':
            result = fixer.fix_all()
            self.wfile.write(json.dumps(result).encode())
        elif path == '/api/fix/gateway':
            result = fixer.fix_gateway()
            self.wfile.write(json.dumps({'fixes': result}).encode())
        elif path == '/api/fix/config':
            result = fixer.fix_config()
            self.wfile.write(json.dumps({'fixes': result}).encode())
        else:
            self.send_response(404)
            self.end_headers()


def add_log(data):
    global logs_data
    logs_data.append({
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        **data
    })
    if len(logs_data) > max_logs:
        logs_data = logs_data[-max_logs:]


def collect_data():
    while True:
        try:
            status = monitor.full_check()
            global logs_data
            logs_data.append({
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
                **status
            })
            if len(logs_data) > max_logs:
                logs_data = logs_data[-max_logs:]
            time.sleep(60)
        except Exception as e:
            print(f"Data collection error: {e}")
            time.sleep(60)


def run_server(port=0):
    server = HTTPServer(('127.0.0.1', port), APIHandler)
    actual_port = server.server_address[1]
    print(f"Server running on http://127.0.0.1:{actual_port}")
    with open('/tmp/clawdoctor-port.txt', 'w') as f:
        f.write(str(actual_port))
    server.serve_forever()


if __name__ == '__main__':
    collector = threading.Thread(target=collect_data, daemon=True)
    collector.start()
    run_server()
