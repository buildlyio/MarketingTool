#!/usr/bin/env python3
"""
Check if the issue is Google Cloud project linking
"""
import os
import sys
import json

# Add automation directory to path
sys.path.append('/Users/greglind/Projects/buildly/website/automation')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/Users/greglind/Projects/buildly/website/.env')

def check_linking_issue():
    """Check if the issue is Google Cloud project linking"""
    print("🔗 Checking Google Analytics <-> Google Cloud Project Linking")
    print("=" * 60)
    
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    main_property_id = os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID')
    
    if not service_account_file or not os.path.exists(service_account_file):
        print("❌ Service account file issue")
        return
    
    with open(service_account_file, 'r') as f:
        sa_data = json.load(f)
    
    print(f"📋 Configuration:")
    print(f"   📧 Service Account: {sa_data['client_email']}")
    print(f"   🏗️  Google Cloud Project: {sa_data['project_id']}")
    print(f"   🎯 GA Property ID: {main_property_id}")
    
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.oauth2 import service_account
        
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        print(f"\n🧪 Testing Different Approaches:")
        
        # Approach 1: Try with exact error details
        print(f"\n1️⃣ Standard approach (we know this fails)...")
        try:
            from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric
            
            request = RunReportRequest(
                property=f"properties/{main_property_id}",
                date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
                metrics=[Metric(name="sessions")],
                limit=1
            )
            
            response = client.run_report(request=request)
            print(f"   ✅ SUCCESS! (unexpected)")
            
        except Exception as e:
            print(f"   ❌ Expected failure: {str(e)[:80]}...")
        
        # Approach 2: Try the Admin API to see what we can access
        print(f"\n2️⃣ Checking Admin API access...")
        try:
            from google.analytics.admin_v1alpha import AnalyticsAdminServiceClient
            
            admin_client = AnalyticsAdminServiceClient(credentials=credentials)
            
            # Try to list accounts
            accounts = admin_client.list_accounts()
            account_list = list(accounts)
            
            print(f"   ✅ Admin API accessible")
            print(f"   📊 Accessible accounts: {len(account_list)}")
            
            if len(account_list) > 0:
                for account in account_list[:3]:  # Show first 3
                    print(f"     • {account.display_name} ({account.name})")
            else:
                print(f"   ⚠️  No accounts accessible via service account")
                
        except Exception as e:
            print(f"   ❌ Admin API error: {str(e)[:80]}...")
            
        # Approach 3: The real solution - Check for project linking issue
        print(f"\n💡 Most Likely Issue: Google Cloud Project Linking")
        print(f"   The service account is properly added to GA, but...")
        print(f"   The GA property might not be linked to the Google Cloud project!")
        
        print(f"\n🔧 Solution Steps:")
        print(f"   1. Go to Google Analytics → Admin → Property Settings")
        print(f"   2. Look for 'Google Cloud Project' or 'Google Cloud Link'")
        print(f"   3. Link the GA property to Cloud project: '{sa_data['project_id']}'")
        print(f"   4. This creates the connection between GA and the service account's project")
        
        print(f"\n📋 Alternative Approach:")
        print(f"   Create a new service account in the SAME Google account")
        print(f"   that owns the Google Analytics property")
        
    except ImportError as e:
        print(f"❌ Missing library: {e}")
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    check_linking_issue()
