#!/usr/bin/env python3
"""
Test script for Buildly API integration
"""

import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_connection():
    """Test basic API connection and authentication"""
    logger.info("=== Testing Buildly API Integration ===")
    
    try:
        from user_engagement import UserEngagementSystem
        
        # Initialize system
        engagement = UserEngagementSystem()
        
        # Test 1: Setup API client
        logger.info("Test 1: Setting up API client...")
        if engagement.setup_buildly_api():
            logger.info("✅ API client setup successful")
        else:
            logger.error("❌ API client setup failed")
            return False
        
        # Test 2: Get current user
        logger.info("Test 2: Getting current user info...")
        current_user = engagement.api_client.get_current_user()
        if current_user:
            logger.info(f"✅ Current user: {current_user.email} ({current_user.full_name})")
            logger.info(f"   Organization: {current_user.organization_uuid}")
            logger.info(f"   User type: {current_user.user_type}")
        else:
            logger.error("❌ Failed to get current user")
            return False
        
        # Test 3: Get organizations
        logger.info("Test 3: Getting organizations...")
        orgs = engagement.get_buildly_organizations()
        logger.info(f"✅ Found {len(orgs)} organizations")
        for org in orgs[:3]:  # Show first 3
            logger.info(f"   • {org.get('name', 'Unknown')} (UUID: {org.get('organization_uuid', 'N/A')})")
        
        # Test 4: Get users (first page only)
        logger.info("Test 4: Getting users (first page)...")
        users_result = engagement.api_client.get_users(page=1)
        users = users_result.get('users', [])
        total_count = users_result.get('count', 0)
        logger.info(f"✅ Found {len(users)} users on first page ({total_count} total)")
        
        # Show first few users
        for i, user in enumerate(users[:3]):
            logger.info(f"   User {i+1}: {user.email} ({user.full_name})")
            logger.info(f"            Active: {user.is_active}, Signup: {user.signup_date}")
        
        # Test 5: Sync new users (dry run - just count what would be synced)
        logger.info("Test 5: Testing user sync (checking for new users)...")
        try:
            stats = engagement.sync_new_users_from_buildly(days_back=30)
            logger.info(f"✅ Sync test completed:")
            logger.info(f"   • Total new users found: {stats['total_new_users']}")
            logger.info(f"   • Users added to database: {stats['added_users']}")
            logger.info(f"   • Users already existed: {stats['existing_users']}")
            logger.info(f"   • Errors: {stats['errors']}")
        except Exception as e:
            logger.error(f"❌ User sync test failed: {e}")
            return False
        
        logger.info("🎉 All API integration tests passed!")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure all required modules are available")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def test_user_engagement_workflow():
    """Test the complete user engagement workflow with API data"""
    logger.info("=== Testing User Engagement Workflow ===")
    
    try:
        from user_engagement import UserEngagementSystem
        
        engagement = UserEngagementSystem()
        
        # Setup API
        if not engagement.setup_buildly_api():
            logger.error("❌ Could not setup API client")
            return False
        
        # Get engagement stats before sync
        stats_before = engagement.get_engagement_stats()
        logger.info(f"Stats before sync: {stats_before.get('user_activity', {})}")
        
        # Sync users
        logger.info("Syncing users from Buildly API...")
        sync_stats = engagement.sync_new_users_from_buildly(days_back=30)
        logger.info(f"Sync results: {sync_stats}")
        
        # Get engagement stats after sync
        stats_after = engagement.get_engagement_stats()
        logger.info(f"Stats after sync: {stats_after.get('user_activity', {})}")
        
        # Show active vs inactive users
        active_users = engagement.get_active_users()
        inactive_users = engagement.get_inactive_users()
        
        logger.info(f"📊 User segmentation:")
        logger.info(f"   • Active users: {len(active_users)}")
        logger.info(f"   • Inactive users: {len(inactive_users)}")
        
        # Test feature announcement (dry run)
        if active_users:
            logger.info("Testing feature announcement template generation...")
            sample_user = active_users[0]
            
            # Generate template but don't send
            template = engagement._generate_feature_announcement_template(
                feature_name="API Integration Test",
                description="Testing our new API integration capabilities",
                release_notes="This is a test of the automated user engagement system.",
                cta_link="https://buildly.io"
            )
            
            if template and len(template) > 100:
                logger.info("✅ Feature announcement template generated successfully")
            else:
                logger.error("❌ Feature announcement template generation failed")
        
        # Test re-engagement template
        if inactive_users:
            logger.info("Testing re-engagement template generation...")
            sample_user = inactive_users[0]
            
            template = engagement._generate_reengagement_template(sample_user)
            
            if template and len(template) > 100:
                logger.info("✅ Re-engagement template generated successfully")
            else:
                logger.error("❌ Re-engagement template generation failed")
        
        logger.info("🎉 User engagement workflow test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Workflow test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting Buildly API integration tests...")
    
    # Check environment variables
    if not os.getenv('BUILDLY_USERNAME'):
        logger.error("❌ BUILDLY_USERNAME environment variable not set")
        logger.info("Set it with: export BUILDLY_USERNAME='your-username'")
        return False
    
    if not os.getenv('BUILDLY_PASSWORD'):
        logger.error("❌ BUILDLY_PASSWORD environment variable not set")
        logger.info("Set it with: export BUILDLY_PASSWORD='your-password'")
        return False
    
    logger.info(f"✅ Using Buildly username: {os.getenv('BUILDLY_USERNAME')}")
    
    # Run tests
    success = True
    
    success &= test_api_connection()
    print()  # Add space between tests
    success &= test_user_engagement_workflow()
    
    if success:
        logger.info("🎉 All tests passed! Buildly API integration is working correctly.")
        return True
    else:
        logger.error("❌ Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)