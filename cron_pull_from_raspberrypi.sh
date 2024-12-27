#!/bin/bash

LOG_FILE=~/git-pull.log
TIMESTAMP=$(date +%Y-%m-%d_%H:%M:%S)

log_message() {
  echo "[$TIMESTAMP] $*" >> "$LOG_FILE"
}

cd ~/heater-control || {
  log_message "ERROR: Failed to change directory to ~/heater-control"
  exit 1
}

# Pull updates and capture the output
PULL_OUTPUT=$(git pull origin main 2>&1)
PULL_STATUS=$?

log_message "$PULL_OUTPUT"

if [[ $PULL_STATUS -eq 0 ]]; then
  # Check if there are updates
  if echo "$PULL_OUTPUT" | grep -q 'Already up to date'; then
    log_message "Already up to date"
  elif echo "$PULL_OUTPUT" | grep -q 'Fast-forward'; then
    # Changes detected—proceed to build and restart the container
    COMMIT_HASH=$(git rev-parse HEAD)
    log_message "Updated to commit: $COMMIT_HASH"

    # Rebuild the Docker image
    docker build -t heater-controller . 2>&1 | tee -a "$LOG_FILE"
    BUILD_STATUS=$?
    if [[ $BUILD_STATUS -eq 0 ]]; then
        # Restart the container
        docker stop heater-controller 2>&1 | tee -a "$LOG_FILE"
        docker rm heater-controller 2>&1 | tee -a "$LOG_FILE"
        docker run -d --name heater-controller --restart unless-stopped --privileged -v /var/run/dbus:/var/run/dbus heater-controller 2>&1 | tee -a "$LOG_FILE"
        log_message "Container restarted successfully"
    else
        log_message "ERROR: Docker build failed"
    fi
  else
    log_message "No clear updates detected, but no errors reported."
  fi
else
  log_message "ERROR: Git pull failed"
fi

exit $PULL_STATUS
