#!/usr/bin/env python3
"""
Marketing Dashboard Generator for Buildly
Creates an HTML dashboard showing all marketing metrics and reports
"""

import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sys

# Add automation directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from status_report import StatusReporter

# Load environment variables
load_dotenv()

# Import advanced analytics
try:
    from advanced_analytics import AdvancedAnalytics
    ADVANCED_ANALYTICS_AVAILABLE = True
except ImportError:
    ADVANCED_ANALYTICS_AVAILABLE = False

class MarketingDashboard:
    def __init__(self):
        self.reporter = StatusReporter()
        
        # Initialize advanced analytics if available
        if ADVANCED_ANALYTICS_AVAILABLE:
            self.advanced_analytics = AdvancedAnalytics()
        else:
            self.advanced_analytics = None
        
    def load_recent_data(self):
        """Load recent marketing data from logs and reports"""
        data = {}
        
        # Get latest analytics data
        data['analytics'] = self.reporter.get_google_analytics_data()
        data['youtube'] = self.reporter.get_youtube_analytics()
        data['linkedin'] = self.reporter.get_linkedin_analytics()
        data['google_ads'] = self.reporter.get_google_ads_analytics()
        data['outreach'] = self.reporter.get_outreach_stats()
        data['leads'] = self.reporter.get_leads_stats()
        
        # Load advanced analytics if available
        if self.advanced_analytics:
            data['sales_funnel'] = self.advanced_analytics.get_sales_funnel_metrics()
            data['seo_content'] = self.advanced_analytics.get_content_seo_metrics()
            data['social_media_deep'] = self.advanced_analytics.get_social_media_deep_analytics()
            data['financial_roi'] = self.advanced_analytics.get_financial_roi_metrics()
            data['competitor_intel'] = self.advanced_analytics.get_competitor_intelligence()
            data['brand_sentiment'] = self.advanced_analytics.get_brand_sentiment_monitoring()
            data['geographic'] = self.advanced_analytics.get_geographic_market_data()
        
        # Load recent outreach history
        try:
            with open('automation/outreach_log.json', 'r') as f:
                outreach_log = json.load(f)
                # Get last 7 days of data
                week_ago = datetime.now() - timedelta(days=7)
                recent_outreach = [
                    entry for entry in outreach_log[-100:]  # Last 100 entries
                    if datetime.fromisoformat(entry['timestamp']) > week_ago
                ]
                data['recent_outreach'] = recent_outreach
        except FileNotFoundError:
            data['recent_outreach'] = []
        
        # Load leads data
        try:
            with open('automation/leads.json', 'r') as f:
                leads = json.load(f)
                # Get recent leads
                week_ago = datetime.now() - timedelta(days=7)
                recent_leads = [
                    lead for lead in leads[-50:]  # Last 50 leads
                    if datetime.fromisoformat(lead['discovered_date']) > week_ago
                ]
                data['recent_leads'] = recent_leads
        except FileNotFoundError:
            data['recent_leads'] = []
            
        return data
    
    def generate_dashboard_html(self):
        """Generate complete marketing dashboard HTML"""
        data = self.load_recent_data()
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Buildly Marketing Dashboard</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                }}
                .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
                .header {{ 
                    background: rgba(255,255,255,0.95); 
                    padding: 30px; 
                    border-radius: 15px; 
                    margin-bottom: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .header h1 {{ color: #667eea; font-size: 2.5em; margin-bottom: 10px; }}
                .header p {{ color: #666; font-size: 1.2em; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .card {{ 
                    background: rgba(255,255,255,0.95); 
                    padding: 25px; 
                    border-radius: 15px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                }}
                .card:hover {{ transform: translateY(-5px); }}
                .card h2 {{ color: #667eea; margin-bottom: 20px; display: flex; align-items: center; }}
                .card h2:before {{ content: '📊'; margin-right: 10px; font-size: 1.2em; }}
                .metric {{ 
                    display: inline-block; 
                    background: linear-gradient(135deg, #667eea, #764ba2); 
                    color: white; 
                    padding: 15px 20px; 
                    margin: 8px; 
                    border-radius: 10px; 
                    text-align: center; 
                    min-width: 120px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }}
                .metric-value {{ font-size: 24px; font-weight: bold; }}
                .metric-label {{ font-size: 12px; opacity: 0.9; text-transform: uppercase; }}
                .table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                .table th, .table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
                .table th {{ background: #f8f9fa; color: #667eea; font-weight: bold; }}
                .status-success {{ color: #28a745; }}
                .status-failed {{ color: #dc3545; }}
                .status-skipped {{ color: #ffc107; }}
                .refresh-time {{ text-align: center; margin-top: 30px; color: rgba(255,255,255,0.8); }}
                .error {{ background: #ffe6e6; color: #d63384; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                .chart-placeholder {{ 
                    background: #f8f9fa; 
                    height: 200px; 
                    border-radius: 10px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    color: #666; 
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Buildly Marketing Dashboard</h1>
                    <p>Real-time marketing metrics and lead generation analytics</p>
                    <p><strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="grid">
                    <!-- Email Outreach Overview -->
                    <div class="card">
                        <h2>📧 Email Outreach</h2>
                        <div class="metric">
                            <div class="metric-value">{data['outreach']['emails_sent_today']}</div>
                            <div class="metric-label">Sent Today</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data['outreach']['emails_failed_today']}</div>
                            <div class="metric-label">Failed</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data['outreach']['total_emails_sent']}</div>
                            <div class="metric-label">Total Sent</div>
                        </div>
                        
                        <h3>Source Breakdown</h3>
                        <table class="table">
                            <tr><th>Source</th><th>Emails</th></tr>
                            {self._generate_table_rows(data['outreach']['sources_breakdown'])}
                        </table>
                    </div>
                    
                    <!-- Lead Generation -->
                    <div class="card">
                        <h2>🎯 Lead Generation</h2>
                        <div class="metric">
                            <div class="metric-value">{data['leads']['new_leads_today']}</div>
                            <div class="metric-label">New Today</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data['leads']['total_leads']}</div>
                            <div class="metric-label">Total Leads</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data['leads']['total_sources']}</div>
                            <div class="metric-label">Sources</div>
                        </div>
                        
                        <h3>Recent Leads by Source</h3>
                        <table class="table">
                            <tr><th>Source</th><th>Leads</th></tr>
                            {self._generate_table_rows(data['leads']['leads_by_source'])}
                        </table>
                    </div>
                    
                    <!-- Website Analytics -->
                    <div class="card">
                        <h2>🌐 Website Analytics</h2>
                        <div class="metric">
                            <div class="metric-value">{data['analytics'].get('sessions', 'N/A')}</div>
                            <div class="metric-label">Sessions</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data['analytics'].get('users', 'N/A')}</div>
                            <div class="metric-label">Users</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data['analytics'].get('page_views', 'N/A')}</div>
                            <div class="metric-label">Page Views</div>
                        </div>
                        
                        {'<div class="error">⚠️ ' + data['analytics']['error'] + '</div>' if 'error' in data['analytics'] else '<div class="chart-placeholder">📈 Connect Google Analytics for detailed charts</div>'}
                    </div>
                    
                    <!-- YouTube Performance -->
                    <div class="card">
                        <h2>🎥 YouTube Performance</h2>
                        <div class="metric">
                            <div class="metric-value">{data['youtube'].get('views', 'N/A')}</div>
                            <div class="metric-label">Views</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data['youtube'].get('subscribers', 'N/A')}</div>
                            <div class="metric-label">Subscribers</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data['youtube'].get('watch_time', 'N/A')}</div>
                            <div class="metric-label">Watch Time</div>
                        </div>
                        
                        {'<div class="error">⚠️ ' + data['youtube']['error'] + '</div>' if 'error' in data['youtube'] else '<div class="chart-placeholder">📹 Connect YouTube Analytics for video insights</div>'}
                    </div>
                    
                    <!-- LinkedIn Marketing -->
                    <div class="card">
                        <h2>💼 LinkedIn Marketing</h2>
                        <div class="metric">
                            <div class="metric-value">{data['linkedin'].get('followers', 'N/A')}</div>
                            <div class="metric-label">Followers</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data['linkedin'].get('impressions', 'N/A')}</div>
                            <div class="metric-label">Impressions</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data['linkedin'].get('engagement_rate', 0):.1f}%</div>
                            <div class="metric-label">Engagement</div>
                        </div>
                        
                        {'<div class="error">⚠️ ' + data['linkedin']['error'] + '</div>' if 'error' in data['linkedin'] else '<div class="chart-placeholder">📊 Connect LinkedIn Marketing API for engagement analytics</div>'}
                    </div>
                    
                    <!-- Google Ads Performance -->
                    <div class="card">
                        <h2>🎯 Google Ads</h2>
                        <div class="metric">
                            <div class="metric-value">{data['google_ads'].get('impressions', 'N/A')}</div>
                            <div class="metric-label">Impressions</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data['google_ads'].get('clicks', 'N/A')}</div>
                            <div class="metric-label">Clicks</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${data['google_ads'].get('cost', 'N/A')}</div>
                            <div class="metric-label">Cost</div>
                        </div>
                        
                        {'<div class="error">⚠️ ' + data['google_ads']['error'] + '</div>' if 'error' in data['google_ads'] else '<div class="chart-placeholder">💰 Connect Google Ads API for campaign performance</div>'}
                    </div>
                </div>
                
                {self._generate_advanced_analytics_section(data) if self.advanced_analytics else ''}
                
                <!-- Recent Activity Section -->
                <div class="grid" style="margin-top: 30px;">
                    <div class="card" style="grid-column: 1 / -1;">
                        <h2>📈 Recent Outreach Activity</h2>
                        <table class="table">
                            <tr>
                                <th>Time</th>
                                <th>Email</th>
                                <th>Status</th>
                                <th>Source</th>
                                <th>Subject</th>
                            </tr>
                            {self._generate_recent_outreach_rows(data['recent_outreach'])}
                        </table>
                    </div>
                </div>
                
                <div class="grid" style="margin-top: 20px;">
                    <div class="card" style="grid-column: 1 / -1;">
                        <h2>🆕 Recent Leads</h2>
                        <table class="table">
                            <tr>
                                <th>Date</th>
                                <th>Email</th>
                                <th>Source</th>
                                <th>Keyword</th>
                                <th>Status</th>
                            </tr>
                            {self._generate_recent_leads_rows(data['recent_leads'])}
                        </table>
                    </div>
                </div>
                
                <div class="refresh-time">
                    <p>🔄 Dashboard auto-refreshes every 5 minutes | 
                    📧 Daily reports sent to {os.getenv('REPORT_EMAIL', 'greg@buildly.io')} | 
                    🚀 Automation runs daily at 9:00 AM</p>
                </div>
            </div>
            
            <script>
                // Auto-refresh every 5 minutes
                setTimeout(function() {{
                    location.reload();
                }}, 300000);
                
                // Add some interactivity
                document.querySelectorAll('.card').forEach(card => {{
                    card.addEventListener('click', function() {{
                        this.style.transform = 'scale(1.02)';
                        setTimeout(() => {{
                            this.style.transform = '';
                        }}, 200);
                    }});
                }});
            </script>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_table_rows(self, data_dict):
        """Generate HTML table rows from dictionary data"""
        if not data_dict:
            return '<tr><td colspan="2">No data available</td></tr>'
        
        rows = []
        for key, value in data_dict.items():
            rows.append(f'<tr><td>{key}</td><td>{value}</td></tr>')
        
        return ''.join(rows)
    
    def _generate_recent_outreach_rows(self, outreach_data):
        """Generate HTML rows for recent outreach activity"""
        if not outreach_data:
            return '<tr><td colspan="5">No recent outreach activity</td></tr>'
        
        rows = []
        for entry in outreach_data[-10:]:  # Last 10 entries
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%m/%d %H:%M')
            email = entry['email']
            status = entry['status']
            source = entry.get('details', {}).get('source', 'Unknown')
            subject = entry.get('details', {}).get('subject', 'N/A')[:50] + '...' if entry.get('details', {}).get('subject') else 'N/A'
            
            status_class = f'status-{status}'
            status_icon = {'sent': '✅', 'failed': '❌', 'skipped': '⏭️'}.get(status, '❓')
            
            rows.append(f'''
                <tr>
                    <td>{timestamp}</td>
                    <td>{email}</td>
                    <td class="{status_class}">{status_icon} {status.title()}</td>
                    <td>{source}</td>
                    <td>{subject}</td>
                </tr>
            ''')
        
        return ''.join(rows)
    
    def _generate_recent_leads_rows(self, leads_data):
        """Generate HTML rows for recent leads"""
        if not leads_data:
            return '<tr><td colspan="5">No recent leads</td></tr>'
        
        rows = []
        for lead in leads_data[-10:]:  # Last 10 leads
            date = datetime.fromisoformat(lead['discovered_date']).strftime('%m/%d')
            email = lead['email']
            source = lead.get('source', 'Unknown')
            keyword = lead.get('keyword_matched', 'N/A')
            status = lead.get('status', 'new')
            
            status_icon = {'new': '🆕', 'contacted': '📧', 'responded': '💬'}.get(status, '❓')
            
            rows.append(f'''
                <tr>
                    <td>{date}</td>
                    <td>{email}</td>
                    <td>{source}</td>
                    <td>{keyword}</td>
                    <td>{status_icon} {status.title()}</td>
                </tr>
            ''')
        
        return ''.join(rows)
    
    def _generate_advanced_analytics_section(self, data):
        """Generate advanced analytics dashboard section"""
        if not self.advanced_analytics:
            return ''
        
        return f'''
                <!-- Advanced Analytics Section -->
                <div class="grid" style="margin-top: 30px;">
                    <!-- Sales Funnel -->
                    <div class="card">
                        <h2>💰 Sales Funnel</h2>
                        <div class="metric">
                            <div class="metric-value">{data.get('sales_funnel', {}).get('conversion_rate', 'N/A')}%</div>
                            <div class="metric-label">Conversion Rate</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${data.get('sales_funnel', {}).get('avg_deal_size', 'N/A'):,}</div>
                            <div class="metric-label">Avg Deal Size</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data.get('sales_funnel', {}).get('sales_cycle_days', 'N/A')} days</div>
                            <div class="metric-label">Sales Cycle</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${data.get('sales_funnel', {}).get('pipeline_value', 'N/A'):,}</div>
                            <div class="metric-label">Pipeline Value</div>
                        </div>
                    </div>
                    
                    <!-- Financial ROI -->
                    <div class="card">
                        <h2>📊 Financial ROI</h2>
                        <div class="metric">
                            <div class="metric-value">${data.get('financial_roi', {}).get('cost_per_lead', 'N/A')}</div>
                            <div class="metric-label">Cost Per Lead</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">${data.get('financial_roi', {}).get('customer_acquisition_cost', 'N/A')}</div>
                            <div class="metric-label">Customer CAC</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data.get('financial_roi', {}).get('marketing_roi', 'N/A')}x</div>
                            <div class="metric-label">Marketing ROI</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data.get('financial_roi', {}).get('budget_utilization', 'N/A')}%</div>
                            <div class="metric-label">Budget Used</div>
                        </div>
                    </div>
                    
                    <!-- SEO & Content -->
                    <div class="card">
                        <h2>🔍 SEO & Content</h2>
                        <div class="metric">
                            <div class="metric-value">{data.get('seo_content', {}).get('organic_keywords', 'N/A'):,}</div>
                            <div class="metric-label">Keywords Tracked</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data.get('seo_content', {}).get('backlinks', 'N/A')}</div>
                            <div class="metric-label">Backlinks</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data.get('seo_content', {}).get('domain_authority', 'N/A')}</div>
                            <div class="metric-label">Domain Authority</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data.get('seo_content', {}).get('page_speed_score', 'N/A')}</div>
                            <div class="metric-label">Page Speed</div>
                        </div>
                    </div>
                    
                    <!-- Brand Sentiment -->
                    <div class="card">
                        <h2>🎭 Brand Sentiment</h2>
                        <div class="metric">
                            <div class="metric-value">{data.get('brand_sentiment', {}).get('brand_mentions', {}).get('total_this_week', 'N/A')}</div>
                            <div class="metric-label">Weekly Mentions</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data.get('brand_sentiment', {}).get('brand_mentions', {}).get('sentiment_breakdown', {}).get('positive', 'N/A')}%</div>
                            <div class="metric-label">Positive Sentiment</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data.get('brand_sentiment', {}).get('net_promoter_score', 'N/A')}</div>
                            <div class="metric-label">Net Promoter Score</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data.get('brand_sentiment', {}).get('brand_health_score', 'N/A')}/10</div>
                            <div class="metric-label">Brand Health</div>
                        </div>
                    </div>
                    
                    <!-- Competitor Intelligence -->
                    <div class="card">
                        <h2>🥊 Competitive Intel</h2>
                        <div class="metric">
                            <div class="metric-value">{data.get('competitor_intel', {}).get('market_position', {}).get('market_share', 'N/A')}%</div>
                            <div class="metric-label">Market Share</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">#{data.get('competitor_intel', {}).get('market_position', {}).get('competitive_rank', 'N/A')}</div>
                            <div class="metric-label">Market Rank</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data.get('competitor_intel', {}).get('opportunity_score', 'N/A')}/10</div>
                            <div class="metric-label">Opportunity Score</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{data.get('competitor_intel', {}).get('threat_level', 'N/A')}</div>
                            <div class="metric-label">Threat Level</div>
                        </div>
                    </div>
                    
                    <!-- Geographic Distribution -->
                    <div class="card">
                        <h2>🌍 Geographic Reach</h2>
                        <h3>Lead Distribution</h3>
                        <table class="table">
                            <tr><th>Region</th><th>Leads</th><th>Conversion %</th></tr>
                            {self._generate_geographic_rows(data.get('geographic', {}).get('lead_geography', {}))}
                        </table>
                    </div>
                </div>
        '''
    
    def _generate_geographic_rows(self, geographic_data):
        """Generate HTML rows for geographic distribution"""
        if not geographic_data:
            return '<tr><td colspan="3">No geographic data available</td></tr>'
        
        rows = []
        for region, info in geographic_data.items():
            if isinstance(info, dict):
                leads = info.get('leads', 0)
                conversion = info.get('conversion_rate', 0)
                rows.append(f'<tr><td>{region}</td><td>{leads}</td><td>{conversion}%</td></tr>')
        
        return ''.join(rows)
    
    def save_dashboard(self, filename='index.html'):
        """Save the dashboard to an HTML file"""
        html_content = self.generate_dashboard_html()
        with open(filename, 'w') as f:
            f.write(html_content)
        print(f"📊 Marketing dashboard saved to {filename}")

if __name__ == "__main__":
    dashboard = MarketingDashboard()
    dashboard.save_dashboard()
