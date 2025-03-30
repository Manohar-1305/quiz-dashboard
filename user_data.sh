#!/bin/bash

# Exit on any error and enable debugging (logs every command)
set -e
set -x

# Install ansible
sudo apt-add-repository ppa:ansible/ansible -y
sudo apt update -y
sudo apt install ansible -y

sudo apt-get install -y python3-pip
pip3 install PyMySQL


# Define log file in the present directory
LOG_FILE="$(pwd)/setup.log"

# Redirect all output (stdout & stderr) to the log file while displaying it on the terminal
exec > >(tee -a "$LOG_FILE") 2>&1

# Function to log messages (for extra manual logs with timestamps)
log() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

log "Starting MySQL self-SSH setup"

# Create a user
user_name="app-user"
user_home="/home/$user_name"
user_ssh_dir="$user_home/.ssh"
ssh_key_path="$user_ssh_dir/authorized_keys"

# Ensure the user exists
if ! id "$user_name" &>/dev/null; then
  sudo adduser --disabled-password --gecos "" "$user_name"
  log "User $user_name created successfully."
else
  log "User $user_name already exists."
fi

# Grant sudo access
echo "$user_name ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/$user_name

# Create SSH directory
sudo -u "$user_name" mkdir -p "$user_ssh_dir"
sudo chmod 700 "$user_ssh_dir"

# Generate an SSH key pair for self-login
if [ ! -f "$user_ssh_dir/id_rsa" ]; then
  sudo -u "$user_name" ssh-keygen -t rsa -b 4096 -f "$user_ssh_dir/id_rsa" -N ""
fi

# Allow self-SSH by adding the public key to authorized_keys
sudo -u "$user_name" cat "$user_ssh_dir/id_rsa.pub" >> "$ssh_key_path"
sudo chmod 600 "$ssh_key_path"
sudo chown -R "$user_name:$user_name" "$user_home"

log "SSH self-access setup completed for $user_name"

# Verify SSH connection
log "Verifying SSH self-access..."
su - "$user_name" -c "ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa localhost 'echo SSH Connection Successful'"

log "MySQL server is now able to SSH into itself."
