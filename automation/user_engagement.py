#!/usr/bin/env python3
"""
User Engagement Automation for Buildly Platform Users

This module handles:
1. Active user feature announcements and release notes
2. Inactive user re-engagement with help offers and tutorials
3. User activity tracking and segmentation
"""

import os
import json
import sqlite3
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from typing import List, Dict, Optional
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PlatformUser:
    """Data class for platform users"""
    user_id: str
    email: str
    name: str
    signup_date: str
    last_login: str
    activity_level: str  # 'active', 'inactive', 'new'
    features_used: List[str]
    subscription_type: str  # 'free', 'pro', 'enterprise'
    
class UserEngagementSystem:
    """Main class for user engagement automation"""
    
    def __init__(self):
        # Email configuration (using existing MailerSend setup)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.mailersend.net')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('EMAIL_HOST_USER', 'team@buildly.io')
        self.bcc_email = os.getenv('BCC_EMAIL', 'greg@buildly.io')
        
        # User database configuration
        self.user_db_path = 'automation/user_engagement.db'
        self.engagement_log_path = 'automation/user_engagement_log.json'
        
        # Activity thresholds (configurable)
        self.active_threshold_days = int(os.getenv('ACTIVE_THRESHOLD_DAYS', '7'))
        self.inactive_threshold_days = int(os.getenv('INACTIVE_THRESHOLD_DAYS', '30'))
        
        # GitHub unsubscribe list configuration
        self.github_owner = os.getenv('GITHUB_OWNER', 'buildlyio')
        self.github_repo = os.getenv('GITHUB_REPO', 'MarketingTool')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.unsubscribe_file_path = 'automation/unsubscribed_emails.json'
        self.unsubscribe_cache = None
        self.unsubscribe_cache_time = None
        self.cache_duration = 300  # 5 minutes cache
        
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize SQLite database for user tracking"""
        try:
            self.conn = sqlite3.connect(self.user_db_path, check_same_thread=False)
            conn = self.conn
            cursor = conn.cursor()
            
            # Create users table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    signup_date TEXT,
                    last_login TEXT,
                    activity_level TEXT,
                    features_used TEXT,  -- JSON string
                    subscription_type TEXT,
                    last_feature_email TEXT,
                    last_reengagement_email TEXT,
                    is_subscribed INTEGER DEFAULT 1,
                    unsubscribed_at TEXT,
                    email_preferences TEXT DEFAULT 'all',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create engagement history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS engagement_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    email_type TEXT NOT NULL,
                    sent_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Create email analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_name TEXT NOT NULL,
                    sent_count INTEGER DEFAULT 0,
                    delivered_count INTEGER DEFAULT 0,
                    opened_count INTEGER DEFAULT 0,
                    clicked_count INTEGER DEFAULT 0,
                    unsubscribed_count INTEGER DEFAULT 0,
                    bounce_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            # Keep connection open for use by other methods
            logger.info("User engagement database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize user database: {e}")
            
    def import_users_from_platform(self, users_data: List[Dict]) -> int:
        """
        Import users from Buildly platform data
        
        Expected format:
        [
            {
                "user_id": "123",
                "email": "user@example.com", 
                "name": "John Doe",
                "signup_date": "2025-01-15",
                "last_login": "2025-09-28",
                "features_used": ["api_builder", "workflow_designer"],
                "subscription_type": "pro"
            }
        ]
        """
        try:
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            
            imported_count = 0
            
            for user_data in users_data:
                # Determine activity level
                activity_level = self._calculate_activity_level(user_data.get('last_login'))
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, email, name, signup_date, last_login, activity_level, 
                     features_used, subscription_type, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_data['user_id'],
                    user_data['email'],
                    user_data.get('name', ''),
                    user_data.get('signup_date'),
                    user_data.get('last_login'),
                    activity_level,
                    json.dumps(user_data.get('features_used', [])),
                    user_data.get('subscription_type', 'free'),
                    datetime.now().isoformat()
                ))
                
                imported_count += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"Imported {imported_count} users successfully")
            return imported_count
            
        except Exception as e:
            logger.error(f"Failed to import users: {e}")
            return 0
    
    def _calculate_activity_level(self, last_login: str) -> str:
        """Calculate user activity level based on last login"""
        if not last_login:
            return 'inactive'
        
        try:
            last_login_date = datetime.fromisoformat(last_login.replace('Z', ''))
            days_since_login = (datetime.now() - last_login_date).days
            
            if days_since_login <= self.active_threshold_days:
                return 'active'
            elif days_since_login <= self.inactive_threshold_days:
                return 'moderately_active'
            else:
                return 'inactive'
                
        except Exception:
            return 'inactive'
    
    def _fetch_unsubscribed_emails(self) -> List[str]:
        """Fetch unsubscribed emails from local JSON file or GitHub raw URL with caching"""
        try:
            # Check cache first
            if (self.unsubscribe_cache and self.unsubscribe_cache_time and 
                (datetime.now() - self.unsubscribe_cache_time).seconds < self.cache_duration):
                return self.unsubscribe_cache
            
            # Try to read local file first (most common case)
            try:
                with open(self.unsubscribe_file_path, 'r') as f:
                    data = json.load(f)
                    unsubscribed_emails = [entry['email'] for entry in data.get('unsubscribed_emails', [])]
                    self.unsubscribe_cache = unsubscribed_emails
                    self.unsubscribe_cache_time = datetime.now()
                    logger.info(f"Loaded {len(unsubscribed_emails)} unsubscribed emails from local file")
                    return unsubscribed_emails
            except FileNotFoundError:
                logger.info("Local unsubscribe file not found, trying GitHub raw URL")
            
            # Fallback: Try to fetch from GitHub raw URL (no token required for public repos)
            raw_url = f"https://raw.githubusercontent.com/{self.github_owner}/{self.github_repo}/main/{self.unsubscribe_file_path}"
            
            response = requests.get(raw_url, timeout=10)
            
            if response.status_code == 200:
                unsubscribe_data = response.json()
                unsubscribed_emails = [entry['email'] for entry in unsubscribe_data.get('unsubscribed_emails', [])]
                
                # Update cache
                self.unsubscribe_cache = unsubscribed_emails
                self.unsubscribe_cache_time = datetime.now()
                
                logger.info(f"Fetched {len(unsubscribed_emails)} unsubscribed emails from GitHub raw URL")
                return unsubscribed_emails
                
            elif response.status_code == 404:
                logger.info("Unsubscribe file not found on GitHub, assuming no unsubscribes yet")
                return []
            else:
                logger.warning(f"Failed to fetch unsubscribe list from GitHub: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching unsubscribed emails: {e}")
            return []
    
    def _is_email_unsubscribed(self, email: str) -> bool:
        """Check if an email address is in the unsubscribe list"""
        unsubscribed_emails = self._fetch_unsubscribed_emails()
        return email.lower() in [e.lower() for e in unsubscribed_emails]
    
    def get_active_users(self) -> List[PlatformUser]:
        """Get list of active users for feature announcements"""
        return self._get_users_by_activity(['active', 'moderately_active'])
    
    def get_inactive_users(self) -> List[PlatformUser]:
        """Get list of inactive users for re-engagement"""
        return self._get_users_by_activity(['inactive'])
    
    def _get_users_by_activity(self, activity_levels: List[str]) -> List[PlatformUser]:
        """Get users by activity level"""
        try:
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            
            placeholders = ','.join(['?' for _ in activity_levels])
            cursor.execute(f'''
                SELECT user_id, email, name, signup_date, last_login, 
                       activity_level, features_used, subscription_type
                FROM users 
                WHERE activity_level IN ({placeholders})
                ORDER BY last_login DESC
            ''', activity_levels)
            
            users = []
            for row in cursor.fetchall():
                users.append(PlatformUser(
                    user_id=row[0],
                    email=row[1],
                    name=row[2] or 'Buildly User',
                    signup_date=row[3],
                    last_login=row[4],
                    activity_level=row[5],
                    features_used=json.loads(row[6]) if row[6] else [],
                    subscription_type=row[7]
                ))
            
            conn.close()
            return users
            
        except Exception as e:
            logger.error(f"Failed to get users by activity: {e}")
            return []
    
    def send_feature_announcement(self, users: List[PlatformUser], 
                                 feature_name: str, feature_description: str,
                                 release_notes: str = "", cta_link: str = "") -> Dict:
        """Send feature announcement email to active users"""
        
        template = self._generate_feature_announcement_template(
            feature_name, feature_description, release_notes, cta_link
        )
        
        results = {
            'sent': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        for user in users:
            try:
                # Check if user received feature email recently (avoid spam)
                if self._should_skip_feature_email(user.user_id):
                    results['skipped'] += 1
                    continue
                
                # Personalize email
                personalized_content = template.replace('[USER_NAME]', user.name)
                personalized_content = personalized_content.replace('[FEATURE_NAME]', feature_name)
                
                # Send email
                if self._send_email(
                    user.email, 
                    f"🚀 New Feature Alert: {feature_name}",
                    personalized_content
                ):
                    results['sent'] += 1
                    self._log_engagement(user.user_id, 'feature_announcement', 
                                       f"New Feature: {feature_name}", 'sent')
                    self._update_last_feature_email(user.user_id)
                else:
                    results['failed'] += 1
                    self._log_engagement(user.user_id, 'feature_announcement', 
                                       f"New Feature: {feature_name}", 'failed')
                
            except Exception as e:
                logger.error(f"Failed to send feature email to {user.email}: {e}")
                results['failed'] += 1
        
        logger.info(f"Feature announcement sent: {results['sent']} sent, {results['failed']} failed, {results['skipped']} skipped")
        return results
    
    def send_reengagement_campaign(self, users: List[PlatformUser]) -> Dict:
        """Send re-engagement emails to inactive users"""
        
        results = {
            'sent': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        for user in users:
            try:
                # Check if user received re-engagement email recently
                if self._should_skip_reengagement_email(user.user_id):
                    results['skipped'] += 1
                    continue
                
                # Generate personalized re-engagement email
                template = self._generate_reengagement_template(user)
                
                # Send email
                if self._send_email(
                    user.email,
                    "We miss you! Let's get you back on track 🏗️",
                    template
                ):
                    results['sent'] += 1
                    self._log_engagement(user.user_id, 'reengagement', 
                                       'Re-engagement campaign', 'sent')
                    self._update_last_reengagement_email(user.user_id)
                else:
                    results['failed'] += 1
                    self._log_engagement(user.user_id, 'reengagement', 
                                       'Re-engagement campaign', 'failed')
                
            except Exception as e:
                logger.error(f"Failed to send re-engagement email to {user.email}: {e}")
                results['failed'] += 1
        
        logger.info(f"Re-engagement campaign sent: {results['sent']} sent, {results['failed']} failed, {results['skipped']} skipped")
        return results
    
    def _generate_feature_announcement_template(self, feature_name: str, 
                                              feature_description: str,
                                              release_notes: str = "",
                                              cta_link: str = "") -> str:
        """Generate HTML template for feature announcements"""
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>New Feature: {feature_name}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background: #f9f9f9; }}
                .feature-highlight {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 20px 0; }}
                .cta-button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; margin: 20px 0; }}
                .release-notes {{ background: #e8f4f8; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea; margin: 15px 0; }}
                .footer {{ background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 New Feature Alert!</h1>
                <p>Hey [USER_NAME], we've got something exciting for you!</p>
            </div>
            
            <div class="content">
                <div class="feature-highlight">
                    <h2>✨ Introducing: {feature_name}</h2>
                    <p>{feature_description}</p>
                    
                    {f'<div class="release-notes"><h3>📋 What{chr(39)}s New:</h3><p>{release_notes}</p></div>' if release_notes else ''}
                    
                    {f'<a href="{cta_link}" class="cta-button">Try It Now →</a>' if cta_link else ''}
                </div>
                
                <h3>🎯 Why You'll Love This:</h3>
                <ul>
                    <li><strong>Save Time:</strong> Streamline your development workflow</li>
                    <li><strong>Increase Productivity:</strong> Focus on what matters most</li>
                    <li><strong>Better Results:</strong> Deliver higher quality applications faster</li>
                </ul>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>📚 Need Help Getting Started?</h3>
                    <p>Our team is here to help! Check out these resources:</p>
                    <ul>
                        <li><a href="https://docs.buildly.io/docs/quickstart.html">📖 Documentation</a></li>
                        <li><a href="https://buildly.io/tutorials">🎥 Video Tutorials</a></li>
                        <li><a href="https://buildly.io/support">💬 Live Support Chat</a></li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p>Happy Building! 🏗️<br>
                The Buildly Team</p>
                <p><a href="https://buildly.io/labs" style="color: white;">Visit Buildly Labs</a> | 
                <a href="https://buildly.io/opt-out?email=[EMAIL]" style="color: white;">Unsubscribe</a></p>
            </div>
        </body>
        </html>
        """
    
    def _generate_reengagement_template(self, user: PlatformUser) -> str:
        """Generate personalized re-engagement email template"""
        
        # Customize based on user's previous features used
        feature_suggestions = self._get_feature_suggestions(user.features_used)
        
        # Pre-format CSS to avoid f-string backslash issues
        css_styles = """
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }
                .header { background: linear-gradient(135deg, #ff7b7b 0%, #667eea 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { padding: 30px; background: #f9f9f9; }
                .help-section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 20px 0; }
                .cta-button { display: inline-block; background: #ff7b7b; color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; margin: 10px 5px; }
                .tutorial-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }
                .tutorial-card { background: white; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; }
                .footer { background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }
        """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>We Miss You at Buildly!</title>
            <style>
                {css_styles}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>👋 Hey {user.name}!</h1>
                <p>We noticed you haven't been around lately...</p>
            </div>
            
            <div class="content">
                <div class="help-section">
                    <h2>🤔 Need Some Help Getting Back on Track?</h2>
                    <p>Building applications can be challenging, and we're here to make it easier for you. 
                    Whether you're stuck on a specific feature or just need some inspiration, we've got your back!</p>
                    
                    <div style="text-align: center; margin: 25px 0;">
                        <a href="https://www.cal.com/buildly" class="cta-button">📅 Book Free 1:1 Session</a>
                        <a href="https://buildly.io/tutorials" class="cta-button">🎥 Watch Tutorials</a>
                    </div>
                </div>
                
                <div class="help-section">
                    <h3>🚀 Here's What You Might Have Missed:</h3>
                    {feature_suggestions}
                </div>
                
                <div class="tutorial-grid">
                    <div class="tutorial-card">
                        <h4>🏁 Quick Start Guide</h4>
                        <p>Get up and running in under 10 minutes with our step-by-step tutorial.</p>
                        <a href="https://docs.buildly.io/docs/quickstart.html">Start Here →</a>
                    </div>
                    
                    <div class="tutorial-card">
                        <h4>💬 Community Support</h4>
                        <p>Join thousands of developers in our active community forum.</p>
                        <a href="https://community.buildly.io">Join Community →</a>
                    </div>
                    
                    <div class="tutorial-card">
                        <h4>📞 Live Support</h4>
                        <p>Chat with our technical team for instant help with any issues.</p>
                        <a href="https://buildly.io/support">Get Help →</a>
                    </div>
                    
                    <div class="tutorial-card">
                        <h4>📚 Learning Center</h4>
                        <p>Comprehensive guides, examples, and best practices.</p>
                        <a href="https://learn.buildly.io">Browse Resources →</a>
                    </div>
                </div>
                
                <div style="background: #e8f4f8; padding: 20px; border-radius: 8px; margin: 25px 0; text-align: center;">
                    <h3>🎁 Special Welcome Back Offer</h3>
                    <p>As a thank you for giving us another chance, enjoy <strong>30 days free</strong> on any paid plan!</p>
                    <a href="https://buildly.io/welcome-back" class="cta-button">Claim Your Offer →</a>
                </div>
                
                <div style="text-align: center; margin: 25px 0;">
                    <p><strong>Still not sure? That's okay!</strong><br>
                    Reply to this email and tell us what you're trying to build. 
                    Our team will personally help you get started.</p>
                </div>
            </div>
            
            <div class="footer">
                <p>We're here when you're ready! 🏗️<br>
                The Buildly Team</p>
                <p><a href="https://buildly.io/labs" style="color: white;">Visit Buildly Labs</a> | 
                <a href="https://buildly.io/opt-out?email={user.email}" style="color: white;">Unsubscribe</a></p>
            </div>
        </body>
        </html>
        """
    
    def _get_feature_suggestions(self, features_used: List[str]) -> str:
        """Generate personalized feature suggestions based on usage history"""
        
        suggestions = {
            'api_builder': '🔗 <strong>Advanced API Integrations:</strong> Connect to any third-party service seamlessly',
            'workflow_designer': '⚡ <strong>Automated Workflows:</strong> Set up triggers and actions to automate your processes',
            'database_manager': '🗄️ <strong>Smart Database Tools:</strong> Advanced querying and data visualization features',
            'ui_builder': '🎨 <strong>Custom UI Components:</strong> Create beautiful, responsive interfaces faster'
        }
        
        if not features_used:
            return '''
            <ul>
                <li>🔗 <strong>API Builder:</strong> Connect any service in minutes, not hours</li>
                <li>⚡ <strong>Workflow Designer:</strong> Automate repetitive tasks with visual workflows</li>
                <li>🗄️ <strong>Database Manager:</strong> Powerful data tools that scale with you</li>
                <li>🎨 <strong>UI Builder:</strong> Create beautiful interfaces without coding</li>
            </ul>
            '''
        
        # Show related features they haven't used yet
        unused_features = [feature for feature in suggestions.keys() if feature not in features_used]
        
        if unused_features:
            return '<ul>' + ''.join([f'<li>{suggestions[feature]}</li>' for feature in unused_features[:3]]) + '</ul>'
        else:
            return '''
            <ul>
                <li>🚀 <strong>Advanced Features:</strong> Discover pro-level tools to supercharge your development</li>
                <li>🔧 <strong>Custom Integrations:</strong> Build exactly what you need with our flexible platform</li>
                <li>📊 <strong>Analytics Dashboard:</strong> Track your application performance and user engagement</li>
            </ul>
            '''
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using MailerSend SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add BCC for tracking
            if self.bcc_email:
                msg['Bcc'] = self.bcc_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Send via SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            
            # Send to both recipient and BCC
            recipients = [to_email]
            if self.bcc_email:
                recipients.append(self.bcc_email)
            
            server.send_message(msg, to_addrs=recipients)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def _should_skip_feature_email(self, user_id: str) -> bool:
        """Check if user received a feature email recently (within 7 days)"""
        try:
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT last_feature_email FROM users WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result or not result[0]:
                return False
            
            last_email_date = datetime.fromisoformat(result[0])
            days_since_last = (datetime.now() - last_email_date).days
            
            return days_since_last < 7  # Skip if sent within last 7 days
            
        except Exception:
            return False
    
    def _should_skip_reengagement_email(self, user_id: str) -> bool:
        """Check if user received a re-engagement email recently (within 14 days)"""
        try:
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT last_reengagement_email FROM users WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result or not result[0]:
                return False
            
            last_email_date = datetime.fromisoformat(result[0])
            days_since_last = (datetime.now() - last_email_date).days
            
            return days_since_last < 14  # Skip if sent within last 14 days
            
        except Exception:
            return False
    
    def _update_last_feature_email(self, user_id: str):
        """Update last feature email timestamp"""
        try:
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET last_feature_email = ?, updated_at = ?
                WHERE user_id = ?
            ''', (datetime.now().isoformat(), datetime.now().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update last feature email for {user_id}: {e}")
    
    def _update_last_reengagement_email(self, user_id: str):
        """Update last re-engagement email timestamp"""
        try:
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET last_reengagement_email = ?, updated_at = ?
                WHERE user_id = ?
            ''', (datetime.now().isoformat(), datetime.now().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update last re-engagement email for {user_id}: {e}")
    
    def _log_engagement(self, user_id: str, campaign_type: str, subject: str, status: str):
        """Log engagement activity"""
        try:
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO engagement_history 
                (user_id, campaign_type, email_subject, status)
                VALUES (?, ?, ?, ?)
            ''', (user_id, campaign_type, subject, status))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to log engagement for {user_id}: {e}")
    
    def get_engagement_stats(self) -> Dict:
        """Get engagement statistics"""
        try:
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            
            # User stats by activity level
            cursor.execute('''
                SELECT activity_level, COUNT(*) 
                FROM users 
                GROUP BY activity_level
            ''')
            activity_stats = dict(cursor.fetchall())
            
            # Email stats from last 30 days
            cursor.execute('''
                SELECT campaign_type, status, COUNT(*) 
                FROM engagement_history 
                WHERE sent_at >= date('now', '-30 days')
                GROUP BY campaign_type, status
            ''')
            email_stats = {}
            for row in cursor.fetchall():
                campaign = row[0]
                status = row[1]
                count = row[2]
                if campaign not in email_stats:
                    email_stats[campaign] = {}
                email_stats[campaign][status] = count
            
            conn.close()
            
            return {
                'user_activity': activity_stats,
                'email_campaigns': email_stats,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get engagement stats: {e}")
            return {}
    
    # === Buildly API Integration Methods ===
    
    def setup_buildly_api(self, username: str = None, password: str = None) -> bool:
        """
        Setup Buildly API integration
        
        Args:
            username: Buildly API username (defaults to BUILDLY_USERNAME env var)
            password: Buildly API password (defaults to BUILDLY_PASSWORD env var)
            
        Returns:
            True if setup successful, False otherwise
        """
        try:
            from buildly_api_client import BuildlyAPIClient, BuildlyUserSync
            
            self.api_client = BuildlyAPIClient(username=username, password=password)
            self.user_sync = BuildlyUserSync(self.api_client, self)
            
            # Test connection
            if self.api_client.test_connection():
                logger.info("Buildly API integration setup successfully")
                return True
            else:
                logger.error("Buildly API connection test failed")
                return False
                
        except ImportError:
            logger.error("buildly_api_client module not found")
            return False
        except Exception as e:
            logger.error(f"Failed to setup Buildly API integration: {e}")
            return False
    
    def sync_users_from_buildly(self, organization_uuid: str = None) -> Dict[str, int]:
        """
        Sync all users from Buildly API to local database
        
        Args:
            organization_uuid: Optional organization filter
            
        Returns:
            Dict with sync statistics
        """
        if not hasattr(self, 'user_sync'):
            if not self.setup_buildly_api():
                raise Exception("Buildly API not configured. Call setup_buildly_api() first.")
        
        return self.user_sync.sync_users(organization_uuid)
    
    def sync_new_users_from_buildly(self, organization_uuid: str = None, days_back: int = 7) -> Dict[str, int]:
        """
        Sync only new users from Buildly API (created in last N days)
        
        Args:
            organization_uuid: Optional organization filter
            days_back: Number of days to look back for new users
            
        Returns:
            Dict with sync statistics
        """
        if not hasattr(self, 'user_sync'):
            if not self.setup_buildly_api():
                raise Exception("Buildly API not configured. Call setup_buildly_api() first.")
        
        return self.user_sync.sync_new_users_only(organization_uuid, days_back)
    
    def get_buildly_organizations(self) -> List[Dict[str, Any]]:
        """
        Get list of organizations from Buildly API
        
        Returns:
            List of organization data
        """
        if not hasattr(self, 'api_client'):
            if not self.setup_buildly_api():
                raise Exception("Buildly API not configured. Call setup_buildly_api() first.")
        
        return self.api_client.get_organizations()
    
    def add_user(self, user_id: str = None, email: str = "", name: str = "", 
                 signup_date: str = None, last_login: str = None, 
                 organization: str = "", user_type: str = "User", 
                 is_active: bool = True, external_id: str = "", 
                 features_used: List[str] = None, subscription_type: str = "free") -> str:
        """
        Add a new user to the database
        
        Args:
            user_id: Unique user identifier (auto-generated if not provided)
            email: User email address
            name: User full name
            signup_date: ISO format signup date
            last_login: ISO format last login date
            organization: Organization UUID or name
            user_type: User type (e.g., "Developer", "Product Team")
            is_active: Whether user is active
            external_id: External system user ID (e.g., Buildly core_user_uuid)
            features_used: List of features used by the user
            subscription_type: Subscription type (free, pro, enterprise)
            
        Returns:
            Generated user_id
        """
        try:
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            
            # Generate user_id if not provided
            if not user_id:
                user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}_{email.split('@')[0]}"
            
            # Set defaults
            if signup_date is None:
                signup_date = datetime.now().isoformat()
            if last_login is None:
                last_login = signup_date
            if features_used is None:
                features_used = []
            
            # Calculate activity level
            activity_level = self._calculate_activity_level(last_login)
            
            cursor.execute('''
                INSERT INTO users 
                (user_id, email, name, signup_date, last_login, activity_level, 
                 features_used, subscription_type, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, email, name, signup_date, last_login, activity_level,
                json.dumps(features_used), subscription_type, datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added user: {email} (ID: {user_id})")
            return user_id
            
        except sqlite3.IntegrityError:
            logger.warning(f"User with email {email} already exists")
            raise ValueError(f"User with email {email} already exists")
        except Exception as e:
            logger.error(f"Failed to add user {email}: {e}")
            raise
    
    def update_user(self, email: str, user_data: Dict[str, Any]) -> bool:
        """
        Update existing user data
        
        Args:
            email: User email address
            user_data: Dict of user fields to update
            
        Returns:
            True if successful, False if user not found
        """
        try:
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
            if not cursor.fetchone():
                conn.close()
                return False
            
            # Build update query
            update_fields = []
            update_values = []
            
            for field, value in user_data.items():
                if field in ['email', 'name', 'signup_date', 'last_login', 'subscription_type']:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
                elif field == 'features_used':
                    update_fields.append("features_used = ?")
                    update_values.append(json.dumps(value) if isinstance(value, list) else value)
                elif field == 'last_login':
                    update_fields.append("last_login = ?")
                    update_fields.append("activity_level = ?")
                    update_values.append(value)
                    update_values.append(self._calculate_activity_level(value))
            
            if update_fields:
                update_fields.append("updated_at = ?")
                update_values.append(datetime.now().isoformat())
                update_values.append(email)  # For WHERE clause
                
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE email = ?"
                cursor.execute(query, update_values)
                
                conn.commit()
                logger.debug(f"Updated user: {email}")
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user {email}: {e}")
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email address
        
        Args:
            email: User email address
            
        Returns:
            User data dict or None if not found
        """
        try:
            conn = sqlite3.connect(self.user_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, email, name, signup_date, last_login, activity_level,
                       features_used, subscription_type, created_at, updated_at
                FROM users 
                WHERE email = ?
            ''', (email,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'user_id': row[0],
                    'email': row[1],
                    'name': row[2],
                    'signup_date': row[3],
                    'last_login': row[4],
                    'activity_level': row[5],
                    'features_used': json.loads(row[6]) if row[6] else [],
                    'subscription_type': row[7],
                    'created_at': row[8],
                    'updated_at': row[9]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user {email}: {e}")
            return None

    def send_marketing_email(self, template_name, subject, campaign_name=None, test_mode=False):
        """Send marketing email to all subscribed users"""
        cursor = self.conn.cursor()
        
        # Get template path
        template_path = os.path.join(os.path.dirname(__file__), 'email_templates', f'{template_name}.html')
        
        if not os.path.exists(template_path):
            logger.error(f"Template {template_name}.html not found")
            return {'sent': 0, 'failed': 1, 'skipped': 0}
        
        # Read template
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        sent_count = 0
        failed_count = 0
        skipped_count = 0
        
        if test_mode:
            # Send test email to BCC address
            test_html = html_content.replace('{{user_name}}', 'Test User')
            test_html = test_html.replace('{{unsubscribe_url}}', 'https://buildly.io/unsubscribe?token=test')
            test_html = test_html.replace('{{manage_preferences_url}}', 'https://buildly.io/preferences?token=test')
            
            if self._send_email(
                to_email=self.bcc_email,
                subject=f"[TEST] {subject}",
                html_content=test_html
            ):
                sent_count = 1
            else:
                failed_count = 1
        else:
            # Get all users 
            cursor.execute('''
                SELECT user_id, email, name 
                FROM users 
            ''')
            users = cursor.fetchall()
            
            for user_id, email, name in users:
                try:
                    # Check if user is unsubscribed
                    if self._is_email_unsubscribed(email):
                        skipped_count += 1
                        logger.info(f"Skipped sending to {email} (unsubscribed)")
                        continue
                    # Generate unsubscribe token
                    unsubscribe_token = self.generate_unsubscribe_token(user_id)
                    
                    # Replace template variables
                    personalized_html = html_content.replace('{{user_name}}', name or 'Valued User')
                    personalized_html = personalized_html.replace(
                        '{{unsubscribe_url}}', 
                        f'https://buildly.io/unsubscribe?token={unsubscribe_token}'
                    )
                    personalized_html = personalized_html.replace(
                        '{{manage_preferences_url}}', 
                        f'https://buildly.io/preferences?token={unsubscribe_token}'
                    )
                    
                    if self._send_email(
                        to_email=email,
                        subject=subject,
                        html_content=personalized_html
                    ):
                        sent_count += 1
                        # Log engagement
                        self._log_engagement(user_id, 'marketing', subject, 'sent')
                    else:
                        failed_count += 1
                        self._log_engagement(user_id, 'marketing', subject, 'failed')
                        
                except Exception as e:
                    logger.error(f"Failed to send marketing email to {email}: {e}")
                    failed_count += 1
        
        # Record campaign analytics
        if campaign_name and not test_mode:
            self.record_campaign_analytics(campaign_name, sent_count)
        
        return {
            'sent': sent_count,
            'failed': failed_count,
            'skipped': skipped_count
        }
    
    def generate_unsubscribe_token(self, user_id):
        """Generate a secure unsubscribe token"""
        import hashlib
        import time
        token_data = f"{user_id}:{time.time()}:{self.smtp_password}"
        return hashlib.sha256(token_data.encode()).hexdigest()[:32]
    
    def record_campaign_analytics(self, campaign_name, sent_count):
        """Record campaign analytics"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO email_analytics 
            (campaign_name, sent_count, created_at)
            VALUES (?, ?, ?)
        ''', (campaign_name, sent_count, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_email_analytics(self):
        """Get email analytics data"""
        cursor = self.conn.cursor()
        
        # Total users and subscription stats
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_subscribed = 1 OR is_subscribed IS NULL')
        subscribed_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_subscribed = 0')
        unsubscribed_users = cursor.fetchone()[0]
        
        # Email campaign stats
        cursor.execute('''
            SELECT campaign_name, 
                   SUM(sent_count) as total_sent,
                   SUM(opened_count) as total_opened,
                   SUM(clicked_count) as total_clicked,
                   SUM(unsubscribed_count) as total_unsubscribed,
                   created_at
            FROM email_analytics 
            GROUP BY campaign_name 
            ORDER BY created_at DESC
        ''')
        campaigns = cursor.fetchall()
        
        # Recent engagement history
        cursor.execute('''
            SELECT u.email, eh.email_type, eh.sent_at, eh.status
            FROM engagement_history eh
            JOIN users u ON eh.user_id = u.user_id
            ORDER BY eh.sent_at DESC
            LIMIT 100
        ''')
        recent_activity = cursor.fetchall()
        
        return {
            'user_stats': {
                'total_users': total_users,
                'subscribed_users': subscribed_users,
                'unsubscribed_users': unsubscribed_users,
                'subscription_rate': round((subscribed_users / total_users * 100) if total_users > 0 else 0, 2)
            },
            'campaigns': [{
                'name': campaign[0],
                'sent': campaign[1],
                'opened': campaign[2],
                'clicked': campaign[3], 
                'unsubscribed': campaign[4],
                'created_at': campaign[5]
            } for campaign in campaigns],
            'recent_activity': [{
                'email': activity[0],
                'type': activity[1],
                'sent_at': activity[2],
                'status': activity[3]
            } for activity in recent_activity]
        }
    
    def send_onboarding_help_email(self, test_mode=False):
        """Send onboarding help email to users who haven't completed setup"""
        cursor = self.conn.cursor()
        
        # Find users who signed up but haven't been active (incomplete onboarding)
        inactive_threshold = (datetime.now() - timedelta(days=3)).isoformat()  # 3+ days ago
        recent_signup = (datetime.now() - timedelta(days=30)).isoformat()  # Within last 30 days
        
        cursor.execute('''
            SELECT user_id, email, name, created_at
            FROM users 
            WHERE created_at >= ? 
            AND (last_login IS NULL OR last_login < ?)
            AND (last_reengagement_email IS NULL OR last_reengagement_email < ?)
            ORDER BY created_at DESC
        ''', (recent_signup, inactive_threshold, inactive_threshold))
        
        incomplete_users = cursor.fetchall()
        
        # Get template
        template_path = os.path.join(os.path.dirname(__file__), 'email_templates', 'onboarding_help.html')
        
        if not os.path.exists(template_path):
            logger.error("Onboarding help template not found")
            return {'sent': 0, 'failed': 1, 'skipped': 0}
        
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        sent_count = 0
        failed_count = 0
        skipped_count = 0
        
        if test_mode:
            # Send test email
            test_html = html_content.replace('{{user_name}}', 'Test User')
            test_html = test_html.replace('{{unsubscribe_url}}', 'https://buildly.io/unsubscribe.html?email=test@buildly.io')
            test_html = test_html.replace('{{manage_preferences_url}}', 'https://buildly.io/unsubscribe.html?email=test@buildly.io')
            
            if self._send_email(
                to_email=self.bcc_email,
                subject="[TEST] Need help getting started with Buildly? We're here! 🤝",
                html_content=test_html
            ):
                sent_count = 1
                logger.info("Test onboarding help email sent successfully")
            else:
                failed_count = 1
                logger.error("Failed to send test onboarding help email")
        else:
            logger.info(f"Found {len(incomplete_users)} users needing onboarding help")
            
            for user_id, email, name, created_at in incomplete_users:
                try:
                    # Check if user is unsubscribed
                    if self._is_email_unsubscribed(email):
                        skipped_count += 1
                        logger.info(f"Skipped onboarding help email to {email} (unsubscribed)")
                        continue
                    # Personalize template
                    personalized_html = html_content.replace('{{user_name}}', name or 'there')
                    personalized_html = personalized_html.replace(
                        '{{unsubscribe_url}}', 
                        f'https://buildly.io/unsubscribe.html?email={email}'
                    )
                    personalized_html = personalized_html.replace(
                        '{{manage_preferences_url}}', 
                        f'https://buildly.io/unsubscribe.html?email={email}'
                    )
                    
                    # Send email
                    if self._send_email(
                        to_email=email,
                        subject=f"Need help getting started with Buildly? We're here! 🤝",
                        html_content=personalized_html
                    ):
                        sent_count += 1
                        
                        # Update last reengagement email timestamp
                        cursor.execute('''
                            UPDATE users SET last_reengagement_email = ?
                            WHERE user_id = ?
                        ''', (datetime.now().isoformat(), user_id))
                        
                        # Record in engagement history
                        cursor.execute('''
                            INSERT INTO engagement_history 
                            (user_id, campaign_type, email_subject, sent_at, status)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (user_id, 'onboarding_help', 'Need help getting started with Buildly? We\'re here! 🤝', datetime.now().isoformat(), 'sent'))
                        
                        logger.info(f"Onboarding help email sent to {email}")
                        
                    else:
                        failed_count += 1
                        logger.error(f"Failed to send onboarding help email to {email}")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error sending onboarding help email to {email}: {e}")
            
            self.conn.commit()
        
        # Record campaign analytics
        if sent_count > 0:
            self.record_campaign_analytics('Onboarding Help', sent_count)
        
        return {
            'sent': sent_count,
            'failed': failed_count,
            'skipped': skipped_count,
            'users_found': len(incomplete_users) if not test_mode else 1
        }


if __name__ == "__main__":
    # Example usage
    engagement_system = UserEngagementSystem()
    
    # Example: Import sample users
    sample_users = [
        {
            "user_id": "user_001",
            "email": "john.doe@example.com",
            "name": "John Doe",
            "signup_date": "2025-08-15",
            "last_login": "2025-09-29",
            "features_used": ["api_builder", "workflow_designer"],
            "subscription_type": "pro"
        },
        {
            "user_id": "user_002", 
            "email": "jane.smith@example.com",
            "name": "Jane Smith",
            "signup_date": "2025-07-01",
            "last_login": "2025-08-15",
            "features_used": ["ui_builder"],
            "subscription_type": "free"
        }
    ]

    def send_marketing_email(self, template_name, subject, campaign_name=None, test_mode=False):
        """Send marketing email to all subscribed users"""
        cursor = self.conn.cursor()
        
        # Get template path
        template_path = os.path.join(os.path.dirname(__file__), 'email_templates', f'{template_name}.html')
        
        if not os.path.exists(template_path):
            logger.error(f"Template {template_name}.html not found")
            return {'sent': 0, 'failed': 1, 'skipped': 0}
        
        # Read template
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        sent_count = 0
        failed_count = 0
        skipped_count = 0
        
        if test_mode:
            # Send test email to BCC address
            test_html = html_content.replace('{{user_name}}', 'Test User')
            test_html = test_html.replace('{{unsubscribe_url}}', 'https://buildly.io/unsubscribe?token=test')
            test_html = test_html.replace('{{manage_preferences_url}}', 'https://buildly.io/preferences?token=test')
            
            if self.send_email(
                to_email=self.bcc_email,
                subject=f"[TEST] {subject}",
                html_content=test_html
            ):
                sent_count = 1
            else:
                failed_count = 1
        else:
            # Get subscribed users
            cursor.execute('''
                SELECT user_id, email, name 
                FROM users 
                WHERE is_subscribed = 1 OR is_subscribed IS NULL
            ''')
            users = cursor.fetchall()
            
            for user_id, email, name in users:
                try:
                    # Generate unsubscribe token
                    unsubscribe_token = self.generate_unsubscribe_token(user_id)
                    
                    # Replace template variables
                    personalized_html = html_content.replace('{{user_name}}', name or 'Valued User')
                    personalized_html = personalized_html.replace(
                        '{{unsubscribe_url}}', 
                        f'https://buildly.io/unsubscribe?token={unsubscribe_token}'
                    )
                    personalized_html = personalized_html.replace(
                        '{{manage_preferences_url}}', 
                        f'https://buildly.io/preferences?token={unsubscribe_token}'
                    )
                    
                    if self.send_email(
                        to_email=email,
                        subject=subject,
                        html_content=personalized_html
                    ):
                        sent_count += 1
                        # Log engagement
                        self.log_engagement(user_id, 'marketing', 'sent')
                    else:
                        failed_count += 1
                        self.log_engagement(user_id, 'marketing', 'failed')
                        
                except Exception as e:
                    logger.error(f"Failed to send marketing email to {email}: {e}")
                    failed_count += 1
        
        # Record campaign analytics
        if campaign_name and not test_mode:
            self.record_campaign_analytics(campaign_name, sent_count)
        
        return {
            'sent': sent_count,
            'failed': failed_count,
            'skipped': skipped_count
        }
    
    def generate_unsubscribe_token(self, user_id):
        """Generate a secure unsubscribe token"""
        import hashlib
        import time
        token_data = f"{user_id}:{time.time()}:{self.smtp_password}"
        return hashlib.sha256(token_data.encode()).hexdigest()[:32]
    
    def record_campaign_analytics(self, campaign_name, sent_count):
        """Record campaign analytics"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO email_analytics 
            (campaign_name, sent_count, created_at)
            VALUES (?, ?, ?)
        ''', (campaign_name, sent_count, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_email_analytics(self):
        """Get email analytics data"""
        cursor = self.conn.cursor()
        
        # Total users and subscription stats
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_subscribed = 1 OR is_subscribed IS NULL')
        subscribed_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_subscribed = 0')
        unsubscribed_users = cursor.fetchone()[0]
        
        # Email campaign stats
        cursor.execute('''
            SELECT campaign_name, 
                   SUM(sent_count) as total_sent,
                   SUM(opened_count) as total_opened,
                   SUM(clicked_count) as total_clicked,
                   SUM(unsubscribed_count) as total_unsubscribed,
                   created_at
            FROM email_analytics 
            GROUP BY campaign_name 
            ORDER BY created_at DESC
        ''')
        campaigns = cursor.fetchall()
        
        # Recent engagement history
        cursor.execute('''
            SELECT u.email, eh.email_type, eh.sent_at, eh.status
            FROM engagement_history eh
            JOIN users u ON eh.user_id = u.user_id
            ORDER BY eh.sent_at DESC
            LIMIT 100
        ''')
        recent_activity = cursor.fetchall()
        
        return {
            'user_stats': {
                'total_users': total_users,
                'subscribed_users': subscribed_users,
                'unsubscribed_users': unsubscribed_users,
                'subscription_rate': round((subscribed_users / total_users * 100) if total_users > 0 else 0, 2)
            },
            'campaigns': [{
                'name': campaign[0],
                'sent': campaign[1],
                'opened': campaign[2],
                'clicked': campaign[3], 
                'unsubscribed': campaign[4],
                'created_at': campaign[5]
            } for campaign in campaigns],
            'recent_activity': [{
                'email': activity[0],
                'type': activity[1],
                'sent_at': activity[2],
                'status': activity[3]
            } for activity in recent_activity]
        }


# Example usage (commented out for library use)
if __name__ == "__main__":
    # Sample test data for demonstration
    sample_users = [
        {
            "user_id": "user_001", 
            "email": "john.doe@example.com",
            "name": "John Doe",
            "signup_date": "2025-06-15",
            "last_login": "2025-09-25",
            "features_used": ["api_gateway", "microservices"], 
            "subscription_type": "premium"
        },
        {
            "user_id": "user_002", 
            "email": "jane.smith@example.com",
            "name": "Jane Smith",
            "signup_date": "2025-07-01",
            "last_login": "2025-08-15",
            "features_used": ["ui_builder"],
            "subscription_type": "free"
        }
    ]
    
    engagement_system = UserEngagementSystem()
    engagement_system.import_users_from_platform(sample_users)
    
    # Get engagement stats
    stats = engagement_system.get_engagement_stats()
    print("Engagement Stats:", json.dumps(stats, indent=2))