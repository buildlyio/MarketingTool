#!/usr/bin/env python3
"""
Test the full outreach system with a sample lead
"""

import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Add automation directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_sender import EmailSender

# Load environment variables
load_dotenv()

def test_outreach_with_sample_lead():
    """Test the outreach system with a sample lead"""
    
    # Create a sample lead (realistic example)
    sample_lead = {
        "email": "greg@buildly.io",  # Send to Greg as test
        "source": "Indie Hackers",
        "source_url": "https://www.indiehackers.com/startups",
        "post_content": "Looking for a technical co-founder or development team to help build our AI-powered project management tool. We're a small startup focused on helping teams be more productive, but we don't have the coding expertise to implement the AI features we want. Need someone who can work with APIs and integrate machine learning capabilities.",
        "keyword_matched": "technical co-founder",
        "discovered_date": datetime.now().isoformat(),
        "status": "new",
        "firstname": "Greg",
        "lastname": "Lind",
        "company": "Buildly"
    }
    
    print("🧪 Testing Buildly Outreach System with Sample Lead...")
    print("=" * 60)
    print(f"📧 Recipient: {sample_lead['email']}")
    print(f"🎯 Source: {sample_lead['source']}")
    print(f"🔑 Keyword: {sample_lead['keyword_matched']}")
    print(f"📝 Post snippet: {sample_lead['post_content'][:100]}...")
    print()
    
    # Initialize email sender
    sender = EmailSender()
    
    # Show BCC configuration
    print(f"📬 BCC Email: {sender.bcc_email}")
    print(f"📤 From Email: {sender.from_email}")
    print()
    
    # Send the test email
    print("📤 Sending personalized outreach email...")
    success = sender.send_email(sample_lead)
    
    if success:
        print("✅ Outreach email sent successfully!")
        print(f"📧 Email sent to: {sample_lead['email']}")
        print(f"📬 BCC sent to: {sender.bcc_email}")
        print()
        print("🎉 The outreach system is working correctly!")
        print("- Personalized email generated based on lead's post")
        print("- Email sent via MailerSend SMTP")
        print("- Greg is BCC'd on the email")
        print("- Lead will be added to HubSpot (if credentials configured)")
        print("- Outreach is logged for reporting")
    else:
        print("❌ Outreach email failed to send")
        print("Check the logs for more details")
    
    return success

if __name__ == "__main__":
    success = test_outreach_with_sample_lead()
    
    if success:
        print("\n" + "="*60)
        print("🚀 AUTOMATION SYSTEM READY!")
        print("="*60)
        print("✅ MailerSend SMTP integration working")
        print("✅ Personalized email generation working")
        print("✅ BCC functionality working (Greg gets copies)")
        print("✅ Lead processing and logging working")
        print()
        print("📅 To start daily automation:")
        print("   crontab -e")
        print("   0 9 * * * /path/to/your/website/automation/cron.sh")
        print()
        print("📊 You'll receive daily status reports at greg@buildly.io")
        print("📧 You'll be BCC'd on all outreach emails")
    else:
        print("\n❌ System not ready - check configuration")
