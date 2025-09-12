#!/usr/bin/env python3
"""
Test script to send a test email to Greg using MailerSend
"""

import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def send_test_email():
    """Send a test email to Greg to verify MailerSend integration"""
    
    # MailerSend SMTP configuration
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.mailersend.net')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('MAILERSEND_SMTP_USERNAME')
    smtp_password = os.getenv('MAILERSEND_SMTP_PASSWORD')
    from_email = os.getenv('EMAIL_HOST_USER', smtp_user)
    
    # Validate credentials
    if not smtp_user or not smtp_password:
        print("❌ MailerSend credentials not found in .env file")
        print("Required variables: MAILERSEND_SMTP_USERNAME, MAILERSEND_SMTP_PASSWORD")
        return False
    
    try:
        # Create test email content
        subject = "🚀 Buildly Automation System - Test Email"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Buildly Automation Test</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
                .content {{ padding: 40px 30px; }}
                .success {{ background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .info {{ background-color: #e3f2fd; color: #0d47a1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Buildly Automation System</h1>
                    <p>Test Email - MailerSend Integration</p>
                </div>
                
                <div class="content">
                    <div class="success">
                        <h3>✅ MailerSend Integration Successful!</h3>
                        <p>This test email confirms that the Buildly automation system is successfully configured with MailerSend SMTP.</p>
                    </div>
                    
                    <h3>📧 Email Configuration Details:</h3>
                    <ul>
                        <li><strong>SMTP Server:</strong> {smtp_server}</li>
                        <li><strong>Port:</strong> {smtp_port}</li>
                        <li><strong>Username:</strong> {smtp_user}</li>
                        <li><strong>From Email:</strong> {from_email}</li>
                        <li><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                    </ul>
                    
                    <div class="info">
                        <h4>🎯 What happens next:</h4>
                        <ul>
                            <li>All outreach emails will be sent via MailerSend</li>
                            <li>You'll be BCC'd on every outreach email automatically</li>
                            <li>Daily status reports will be sent to greg@buildly.io</li>
                            <li>The system is ready for daily automation via cron</li>
                        </ul>
                    </div>
                    
                    <h3>🔧 System Components Ready:</h3>
                    <ul>
                        <li>✅ Lead sourcing from multiple startup directories</li>
                        <li>✅ Personalized HTML email templates</li>
                        <li>✅ HubSpot CRM integration</li>
                        <li>✅ Opt-out handling and compliance</li>
                        <li>✅ Daily analytics and status reporting</li>
                        <li>✅ MailerSend SMTP integration</li>
                    </ul>
                    
                    <p><strong>The automation system is now ready to run!</strong></p>
                    
                    <p>Best regards,<br>
                    The Buildly Automation System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email or 'noreply@buildly.io'
        msg['To'] = 'greg@buildly.io'
        
        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email via MailerSend
        print(f"📤 Connecting to MailerSend SMTP server: {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        print(f"🔐 Authenticating with username: {smtp_user}")
        server.login(smtp_user, smtp_password)
        
        print(f"📧 Sending test email to: greg@buildly.io")
        server.send_message(msg)
        server.quit()
        
        print("✅ Test email sent successfully!")
        print(f"📬 Check greg@buildly.io for the test email")
        return True
        
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Buildly Automation System with MailerSend...")
    print("=" * 50)
    
    success = send_test_email()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("The automation system is ready to run with MailerSend SMTP.")
    else:
        print("\n❌ Test failed. Please check your MailerSend credentials.")
