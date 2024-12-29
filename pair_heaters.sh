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

# Read rooms.json and extract devices with room info
ROOMS=$(jq -r 'to_entries[] | {room: .key, heaters: .value}' $CONFIG_FILE)

# Start Scanning
(
    echo "scan on"
    sleep 1
    echo "agent on"
    sleep 1
    echo "default-agent"
    sleep 1
) | bluetoothctl

declare -A SUMMARY  # Store results for summary

for ROOM in $(echo "$ROOMS" | jq -c '.'); do
  ROOM_NAME=$(echo "$ROOM" | jq -r '.room')
  HEATERS=$(echo "$ROOM" | jq -r '.heaters[]')

  INDEX=1
  for HEATER in $HEATERS; do
    log "Processing heater $INDEX in room $ROOM_NAME (ID: $HEATER)"

    # Check if the device is already paired
    PAIRED=$(bluetoothctl info $HEATER | grep "Paired: yes")

    if [ ! -z "$PAIRED" ]; then
      # Attempt to connect up to 3 times
      RETRIES=3
      while [ $RETRIES -gt 0 ]; do
        log "Attempting to connect to paired heater $INDEX in room $ROOM_NAME (ID: $HEATER) (Retries left: $RETRIES)"
        bluetoothctl connect $HEATER
        sleep 4  # Increased delay to 4 seconds

        # Log device info for debugging
        DEVICE_INFO=$(bluetoothctl info $HEATER)
        log "Device Info After Connect Attempt for $HEATER: $DEVICE_INFO"

        # Check if connected
        if echo "$DEVICE_INFO" | grep -q "Connected: yes"; then
          log "Heater $INDEX in room $ROOM_NAME (ID: $HEATER) is connectable. Skipping..."
          bluetoothctl disconnect $HEATER
          log "Disconnecting heater $INDEX in room $ROOM_NAME (ID: $HEATER) to free it for the Python script."
          sleep 2
          SUMMARY["$ROOM_NAME - Heater $INDEX (ID: $HEATER)"]="Connectable"
          continue 2  # Skip the rest and move to the next heater
        fi

        RETRIES=$((RETRIES - 1))
      done

      # If retries fail, remove the device and prompt user
      log "Failed to connect to heater $INDEX in room $ROOM_NAME (ID: $HEATER) after retries. Removing device."
      bluetoothctl remove $HEATER
      sleep 2
    fi

    # Prompt user for pairing mode
    while true; do
      read -p "Put heater $INDEX in room $ROOM_NAME (ID: $HEATER) in pairing mode (blinking light). Ready? (y/n): " CONFIRM
      if [[ "$CONFIRM" == "y" ]]; then
        break
      elif [[ "$CONFIRM" == "n" ]]; then
        log "User skipped pairing for heater $INDEX in room $ROOM_NAME (ID: $HEATER)."
        SUMMARY["$ROOM_NAME - Heater $INDEX (ID: $HEATER)"]="Skipped by User"
        continue 2  # Skip to next heater
      else
        echo "Invalid response. Please type 'y' or 'n'."
      fi
    done

    # Attempt pairing
    log "Attempting to pair heater $INDEX in room $ROOM_NAME (ID: $HEATER)"
    (
        echo "pair $HEATER"
        sleep 2
        echo $PIN
        sleep 2
        echo "trust $HEATER"
        sleep 2
        echo "connect $HEATER"
        sleep 2
    ) | bluetoothctl

    # Verify connection
    if bluetoothctl info $HEATER | grep -q "Connected: yes"; then
        log "Successfully paired and connected heater $INDEX in room $ROOM_NAME (ID: $HEATER)"

        # Disconnect to allow Python script access
        log "Disconnecting heater $INDEX in room $ROOM_NAME (ID: $HEATER) to free it for the Python script."
        bluetoothctl disconnect $HEATER
        sleep 2
        SUMMARY["$ROOM_NAME - Heater $INDEX (ID: $HEATER)"]="Paired and Connectable"
    else
        log "Failed to connect heater $INDEX in room $ROOM_NAME (ID: $HEATER)"
        SUMMARY["$ROOM_NAME - Heater $INDEX (ID: $HEATER)"]="Failed"
    fi

    INDEX=$((INDEX + 1))
  done
done

# Print Summary
log "Pairing process completed!"
log "Heater Pairing Summary:"
for KEY in "${!SUMMARY[@]}"; do
  log "$KEY - ${SUMMARY[$KEY]}"
done
