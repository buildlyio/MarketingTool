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
        
        # Step 3: Send status report
        logger.info("Step 3: Sending status report...")
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
