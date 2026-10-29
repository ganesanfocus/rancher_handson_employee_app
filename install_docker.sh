#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== Step 1: Removing old Docker versions (if any) ==="
sudo apt-get remove -y docker docker-engine docker.io containerd runc || true

echo "=== Step 2: Installing prerequisites and GPG key ==="
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "=== Step 3: Setting up the Docker repository ==="
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

echo "=== Step 4: Installing Docker Engine and Compose plugin ==="
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "=== Step 5: Configuring non-root user access ==="
if ! getent group docker > /dev/null; then
    sudo groupadd docker
fi
sudo usermod -aG docker $USER

echo "=== Step 6: Verifying Docker Versions ==="
docker --version
docker compose version

# ==============================================================================
# OPTIONAL: Uncomment the lines below when you want to pull and start Nginx
# ==============================================================================
# echo "=== Step 7 (Optional): Pulling and starting Nginx ==="
# docker pull nginx:latest
# docker run -d -p 8080:80 --name my-nginx-container nginx:latest
# echo "Nginx is running! Access it at http://<your-vm-ip>:8080"
# ==============================================================================

echo "=== Installation Complete! ==="
echo "To apply group changes without logging out your terminal session, run: newgrp docker"