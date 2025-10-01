#!/usr/bin/env python3
"""
Debug script to see actual API responses from Buildly
"""
import requests
import json
import os

# Get credentials
username = os.getenv('BUILDLY_USERNAME', 'glind')
password = os.getenv('BUILDLY_PASSWORD', 'S@rah1013')

print(f"Testing Buildly API endpoints with user: {username}")

# Authenticate
print("\n=== Authentication ===")
auth_response = requests.post(
    "https://labs-api.buildly.io/token/",
    json={"username": username, "password": password}
)
print(f"Auth Status: {auth_response.status_code}")
if auth_response.status_code == 200:
    tokens = auth_response.json()
    access_token = tokens['access']
    print("✅ Authentication successful")
else:
    print("❌ Authentication failed")
    exit(1)

# Set up headers
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Test organizations endpoint
print("\n=== Organizations Endpoint ===")
org_response = requests.get("https://labs-api.buildly.io/organization/", headers=headers)
print(f"Organizations Status: {org_response.status_code}")
print(f"Organizations Response Type: {type(org_response.json())}")
print(f"Organizations Data (first 500 chars): {str(org_response.json())[:500]}...")

# Test users endpoint  
print("\n=== Users Endpoint ===")
users_response = requests.get("https://labs-api.buildly.io/coreuser/", headers=headers)
print(f"Users Status: {users_response.status_code}")
print(f"Users Response Type: {type(users_response.json())}")

users_data = users_response.json()
print(f"Users Data Structure: {list(users_data.keys()) if isinstance(users_data, dict) else 'Not a dict'}")

if isinstance(users_data, dict):
    print(f"Users Count: {users_data.get('count', 'No count field')}")
    results = users_data.get('results', [])
    print(f"Users Results Length: {len(results)}")
    
    if results:
        print(f"First User Sample: {json.dumps(results[0], indent=2)[:500]}...")
        
        # Show all users briefly
        print(f"\n=== All Users (Brief) ===")
        for i, user in enumerate(results):
            print(f"{i+1}. {user.get('email', 'No email')} - {user.get('first_name', '')} {user.get('last_name', '')} - Active: {user.get('is_active', 'Unknown')}")
else:
    print(f"Users Response (first 500 chars): {str(users_data)[:500]}...")