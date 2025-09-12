#!/usr/bin/env python3
"""
Deep troubleshooting for Google Analytics API access
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

def deep_troubleshoot():
    """Deep troubleshooting for GA API access"""
    print("🔍 Deep Google Analytics API Troubleshooting")
    print("=" * 60)
    
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    main_property_id = os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID')
    
    if not service_account_file or not os.path.exists(service_account_file):
        print("❌ Service account file issue")
        return
    
    # Load service account details
    with open(service_account_file, 'r') as f:
        sa_data = json.load(f)
    
    print(f"📋 Service Account: {sa_data['client_email']}")
    print(f"🏗️  Project ID: {sa_data['project_id']}")
    print(f"🎯 Property ID: {main_property_id}")
    
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.oauth2 import service_account
        import google.auth.exceptions
        
        # Test different credential loading approaches
        print(f"\n🧪 Testing Different Authentication Approaches:")
        
        # Method 1: Direct file loading
        print(f"1️⃣ Testing direct file loading...")
        try:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=['https://www.googleapis.com/auth/analytics.readonly']
            )
            print(f"   ✅ Credentials loaded")
            print(f"   📧 Service account: {credentials.service_account_email}")
            print(f"   🔑 Project ID: {credentials.project_id}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        # Method 2: Test token refresh
        print(f"\n2️⃣ Testing credential refresh...")
        try:
            from google.auth.transport.requests import Request
            credentials.refresh(Request())
            print(f"   ✅ Token refreshed successfully")
            print(f"   🕐 Token expires: {credentials.expiry}")
            
        except Exception as e:
            print(f"   ❌ Token refresh error: {e}")
        
        # Method 3: Try different scopes
        print(f"\n3️⃣ Testing with broader Analytics scope...")
        try:
            broad_credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=[
                    'https://www.googleapis.com/auth/analytics.readonly',
                    'https://www.googleapis.com/auth/analytics'
                ]
            )
            print(f"   ✅ Broader scope credentials loaded")
            
        except Exception as e:
            print(f"   ❌ Broader scope error: {e}")
        
        # Method 4: Test client initialization with different options
        print(f"\n4️⃣ Testing client initialization...")
        try:
            client = BetaAnalyticsDataClient(credentials=credentials)
            print(f"   ✅ Client initialized")
            
            # Try to get the service info
            print(f"   🔍 Client info: {type(client)}")
            
        except Exception as e:
            print(f"   ❌ Client init error: {e}")
            
        # Method 5: Try with explicit project
        print(f"\n5️⃣ Testing API call with explicit project...")
        try:
            from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric
            
            # Try with different property format
            property_formats = [
                f"properties/{main_property_id}",
                f"{main_property_id}",
                f"properties/{main_property_id}/",
            ]
            
            for prop_format in property_formats:
                print(f"   🧪 Trying property format: '{prop_format}'")
                try:
                    request = RunReportRequest(
                        property=prop_format,
                        date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
                        metrics=[Metric(name="sessions")]
                    )
                    
                    response = client.run_report(request=request)
                    print(f"   ✅ SUCCESS with format: {prop_format}")
                    print(f"   📊 Rows returned: {len(response.rows)}")
                    break
                    
                except Exception as e:
                    print(f"   ❌ Failed with {prop_format}: {str(e)[:100]}...")
                    
        except Exception as e:
            print(f"   ❌ API call error: {e}")
            
        # Method 6: Check if it's a quota/billing issue
        print(f"\n6️⃣ Checking for quota/billing issues...")
        try:
            # Try a very simple metadata request
            from google.analytics.data_v1beta.types import GetMetadataRequest
            
            metadata_request = GetMetadataRequest(
                name=f"properties/{main_property_id}/metadata"
            )
            
            metadata = client.get_metadata(metadata_request)
            print(f"   ✅ Metadata accessible!")
            
        except Exception as e:
            error_str = str(e)
            if "quota" in error_str.lower():
                print(f"   🚫 Quota issue detected")
            elif "billing" in error_str.lower():
                print(f"   💳 Billing issue detected")
            elif "403" in error_str:
                print(f"   🔐 Permission issue confirmed")
                print(f"   💡 This suggests the service account is not properly added to the GA property")
            else:
                print(f"   ❌ Other error: {error_str}")
                
        # Method 7: Verify the property exists and is accessible
        print(f"\n7️⃣ Property verification suggestions:")
        print(f"   📋 Double-check these in Google Analytics:")
        print(f"   • Property ID is exactly: {main_property_id}")
        print(f"   • Property is GA4 (not Universal Analytics)")
        print(f"   • Service account email is in Property Access Management")
        print(f"   • Service account has 'Viewer' or higher permissions")
        print(f"   • You're looking at the right Google Analytics account")
        
    except ImportError as e:
        print(f"❌ Missing library: {e}")
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    deep_troubleshoot()
