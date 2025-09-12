#!/usr/bin/env python3
"""
Auto-refresh script for marketing dashboard
Updates the dashboard HTML every few minutes
"""

import time
import subprocess
import sys
import os
from datetime import datetime

def update_dashboard():
    """Update the marketing dashboard"""
    try:
        # Run the dashboard generator
        result = subprocess.run([
            sys.executable, 'automation/dashboard_generator.py'
        ], capture_output=True, text=True, cwd='/Users/greglind/Projects/buildly/website')
        
        if result.returncode == 0:
            print(f"✅ Dashboard updated at {datetime.now().strftime('%H:%M:%S')}")
        else:
            print(f"❌ Dashboard update failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error updating dashboard: {e}")

def main():
    """Main loop - update dashboard every 5 minutes"""
    print("🚀 Starting Buildly Marketing Dashboard Auto-Updater")
    print("Dashboard will refresh every 5 minutes...")
    
    # Update immediately
    update_dashboard()
    
    # Then update every 5 minutes
    while True:
        time.sleep(300)  # 5 minutes
        update_dashboard()

if __name__ == "__main__":
    main()
