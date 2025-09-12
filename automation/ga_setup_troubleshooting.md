# Google Analytics Service Account Setup Verification

## Current Status
- ✅ Service account JSON file configured
- ✅ Google Analytics Data API library installed
- ✅ Service account credentials loading correctly
- ❌ 403 Permission error - service account needs access

## Service Account Email
`buildly-analytics-reader@dev-buildly.iam.gserviceaccount.com`

## Required Steps to Complete Setup

### 1. Verify Property IDs
Make sure you're adding the service account to the correct GA4 properties:
- **buildly.io**: Property ID `318805421`
- **labs.buildly.io**: Property ID `145772893`

### 2. Add Service Account to BOTH Properties
You need to add the service account to both GA4 properties:

1. Go to [Google Analytics](https://analytics.google.com/)
2. Select the **buildly.io** property (ID: 318805421)
3. Go to **Admin** (gear icon, bottom left)
4. Under **Property**, click **Property access management**
5. Click **+** (Add users)
6. Add email: `buildly-analytics-reader@dev-buildly.iam.gserviceaccount.com`
7. Select role: **Viewer**
8. Click **Add**

Repeat for **labs.buildly.io** property (ID: 145772893)

### 3. Verify GA4 vs Universal Analytics
Make sure you're in **GA4** (Google Analytics 4), not Universal Analytics:
- GA4 property IDs are typically 9 digits (like yours: 318805421)
- Universal Analytics IDs start with "UA-"

### 4. Wait for Propagation
- Google Analytics permissions can take 5-10 minutes to propagate
- Try running the test again in a few minutes

### 5. Test Commands
```bash
# Test service account authentication
.venv/bin/python automation/test_service_account.py

# Run status report with live data
.venv/bin/python automation/status_report.py

# Generate dashboard with live data
.venv/bin/python automation/dashboard_generator.py
```

## Common Issues

### Issue: Still getting 403 errors
**Solution**: Double-check that you added the service account to the **Property level**, not the Account level

### Issue: Can't find the property
**Solution**: Make sure you're logged in as the correct Google account that owns the Analytics properties

### Issue: Added to wrong property
**Solution**: Check the Property ID in the top-left corner of Google Analytics to confirm you're in the right property

## What Happens Next
Once permissions are properly configured:
- ✅ Live Google Analytics data will replace demo data
- ✅ Daily reports will show real metrics
- ✅ Dashboard will display actual traffic data
- ✅ Both buildly.io and labs.buildly.io will be tracked

## Fallback
If live data setup takes time, the system will continue using enhanced demo data that matches your property structure until authentication is resolved.
