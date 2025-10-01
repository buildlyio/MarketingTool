#!/usr/bin/env python3
"""
Main automation script for Buildly lead generation and outreach
Orchestrates lead sourcing, email sending, and status reporting
"""

import sys
import os
import logging
from datetime import datetime

# Add automation directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lead_sourcing import LeadSourcing
from email_sender import EmailSender
from status_report import StatusReporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation/automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main automation workflow"""
    logger.info("=== Starting Buildly Daily Automation ===")
    
    try:
        # Step 1: Source new leads
        logger.info("Step 1: Sourcing leads...")
        sourcing = LeadSourcing()
        leads = sourcing.find_leads()
        new_leads_count = sourcing.save_leads()
        logger.info(f"Found {len(leads)} total leads, {new_leads_count} new ones")
        
        # Step 2: Send outreach emails
        if new_leads_count > 0:
            logger.info("Step 2: Sending outreach emails...")
            sender = EmailSender()
            
            # Load leads and filter for new ones
            import json
            with open('automation/leads.json', 'r') as f:
                all_leads = json.load(f)
            
            new_leads = [lead for lead in all_leads if lead.get('status') == 'new']
            sent_count, failed_count = sender.send_bulk_emails(new_leads, max_per_day=50)
            
            # Update lead status for sent emails
            for lead in all_leads:
                if lead.get('status') == 'new' and lead['email'] in [l['email'] for l in new_leads[:sent_count]]:
                    lead['status'] = 'contacted'
                    lead['contacted_date'] = datetime.now().isoformat()
            
            # Save updated leads
            with open('automation/leads.json', 'w') as f:
                json.dump(all_leads, f, indent=2)
            
            logger.info(f"Sent {sent_count} emails, {failed_count} failed")
        else:
            logger.info("No new leads to contact today")
        
        # Step 3: User engagement campaigns (runs on specific days)
        logger.info("Step 3: Checking user engagement campaigns...")
        try:
            from user_engagement import UserEngagementSystem
            engagement = UserEngagementSystem()
            
            # Check if it's time for user engagement (e.g., Tuesdays and Fridays)
            current_day = datetime.now().weekday()  # 0=Monday, 1=Tuesday, etc.
            
            if current_day == 1:  # Tuesday - Feature announcements for active users
                logger.info("Tuesday: Checking for pending feature announcements...")
                # Note: Feature announcements should be triggered manually via CLI
                # This is just a placeholder for future automated feature releases
                
            elif current_day == 4:  # Friday - Sync users and run re-engagement campaigns
                logger.info("Friday: Syncing users from Buildly API...")
                
                # First, sync new users from Buildly API
                try:
                    sync_stats = engagement.sync_new_users_from_buildly(days_back=7)
                    logger.info(f"User sync completed: {sync_stats['added_users']} new users, {sync_stats['existing_users']} already existed")
                except Exception as e:
                    logger.warning(f"API user sync failed: {e}")
                
                # Then run re-engagement campaigns
                logger.info("Running re-engagement campaigns...")
                inactive_users = engagement.get_inactive_users()
                if len(inactive_users) > 0:
                    # Limit to 20 re-engagement emails per week to avoid spam
                    limited_users = inactive_users[:20]
                    results = engagement.send_reengagement_campaign(limited_users)
                    logger.info(f"Re-engagement sent: {results['sent']} emails, {results['skipped']} skipped")
                else:
                    logger.info("No inactive users found for re-engagement")
            
        except ImportError:
            logger.warning("User engagement system not available")
        except Exception as e:
            logger.error(f"User engagement error: {e}")
        
        # Step 4: Send status report
        logger.info("Step 4: Sending status report...")
        reporter = StatusReporter()
        report_sent = reporter.send_status_report()
        
        if report_sent:
            logger.info("Status report sent successfully")
        else:
            logger.error("Failed to send status report")
        
        logger.info("=== Daily automation completed successfully ===")
        
    except Exception as e:
        logger.error(f"Automation failed: {e}")
        raise

if __name__ == "__main__":
    main()
