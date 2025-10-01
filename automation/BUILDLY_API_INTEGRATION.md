# Buildly API Integration Setup

## Overview

The user engagement system now includes full integration with the Buildly Labs API to automatically sync user data and activity. This allows the system to:

1. **Automatically import new users** from the Buildly platform
2. **Update user activity data** based on login patterns
3. **Send targeted campaigns** to active and inactive platform users
4. **Track user engagement** across the entire platform

## Environment Setup

### 1. API Credentials

Set your Buildly Labs API credentials as environment variables:

```bash
export BUILDLY_USERNAME="your-buildly-username"
export BUILDLY_PASSWORD="your-buildly-password"
```

### 2. Test API Connection

Before using the system, test your API connection:

```bash
python automation/test_api_integration.py
```

This will verify:
- Authentication with Buildly API
- Access to user data
- Organization information
- User sync capabilities

## CLI Commands

### Sync Users from Buildly API

**Sync all users:**
```bash
python automation/user_engagement_cli.py sync-buildly
```

**Sync only new users from last 7 days:**
```bash
python automation/user_engagement_cli.py sync-buildly --new-only
```

**Sync new users from specific time period:**
```bash
python automation/user_engagement_cli.py sync-buildly --new-only --days 30
```

**Sync users from specific organization:**
```bash
python automation/user_engagement_cli.py sync-buildly --organization "org-uuid-here"
```

### Test and Manage API Integration

**Test API connection:**
```bash
python automation/user_engagement_cli.py test-api
```

**List available organizations:**
```bash
python automation/user_engagement_cli.py list-orgs
```

### Regular User Engagement Commands

All existing commands still work:

```bash
# Send feature announcements to active users
python automation/user_engagement_cli.py feature-announcement \
  --name "New API Builder" \
  --description "Build APIs faster with our new visual interface" \
  --cta-link "https://labs.buildly.io/api-builder"

# Send re-engagement emails to inactive users
python automation/user_engagement_cli.py reengagement-campaign

# View user statistics
python automation/user_engagement_cli.py stats

# List users by activity level
python automation/user_engagement_cli.py list-users --activity active
python automation/user_engagement_cli.py list-users --activity inactive
```

## Automated Workflow

The system now automatically syncs users and sends campaigns:

### Tuesday: Feature Announcements
- Manual trigger via CLI for active users
- Target users who have logged in recently
- Showcase new features and product updates

### Friday: Re-engagement Campaigns  
- **Automatic user sync** from Buildly API (last 7 days)
- **Automatic re-engagement emails** to inactive users (max 20 per week)
- Thank users for signing up and offer help/tutorials

## User Data Mapping

The system maps Buildly API user data to local engagement tracking:

| Buildly Field | Local Field | Purpose |
|---------------|-------------|---------|
| `core_user_uuid` | `external_id` | Unique user identifier |
| `email` | `email` | Primary contact method |
| `first_name` + `last_name` | `name` | Personalization |
| `create_date` | `signup_date` | User lifecycle tracking |
| `edit_date` | `last_login` | Activity level calculation |
| `organization.organization_uuid` | `organization` | User segmentation |
| `user_type` | `user_type` | Campaign targeting |
| `is_active` | Activity calculation | User status |

## Activity Level Calculation

Users are automatically categorized based on their last login:

- **Active**: Logged in within last 7 days
- **Moderately Active**: Logged in within last 30 days  
- **Inactive**: No login in 30+ days

## Database Schema

The system maintains a local SQLite database for engagement tracking:

### Users Table
- `user_id` - Internal unique ID
- `email` - User email (unique)
- `name` - Full name for personalization
- `signup_date` - When user joined platform
- `last_login` - Most recent activity
- `activity_level` - Calculated engagement level
- `features_used` - JSON array of used features
- `subscription_type` - User's subscription level
- `last_feature_email` - Last feature announcement sent
- `last_reengagement_email` - Last re-engagement email sent

### Engagement History Table
- `user_id` - Reference to user
- `campaign_type` - Type of email sent
- `email_subject` - Subject line used
- `sent_at` - Timestamp of send
- `status` - Delivery status

## Security Notes

1. **API Credentials**: Store securely as environment variables
2. **Rate Limiting**: System respects API rate limits
3. **Email Limits**: Maximum 20 re-engagement emails per week
4. **Data Privacy**: Local database for engagement tracking only
5. **Error Handling**: Graceful fallback if API unavailable

## Troubleshooting

### API Connection Issues

```bash
# Test your connection
python automation/user_engagement_cli.py test-api

# Check credentials are set
echo $BUILDLY_USERNAME
echo $BUILDLY_PASSWORD
```

### Import Errors

```bash
# Make sure you're in the right directory
cd /path/to/buildly/website

# Check Python path
python -c "import sys; print(sys.path)"
```

### Email Delivery Issues

Check your MailerSend configuration in `.env`:
- `MAILERSEND_API_TOKEN`
- `MAILERSEND_FROM_EMAIL`
- `MAILERSEND_FROM_NAME`

## Example Workflow

1. **Setup** (one-time):
   ```bash
   export BUILDLY_USERNAME="greg@buildly.io"
   export BUILDLY_PASSWORD="your-password"
   python automation/test_api_integration.py
   ```

2. **Manual user sync**:
   ```bash
   python automation/user_engagement_cli.py sync-buildly --new-only
   ```

3. **Send feature announcement**:
   ```bash
   python automation/user_engagement_cli.py feature-announcement \
     --name "Enhanced Dashboard" \
     --description "New analytics and insights for your projects"
   ```

4. **Check results**:
   ```bash
   python automation/user_engagement_cli.py stats
   ```

The system is now fully integrated with the Buildly platform for comprehensive user engagement automation!