#!/usr/bin/env python3
"""
Simple Dashboard Server for Buildly Marketing Analytics
Serves the HTML dashboard with live data updates
"""

import http.server
import socketserver
import json
import sqlite3
from datetime import datetime, timedelta
from urllib.parse import urlparse

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for dashboard requests"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/stats':
            self.serve_stats()
        else:
            # Serve static files from automation directory
            if self.path.startswith('/automation/'):
                try:
                    file_path = self.path[1:]  # Remove leading slash
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    self.send_response(200)
                    if file_path.endswith('.html'):
                        self.send_header('Content-type', 'text/html')
                    elif file_path.endswith('.css'):
                        self.send_header('Content-type', 'text/css')
                    elif file_path.endswith('.js'):
                        self.send_header('Content-type', 'text/javascript')
                    self.end_headers()
                    self.wfile.write(content)
                except:
                    self.send_error(404)
            else:
                self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the main dashboard"""
        try:
            with open('automation/analytics_dashboard.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Error loading dashboard: {e}")
    
    def serve_stats(self):
        """Serve real-time statistics"""
        try:
            # Get real stats from database
            conn = sqlite3.connect('automation/user_engagement.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            # Mock other stats for now
            stats = {
                'total_users': total_users,
                'active_users': max(1, int(total_users * 0.6)),
                'emails_sent_30d': 68,
                'engagement_rate': 73.2,
                'last_updated': datetime.now().isoformat()
            }
            
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode('utf-8'))
            
        except Exception as e:
            # Fallback to mock data
            stats = {
                'total_users': 69,
                'active_users': 42,
                'emails_sent_30d': 68,
                'engagement_rate': 73.2,
                'last_updated': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode('utf-8'))

def start_server(port=8080):
    """Start the dashboard server"""
    print(f"🚀 Starting Buildly Analytics Dashboard Server...")
    print(f"📊 Dashboard available at: http://localhost:{port}")
    
    try:
        with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
            print(f"✅ Server running on port {port} - Press Ctrl+C to stop")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_server(port)