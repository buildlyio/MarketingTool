# 📊 Analytics Integration Guide for Buildly Automation

## Overview
The Buildly automation system can integrate with multiple analytics platforms to provide comprehensive daily reports. Here's what you need to set up each integration:

## 🌐 Google Analytics (GA4) Integration

### What You Need:
1. **Service Account Key** (Recommended) OR **OAuth 2.0 credentials**
2. **GA4 Property ID**

### Setup Steps:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Google Analytics Data API (GA4)**
4. Create a **Service Account**:
   - Go to IAM & Admin > Service Accounts
   - Create Service Account with Analytics Data API access
   - Download the JSON key file
5. In Google Analytics:
   - Go to Admin > Property Access Management
   - Add the service account email with "Viewer" permissions
6. Get your GA4 Property ID from Admin > Property Settings

### Environment Variables:
```bash
# Option 1: Service Account (Recommended)
GOOGLE_ANALYTICS_SERVICE_ACCOUNT_JSON=path/to/service-account.json
GOOGLE_ANALYTICS_PROPERTY_ID=123456789

# Option 2: OAuth (if you prefer)
GOOGLE_ANALYTICS_API_KEY=your-oauth-token
GOOGLE_ANALYTICS_PROPERTY_ID=123456789
```

## 🎥 YouTube Analytics Integration

### What You Need:
1. **YouTube Data API key** OR **OAuth 2.0 credentials**
2. **Channel ID**

### Setup Steps:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **YouTube Analytics API** and **YouTube Data API v3**
3. Create **API Key** or **OAuth 2.0 credentials**
4. Find your Channel ID:
   - Go to YouTube Studio
   - Settings > Channel > Advanced settings
   - Copy your Channel ID

### Environment Variables:
```bash
YOUTUBE_API_KEY=your-api-key
YOUTUBE_CHANNEL_ID=UCyour-channel-id
```

## 💼 LinkedIn Marketing Integration

### What You Need:
1. **LinkedIn Developer App**
2. **OAuth 2.0 Access Token**
3. **Organization ID**

### Setup Steps:
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Create a new app for your company
3. Request access to **Marketing Developer Platform**
4. Get OAuth 2.0 authorization:
   - Set up OAuth flow to get access token
   - Scopes needed: `r_organization_social`, `r_ads_reporting`
5. Find your Organization ID:
   - Use LinkedIn API: `/v2/organizations?q=vanityName&vanityName=your-company`

### Environment Variables:
```bash
LINKEDIN_ACCESS_TOKEN=your-oauth-access-token
LINKEDIN_ORGANIZATION_ID=your-org-id
```

## 🎯 Google Ads Integration

### What You Need:
1. **Google Ads Developer Token**
2. **OAuth 2.0 credentials**
3. **Customer ID**

### Setup Steps:
1. Apply for [Google Ads API access](https://developers.google.com/google-ads/api/docs/first-call/overview)
2. Get **Developer Token** (requires approval)
3. Set up OAuth 2.0:
   - Go to Google Cloud Console
   - Create OAuth 2.0 credentials
   - Get refresh token through OAuth flow
4. Find your Customer ID in Google Ads account

### Environment Variables:
```bash
GOOGLE_ADS_DEVELOPER_TOKEN=your-developer-token
GOOGLE_ADS_CLIENT_ID=your-oauth-client-id
GOOGLE_ADS_CLIENT_SECRET=your-oauth-client-secret
GOOGLE_ADS_REFRESH_TOKEN=your-refresh-token
GOOGLE_ADS_CUSTOMER_ID=123-456-7890
```

## 📋 Current Implementation Status

### ✅ Implemented and Ready:
- **Email Outreach**: MailerSend SMTP integration working
- **HubSpot CRM**: Ready (needs access token)
- **Basic Analytics**: Placeholder data structure ready

### 🚧 Partially Implemented:
- **Google Analytics GA4**: API calls implemented, needs credentials
- **YouTube Analytics**: API calls implemented, needs credentials
- **LinkedIn Marketing**: API calls implemented, needs OAuth setup
- **Google Ads**: Structure ready, needs full implementation

### 📊 What Data You'll Get:

#### Google Analytics:
- Sessions, page views, users
- Bounce rate, session duration
- Top pages
- Traffic sources
- Conversions

#### YouTube:
- Views, watch time
- Subscriber growth
- Likes, comments
- Top performing videos

#### LinkedIn:
- Follower count
- Post impressions and clicks
- Engagement rates
- Post performance

#### Google Ads:
- Impressions, clicks, cost
- Conversions
- Click-through rate (CTR)
- Cost per click (CPC)

## 🚀 Quick Start Options

### Option 1: Start with Google Analytics Only
1. Set up GA4 service account (easiest)
2. Add to `.env`: 
   ```bash
   GOOGLE_ANALYTICS_PROPERTY_ID=your-property-id
   GOOGLE_ANALYTICS_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
   ```

### Option 2: Add YouTube (if you have a channel)
1. Get YouTube API key
2. Add to `.env`:
   ```bash
   YOUTUBE_API_KEY=your-api-key
   YOUTUBE_CHANNEL_ID=your-channel-id
   ```

### Option 3: Full Integration (All Platforms)
Set up all the above credentials for comprehensive reporting.

## 🔧 Testing Your Setup

Run this to test each integration:
```bash
.venv/bin/python automation/status_report.py
```

The system will show which integrations are working and which need credentials.

## 📈 Sample Daily Report

With all integrations, your daily report will include:
- **Email Outreach**: 15 emails sent, 2 failed, 5 sources
- **Lead Generation**: 8 new leads, 125 total
- **Website Traffic**: 1,250 sessions, 2,100 page views
- **YouTube**: 500 views, 45 minutes watch time
- **LinkedIn**: 15 new followers, 2,300 impressions
- **Google Ads**: 5,000 impressions, 125 clicks, $45 spent

## 🔒 Security Notes

- Store all credentials in `.env` file (never commit to git)
- Use service accounts when possible (more secure than OAuth)
- Regularly rotate access tokens
- Monitor API usage to stay within quotas

---

**Need help setting up any of these integrations? The automation system will work with whatever analytics you have configured - you don't need all of them to get started!**
