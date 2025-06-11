#!/bin/bash
# Script to ensure port 6379 (Redis) is free before running tests

echo "Freeing Redis port 6379..."

# 1. Remove any Docker containers using port 6379
echo "Removing Docker containers using port 6379..."
docker ps -q --filter "publish=6379" | xargs -r docker rm -f || true
docker ps -q --filter "expose=6379" | xargs -r docker rm -f || true
docker ps -a --filter "status=exited" | xargs -r docker rm || true

# 2. Stop system Redis services based on platform
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  echo "Detected macOS: Stopping Homebrew Redis service..."
  brew services stop redis || true
  pkill redis-server || true
else
  # Linux/Ubuntu
  echo "Detected Linux: Stopping system Redis service..."
  sudo service redis-server stop || true
  sudo systemctl stop redis-server || true
  sudo killall redis-server || true
fi

# 3. Force kill any process still using port 6379
echo "Checking for processes still using port 6379..."
if command -v lsof >/dev/null 2>&1; then
  if lsof -i :6379 >/dev/null 2>&1; then
    echo "Process still using port 6379, forcefully killing..."
    lsof -i :6379 | awk 'NR!=1 {print $2}' | xargs -r kill -9 || true
    sleep 1
  fi
  
  # Final verification
  if lsof -i :6379 >/dev/null 2>&1; then
    echo "WARNING: Port 6379 is still in use!"
    lsof -i :6379
    exit 1
  else
    echo "Success: Port 6379 is free and ready for use"
  fi
else
  echo "Warning: 'lsof' command not found, skipping port check"
fi

exit 0
