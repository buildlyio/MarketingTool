#!/usr/bin/env python3
"""
Check for Google Cloud project and Google Analytics property ownership mismatch
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

def check_project_property_mismatch():
    """Check if there's a project/property ownership mismatch"""
    print("🔍 Checking Google Cloud Project vs Google Analytics Property Ownership")
    print("=" * 70)
    
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    main_property_id = os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID')
    
    with open(service_account_file, 'r') as f:
        sa_data = json.load(f)
    
    print(f"📋 Service Account Details:")
    print(f"   📧 Email: {sa_data['client_email']}")
    print(f"   🏗️  Google Cloud Project: {sa_data['project_id']}")
    print(f"   🎯 Target GA Property: {main_property_id}")
    
    print(f"\n🤔 Potential Issues to Check:")
    
    print(f"\n1️⃣ Google Analytics Data API Quota/Limits")
    print(f"   💡 Even with permissions, the API might have quotas")
    
    print(f"\n2️⃣ Service Account vs User Account Ownership")
    print(f"   💡 The GA property might be owned by a personal Google account")
    print(f"   💡 But the service account is in a different Google Cloud organization")
    
    print(f"\n3️⃣ Google Analytics Property Linking")
    print(f"   💡 GA4 properties need to be linked to the correct Cloud project")
    
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.oauth2 import service_account
        
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        
        client = BetaAnalyticsDataClient(credentials=credentials)
        
        # Try to list available properties (this might work even if specific property access fails)
        print(f"\n4️⃣ Attempting to verify service account scope...")
        
        try:
            # Try a different approach - check if we can access any properties at all
            from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
            from google.analytics.admin_v1beta.types import ListAccountsRequest
            
            admin_client = AnalyticsAdminServiceClient(credentials=credentials)
            
            # Try to list accounts
            try:
                accounts_request = ListAccountsRequest()
                accounts = admin_client.list_accounts(request=accounts_request)
                
                print(f"   ✅ Can access Analytics Admin API")
                account_count = len(list(accounts))
                print(f"   📊 Accessible accounts: {account_count}")
                
                if account_count == 0:
                    print(f"   ⚠️  No accounts accessible - this is the issue!")
                    print(f"   💡 Service account has no access to ANY GA accounts")
                
            except Exception as e:
                print(f"   ❌ Admin API error: {str(e)[:100]}...")
                if "403" in str(e):
                    print(f"   💡 Admin API also blocked - confirms permission issue")
                
        except ImportError:
            print(f"   ⚠️  Admin API not available, trying alternative approach...")
            
        # Alternative: Try with a completely different property format or approach
        print(f"\n5️⃣ Testing alternative API approaches...")
        
        try:
            # Try using the measurement ID instead of property ID (if we can figure it out)
            print(f"   🧪 Trying different property access patterns...")
            
            # Check if the error gives us more specific information
            from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric
            
            request = RunReportRequest(
                property=f"properties/{main_property_id}",
                date_ranges=[DateRange(start_date="yesterday", end_date="yesterday")],
                metrics=[Metric(name="sessions")],
                limit=1
            )
            
            try:
                response = client.run_report(request=request)
                print(f"   🎉 SUCCESS! Property is accessible!")
                
            except Exception as e:
                error_message = str(e)
                print(f"   ❌ Error: {error_message}")
                
                # Parse the error for more specific information
                if "does not have sufficient permissions" in error_message:
                    print(f"\n🔍 Detailed Error Analysis:")
                    print(f"   • Service account IS authenticated")
                    print(f"   • Service account CAN reach the API")
                    print(f"   • Service account CANNOT access this specific property")
                    print(f"   • This suggests a LINKING issue, not a permission issue")
                    
                    print(f"\n💡 Possible Solutions:")
                    print(f"   1. Check if GA property is linked to Google Cloud project '{sa_data['project_id']}'")
                    print(f"   2. Try linking the GA property to the Cloud project in GA Admin")
                    print(f"   3. Verify the property owner's Google account matches the Cloud project owner")
                    
                elif "property not found" in error_message.lower():
                    print(f"   💡 Property ID {main_property_id} might be incorrect")
                    
        except Exception as e:
            print(f"   ❌ Alternative approach error: {e}")
            
    except Exception as e:
        print(f"❌ Setup error: {e}")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. In Google Analytics, go to Admin → Property Settings")
    print(f"   2. Look for 'Google Cloud Link' or 'Google Cloud Project'")
    print(f"   3. Ensure it's linked to project: {sa_data['project_id']}")
    print(f"   4. If not linked, create the link between GA and Cloud project")

if __name__ == "__main__":
    check_project_property_mismatch()
