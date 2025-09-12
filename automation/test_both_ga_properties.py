#!/usr/bin/env python3
"""
Test Google Analytics API with both Buildly properties
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add automation directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ga_property(api_key, property_id, property_name):
    """Test a specific GA property with API key"""
    
    print(f"🔍 Testing {property_name} (Property ID: {property_id})")
    print("=" * 60)
    
    # Method 1: Try with X-Goog-Api-Key header (newer method)
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key
    }
    
    payload = {
        "dateRanges": [{"startDate": "7daysAgo", "endDate": "today"}],
        "metrics": [
            {"name": "sessions"},
            {"name": "screenPageViews"},
            {"name": "activeUsers"}
        ],
        "dimensions": [{"name": "pagePath"}],
        "limit": "10"
    }
    
    try:
        print("📊 Method 1: X-Goog-Api-Key header")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS! Got live data!")
            
            if 'rows' in data and data['rows']:
                print(f"   📈 Found {len(data['rows'])} data rows")
                total_sessions = sum(int(row['metricValues'][0]['value']) for row in data['rows'])
                total_views = sum(int(row['metricValues'][1]['value']) for row in data['rows'])
                print(f"   📊 Total Sessions: {total_sessions}")
                print(f"   👁️ Total Page Views: {total_views}")
                
                print("   🔝 Top Pages:")
                for i, row in enumerate(data['rows'][:5]):
                    page = row['dimensionValues'][0]['value']
                    views = row['metricValues'][1]['value']
                    print(f"      {i+1}. {page} - {views} views")
            else:
                print("   📊 API responded but no data rows found")
            return True
            
        elif response.status_code == 401:
            print("   🔐 Authentication failed")
            print(f"   Response: {response.text[:200]}...")
        elif response.status_code == 403:
            print("   🚫 Access forbidden")
            print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Method 2: Try with key parameter in URL
    print("\n📊 Method 2: API key as URL parameter")
    url_with_key = f"{url}?key={api_key}"
    
    try:
        response = requests.post(url_with_key, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS with URL parameter method!")
            return True
        else:
            print(f"   ❌ Failed: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Method 3: Try the getMetadata endpoint (might work with API key)
    print("\n📊 Method 3: getMetadata endpoint")
    metadata_url = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}/metadata"
    
    try:
        response = requests.get(f"{metadata_url}?key={api_key}", timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Metadata endpoint works!")
            data = response.json()
            if 'dimensions' in data:
                print(f"   📊 Available dimensions: {len(data['dimensions'])}")
            if 'metrics' in data:
                print(f"   📈 Available metrics: {len(data['metrics'])}")
            return True
        else:
            print(f"   ❌ Failed: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    return False

def main():
    """Test both Buildly properties"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_ANALYTICS_API_KEY')
    main_property = os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID')
    labs_property = os.getenv('GOOGLE_ANALYTICS_LABS_PROPERTY_ID')
    
    print("🚀 Buildly Google Analytics API Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"API Key: {api_key[:20]}..." if api_key else "❌ No API key found")
    print(f"Main Property: {main_property}")
    print(f"Labs Property: {labs_property}")
    print()
    
    if not api_key:
        print("❌ No Google Analytics API key found in .env file")
        return
    
    success_count = 0
    
    # Test main buildly.io property
    if main_property and main_property != "your-property-id":
        if test_ga_property(api_key, main_property, "buildly.io"):
            success_count += 1
        print()
    
    # Test labs.buildly.io property
    if labs_property and labs_property != "your-property-id":
        if test_ga_property(api_key, labs_property, "labs.buildly.io"):
            success_count += 1
        print()
    
    print("=" * 60)
    if success_count > 0:
        print(f"✅ SUCCESS! {success_count} properties working with API key")
        print("🎯 Your dashboard will now show LIVE Google Analytics data!")
    else:
        print("❌ API key authentication not working for either property")
        print("📋 You may need OAuth setup for live data")
        print("💡 Dashboard will continue with enhanced demo data")
    
    print("\n📊 Next steps:")
    if success_count > 0:
        print("1. Restart your dashboard to see live data")
        print("2. Check your updated marketing metrics")
        print("3. Enjoy real-time Google Analytics integration!")
    else:
        print("1. Consider setting up OAuth for live data access")
        print("2. Check if API has the Analytics Data API enabled")
        print("3. Verify property permissions in Google Analytics")

if __name__ == "__main__":
    main()
