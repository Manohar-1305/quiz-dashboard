#!/bin/bash

LOG_FILE="/var/log/setup_quiz_dashboard.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Starting setup at $(date)"

# Update system and install dependencies
sudo DEBIAN_FRONTEND=noninteractive apt update -y
sudo DEBIAN_FRONTEND=noninteractive apt install python3-pip -y
sudo DEBIAN_FRONTEND=noninteractive apt install -y python3.10-venv pkg-config libmysqlclient-dev git

# Create application directory
echo "Creating application directory..."
mkdir -p /root/app
cd /root/app

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Clone the repository
echo "Cloning repository..."
git clone https://github.com/Manohar-1305/quiz-dashboard.git

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r /root/app/quiz-dashboard/requirements.txt

# Create systemd service file
echo "Creating systemd service..."
cat <<EOF | sudo tee /etc/systemd/system/quiz-dashboard.service
[Unit]
Description=Quiz Dashboard Service
After=network.target

[Service]
User=root
WorkingDirectory=/root/app/quiz-dashboard
ExecStart=/root/app/quiz-dashboard/venv/bin/python /root/app/quiz-dashboard/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, enable, and start the service
echo "Enabling and starting the service..."
sudo systemctl daemon-reload
sudo systemctl enable quiz-dashboard
sudo systemctl start quiz-dashboard
sudo systemctl status quiz-dashboard

# Check service status
echo "Checking service status..."
sudo systemctl status quiz-dashboard --no-pager

echo "Setup completed at $(date)"
