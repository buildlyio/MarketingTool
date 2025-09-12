#!/usr/bin/env python3
"""
Lead Sourcing Module for Buildly Automation
Searches multiple sources for startups needing development help and project managers interested in AI
"""

import json
import requests
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LeadSourcing:
    def __init__(self, sources_file='automation/sources.json'):
        self.sources_file = sources_file
        self.sources = self.load_sources()
        self.leads = []
        
    def load_sources(self):
        """Load sources from JSON file"""
        try:
            with open(self.sources_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Sources file {self.sources_file} not found")
            return []
    
    def save_sources(self):
        """Save updated sources to JSON file"""
        with open(self.sources_file, 'w') as f:
            json.dump(self.sources, f, indent=2)
    
    def discover_new_sources(self):
        """Discover new startup directories and forums"""
        search_terms = [
            "startup directory",
            "entrepreneur forum",
            "indie hackers community",
            "startup showcase",
            "project manager community"
        ]
        
        new_sources = []
        for term in search_terms:
            try:
                # Use DuckDuckGo search (no API key required)
                search_url = f"https://duckduckgo.com/html/?q={term.replace(' ', '+')}"
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
                
                # Note: In production, you might want to use a proper search API
                # For now, we'll add some known sources manually
                pass
            except Exception as e:
                logger.error(f"Error discovering sources for {term}: {e}")
        
        # Add some additional known sources
        potential_new_sources = [
            {
                "name": "Hacker News Who's Hiring",
                "url": "https://news.ycombinator.com/item?id=whoishiring",
                "type": "job_board"
            },
            {
                "name": "Reddit Entrepreneur",
                "url": "https://www.reddit.com/r/Entrepreneur/",
                "type": "community"
            },
            {
                "name": "Founder Groups",
                "url": "https://foundergroups.com/",
                "type": "community"
            }
        ]
        
        # Check if sources are already in our list
        existing_urls = [source['url'] for source in self.sources]
        for source in potential_new_sources:
            if source['url'] not in existing_urls:
                self.sources.append(source)
                new_sources.append(source)
                logger.info(f"Added new source: {source['name']}")
        
        if new_sources:
            self.save_sources()
        
        return new_sources
    
    def extract_contact_info(self, text, url):
        """Extract email addresses and other contact info from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        return {
            'emails': list(set(emails)),  # Remove duplicates
            'source_url': url,
            'content_snippet': text[:500]  # First 500 chars for context
        }
    
    def search_startup_posts(self, source):
        """Search for relevant posts from a specific source"""
        leads = []
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
            response = requests.get(source['url'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Keywords to look for
                keywords = [
                    'need developer', 'looking for development', 'software development',
                    'need tech help', 'technical co-founder', 'CTO needed',
                    'project manager', 'AI implementation', 'don\'t know code',
                    'no-code solution', 'need technical guidance'
                ]
                
                # Search for posts containing keywords
                for keyword in keywords:
                    elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
                    
                    for element in elements[:5]:  # Limit to 5 per keyword
                        parent = element.parent
                        if parent:
                            post_text = parent.get_text(strip=True)
                            contact_info = self.extract_contact_info(post_text, source['url'])
                            
                            if contact_info['emails']:
                                lead = {
                                    'source': source['name'],
                                    'source_url': source['url'],
                                    'email': contact_info['emails'][0],  # Primary email
                                    'post_content': post_text[:1000],  # Store for personalization
                                    'keyword_matched': keyword,
                                    'discovered_date': datetime.now().isoformat(),
                                    'status': 'new'
                                }
                                leads.append(lead)
                
                logger.info(f"Found {len(leads)} leads from {source['name']}")
                
            else:
                logger.warning(f"Could not access {source['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error searching {source['name']}: {e}")
        
        # Add delay to be respectful to servers
        time.sleep(2)
        return leads
    
    def find_leads(self):
        """Main method to find leads from all sources"""
        logger.info("Starting lead sourcing...")
        
        # First, discover new sources
        new_sources = self.discover_new_sources()
        logger.info(f"Discovered {len(new_sources)} new sources")
        
        # Search all sources for leads
        all_leads = []
        for source in self.sources:
            source_leads = self.search_startup_posts(source)
            all_leads.extend(source_leads)
        
        # Remove duplicates based on email
        unique_leads = {}
        for lead in all_leads:
            email = lead['email']
            if email not in unique_leads:
                unique_leads[email] = lead
        
        self.leads = list(unique_leads.values())
        logger.info(f"Found {len(self.leads)} unique leads")
        
        return self.leads
    
    def save_leads(self, filename='automation/leads.json'):
        """Save leads to JSON file"""
        try:
            # Load existing leads
            try:
                with open(filename, 'r') as f:
                    existing_leads = json.load(f)
            except FileNotFoundError:
                existing_leads = []
            
            # Merge with new leads (avoid duplicates)
            existing_emails = [lead['email'] for lead in existing_leads]
            new_leads = [lead for lead in self.leads if lead['email'] not in existing_emails]
            
            all_leads = existing_leads + new_leads
            
            with open(filename, 'w') as f:
                json.dump(all_leads, f, indent=2)
            
            logger.info(f"Saved {len(new_leads)} new leads to {filename}")
            return len(new_leads)
            
        except Exception as e:
            logger.error(f"Error saving leads: {e}")
            return 0

if __name__ == "__main__":
    sourcing = LeadSourcing()
    leads = sourcing.find_leads()
    new_count = sourcing.save_leads()
    print(f"Lead sourcing complete. Found {len(leads)} total leads, {new_count} new ones.")
