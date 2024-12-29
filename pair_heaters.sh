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
    sleep 2
    echo "agent on"
    sleep 2
    echo "default-agent"
    sleep 2
) | bluetoothctl

for HEATER in $HEATERS; do
  log "Processing heater: $HEATER"

  # Check if the device is already paired
  PAIRED=$(bluetoothctl info $HEATER | grep "Paired: yes")

  if [ ! -z "$PAIRED" ]; then
   # Attempt to connect first
	 	log "Attempting to connect already paired device: $HEATER"
		bluetoothctl connect $HEATER
		sleep 2  # Wait 2 seconds to allow connection to establish

		# Check if the device is now connected
		if bluetoothctl info $HEATER | grep -q "Connected: yes"; then
        log "Device $HEATER is already connectable. Skipping..."
        bluetoothctl disconnect $HEATER
				log "Disconnecting $HEATER to free it for the Python script."
				sleep 2
				continue
    fi

    # If paired but not connectable, remove and retry pairing
    log "Device $HEATER is paired but not connectable. Removing..."
    bluetoothctl remove $HEATER
  fi

  # Attempt pairing if not connectable
  log "Attempting to pair $HEATER"
  (
      echo "pair $HEATER"
      sleep 2
      echo $PIN
      sleep 2
			echo "trust $HEATER"
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
