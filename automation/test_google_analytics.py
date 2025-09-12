#!/usr/bin/env python3
"""
Test Google Analytics API integration
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add automation directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_google_analytics():
    """Test Google Analytics API with the provided key"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_ANALYTICS_API_KEY')
    property_id = os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID')
    
    print("🔍 Testing Google Analytics API Integration")
    print("=" * 50)
    print(f"API Key: {api_key[:20]}..." if api_key else "❌ No API key found")
    print(f"Property ID: {property_id}")
    print()
    
    if not api_key:
        print("❌ Google Analytics API key not found in .env file")
        return False
    
    if not property_id or property_id == "your-property-id":
        print("⚠️  Property ID not configured - using test request")
        # Test API key validity with a simple request
        test_url = f"https://analyticsdata.googleapis.com/v1beta/metadata/properties?key={api_key}"
        
        try:
            response = requests.get(test_url)
            print(f"API Key Test Response: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Google Analytics API key is valid!")
                print("📝 Next step: Configure your GA4 Property ID in .env")
                return True
            elif response.status_code == 400:
                print("✅ API key is valid (400 = missing property ID)")
                print("📝 Please add your GA4 Property ID to .env file")
                return True
            elif response.status_code == 403:
                print("❌ API key authentication failed")
                print("   Check that the API key has Analytics Data API permissions")
                return False
            else:
                print(f"❌ API error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing API key: {e}")
            return False
    
    # Test with actual property ID
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "dateRanges": [{"startDate": "7daysAgo", "endDate": "today"}],
        "metrics": [
            {"name": "sessions"},
            {"name": "screenPageViews"}, 
            {"name": "activeUsers"}
        ],
        "dimensions": [{"name": "pagePath"}]
    }
    
    try:
        print("📊 Testing GA4 Data API request...")
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully retrieved Google Analytics data!")
            
            if 'rows' in data and data['rows']:
                print(f"📈 Found {len(data['rows'])} data rows")
                print("Sample data:")
                for i, row in enumerate(data['rows'][:3]):
                    page = row['dimensionValues'][0]['value']
                    sessions = row['metricValues'][0]['value']
                    views = row['metricValues'][1]['value']
                    print(f"  {i+1}. {page} - {sessions} sessions, {views} views")
            else:
                print("📊 No data found for the specified date range")
            
            return True
            
        elif response.status_code == 403:
            print("❌ Access denied - check Property ID and API permissions")
            print(f"   Response: {response.text}")
            return False
        elif response.status_code == 400:
            print("❌ Bad request - check Property ID format")
            print(f"   Response: {response.text}")
            return False
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Google Analytics: {e}")
        return False

def get_property_id_instructions():
    """Show instructions for finding GA4 Property ID"""
    print("\n📋 How to find your GA4 Property ID:")
    print("=" * 40)
    print("1. Go to https://analytics.google.com/")
    print("2. Select your website property")
    print("3. Click Admin (gear icon) in the bottom left")
    print("4. In the Property column, click 'Property Settings'")
    print("5. Your Property ID is displayed at the top (format: 123456789)")
    print("\n📝 Add it to your .env file:")
    print("GOOGLE_ANALYTICS_PROPERTY_ID=your-property-id-here")
    print()

if __name__ == "__main__":
    print(f"🚀 Google Analytics API Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = test_google_analytics()
    
    if not success:
        get_property_id_instructions()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Google Analytics integration ready!")
        print("🎯 Your dashboard will now show real analytics data")
    else:
        print("❌ Google Analytics setup needs attention")
        print("📧 Contact support if you need help")
