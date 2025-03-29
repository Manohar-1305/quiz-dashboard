#!/bin/bash

LOG_FILE="/root/setup_log.txt"

# Function to log output with timestamp
log_message() {
    echo "$(date) - $1" | tee -a $LOG_FILE
}

apt-get update -y

# Install git
log_message "Installing git..."
sudo apt update -y && sudo apt install git -y && log_message "Git installed successfully" || log_message "Git installation failed"

# Update system packages
log_message "Updating system packages..."
sudo apt update -y && log_message "System update completed successfully" || log_message "System update failed"

# Install python3-pip
log_message "Installing python3-pip..."
sudo apt install python3-pip -y && log_message "python3-pip installed successfully" || log_message "python3-pip installation failed"

# Create app directory
log_message "Creating application directory..."
mkdir -p /root/quiz-dashboard && log_message "Application directory created" || log_message "Directory creation failed"

# Navigate to app directory
cd /root/quiz-dashboard
log_message "Changed directory to /root/quiz-dashboard"

# Create Python virtual environment
log_message "Installing python3.10-venv..."
sudo apt install -y python3.10-venv && log_message "python3.10-venv installed successfully" || log_message "python3.10-venv installation failed"

log_message "Creating virtual environment..."
python3 -m venv venv && log_message "Virtual environment created successfully" || log_message "Virtual environment creation failed"

# Activate virtual environment
log_message "Activating virtual environment..."
source venv/bin/activate && log_message "Virtual environment activated" || log_message "Virtual environment activation failed"

# Install additional dependencies
log_message "Installing pkg-config and libmysqlclient-dev..."
sudo apt install -y pkg-config libmysqlclient-dev && log_message "Dependencies installed successfully" || log_message "Dependency installation failed"

# Export MySQL flags
export MYSQLCLIENT_CFLAGS="$(pkg-config --cflags mysqlclient)"
export MYSQLCLIENT_LDFLAGS="$(pkg-config --libs mysqlclient)"

# Clone the repository only if it doesn't already exist
if [ ! -d "/root/quiz-dashboard/.git" ]; then
    log_message "Cloning repository from GitHub..."
    git clone https://github.com/Manohar-1305/quiz-dashboard.git && log_message "Repository cloned successfully" || log_message "Repository cloning failed"
else
    log_message "Repository already exists, skipping cloning."
fi

# Change to the cloned directory
cd quiz-dashboard
log_message "Changed directory to quiz-dashboard"

# Install Python dependencies
log_message "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt && log_message "Dependencies installed successfully" || log_message "Dependency installation failed"

# Ensure log directory exists
mkdir -p /root/quiz-dashboard/
touch /root/quiz-dashboard//app.log
chown root:root /root/quiz-dashboard/app.log
chmod 666 /root/quiz-dashboard/app.log

# Create systemd service for Flask app
log_message "Creating systemd service for Flask app..."
sudo bash -c 'cat <<EOF > /etc/systemd/system/flaskapp.service
[Unit]
Description=flask app
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/quiz-dashboard/
Environment="PATH=/root/quiz-dashboard/venv/bin"
ExecStart=/root/quiz-dashboard/venv/bin/python3 /root/quiz-dashboard/app.py

[Install]
WantedBy=multi-user.target
EOF' && log_message "Systemd service created successfully" || log_message "Service creation failed"

# Reload systemd and enable the service
log_message "Reloading systemd and enabling Flask app service..."
sudo systemctl daemon-reload && log_message "Systemd daemon reloaded" || log_message "Daemon reload failed"
sudo systemctl enable flaskapp.service && log_message "Flask app service enabled" || log_message "Flask app service enable failed"

# Start the Flask app service
log_message "Starting Flask app service..."
sudo systemctl start flaskapp.service && log_message "Flask app service started" || log_message "Flask app service start failed"

# Check Flask service status
log_message "Checking Flask app service status..."
systemctl status flaskapp.service
