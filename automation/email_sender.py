#!/usr/bin/env python3
"""
Email Sender Module for Buildly Automation
Sends personalized HTML emails and integrates with HubSpot CRM
"""

import json
import smtplib
import os
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

        # Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        # MailerSend SMTP configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.mailersend.net')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('MAILERSEND_SMTP_USERNAME', os.getenv('SMTP_USER'))
        self.smtp_password = os.getenv('MAILERSEND_SMTP_PASSWORD', os.getenv('SMTP_PASSWORD'))
        
        # Email addresses
        self.from_email = os.getenv('EMAIL_HOST_USER', self.smtp_user)
        self.bcc_email = os.getenv('BCC_EMAIL', 'greg@buildly.io')
        
        # HubSpot credentials
        self.hubspot_app_id = os.getenv('HUBSPOT_APP_ID')
        self.hubspot_client_id = os.getenv('HUBSPOT_CLIENT_ID')
        self.hubspot_client_secret = os.getenv('HUBSPOT_CLIENT_SECRET')
        
        self.opt_out_file = 'automation/opt_out.json'
        self.outreach_log_file = 'automation/outreach_log.json'
        
        self.opt_outs = self.load_opt_outs()
        
    def load_opt_outs(self):
        """Load opt-out list from JSON file"""
        try:
            with open(self.opt_out_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_opt_outs(self):
        """Save opt-out list to JSON file"""
        with open(self.opt_out_file, 'w') as f:
            json.dump(self.opt_outs, f, indent=2)
    
    def log_outreach(self, email, status, details=None):
        """Log outreach attempt"""
        try:
            try:
                with open(self.outreach_log_file, 'r') as f:
                    log = json.load(f)
            except FileNotFoundError:
                log = []
            
            log_entry = {
                'email': email,
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'details': details or {}
            }
            
            log.append(log_entry)
            
            with open(self.outreach_log_file, 'w') as f:
                json.dump(log, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error logging outreach: {e}")
    
    def add_to_hubspot(self, lead):
        """Add lead to HubSpot CRM"""
        try:
            # HubSpot Contacts API endpoint
            url = "https://api.hubapi.com/crm/v3/objects/contacts"
            
            # Prepare contact data
            contact_data = {
                "properties": {
                    "email": lead['email'],
                    "firstname": lead.get('firstname', ''),
                    "lastname": lead.get('lastname', ''),
                    "company": lead.get('company', ''),
                    "website": lead.get('source_url', ''),
                    "hs_lead_status": "NEW",
                    "source": f"Automation - {lead.get('source', 'Unknown')}",
                    "notes_last_contacted": f"Automated outreach on {datetime.now().strftime('%Y-%m-%d')}",
                    "buildly_keyword_matched": lead.get('keyword_matched', ''),
                    "buildly_post_content": lead.get('post_content', '')[:1000]  # HubSpot field length limit
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.get_hubspot_access_token()}"
            }
            
            response = requests.post(url, json=contact_data, headers=headers)
            
            if response.status_code == 201:
                logger.info(f"Successfully added {lead['email']} to HubSpot")
                return True
            elif response.status_code == 409:
                # Contact already exists, update instead
                logger.info(f"Contact {lead['email']} already exists in HubSpot, updating...")
                return self.update_hubspot_contact(lead)
            else:
                logger.error(f"Failed to add to HubSpot: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding to HubSpot: {e}")
            return False
    
    def get_hubspot_access_token(self):
        """Get HubSpot access token (simplified - in production, implement proper OAuth flow)"""
        # For now, return a placeholder - you'll need to implement OAuth flow
        # or use a private app access token from HubSpot
        return "YOUR_HUBSPOT_ACCESS_TOKEN"
    
    def update_hubspot_contact(self, lead):
        """Update existing HubSpot contact"""
        try:
            # Search for contact by email first
            search_url = f"https://api.hubapi.com/crm/v3/objects/contacts/search"
            search_data = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": lead['email']
                    }]
                }]
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.get_hubspot_access_token()}"
            }
            
            search_response = requests.post(search_url, json=search_data, headers=headers)
            
            if search_response.status_code == 200:
                results = search_response.json().get('results', [])
                if results:
                    contact_id = results[0]['id']
                    
                    # Update the contact
                    update_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
                    update_data = {
                        "properties": {
                            "notes_last_contacted": f"Automated outreach on {datetime.now().strftime('%Y-%m-%d')}",
                            "buildly_last_campaign": "Daily Automation"
                        }
                    }
                    
                    update_response = requests.patch(update_url, json=update_data, headers=headers)
                    return update_response.status_code == 200
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating HubSpot contact: {e}")
            return False
    
    def generate_personalized_email(self, lead):
        """Generate personalized HTML email content"""
        # Extract key info for personalization
        keyword = lead.get('keyword_matched', 'development help')
        source = lead.get('source', 'a startup community')
        post_snippet = lead.get('post_content', '')[:200] + "..." if lead.get('post_content') else ""
        
        # Generate personalized greeting
        if 'CTO' in post_snippet or 'technical co-founder' in post_snippet:
            pain_point = "finding technical leadership"
            solution = "our experienced technical team and AI-powered development platform"
        elif 'project manager' in keyword.lower():
            pain_point = "implementing AI without coding"
            solution = "our no-code AI platform and expert guidance"
        else:
            pain_point = "software development challenges"
            solution = "our comprehensive development platform and 30-day free trial"
        
        subject = f"Saw your post on {source} - Buildly can help with {pain_point}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Buildly Can Help</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
                .content {{ padding: 40px 30px; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #f8f9fa; padding: 30px; text-align: center; font-size: 14px; color: #666; }}
                .highlight {{ background-color: #e3f2fd; padding: 15px; border-left: 4px solid #2196f3; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Buildly Labs</h1>
                    <p>AI-Powered Software Development Platform</p>
                </div>
                
                <div class="content">
                    <p>Hi there,</p>
                    
                    <p>I noticed your post on {source} about {pain_point}. I thought you might be interested in how Buildly can help.</p>
                    
                    {f'<div class="highlight"><strong>Your post:</strong> "{post_snippet}"</div>' if post_snippet else ''}
                    
                    <p><strong>Here's how Buildly Labs can solve your challenges:</strong></p>
                    <ul>
                        <li>🚀 <strong>AI-Powered Development:</strong> Build software 10x faster with our intelligent platform</li>
                        <li>🛠️ <strong>No-Code/Low-Code Solutions:</strong> Perfect for project managers who want AI without coding</li>
                        <li>👥 <strong>Expert Technical Team:</strong> Get access to experienced developers and technical guidance</li>
                        <li>⚡ <strong>Rapid Prototyping:</strong> Turn your ideas into working software in days, not months</li>
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://buildly.io/labs" class="cta-button">Explore Buildly Labs</a>
                    </div>
                    
                    <div class="highlight">
                        <strong>🎁 Special Offer:</strong> Get a <strong>30-day free trial</strong> of our platform plus a free consultation with our technical team to discuss your specific needs.
                    </div>
                    
                    <p>Thousands of startups and project managers have already accelerated their development with Buildly. We'd love to show you how we can help with {pain_point}.</p>
                    
                    <p>Interested in learning more? Simply reply to this email or visit our Labs page to get started.</p>
                    
                    <p>Best regards,<br>
                    The Buildly Labs Team</p>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    
                    <p style="font-size: 12px; color: #888;">
                        P.S. We're always looking to connect with innovative teams like yours. Feel free to reach out even if you just want to chat about your technical challenges.
                    </p>
                </div>
                
                <div class="footer">
                    <p><strong>Buildly Labs</strong> | AI-Powered Software Development</p>
                    <p>
                        <a href="https://buildly.io/labs">Visit Labs</a> | 
                        <a href="https://buildly.io/free-trial">30-Day Free Trial</a> | 
                        <a href="https://buildly.io/opt-out?email={lead['email']}">Unsubscribe</a>
                    </p>
                    <p style="font-size: 11px; margin-top: 20px;">
                        This email was sent because we found your post about software development needs. 
                        If you'd prefer not to receive these emails, <a href="https://buildly.io/opt-out?email={lead['email']}">click here to opt out</a>.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return subject, html_content
    
    def send_email(self, lead):
        """Send personalized email to lead"""
        if lead['email'] in self.opt_outs:
            logger.info(f"Skipping {lead['email']} - opted out")
            self.log_outreach(lead['email'], 'skipped', {'reason': 'opted_out'})
            return False
        
        # Validate required credentials
        if not self.smtp_user or not self.smtp_password:
            logger.error("MailerSend SMTP credentials not configured")
            return False
        
        try:
            subject, html_content = self.generate_personalized_email(lead)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email or 'noreply@buildly.io'
            msg['To'] = lead['email']
            
            # Always BCC Greg on outreach emails
            if self.bcc_email:
                msg['Bcc'] = self.bcc_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email via MailerSend SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            
            # Send to all recipients (including BCC)
            recipients = [lead['email']]
            if self.bcc_email:
                recipients.append(self.bcc_email)
            
            server.send_message(msg, to_addrs=recipients)
            server.quit()
            
            logger.info(f"Email sent successfully to {lead['email']} (BCC: {self.bcc_email})")
            
            # Add to HubSpot
            hubspot_success = self.add_to_hubspot(lead)
            
            # Log outreach
            self.log_outreach(lead['email'], 'sent', {
                'subject': subject,
                'hubspot_added': hubspot_success,
                'source': lead.get('source', 'Unknown')
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {lead['email']}: {e}")
            self.log_outreach(lead['email'], 'failed', {'error': str(e)})
            return False
    
    def send_bulk_emails(self, leads, max_per_day=50):
        """Send emails to multiple leads with daily limit"""
        sent_count = 0
        failed_count = 0
        
        for lead in leads[:max_per_day]:
            if self.send_email(lead):
                sent_count += 1
            else:
                failed_count += 1
            
            # Add delay between emails to avoid being flagged as spam
            import time
            time.sleep(2)
        
        logger.info(f"Bulk email complete: {sent_count} sent, {failed_count} failed")
        return sent_count, failed_count

if __name__ == "__main__":
    # Load leads and send emails
    try:
        with open('automation/leads.json', 'r') as f:
            leads = json.load(f)
        
        # Filter for new leads only
        new_leads = [lead for lead in leads if lead.get('status') == 'new']
        
        sender = EmailSender()
        sent, failed = sender.send_bulk_emails(new_leads)
        
        print(f"Email campaign complete: {sent} sent, {failed} failed")
        
    except FileNotFoundError:
        print("No leads file found. Run lead_sourcing.py first.")
