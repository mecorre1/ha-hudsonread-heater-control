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

# Start scanning
bluetoothctl <<EOF
scan on
agent on
default-agent
EOF

for HEATER in $HEATERS; do
  log "Processing heater: $HEATER"

  # Check if the device is already paired
  PAIRED=$(bluetoothctl paired-devices | grep $HEATER)

  if [ ! -z "$PAIRED" ]; then
   # Attempt to connect first
		bluetoothctl connect $HEATER
		sleep 2  # Wait 2 seconds to allow connection to establish

		# Check if the device is now connected
		if bluetoothctl info $HEATER | grep -q "Connected: yes"; then
        log "Device $HEATER is already connectable. Skipping..."
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
      sleep 1
      echo "trust $HEATER"
      sleep 1
      echo "connect $HEATER"
      sleep 2
  ) | bluetoothctl

  # Verify connection
  if bluetoothctl info $HEATER | grep -q "Connected: yes"; then
      log "Successfully paired and connected to $HEATER"

      # **Disconnect the heater to allow Python script access**
      log "Disconnecting $HEATER to free it for the Python script."
      bluetoothctl disconnect $HEATER
  else
      log "Failed to connect to $HEATER"
  fi
done

log "Pairing process completed!"
