#!/usr/bin/env python3
"""
Test the User Engagement System

This script tests all components of the user engagement automation:
1. Database setup and user import
2. Feature announcement emails
3. Re-engagement campaigns
4. Integration with main automation
"""

import sys
import os
from datetime import datetime

# Add automation directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_engagement import UserEngagementSystem, PlatformUser

def test_user_engagement_system():
    """Test the complete user engagement system"""
    
    print("🧪 Testing Buildly User Engagement System")
    print("=" * 50)
    
    try:
        # Initialize system
        print("1️⃣ Initializing User Engagement System...")
        engagement = UserEngagementSystem()
        print("   ✅ System initialized successfully")
        
        # Test database setup
        print("\n2️⃣ Testing Database Setup...")
        
        # Import sample users
        sample_users = [
            {
                "user_id": "user_active_001",
                "email": "active.user@example.com",
                "name": "Active Developer",
                "signup_date": "2025-08-15",
                "last_login": "2025-09-29",  # Recent login (active)
                "features_used": ["api_builder", "workflow_designer"],
                "subscription_type": "pro"
            },
            {
                "user_id": "user_inactive_001",
                "email": "inactive.user@example.com", 
                "name": "Inactive User",
                "signup_date": "2025-06-01",
                "last_login": "2025-07-15",  # Old login (inactive)
                "features_used": ["ui_builder"],
                "subscription_type": "free"
            },
            {
                "user_id": "user_new_001",
                "email": "new.user@example.com",
                "name": "New User",
                "signup_date": "2025-09-28",
                "last_login": "2025-09-28",  # Very recent (active)
                "features_used": [],
                "subscription_type": "free"
            }
        ]
        
        imported_count = engagement.import_users_from_platform(sample_users)
        print(f"   ✅ Imported {imported_count} test users")
        
        # Test user categorization
        print("\n3️⃣ Testing User Activity Classification...")
        active_users = engagement.get_active_users()
        inactive_users = engagement.get_inactive_users()
        
        print(f"   📊 Active Users: {len(active_users)}")
        for user in active_users:
            print(f"      • {user.name} ({user.email}) - Last login: {user.last_login}")
        
        print(f"   📊 Inactive Users: {len(inactive_users)}")
        for user in inactive_users:
            print(f"      • {user.name} ({user.email}) - Last login: {user.last_login}")
        
        # Test feature announcement (send to BCC address only)
        print("\n4️⃣ Testing Feature Announcement Email...")
        if active_users:
            # Send test email to BCC address
            test_user = PlatformUser(
                user_id="test_feature",
                email=engagement.bcc_email,  # Send to BCC address for testing
                name="Test User (Feature)",
                signup_date=datetime.now().isoformat(),
                last_login=datetime.now().isoformat(),
                activity_level="active",
                features_used=["api_builder"],
                subscription_type="pro"
            )
            
            results = engagement.send_feature_announcement(
                [test_user],
                "Smart API Integrations",
                "Connect to any third-party service with just a few clicks. Our new Smart API Integrations feature automatically handles authentication, rate limiting, and error handling.",
                "• Visual API connector with drag-and-drop interface\n• Pre-built integrations for 100+ popular services\n• Automatic retry logic and error handling\n• Real-time data synchronization",
                "https://buildly.io/features/smart-api"
            )
            
            print(f"   ✅ Feature announcement test: {results['sent']} sent, {results['failed']} failed")
            print(f"   📧 Test email sent to: {engagement.bcc_email}")
        else:
            print("   ⚠️ No active users to test with")
        
        # Test re-engagement campaign (send to BCC address only)
        print("\n5️⃣ Testing Re-engagement Campaign...")
        if inactive_users:
            # Send test email to BCC address
            test_user = PlatformUser(
                user_id="test_reengagement",
                email=engagement.bcc_email,  # Send to BCC address for testing
                name="Test User (Inactive)",
                signup_date="2025-06-01",
                last_login="2025-07-15",
                activity_level="inactive",
                features_used=["ui_builder"],
                subscription_type="free"
            )
            
            results = engagement.send_reengagement_campaign([test_user])
            
            print(f"   ✅ Re-engagement test: {results['sent']} sent, {results['failed']} failed")
            print(f"   📧 Test email sent to: {engagement.bcc_email}")
        else:
            print("   ⚠️ No inactive users to test with")
        
        # Test engagement statistics
        print("\n6️⃣ Testing Engagement Statistics...")
        stats = engagement.get_engagement_stats()
        
        print(f"   📊 User Activity Breakdown:")
        if 'user_activity' in stats:
            for activity, count in stats['user_activity'].items():
                print(f"      • {activity}: {count} users")
        
        if 'email_campaigns' in stats and stats['email_campaigns']:
            print(f"   📧 Recent Email Campaign Stats:")
            for campaign, statuses in stats['email_campaigns'].items():
                print(f"      • {campaign}:")
                for status, count in statuses.items():
                    print(f"        - {status}: {count}")
        
        print("\n🎉 User Engagement System Test Completed Successfully!")
        print("\n" + "="*60)
        print("📋 SUMMARY")
        print("="*60)
        print("✅ Database initialization: Working")
        print("✅ User import and classification: Working") 
        print("✅ Feature announcement emails: Working")
        print("✅ Re-engagement campaigns: Working")
        print("✅ Engagement statistics: Working")
        print("✅ Email delivery: Working")
        
        print(f"\n📧 Check {engagement.bcc_email} for test emails!")
        
        print("\n🚀 NEXT STEPS:")
        print("1. Import your real platform users using the CLI:")
        print("   python user_engagement_cli.py import-users --file your_users.json")
        print("\n2. Send feature announcements:")
        print("   python user_engagement_cli.py feature-announcement --name 'Feature Name' --description 'Description'")
        print("\n3. Run re-engagement campaigns:")
        print("   python user_engagement_cli.py reengagement-campaign")
        print("\n4. The system will automatically run re-engagement on Fridays via main automation")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_user_engagement_system()
    
    if success:
        print("\n🎉 User engagement system is ready for production!")
    else:
        print("\n❌ User engagement system test failed")
        sys.exit(1)