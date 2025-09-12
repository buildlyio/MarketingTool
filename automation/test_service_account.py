#!/usr/bin/env python3
"""
Test Google Analytics service account authentication
"""
import os
import sys
from datetime import datetime

# Add automation directory to path
sys.path.append('/Users/greglind/Projects/buildly/website/automation')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/Users/greglind/Projects/buildly/website/.env')

def test_service_account_auth():
    """Test service account authentication with Google Analytics"""
    print("🔐 Testing Google Analytics Service Account Authentication")
    print("=" * 60)
    
    service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    main_property_id = os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID')
    labs_property_id = os.getenv('GOOGLE_ANALYTICS_LABS_PROPERTY_ID')
    
    print(f"Service Account File: {service_account_file}")
    print(f"Main Property ID: {main_property_id}")
    print(f"Labs Property ID: {labs_property_id}")
    print()
    
    # Check if service account file exists
    if not service_account_file:
        print("❌ GOOGLE_SERVICE_ACCOUNT_FILE not set in .env")
        return False
    
    if not os.path.exists(service_account_file):
        print(f"❌ Service account file not found: {service_account_file}")
        return False
    
    print(f"✅ Service account file found: {service_account_file}")
    
    try:
        # Import required libraries
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
        from google.oauth2 import service_account
        
        print("✅ Google Analytics Data API libraries imported successfully")
        
        # Load service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        
        print("✅ Service account credentials loaded successfully")
        
        # Initialize the client
        client = BetaAnalyticsDataClient(credentials=credentials)
        print("✅ Google Analytics Data API client initialized")
        
        # Test connection with main property
        print(f"\n🧪 Testing connection to buildly.io (Property ID: {main_property_id})")
        
        request = RunReportRequest(
            property=f"properties/{main_property_id}",
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="screenPageViews"),
                Metric(name="activeUsers")
            ],
            dimensions=[Dimension(name="date")],
            limit=5  # Limit to 5 rows for testing
        )
        
        response = client.run_report(request=request)
        
        print(f"✅ Successfully connected to buildly.io!")
        print(f"   📊 Received {len(response.rows)} rows of data")
        
        # Display sample data
        if response.rows:
            print("   📈 Sample data (last 5 days):")
            for i, row in enumerate(response.rows[:3]):  # Show first 3 rows
                date = row.dimension_values[0].value
                sessions = row.metric_values[0].value
                page_views = row.metric_values[1].value
                users = row.metric_values[2].value
                print(f"     {date}: {sessions} sessions, {page_views} page views, {users} users")
        
        # Test labs property if configured
        if labs_property_id:
            print(f"\n🧪 Testing connection to labs.buildly.io (Property ID: {labs_property_id})")
            
            labs_request = RunReportRequest(
                property=f"properties/{labs_property_id}",
                date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="screenPageViews"),
                    Metric(name="activeUsers")
                ],
                dimensions=[Dimension(name="date")],
                limit=5
            )
            
            labs_response = client.run_report(request=labs_request)
            print(f"✅ Successfully connected to labs.buildly.io!")
            print(f"   📊 Received {len(labs_response.rows)} rows of data")
            
            if labs_response.rows:
                print("   📈 Sample data (last 5 days):")
                for i, row in enumerate(labs_response.rows[:3]):
                    date = row.dimension_values[0].value
                    sessions = row.metric_values[0].value
                    page_views = row.metric_values[1].value
                    users = row.metric_values[2].value
                    print(f"     {date}: {sessions} sessions, {page_views} page views, {users} users")
        
        print("\n🎉 Service account authentication test completed successfully!")
        print("💡 Your status reports will now use live Google Analytics data")
        return True
        
    except ImportError as e:
        print(f"❌ Missing library: {e}")
        print("   Run: pip install google-analytics-data")
        return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Verify the service account has 'Viewer' access to both GA properties")
        print("2. Check that the Google Analytics Data API is enabled in Google Cloud Console")
        print("3. Ensure the service account JSON file is valid")
        return False

if __name__ == "__main__":
    test_service_account_auth()
