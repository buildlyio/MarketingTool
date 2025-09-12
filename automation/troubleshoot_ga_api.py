#!/usr/bin/env python3
"""
Comprehensive Google Analytics API troubleshooting
"""
import os
import sys
import json
from datetime import datetime

# Add automation directory to path
sys.path.append('/Users/greglind/Projects/buildly/website/automation')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/Users/greglind/Projects/buildly/website/.env')

def check_api_access():
    """Check Google Analytics API access and provide detailed troubleshooting"""
    print("🔍 Google Analytics API Troubleshooting")
    print("=" * 50)
    
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    main_property_id = os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID')
    labs_property_id = os.getenv('GOOGLE_ANALYTICS_LABS_PROPERTY_ID')
    
    # Check service account file details
    print("📋 Service Account Information:")
    if service_account_file and os.path.exists(service_account_file):
        with open(service_account_file, 'r') as f:
            sa_data = json.load(f)
            print(f"   ✅ Email: {sa_data['client_email']}")
            print(f"   ✅ Project ID: {sa_data['project_id']}")
            print(f"   ✅ Private Key ID: {sa_data['private_key_id'][:8]}...")
    else:
        print(f"   ❌ File not found: {service_account_file}")
        return
    
    print(f"\n🎯 Target Properties:")
    print(f"   📊 buildly.io: {main_property_id}")
    print(f"   📊 labs.buildly.io: {labs_property_id}")
    
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.oauth2 import service_account
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        print(f"\n🔧 API Status:")
        print(f"   ✅ Credentials loaded successfully")
        print(f"   ✅ Client initialized")
        
        # Try to get metadata for the property (simpler request)
        print(f"\n🧪 Testing Property Access:")
        
        try:
            from google.analytics.data_v1beta.types import GetMetadataRequest
            
            # Test main property metadata access
            metadata_request = GetMetadataRequest(name=f"properties/{main_property_id}/metadata")
            metadata_response = client.get_metadata(metadata_request)
            
            print(f"   ✅ buildly.io metadata accessible!")
            print(f"      📊 Property name: {metadata_response.name}")
            
        except Exception as e:
            print(f"   ❌ buildly.io metadata error: {str(e)}")
            
            # Try a different approach - list accessible properties
            print(f"\n🔍 Checking what properties are accessible...")
            
            # This would require the Analytics Admin API, but let's try a simpler approach
            print("   💡 Suggestion: Verify in Google Analytics that the service account")
            print("      is added with 'Viewer' role to BOTH properties:")
            print(f"      - buildly.io (Property ID: {main_property_id})")
            print(f"      - labs.buildly.io (Property ID: {labs_property_id})")
            
        # Check if we can make a simple data request
        print(f"\n📈 Testing Data Access:")
        
        try:
            from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric
            
            simple_request = RunReportRequest(
                property=f"properties/{main_property_id}",
                date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
                metrics=[Metric(name="sessions")],
                limit=1
            )
            
            response = client.run_report(simple_request)
            print(f"   ✅ Data access successful!")
            print(f"   📊 Response rows: {len(response.rows)}")
            
        except Exception as e:
            print(f"   ❌ Data access error: {str(e)}")
            
            if "403" in str(e):
                print(f"\n🔧 Permission Issue Detected:")
                print(f"   1. Go to Google Analytics → Admin → Property access management")
                print(f"   2. Ensure '{sa_data['client_email']}' has 'Viewer' role")
                print(f"   3. Wait 5-10 minutes for permissions to propagate")
                print(f"   4. Verify you're in GA4 (not Universal Analytics)")
            elif "404" in str(e):
                print(f"\n🔧 Property Not Found:")
                print(f"   1. Double-check Property IDs in Google Analytics")
                print(f"   2. Ensure you're looking at GA4 properties (9-digit IDs)")
            
    except ImportError as e:
        print(f"❌ Missing library: {e}")
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    check_api_access()
