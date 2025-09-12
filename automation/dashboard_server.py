#!/usr/bin/env python3
"""
Simple web server for Buildly Marketing Dashboard
Serves the dashboard HTML and auto-updates it
"""

import http.server
import socketserver
import threading
import time
import subprocess
import sys
import os
from datetime import datetime

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='/Users/greglind/Projects/buildly/website', **kwargs)
    
    def end_headers(self):
        # Add headers to prevent caching for real-time updates
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def update_dashboard_periodically():
    """Update dashboard every 5 minutes"""
    while True:
        try:
            # Change to the website directory
            os.chdir('/Users/greglind/Projects/buildly/website')
            
            # Run the dashboard generator
            result = subprocess.run([
                sys.executable, 'automation/dashboard_generator.py'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Dashboard updated at {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"❌ Dashboard update failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error updating dashboard: {e}")
        
        # Wait 5 minutes before next update
        time.sleep(300)

def start_server(port=8000):
    """Start the dashboard web server"""
    
    # Start the dashboard updater in a separate thread
    updater_thread = threading.Thread(target=update_dashboard_periodically, daemon=True)
    updater_thread.start()
    
    # Start the web server
    with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
        print(f"""
🚀 Buildly Marketing Dashboard Server Started!

📊 Dashboard URL: http://localhost:{port}
🔄 Auto-refreshes every 5 minutes
📧 Email reports sent to {os.getenv('REPORT_EMAIL', 'greg@buildly.io')}

Press Ctrl+C to stop the server
        """)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Dashboard server stopped")
            httpd.shutdown()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Buildly Marketing Dashboard Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on (default: 8000)')
    args = parser.parse_args()
    
    start_server(args.port)
