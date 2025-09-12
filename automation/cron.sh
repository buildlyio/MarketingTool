#!/bin/bash

# Buildly Marketing Automation & Dashboard Update Script
# This script runs the daily automation and updates the marketing dashboard

# Set the working directory
cd /Users/greglind/Projects/buildly/website

# Activate virtual environment if you have one
# source venv/bin/activate

# Run the main automation script (lead generation, outreach, reporting)
echo "$(date): Starting daily marketing automation" >> automation/cron.log
python3 automation/main.py

# Update the marketing dashboard with latest data
echo "$(date): Updating marketing dashboard" >> automation/cron.log
python3 automation/dashboard_generator.py

# Log the completion
echo "$(date): Buildly marketing automation and dashboard update completed" >> automation/cron.log
