#!/usr/bin/env python3
"""
Manual Unsubscribe List Manager

This script helps you manually update the unsubscribe list by adding emails
and committing changes to GitHub using your local git setup.
"""

import json
import os
import subprocess
from datetime import datetime

def load_unsubscribe_list():
    """Load the current unsubscribe list"""
    file_path = 'automation/unsubscribed_emails.json'
    
    if not os.path.exists(file_path):
        # Create empty list if file doesn't exist
        data = {
            "unsubscribed_emails": [],
            "last_updated": None,
            "version": 1
        }
        save_unsubscribe_list(data)
        return data
    
    with open(file_path, 'r') as f:
        return json.load(f)

def save_unsubscribe_list(data):
    """Save the unsubscribe list"""
    file_path = 'automation/unsubscribed_emails.json'
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def add_unsubscribe_email(email, reason="Manual unsubscribe"):
    """Add an email to the unsubscribe list"""
    data = load_unsubscribe_list()
    
    # Check if email already exists
    existing = next((item for item in data['unsubscribed_emails'] 
                    if item['email'].lower() == email.lower()), None)
    
    if existing:
        print(f"Email {email} is already unsubscribed (on {existing['unsubscribed_at']})")
        return False
    
    # Add new unsubscribe entry
    now = datetime.now().isoformat()
    data['unsubscribed_emails'].append({
        "email": email.lower(),
        "unsubscribed_at": now,
        "reason": reason,
        "processed_by": "manual"
    })
    
    data['last_updated'] = now
    data['version'] = data.get('version', 1) + 1
    
    save_unsubscribe_list(data)
    
    # Commit to git
    try:
        subprocess.run(['git', 'add', 'automation/unsubscribed_emails.json'], check=True)
        subprocess.run(['git', 'commit', '-m', f'Unsubscribe: {email}'], check=True)
        print(f"✅ Successfully unsubscribed {email} and committed to git")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to commit to git: {e}")
        return False

def remove_unsubscribe_email(email):
    """Remove an email from the unsubscribe list (re-subscribe)"""
    data = load_unsubscribe_list()
    
    # Find and remove the email
    original_count = len(data['unsubscribed_emails'])
    data['unsubscribed_emails'] = [
        item for item in data['unsubscribed_emails'] 
        if item['email'].lower() != email.lower()
    ]
    
    if len(data['unsubscribed_emails']) < original_count:
        data['last_updated'] = datetime.now().isoformat()
        data['version'] = data.get('version', 1) + 1
        save_unsubscribe_list(data)
        
        # Commit to git
        try:
            subprocess.run(['git', 'add', 'automation/unsubscribed_emails.json'], check=True)
            subprocess.run(['git', 'commit', '-m', f'Re-subscribe: {email}'], check=True)
            print(f"✅ Successfully re-subscribed {email} and committed to git")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to commit to git: {e}")
            return False
    else:
        print(f"Email {email} was not found in the unsubscribe list")
        return False

def list_unsubscribed_emails():
    """List all unsubscribed emails"""
    data = load_unsubscribe_list()
    
    if not data['unsubscribed_emails']:
        print("No unsubscribed emails found.")
        return
    
    print(f"\n📧 Unsubscribed Emails ({len(data['unsubscribed_emails'])} total):")
    print("-" * 60)
    
    for item in sorted(data['unsubscribed_emails'], key=lambda x: x['unsubscribed_at'], reverse=True):
        email = item['email']
        date = item['unsubscribed_at'][:10]  # Just the date part
        reason = item.get('reason', 'Unknown')
        print(f"{email:<35} | {date} | {reason}")

def push_changes():
    """Push changes to remote repository"""
    try:
        subprocess.run(['git', 'push'], check=True)
        print("✅ Successfully pushed changes to remote repository")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to push to remote: {e}")
        return False

def main():
    """Main CLI interface"""
    print("🚫 Buildly Unsubscribe List Manager")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Add unsubscribe email")
        print("2. Remove email (re-subscribe)")
        print("3. List all unsubscribed emails")
        print("4. Push changes to GitHub")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            email = input("Enter email to unsubscribe: ").strip()
            reason = input("Reason (optional): ").strip() or "Manual unsubscribe"
            
            if email:
                add_unsubscribe_email(email, reason)
            else:
                print("Please enter a valid email address.")
        
        elif choice == '2':
            email = input("Enter email to re-subscribe: ").strip()
            
            if email:
                remove_unsubscribe_email(email)
            else:
                print("Please enter a valid email address.")
        
        elif choice == '3':
            list_unsubscribed_emails()
        
        elif choice == '4':
            push_changes()
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()