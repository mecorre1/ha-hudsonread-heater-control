#!/bin/bash

CONFIG_FILE="rooms.json"
PIN="123456"

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Check if bluetoothctl is installed
if ! command -v bluetoothctl &> /dev/null; then
  log "ERROR: bluetoothctl not found!"
  exit 1
fi

# Read rooms.json and extract devices
HEATERS=$(jq -r '.[] | .[]' $CONFIG_FILE)

for HEATER in $HEATERS; do
  log "Processing heater: $HEATER"

  # Check if the device is already paired
  PAIRED=$(bluetoothctl devices Paired | grep $HEATER)

  # Remove device if already paired but not connected
  if [ ! -z "$PAIRED" ]; then
    log "Device $HEATER is already connected. Skipping..."
    continue
  fi
  # Pair and trust the device
  log "Attempting to pair $HEATER"
  (
    echo "scan on"
    echo "agent on"
    echo "default-agent"
    sleep 1
    echo "pair $HEATER"
    sleep 1
    echo $PIN
    sleep 1
    echo "trust $HEATER"
    echo "connect $HEATER"
  ) | bluetoothctl

  # Verify connection
  CONNECTED=$(bluetoothctl info $HEATER | grep "Connected: yes")
  if [ ! -z "$CONNECTED" ]; then
    log "Successfully paired and connected to $HEATER"
    (
    echo "disconnect $HEATER"
    echo "quit"
    ) | bluetoothctl
  else
    log "Failed to connect to $HEATER"
  fi
done

log "Pairing process completed!"
