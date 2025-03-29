#!/bin/bash

LOG_FILE="/var/log/setup_quiz_dashboard.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Starting setup at $(date)"

sudo DEBIAN_FRONTEND=noninteractive apt update -y
sudo DEBIAN_FRONTEND=noninteractive apt install python3-pip -y
sudo DEBIAN_FRONTEND=noninteractive apt install -y python3.10-venv

echo "Creating application directory..."
mkdir -p /root/app
cd /root/app

echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Updating package lists..."
sudo DEBIAN_FRONTEND=noninteractive apt update -y

echo "Installing dependencies..."
sudo DEBIAN_FRONTEND=noninteractive apt install -y pkg-config libmysqlclient-dev

echo "Cloning repository..."
git clone https://github.com/Manohar-1305/quiz-dashboard.git

echo "Installing Python dependencies..."
pip install -r /root/app/quiz-dashboard/requirements.txt

# Reload systemd, enable, and start the service
echo "Reloading systemd and starting the service..."
sudo systemctl daemon-reload
sudo systemctl enable quiz-dashboard
sudo systemctl restart quiz-dashboard

# Check service status
echo "Checking service status..."
if ! sudo systemctl status quiz-dashboard --no-pager; then
    echo "Service failed. Checking logs..."
    journalctl -u quiz-dashboard --no-pager --since "10 minutes ago"
fi
echo "Setup completed at $(date)"
