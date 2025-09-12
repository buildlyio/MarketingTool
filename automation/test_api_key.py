#!/usr/bin/env python3
"""
Simple test for Google API key validation
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_ANALYTICS_API_KEY')

print(f"🔑 Testing API Key: {api_key[:20]}...")

# Test with Google Analytics Reporting API v4 (simpler endpoint)
test_urls = [
    "https://www.googleapis.com/analytics/v3/management/accounts",
    "https://analyticsreporting.googleapis.com/v4/reports:batchGet",
    "https://content-analyticsdata.googleapis.com/v1beta/properties"
]

for url in test_urls:
    try:
        response = requests.get(f"{url}?key={api_key}")
        print(f"📊 {url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Success!")
        elif response.status_code == 401:
            print("   🔐 Auth required (API key invalid)")
        elif response.status_code == 403:
            print("   🚫 Forbidden (API not enabled or quota exceeded)")
        elif response.status_code == 400:
            print("   ⚠️  Bad request (needs proper payload)")
        else:
            print(f"   ❓ Other: {response.text[:100]}")
        print()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
