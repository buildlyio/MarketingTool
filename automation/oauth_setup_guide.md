# Google Analytics OAuth Setup Guide

## Current Status
- ✅ Property IDs configured: 318805421 (buildly.io), 145772893 (labs.buildly.io)
- ❌ API key authentication not supported by GA4 Data API
- 🔧 OAuth authentication required for live data

## Option 1: Service Account (Recommended for Automation)

### Step 1: Create Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to IAM & Admin > Service Accounts
4. Click "Create Service Account"
5. Name it "buildly-analytics-reader"
6. Download the JSON key file

### Step 2: Enable Analytics Data API
1. Go to APIs & Services > Library
2. Search for "Google Analytics Data API"
3. Click "Enable"

### Step 3: Grant Analytics Access
1. Open Google Analytics
2. Go to Admin > Property Settings
3. Add the service account email as a "Viewer"
4. Do this for both properties (buildly.io and labs.buildly.io)

### Step 4: Update Environment
```bash
# Add to .env file
GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/service-account-key.json
```

## Option 2: OAuth Client (Interactive Setup)

### For Development/Testing
1. Create OAuth 2.0 Client ID in Cloud Console
2. Download client_secrets.json
3. Use interactive authentication flow

## Quick Implementation

I can implement either option. Service Account is better for automation since it doesn't require interactive login.

Which would you prefer?
1. **Service Account** (automated, requires Google Cloud setup)
2. **OAuth Client** (interactive, simpler initial setup)
3. **Continue with enhanced demo data** (no setup required)
