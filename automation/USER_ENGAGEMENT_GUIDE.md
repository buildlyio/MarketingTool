# 🎯 User Engagement Automation - Complete Setup Guide

## Overview

The User Engagement System automates email campaigns for your Buildly platform users:

- **Active Users**: Feature announcements and release notes  
- **Inactive Users**: Re-engagement campaigns with help offers and tutorials
- **Automated Scheduling**: Integrated with your existing daily automation
- **Smart Targeting**: Activity-based user segmentation

## 🚀 Quick Setup

### 1. Test the System
```bash
# Test all components
.venv/bin/python automation/test_user_engagement.py
```

### 2. Create Sample Data (Optional)
```bash
# Generate sample users file for testing
.venv/bin/python automation/user_engagement_cli.py create-sample
```

### 3. Import Your Users
```bash
# Import from JSON file
.venv/bin/python automation/user_engagement_cli.py import-users --file users.json

# Import from CSV file  
.venv/bin/python automation/user_engagement_cli.py import-users --file users.csv
```

## 📊 User Data Format

### JSON Format
```json
[
  {
    "user_id": "unique_id",
    "email": "user@example.com",
    "name": "User Name",
    "signup_date": "2025-08-15",
    "last_login": "2025-09-29", 
    "features_used": ["api_builder", "workflow_designer"],
    "subscription_type": "pro"
  }
]
```

### CSV Format
```csv
user_id,email,name,signup_date,last_login,features_used,subscription_type
user_001,john@example.com,John Doe,2025-08-15,2025-09-29,"[""api_builder"",""workflow_designer""]",pro
user_002,jane@example.com,Jane Smith,2025-07-01,2025-08-15,"[""ui_builder""]",free
```

## 📧 Campaign Management

### Feature Announcements (Active Users)
```bash
# Send to all active users
.venv/bin/python automation/user_engagement_cli.py feature-announcement \
  --name "Smart Workflows" \
  --description "Automate your development process with visual workflows" \
  --release-notes "• Drag-and-drop interface • 50+ pre-built templates • Real-time collaboration" \
  --cta-link "https://buildly.io/features/workflows"

# Test mode (sends to BCC address only)
.venv/bin/python automation/user_engagement_cli.py feature-announcement \
  --name "Test Feature" \
  --description "Test description" \
  --test
```

### Re-engagement Campaigns (Inactive Users)
```bash
# Send to all inactive users
.venv/bin/python automation/user_engagement_cli.py reengagement-campaign

# Test mode (sends to BCC address only)  
.venv/bin/python automation/user_engagement_cli.py reengagement-campaign --test
```

### View Statistics
```bash
# Get engagement stats and user counts
.venv/bin/python automation/user_engagement_cli.py stats

# List users by activity
.venv/bin/python automation/user_engagement_cli.py list-users --activity active
.venv/bin/python automation/user_engagement_cli.py list-users --activity inactive
```

## 🔄 Automated Integration

### Daily Automation Schedule
The system integrates with your existing `automation/main.py`:

- **Tuesday**: Check for pending feature announcements (manual trigger)
- **Friday**: Automatic re-engagement campaign (max 20 emails/week)
- **Daily**: Lead generation and status reports continue as normal

### Configuration
User engagement uses your existing MailerSend configuration from `.env`:

```bash
```bash
# Required environment variables (.env file)
SMTP_SERVER=smtp.mailersend.net
SMTP_USER=YOUR_MAILERSEND_USERNAME
SMTP_PASSWORD=YOUR_MAILERSEND_PASSWORD
BCC_EMAIL=greg@buildly.io

# User engagement settings (optional)
ACTIVE_THRESHOLD_DAYS=7     # Users active within 7 days
INACTIVE_THRESHOLD_DAYS=30  # Users inactive after 30 days
```

## 📈 User Activity Classification

### Activity Levels
- **Active**: Logged in within last 7 days
- **Moderately Active**: Logged in within last 30 days  
- **Inactive**: No login for 30+ days

### Email Frequency Limits
- **Feature Announcements**: Max 1 per week per user
- **Re-engagement**: Max 1 per 2 weeks per user
- **Total Weekly Limit**: 20 re-engagement emails (Fridays only)

## 🎨 Email Templates

### Feature Announcements Include:
- Personalized greeting with user name
- Feature highlight with benefits
- Release notes and what's new
- Call-to-action button to try feature
- Help resources (docs, tutorials, support)
- Professional Buildly branding

### Re-engagement Emails Include:
- Personal message acknowledging their absence
- Offer for free 1:1 onboarding session
- Tutorials and quick start guides
- Community and support resources
- Special welcome-back offers
- Personalized feature suggestions based on past usage

## 📊 Tracking & Analytics

### Database Storage
User data is stored in `automation/user_engagement.db`:
- User profiles and activity levels
- Email campaign history
- Engagement tracking and statistics

### Available Reports
- User count by activity level
- Email campaign success rates
- Engagement history per user
- Feature adoption tracking

## 🔧 Integrating with Your Platform

### Data Export from Your Platform
Create a script to export user data from your Buildly platform database:

```python
# Example: Export users from Django
def export_users_for_engagement():
    users = []
    for user in User.objects.all():
        users.append({
            'user_id': str(user.id),
            'email': user.email,
            'name': f"{user.first_name} {user.last_name}",
            'signup_date': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'features_used': get_user_features(user),  # Your custom logic
            'subscription_type': user.subscription.plan_type
        })
    
    with open('users_export.json', 'w') as f:
        json.dump(users, f)
```

### Automated Import
Set up a daily task to import updated user data:

```bash
# Add to your existing cron job
0 8 * * * /path/to/export_and_import_users.sh
```

## 🎯 Best Practices

### Timing Recommendations
- **Feature Announcements**: Send within 24 hours of feature release
- **Major Releases**: Tuesday/Wednesday for maximum visibility  
- **Re-engagement**: Friday afternoons work well
- **Avoid Mondays/Weekends**: Lower engagement rates

### Content Guidelines
- Keep feature descriptions concise and benefit-focused
- Include visual elements (screenshots, GIFs) when possible
- Always provide clear next steps and help resources
- Personalize based on user's subscription level and usage history

### Compliance
- All emails include unsubscribe links
- Respects user preferences and opt-outs
- GDPR compliant with data handling
- Automatic bounce and complaint handling

## 🚨 Troubleshooting

### Common Issues

**"No users found"**
```bash
# Import users first
.venv/bin/python automation/user_engagement_cli.py import-users --file users.json
```

**"Email sending failed"**
- Check MailerSend credentials in `.env`
- Verify SMTP settings are correct
- Test basic email sending: `.venv/bin/python automation/test_mailersend.py`

**"Database errors"**
- Database is created automatically on first run
- Check file permissions in `automation/` directory
- Delete `automation/user_engagement.db` to reset if needed

### Testing Mode
Always test campaigns before sending to real users:
```bash
# Test feature announcements
.venv/bin/python automation/user_engagement_cli.py feature-announcement --name "Test" --description "Test" --test

# Test re-engagement 
.venv/bin/python automation/user_engagement_cli.py reengagement-campaign --test
```

## 📞 Support

The user engagement system integrates seamlessly with your existing marketing automation. All emails are BCC'd to `greg@buildly.io` for monitoring, and detailed logs are available in the engagement database.

For questions or custom modifications, the system is designed to be easily extensible with additional campaign types, user segments, and email templates.

---

**Your complete user engagement automation is ready! 🚀**

Start by testing the system, then import your users and begin targeted campaigns to increase platform engagement and reduce churn.