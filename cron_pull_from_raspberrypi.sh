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

git pull origin main 2>&1 | tee -a "$LOG_FILE"
PULL_STATUS=$?

if [[ $PULL_STATUS -eq 0 ]]; then
  if grep -q 'Already up to date' "$LOG_FILE"; then
      log_message "Already up to date"
  else
    COMMIT_HASH=$(git rev-parse HEAD)
    log_message "Updated to commit: $COMMIT_HASH"
    docker build -t heater-controller . 2>&1 | tee -a "$LOG_FILE"
    BUILD_STATUS=$?
    if [[ $BUILD_STATUS -eq 0 ]]; then
        docker stop heater-controller 2>&1 | tee -a "$LOG_FILE"
        docker rm heater-controller 2>&1 | tee -a "$LOG_FILE"
        docker run -d --name heater-controller --restart unless-stopped --privileged -v /var/run/dbus:/var/run/dbus heater-controller 2>&1 | tee -a "$LOG_FILE"
    else
        log_message "Error during docker build"
    fi
  fi
else
  log_message "ERROR: Git pull failed"
fi

exit $PULL_STATUS