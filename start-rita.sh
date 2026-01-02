#!/bin/bash
# Start RITA polling client

# Activate virtual environment
source ~/Desktop/venv/bin/activate

# Change to project directory
cd ~/Documents/GitHub/rita-pi

# Run polling client
python polling_client.py https://rita-pi-five.vercel.app/ pi-001 5
