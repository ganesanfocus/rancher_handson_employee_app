#!/bin/bash

echo "=== Starting Nginx Container ==="

# Stop and remove existing container if it already exists to avoid naming conflicts
docker stop my-nginx-container 2>/dev/null || true
docker rm my-nginx-container 2>/dev/null || true

# Run the new Nginx container
docker run -d -p 8080:80 --name my-nginx-container nginx:latest

echo "=== Nginx is running! ==="
echo "Access it at http://<your-vm-ip>:8080 (make sure port 8080 is open in Azure NSG)"