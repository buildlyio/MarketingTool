#!/bin/bash

# Buildly Automation Setup Script
# This script sets up the automation system for lead generation and outreach

echo "🚀 Setting up Buildly Automation System..."

# Create necessary directories
mkdir -p automation/logs
mkdir -p automation/data

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r automation/requirements.txt

# Create initial data files if they don't exist
if [ ! -f "automation/leads.json" ]; then
    echo "[]" > automation/leads.json
    echo "✅ Created leads.json"
fi

if [ ! -f "automation/outreach_log.json" ]; then
    echo "[]" > automation/outreach_log.json
    echo "✅ Created outreach_log.json"
fi

# Make scripts executable
chmod +x automation/cron.sh
chmod +x automation/main.py
chmod +x automation/lead_sourcing.py
chmod +x automation/email_sender.py
chmod +x automation/status_report.py

echo "✅ Made scripts executable"

# Check if .env file exists and has required variables
if [ ! -f ".env" ]; then
    echo "❌ .env file not found! Please create it with the required variables."
    echo "   See README_AUTOMATION.md for details."
    exit 1
fi

# Check for required environment variables
required_vars=("SMTP_SERVER" "SMTP_USER" "SMTP_PASSWORD")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env || grep -q "^${var}=$" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "⚠️  Warning: The following required variables are missing or empty in .env:"
    printf '%s\n' "${missing_vars[@]}"
    echo "   Please update .env before running the automation."
fi

# Set up cron job
echo ""
echo "📅 To set up daily automation via cron, run:"
echo "   crontab -e"
echo ""
echo "Then add this line to run daily at 9 AM:"
echo "   0 9 * * * /Users/$(whoami)/Projects/buildly/website/automation/cron.sh"
echo ""

# Create a test run script
cat > automation/test_run.sh << 'EOF'
#!/bin/bash
echo "🧪 Running Buildly Automation Test..."
cd /Users/$(whoami)/Projects/buildly/website
python3 automation/main.py
echo "✅ Test run completed. Check automation/automation.log for details."
EOF

chmod +x automation/test_run.sh

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your actual API keys and credentials"
echo "2. Run 'automation/test_run.sh' to test the system"
echo "3. Set up the cron job for daily automation"
echo "4. Integrate opt-out handling with Django (see DJANGO_INTEGRATION.md)"
echo ""
echo "📚 Documentation:"
echo "   - README_AUTOMATION.md - Main documentation"
echo "   - DJANGO_INTEGRATION.md - Django integration guide"
echo ""
