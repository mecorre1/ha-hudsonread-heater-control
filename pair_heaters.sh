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

# Start Scanning
(
    echo "scan on"
    sleep 1
    echo "agent on"
    sleep 1
    echo "default-agent"
    sleep 1
) | bluetoothctl

for HEATER in $HEATERS; do
  log "Processing heater: $HEATER"

  # Check if the device is already paired
  PAIRED=$(bluetoothctl info $HEATER | grep "Paired: yes")

  if [ ! -z "$PAIRED" ]; then
    # Attempt to connect up to 3 times
    RETRIES=3
    while [ $RETRIES -gt 0 ]; do
      log "Attempting to connect to already paired device: $HEATER (Retries left: $RETRIES)"
      bluetoothctl connect $HEATER
      sleep 4  # Increased delay to 4 seconds

      # Log the full device info for debugging
      DEVICE_INFO=$(bluetoothctl info $HEATER)
      log "Device Info After Connect Attempt: $DEVICE_INFO"

      # Check if the device is now connected
      if echo "$DEVICE_INFO" | grep -q "Connected: yes"; then
        log "Device $HEATER is already connectable. Skipping..."
        bluetoothctl disconnect $HEATER
        log "Disconnecting $HEATER to free it for the Python script."
        sleep 2
        continue 2  # Skip the rest and move to the next heater
      fi

      RETRIES=$((RETRIES - 1))
    done

    # If retries fail, remove the device and prompt user
    log "Failed to connect to $HEATER after retries. Removing device."
    bluetoothctl remove $HEATER
    sleep 2
	fi

	# Prompt user to put heater in pairing mode
	while true; do
		read -p "Please put heater $HEATER in pairing mode (blinking light). Ready? (yes/no): " CONFIRM
		if [[ "$CONFIRM" == "yes" ]]; then
			break
		elif [[ "$CONFIRM" == "no" ]]; then
			log "User chose to skip pairing for $HEATER."
			continue 2  # Skip to the next heater
		else
			echo "Invalid response. Please type 'yes' or 'no'."
		fi
	done

  # Attempt pairing if not connectable
  log "Attempting to pair $HEATER"
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
      log "Successfully paired and connected to $HEATER"

      # **Disconnect the heater to allow Python script access**
      log "Disconnecting $HEATER to free it for the Python script."
      bluetoothctl disconnect $HEATER
      sleep 2
  else
      log "Failed to connect to $HEATER"
  fi
done

log "Pairing process completed!"
