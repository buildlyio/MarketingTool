# Google Analytics Property Access - Step by Step Guide

## Issue Confirmed ✅
Your service account authentication is **PERFECT**! The issue is simply that the service account isn't properly added to the Google Analytics property.

## Service Account Details
- **Email**: `buildly-analytics-reader@dev-buildly.iam.gserviceaccount.com`
- **Status**: ✅ Valid and working
- **Token**: ✅ Refreshing correctly
- **API Access**: ✅ Fully functional

## The Problem
403 error = Service account can authenticate but doesn't have permission to access GA property `318805421`

## Exact Steps to Fix

### 1. Verify You're in the Right Google Analytics Account
1. Go to [analytics.google.com](https://analytics.google.com)
2. Make sure you're logged in as the account owner of buildly.io analytics
3. Check the account selector (top left) - ensure you're in the right account

### 2. Find the Correct Property
1. Look for **"buildly - GA4"** or similar in the property list
2. Click on it to select it
3. **Verify the Property ID**:
   - Look in the top left corner or property settings
   - Should show Property ID: `318805421`
   - If it shows a different number, update the .env file

### 3. Add Service Account (Step-by-Step Screenshots)
1. Click **Admin** (gear icon, bottom left)
2. In the **Property** column (middle column), click **"Property access management"**
3. Click **"+"** (plus icon) to add users
4. Enter email: `buildly-analytics-reader@dev-buildly.iam.gserviceaccount.com`
5. Select role: **"Viewer"**
6. Click **"Add"**
7. **VERIFY**: The email should appear in the user list

### 4. Common Issues

#### Issue: "Email not found" or "Invalid email"
**Solution**: Make sure you're typing the EXACT email:
```
buildly-analytics-reader@dev-buildly.iam.gserviceaccount.com
```

#### Issue: "Can't find Property access management"
**Solution**: 
- Make sure you're in **GA4** (not Universal Analytics)
- GA4 properties have 9-digit IDs like `318805421`
- Universal Analytics has IDs like `UA-123456-1`

#### Issue: Added but still getting 403
**Solutions**:
- Wait 5-10 minutes for propagation
- Check that you added to the **Property** level, not Account level
- Verify you're in the correct property

### 5. Alternative: Check Different Property
If `318805421` doesn't work, let's find the correct Property ID:

1. In Google Analytics, go to **Admin**
2. Click **Property Settings** (under Property column)
3. Look for **"Property ID"** - copy this exact number
4. Update your `.env` file if it's different

### 6. Test After Adding
```bash
# Test the connection
.venv/bin/python automation/test_service_account.py

# If successful, generate live dashboard
.venv/bin/python automation/dashboard_generator.py
```

## Double-Check List
- [ ] Correct Google account (owns buildly.io analytics)
- [ ] GA4 property (not Universal Analytics)
- [ ] Property ID exactly: `318805421`
- [ ] Service account email exactly: `buildly-analytics-reader@dev-buildly.iam.gserviceaccount.com`
- [ ] Added at **Property** level with **Viewer** role
- [ ] User appears in the access management list

The moment this is fixed, you'll immediately get live Google Analytics data!
