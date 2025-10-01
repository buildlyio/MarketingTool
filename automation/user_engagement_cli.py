#!/usr/bin/env python3
"""
User Engagement CLI - Command line interface for managing user engagement campaigns

Usage examples:
    # Import users from CSV or JSON
    python user_engagement_cli.py import-users --file users.json
    
    # Send feature announcement to active users
    python user_engagement_cli.py feature-announcement --name "Smart Workflows" --description "Automate your development process"
    
    # Send re-engagement to inactive users  
    python user_engagement_cli.py reengagement-campaign
    
    # Get engagement statistics
    python user_engagement_cli.py stats
"""

import argparse
import json
import csv
import sys
import os
from datetime import datetime
from typing import List, Dict

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_engagement import UserEngagementSystem

def import_users_from_file(file_path: str) -> List[Dict]:
    """Import users from JSON or CSV file"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return []
    
    users = []
    
    try:
        if file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    users = data
                elif isinstance(data, dict) and 'users' in data:
                    users = data['users']
                else:
                    print("❌ JSON file must contain a list of users or have a 'users' key")
                    return []
        
        elif file_path.endswith('.csv'):
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert features_used from string to list if needed
                    if 'features_used' in row and isinstance(row['features_used'], str):
                        try:
                            row['features_used'] = json.loads(row['features_used'])
                        except:
                            row['features_used'] = row['features_used'].split(',') if row['features_used'] else []
                    users.append(row)
        
        else:
            print("❌ Unsupported file format. Use .json or .csv")
            return []
        
        print(f"✅ Loaded {len(users)} users from {file_path}")
        return users
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []

def create_sample_users_file():
    """Create a sample users file for testing"""
    sample_users = [
        {
            "user_id": "user_001",
            "email": "john.doe@example.com", 
            "name": "John Doe",
            "signup_date": "2025-08-15",
            "last_login": "2025-09-29",
            "features_used": ["api_builder", "workflow_designer"],
            "subscription_type": "pro"
        },
        {
            "user_id": "user_002",
            "email": "jane.smith@example.com",
            "name": "Jane Smith", 
            "signup_date": "2025-07-01",
            "last_login": "2025-08-15",
            "features_used": ["ui_builder"],
            "subscription_type": "free"
        },
        {
            "user_id": "user_003",
            "email": "mike.wilson@example.com",
            "name": "Mike Wilson",
            "signup_date": "2025-06-01",
            "last_login": "2025-07-20",
            "features_used": [],
            "subscription_type": "free"
        }
    ]
    
    with open('automation/sample_users.json', 'w') as f:
        json.dump(sample_users, f, indent=2)
    
    print("✅ Created automation/sample_users.json with sample data")
    print("💡 You can use this as a template for your user data")

def main():
    parser = argparse.ArgumentParser(description='Buildly User Engagement System')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Import users command
    import_parser = subparsers.add_parser('import-users', help='Import users from file')
    import_parser.add_argument('--file', required=True, help='Path to JSON or CSV file with user data')
    
    # Feature announcement command
    feature_parser = subparsers.add_parser('feature-announcement', help='Send feature announcement to active users')
    feature_parser.add_argument('--name', required=True, help='Feature name')
    feature_parser.add_argument('--description', required=True, help='Feature description')
    feature_parser.add_argument('--release-notes', help='Additional release notes')
    feature_parser.add_argument('--cta-link', help='Call-to-action link')
    feature_parser.add_argument('--test', action='store_true', help='Send test email to configured BCC address only')
    
    # Re-engagement command
    reengagement_parser = subparsers.add_parser('reengagement-campaign', help='Send re-engagement emails to inactive users')
    reengagement_parser.add_argument('--test', action='store_true', help='Send test email to configured BCC address only')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show engagement statistics')
    
    # Sample users command
    sample_parser = subparsers.add_parser('create-sample', help='Create sample users file for testing')
    
    # User list commands
    list_parser = subparsers.add_parser('list-users', help='List users by activity level')
    list_parser.add_argument('--activity', choices=['active', 'inactive', 'all'], default='all', 
                           help='Filter users by activity level')
    
    # Buildly API sync commands
    sync_parser = subparsers.add_parser('sync-buildly', help='Sync users from Buildly API')
    sync_parser.add_argument('--organization', help='Organization UUID filter')
    sync_parser.add_argument('--new-only', action='store_true', help='Sync only new users from last 7 days')
    sync_parser.add_argument('--days', type=int, default=7, help='Days to look back for new users (default: 7)')
    
    # Test API connection
    test_api_parser = subparsers.add_parser('test-api', help='Test Buildly API connection')
    
    # List organizations
    orgs_parser = subparsers.add_parser('list-orgs', help='List Buildly organizations')
    
    # Marketing email
    marketing_parser = subparsers.add_parser('marketing-email', help='Send marketing email to all subscribers')
    marketing_parser.add_argument('--template', required=True, help='Email template name (without .html extension)')
    marketing_parser.add_argument('--subject', required=True, help='Email subject line')
    marketing_parser.add_argument('--campaign-name', help='Campaign name for analytics tracking')
    marketing_parser.add_argument('--test', action='store_true', help='Send test email to BCC address only')
    
    # Onboarding help email
    onboarding_parser = subparsers.add_parser('onboarding-help', help='Send onboarding help email to incomplete users')
    onboarding_parser.add_argument('--test', action='store_true', help='Send test email to BCC address only')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize engagement system
    engagement = UserEngagementSystem()
    
    try:
        if args.command == 'import-users':
            users = import_users_from_file(args.file)
            if users:
                imported_count = engagement.import_users_from_platform(users)
                print(f"✅ Successfully imported {imported_count} users")
            else:
                print("❌ No users to import")
        
        elif args.command == 'feature-announcement':
            print(f"📢 Sending feature announcement: {args.name}")
            
            if args.test:
                # Send test email to BCC address
                print("🧪 Test mode: sending to configured BCC address only")
                from user_engagement import PlatformUser
                test_user = PlatformUser(
                    user_id="test_user",
                    email=engagement.bcc_email,
                    name="Test User",
                    signup_date=datetime.now().isoformat(),
                    last_login=datetime.now().isoformat(),
                    activity_level="active",
                    features_used=["api_builder"],
                    subscription_type="pro"
                )
                results = engagement.send_feature_announcement(
                    [test_user], args.name, args.description, 
                    args.release_notes or "", args.cta_link or ""
                )
            else:
                active_users = engagement.get_active_users()
                if not active_users:
                    print("⚠️ No active users found. Import users first or create sample data.")
                    return
                
                print(f"📊 Found {len(active_users)} active users")
                results = engagement.send_feature_announcement(
                    active_users, args.name, args.description,
                    args.release_notes or "", args.cta_link or ""
                )
            
            print(f"✅ Results: {results['sent']} sent, {results['failed']} failed, {results['skipped']} skipped")
        
        elif args.command == 'reengagement-campaign':
            print("💌 Sending re-engagement campaign")
            
            if args.test:
                # Send test email to BCC address
                print("🧪 Test mode: sending to configured BCC address only")
                from user_engagement import PlatformUser
                test_user = PlatformUser(
                    user_id="test_user_inactive",
                    email=engagement.bcc_email,
                    name="Test User",
                    signup_date="2025-06-01",
                    last_login="2025-07-15",
                    activity_level="inactive",
                    features_used=["ui_builder"],
                    subscription_type="free"
                )
                results = engagement.send_reengagement_campaign([test_user])
            else:
                inactive_users = engagement.get_inactive_users()
                if not inactive_users:
                    print("⚠️ No inactive users found. Import users first or create sample data.")
                    return
                
                print(f"📊 Found {len(inactive_users)} inactive users")
                results = engagement.send_reengagement_campaign(inactive_users)
            
            print(f"✅ Results: {results['sent']} sent, {results['failed']} failed, {results['skipped']} skipped")
        
        elif args.command == 'stats':
            print("📊 User Engagement Statistics")
            print("=" * 40)
            
            stats = engagement.get_engagement_stats()
            
            if 'user_activity' in stats:
                print("\n👥 User Activity Levels:")
                for activity, count in stats['user_activity'].items():
                    print(f"   {activity}: {count} users")
            
            if 'email_campaigns' in stats:
                print("\n📧 Email Campaign Stats (Last 30 Days):")
                for campaign, statuses in stats['email_campaigns'].items():
                    print(f"\n   {campaign.title()}:")
                    for status, count in statuses.items():
                        print(f"     {status}: {count}")
            
            print(f"\n🕐 Last Updated: {stats.get('last_updated', 'Unknown')}")
        
        elif args.command == 'create-sample':
            create_sample_users_file()
        
        elif args.command == 'list-users':
            print(f"👥 Listing users (filter: {args.activity})")
            print("=" * 50)
            
            if args.activity == 'active':
                users = engagement.get_active_users()
            elif args.activity == 'inactive':
                users = engagement.get_inactive_users()
            else:
                # Get all users
                users = engagement.get_active_users() + engagement.get_inactive_users()
            
            if not users:
                print("⚠️ No users found. Import users first or create sample data.")
                return
            
            for user in users:
                status_emoji = "🟢" if user.activity_level == "active" else "🟡" if user.activity_level == "moderately_active" else "🔴"
                print(f"{status_emoji} {user.name} ({user.email})")
                print(f"   Activity: {user.activity_level} | Last Login: {user.last_login}")
                print(f"   Features: {', '.join(user.features_used) if user.features_used else 'None'}")
                print(f"   Subscription: {user.subscription_type}")
                print()
        
        elif args.command == 'sync-buildly':
            print("🔄 Syncing users from Buildly API...")
            
            try:
                if args.new_only:
                    print(f"📅 Syncing new users from last {args.days} days")
                    stats = engagement.sync_new_users_from_buildly(
                        organization_uuid=args.organization,
                        days_back=args.days
                    )
                    print(f"✅ New user sync completed:")
                    print(f"   • Total new users in API: {stats['total_new_users']}")
                    print(f"   • Users added to database: {stats['added_users']}")
                    print(f"   • Users already existed: {stats['existing_users']}")
                    if stats['errors'] > 0:
                        print(f"   • Errors: {stats['errors']}")
                else:
                    print("📋 Syncing all users")
                    stats = engagement.sync_users_from_buildly(organization_uuid=args.organization)
                    print(f"✅ Full user sync completed:")
                    print(f"   • Total users in API: {stats['total_api_users']}")
                    print(f"   • New users added: {stats['new_users']}")
                    print(f"   • Existing users updated: {stats['updated_users']}")
                    if stats['errors'] > 0:
                        print(f"   • Errors: {stats['errors']}")
                        
            except Exception as e:
                print(f"❌ API sync failed: {e}")
                print("💡 Make sure BUILDLY_USERNAME and BUILDLY_PASSWORD environment variables are set")
        
        elif args.command == 'test-api':
            print("🔌 Testing Buildly API connection...")
            
            try:
                if engagement.setup_buildly_api():
                    current_user = engagement.api_client.get_current_user()
                    if current_user:
                        print(f"✅ API connection successful!")
                        print(f"   • Authenticated as: {current_user.email}")
                        print(f"   • User name: {current_user.full_name}")
                        print(f"   • Organization: {current_user.organization_uuid}")
                        print(f"   • User type: {current_user.user_type}")
                    else:
                        print("⚠️ API connection established but couldn't get user info")
                else:
                    print("❌ API connection failed")
                    
            except Exception as e:
                print(f"❌ API connection test failed: {e}")
                print("💡 Make sure BUILDLY_USERNAME and BUILDLY_PASSWORD environment variables are set")
        
        elif args.command == 'list-orgs':
            print("🏢 Fetching Buildly organizations...")
            
            try:
                orgs = engagement.get_buildly_organizations()
                if orgs:
                    print(f"Found {len(orgs)} organizations:")
                    print("=" * 60)
                    for org in orgs:
                        print(f"🏢 {org.get('name', 'Unknown')}")
                        print(f"   • UUID: {org.get('organization_uuid', 'N/A')}")
                        print(f"   • Type: {org.get('organization_type', 'N/A')}")
                        print(f"   • Created: {org.get('create_date', 'N/A')}")
                        if org.get('description'):
                            print(f"   • Description: {org['description'][:100]}...")
                        print()
                else:
                    print("⚠️ No organizations found")
                    
            except Exception as e:
                print(f"❌ Failed to get organizations: {e}")
                print("💡 Make sure BUILDLY_USERNAME and BUILDLY_PASSWORD environment variables are set")
        
        elif args.command == 'marketing-email':
            print(f"📧 Sending marketing email: {args.subject}")
            if args.test:
                print("🧪 Test mode: sending to configured BCC address only")
            
            try:
                results = engagement.send_marketing_email(
                    template_name=args.template,
                    subject=args.subject,
                    campaign_name=args.campaign_name,
                    test_mode=args.test
                )
                print(f"✅ Results: {results['sent']} sent, {results['failed']} failed, {results['skipped']} skipped")
                
            except Exception as e:
                print(f"❌ Failed to send marketing email: {e}")
        
        elif args.command == 'onboarding-help':
            print("🤝 Sending onboarding help emails to incomplete users...")
            if args.test:
                print("🧪 Test mode: sending to configured BCC address only")
            
            try:
                results = engagement.send_onboarding_help_email(test_mode=args.test)
                users_found = results.get('users_found', 0)
                print(f"👥 Found {users_found} users needing onboarding help")
                print(f"✅ Results: {results['sent']} sent, {results['failed']} failed, {results['skipped']} skipped")
                
            except Exception as e:
                print(f"❌ Failed to send onboarding help emails: {e}")
    
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()