"""
Buildly Labs API Client for User Engagement System
Handles authentication and user data synchronization with Buildly platform
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BuildlyUser:
    """Data class for Buildly user information"""
    core_user_uuid: str
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    create_date: str
    edit_date: str
    organization_uuid: str
    subscription_active: str = ""
    user_type: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def signup_date(self) -> datetime:
        """Parse create_date to datetime"""
        if not self.create_date:
            return datetime.now()
        return datetime.fromisoformat(self.create_date.replace('Z', '+00:00'))
    
    @property
    def last_activity_date(self) -> datetime:
        """Parse edit_date to datetime for activity tracking"""
        if not self.edit_date:
            return self.signup_date
        return datetime.fromisoformat(self.edit_date.replace('Z', '+00:00'))


class BuildlyAPIClient:
    """Client for interacting with Buildly Labs API"""
    
    def __init__(self, base_url: str = "https://labs-api.buildly.io", 
                 username: str = None, password: str = None):
        self.base_url = base_url.rstrip('/')
        self.username = username or os.getenv('BUILDLY_USERNAME')
        self.password = password or os.getenv('BUILDLY_PASSWORD')
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.session = requests.Session()
        
        if not self.username or not self.password:
            raise ValueError("Buildly username and password must be provided via parameters or environment variables")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Buildly API using username/password
        Returns True if successful, False otherwise
        """
        try:
            auth_data = {
                "username": self.username,
                "password": self.password
            }
            
            response = self.session.post(
                f"{self.base_url}/token/",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.access_token = data.get('access')
                self.refresh_token = data.get('refresh')
                
                if self.access_token:
                    # Set token expiration (JWT tokens typically expire in 1 hour)
                    self.token_expires_at = datetime.now() + timedelta(minutes=55)
                    
                    # Update session headers
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json'
                    })
                    
                    logger.info("Successfully authenticated with Buildly API")
                    return True
                    
            logger.error(f"Authentication failed: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def refresh_access_token(self) -> bool:
        """
        Refresh the access token using refresh token
        Returns True if successful, False otherwise
        """
        if not self.refresh_token:
            logger.warning("No refresh token available, re-authenticating")
            return self.authenticate()
        
        try:
            response = self.session.post(
                f"{self.base_url}/token/refresh/",
                json={"refresh": self.refresh_token}
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.access_token = data.get('access')
                
                if self.access_token:
                    self.token_expires_at = datetime.now() + timedelta(minutes=55)
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                    logger.info("Successfully refreshed access token")
                    return True
            
            logger.warning(f"Token refresh failed: {response.status_code}, re-authenticating")
            return self.authenticate()
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}, re-authenticating")
            return self.authenticate()
    
    def ensure_authenticated(self) -> bool:
        """
        Ensure we have a valid authentication token
        Returns True if authenticated, False otherwise
        """
        if not self.access_token:
            return self.authenticate()
        
        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            return self.refresh_access_token()
        
        return True
    
    def get_users(self, organization_uuid: str = None, page: int = 1) -> Dict[str, Any]:
        """
        Get users from Buildly API
        
        Args:
            organization_uuid: Filter users by organization
            page: Page number for pagination
            
        Returns:
            Dict containing user data and pagination info
        """
        if not self.ensure_authenticated():
            raise Exception("Failed to authenticate with Buildly API")
        
        params = {"page": page}
        if organization_uuid:
            params["organization__organization_uuid"] = organization_uuid
        
        try:
            response = self.session.get(
                f"{self.base_url}/coreuser/",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle direct array response
                if isinstance(data, list):
                    user_list = data
                    total_count = len(data)
                else:
                    # Handle paginated response
                    user_list = data.get('results', [])
                    total_count = data.get('count', len(user_list))
                
                # Parse users into BuildlyUser objects
                users = []
                for user_data in user_list:
                    try:
                        # Extract organization UUID from nested organization object
                        org_uuid = ""
                        if user_data.get('organization'):
                            org_uuid = user_data['organization'].get('organization_uuid', '')
                        
                        user = BuildlyUser(
                            core_user_uuid=user_data.get('core_user_uuid', ''),
                            username=user_data.get('username', ''),
                            email=user_data.get('email', ''),
                            first_name=user_data.get('first_name', ''),
                            last_name=user_data.get('last_name', ''),
                            is_active=user_data.get('is_active', False),
                            create_date=user_data.get('create_date', ''),
                            edit_date=user_data.get('edit_date', ''),
                            organization_uuid=org_uuid,
                            subscription_active=user_data.get('subscription_active', ''),
                            user_type=user_data.get('user_type')
                        )
                        users.append(user)
                    except Exception as e:
                        logger.warning(f"Failed to parse user data: {user_data}, error: {str(e)}")
                
                return {
                    'users': users,
                    'count': total_count,
                    'next': None if isinstance(data, list) else data.get('next'),
                    'previous': None if isinstance(data, list) else data.get('previous'),
                    'total_pages': 1 if isinstance(data, list) else (total_count + 19) // 20
                }
                
            else:
                logger.error(f"Failed to get users: {response.status_code} - {response.text}")
                raise Exception(f"API request failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            raise
    
    def get_all_users(self, organization_uuid: str = None) -> List[BuildlyUser]:
        """
        Get all users from all pages
        
        Args:
            organization_uuid: Filter users by organization
            
        Returns:
            List of all BuildlyUser objects
        """
        all_users = []
        page = 1
        
        while True:
            try:
                result = self.get_users(organization_uuid=organization_uuid, page=page)
                users = result.get('users', [])
                
                if not users:
                    break
                
                all_users.extend(users)
                
                # Check if there are more pages
                if not result.get('next'):
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching users page {page}: {str(e)}")
                break
        
        logger.info(f"Retrieved {len(all_users)} total users from Buildly API")
        return all_users
    
    def get_user_by_id(self, user_id: str) -> Optional[BuildlyUser]:
        """
        Get a specific user by their ID
        
        Args:
            user_id: User ID (core_user_uuid or numeric ID)
            
        Returns:
            BuildlyUser object or None if not found
        """
        if not self.ensure_authenticated():
            raise Exception("Failed to authenticate with Buildly API")
        
        try:
            response = self.session.get(f"{self.base_url}/coreuser/{user_id}/")
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Extract organization UUID
                org_uuid = ""
                if user_data.get('organization'):
                    org_uuid = user_data['organization'].get('organization_uuid', '')
                
                return BuildlyUser(
                    core_user_uuid=user_data.get('core_user_uuid', ''),
                    username=user_data.get('username', ''),
                    email=user_data.get('email', ''),
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    is_active=user_data.get('is_active', False),
                    create_date=user_data.get('create_date', ''),
                    edit_date=user_data.get('edit_date', ''),
                    organization_uuid=org_uuid,
                    subscription_active=user_data.get('subscription_active', ''),
                    user_type=user_data.get('user_type')
                )
            
            elif response.status_code == 404:
                logger.warning(f"User {user_id} not found")
                return None
            
            else:
                logger.error(f"Failed to get user {user_id}: {response.status_code} - {response.text}")
                raise Exception(f"API request failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            raise
    
    def get_current_user(self) -> Optional[BuildlyUser]:
        """
        Get current authenticated user information
        
        Returns:
            BuildlyUser object or None if failed
        """
        if not self.ensure_authenticated():
            raise Exception("Failed to authenticate with Buildly API")
        
        try:
            response = self.session.get(f"{self.base_url}/coreuser/me/")
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle direct user data (not paginated)
                if 'core_user_uuid' in data:
                    user_data = data
                else:
                    # Handle paginated results
                    results = data.get('results', [])
                    if results:
                        user_data = results[0]
                    else:
                        user_data = None
                
                if user_data:
                    
                    # Extract organization UUID
                    org_uuid = ""
                    if user_data.get('organization'):
                        org_uuid = user_data['organization'].get('organization_uuid', '')
                    
                    return BuildlyUser(
                        core_user_uuid=user_data.get('core_user_uuid', ''),
                        username=user_data.get('username', ''),
                        email=user_data.get('email', ''),
                        first_name=user_data.get('first_name', ''),
                        last_name=user_data.get('last_name', ''),
                        is_active=user_data.get('is_active', False),
                        create_date=user_data.get('create_date', ''),
                        edit_date=user_data.get('edit_date', ''),
                        organization_uuid=org_uuid,
                        subscription_active=user_data.get('subscription_active', ''),
                        user_type=user_data.get('user_type')
                    )
            
            logger.error(f"Failed to get current user: {response.status_code} - {response.text}")
            return None
                
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            return None
    
    def get_organizations(self) -> List[Dict[str, Any]]:
        """
        Get list of organizations
        
        Returns:
            List of organization data dictionaries
        """
        if not self.ensure_authenticated():
            raise Exception("Failed to authenticate with Buildly API")
        
        try:
            response = self.session.get(f"{self.base_url}/organization/")
            
            if response.status_code == 200:
                data = response.json()
                # Handle direct array response
                if isinstance(data, list):
                    return data
                else:
                    return data.get('results', [])
            
            else:
                logger.error(f"Failed to get organizations: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting organizations: {str(e)}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test the API connection and authentication
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.authenticate():
                current_user = self.get_current_user()
                if current_user:
                    logger.info(f"API connection test successful - authenticated as {current_user.email}")
                    return True
            
            logger.error("API connection test failed")
            return False
            
        except Exception as e:
            logger.error(f"API connection test error: {str(e)}")
            return False


class BuildlyUserSync:
    """Handles synchronization between Buildly API and local user engagement database"""
    
    def __init__(self, api_client: BuildlyAPIClient, engagement_system):
        self.api_client = api_client
        self.engagement_system = engagement_system
    
    def sync_users(self, organization_uuid: str = None) -> Dict[str, int]:
        """
        Sync users from Buildly API to local database
        
        Args:
            organization_uuid: Optional organization filter
            
        Returns:
            Dict with sync statistics
        """
        logger.info("Starting user sync from Buildly API")
        
        try:
            # Get all users from API
            buildly_users = self.api_client.get_all_users(organization_uuid)
            
            stats = {
                'total_api_users': len(buildly_users),
                'new_users': 0,
                'updated_users': 0,
                'errors': 0
            }
            
            for buildly_user in buildly_users:
                try:
                    # Check if user exists in local database
                    existing_user = self.engagement_system.get_user_by_email(buildly_user.email)
                    
                    user_data = {
                        'email': buildly_user.email,
                        'name': buildly_user.full_name,
                        'signup_date': buildly_user.signup_date.isoformat(),
                        'last_login': buildly_user.last_activity_date.isoformat(),
                        'organization': buildly_user.organization_uuid,
                        'user_type': buildly_user.user_type or 'User',
                        'is_active': buildly_user.is_active,
                        'external_id': buildly_user.core_user_uuid
                    }
                    
                    if existing_user:
                        # Update existing user
                        self.engagement_system.update_user(buildly_user.email, user_data)
                        stats['updated_users'] += 1
                        logger.debug(f"Updated user: {buildly_user.email}")
                    else:
                        # Add new user
                        self.engagement_system.add_user(**user_data)
                        stats['new_users'] += 1
                        logger.info(f"Added new user: {buildly_user.email}")
                
                except Exception as e:
                    logger.error(f"Error syncing user {buildly_user.email}: {str(e)}")
                    stats['errors'] += 1
            
            logger.info(f"User sync completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"User sync failed: {str(e)}")
            raise
    
    def sync_new_users_only(self, organization_uuid: str = None, days_back: int = 7) -> Dict[str, int]:
        """
        Sync only newly created users from the last N days
        
        Args:
            organization_uuid: Optional organization filter
            days_back: Number of days to look back for new users
            
        Returns:
            Dict with sync statistics
        """
        logger.info(f"Syncing new users from last {days_back} days")
        
        try:
            buildly_users = self.api_client.get_all_users(organization_uuid)
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            new_users = [
                user for user in buildly_users 
                if user.signup_date >= cutoff_date
            ]
            
            stats = {
                'total_new_users': len(new_users),
                'added_users': 0,
                'existing_users': 0,
                'errors': 0
            }
            
            for buildly_user in new_users:
                try:
                    existing_user = self.engagement_system.get_user_by_email(buildly_user.email)
                    
                    if not existing_user:
                        user_data = {
                            'email': buildly_user.email,
                            'name': buildly_user.full_name,
                            'signup_date': buildly_user.signup_date.isoformat(),
                            'last_login': buildly_user.last_activity_date.isoformat(),
                            'organization': buildly_user.organization_uuid,
                            'user_type': buildly_user.user_type or 'User',
                            'is_active': buildly_user.is_active,
                            'external_id': buildly_user.core_user_uuid
                        }
                        
                        self.engagement_system.add_user(**user_data)
                        stats['added_users'] += 1
                        logger.info(f"Added new user: {buildly_user.email}")
                    else:
                        stats['existing_users'] += 1
                        logger.debug(f"User already exists: {buildly_user.email}")
                
                except Exception as e:
                    logger.error(f"Error processing new user {buildly_user.email}: {str(e)}")
                    stats['errors'] += 1
            
            logger.info(f"New user sync completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"New user sync failed: {str(e)}")
            raise