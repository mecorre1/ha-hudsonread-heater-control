from bleak import BleakClient, BleakError
import asyncio

# 2024-12-26T21:03:06.291629861Z Found device: Terma Wireless, Address: CC:22:37:11:30:EC
# 2024-12-26T21:03:06.291661582Z Found device: Terma Wireless, Address: CC:22:37:11:5D:02
# 2024-12-26T21:03:06.291725433Z Found device: Terma Wireless, Address: CC:22:37:11:1E:84
# 2024-12-26T21:03:06.291819395Z Found device: Terma Wireless, Address: CC:22:37:11:26:4F
# 2024-12-26T21:03:06.291847246Z Found device: Terma Wireless, Address: CC:22:37:11:1E:40


# Bluetooth device address
DEVICE_ADDRESS = "CC:22:37:11:26:4F"

# UUIDs for heater characteristics
ROOM_TEMP_UUID = "D97352B1-D19E-11E2-9E96-0800200C9A66"
HEAT_TEMP_UUID = "D97352B2-D19E-11E2-9E96-0800200C9A66"
MODE_UUID = "D97352B3-D19E-11E2-9E96-0800200C9A66"

# Operating modes
MODES = {
    0: "Off",
    5: "Manual (Room Temp)",
    6: "Manual (Heating Element Temp)"
}

# Helper: Decode temperature values
def decode_temperature(data):
    current_temp = ((data[1] << 8) | data[0]) / 10
    target_temp = ((data[3] << 8) | data[2]) / 10
    return round(current_temp, 1), round(target_temp, 1)

# Helper: Encode target temperature
def encode_temperature(target_temp):
    temp_value = int(target_temp * 10)
    return temp_value.to_bytes(2, 'little')

# Read heater settings
async def read_heater_settings():
    async with BleakClient(DEVICE_ADDRESS) as client:
        print("Connected to heater")

        # Read current mode with bit masking
        mode = await client.read_gatt_char(MODE_UUID)
        print(f"Raw Mode Value: {mode}") # To compare against raw data
        mode = int.from_bytes(mode, byteorder='little') & 0x0F  # Mask unexpected bits
        print(f"Current Mode: {MODES.get(mode, 'Unknown')}")

        # Read room temperature
        room_temp = await client.read_gatt_char(ROOM_TEMP_UUID)
        current_temp, target_temp = decode_temperature(room_temp)
        print(f"Room Temp - Current: {current_temp}°C, Target: {target_temp}°C")

        # Read heating element temperature
        heat_temp = await client.read_gatt_char(HEAT_TEMP_UUID)
        current_temp, target_temp = decode_temperature(heat_temp)
        print(f"Heating Element - Current: {current_temp}°C, Target: {target_temp}°C")

# Set mode
async def set_mode(mode):
    async with BleakClient(DEVICE_ADDRESS) as client:
        # Write the mode value
        await client.write_gatt_char(MODE_UUID, mode.to_bytes(1, 'little'))
        print(f"Mode set to {MODES.get(mode, 'Unknown')}")

# Set target temperature and mode
async def set_target_temperature(target_temp, mode):
    async with BleakClient(DEVICE_ADDRESS) as client:
        print("Connected to heater")

        # Update the mode first
        await client.write_gatt_char(MODE_UUID, mode.to_bytes(1, 'little'))
        print(f"Mode set to {MODES.get(mode, 'Unknown')}")

        # Encode temperature
        encoded_temp = b'\x00\x00' + encode_temperature(target_temp)

        # Write temperature to appropriate characteristic
        if mode == 5:  # Room temp mode
            await client.write_gatt_char(ROOM_TEMP_UUID, encoded_temp)
        elif mode == 6:  # Heating element temp mode
            await client.write_gatt_char(HEAT_TEMP_UUID, encoded_temp)

        print(f"Set target temperature to {target_temp}°C in mode {MODES.get(mode, 'Unknown')}")

# Main interactive menu
if __name__ == "__main__":
    while True:
        print("\nOptions:")
        print("  r - Read heater settings")
        print("  m - Set mode")
        print("  t - Set target temperature")
        print("  q - Quit")

        action = input("Choose action: ").strip().lower()

        if action == "r":
            asyncio.run(read_heater_settings())
        elif action == "m":
            print("\nAvailable Modes:")
            for k, v in MODES.items():
                print(f"  {k}: {v}")
            mode = int(input("Enter mode: "))
            asyncio.run(set_mode(mode))
        elif action == "t":
            temp = float(input("Enter target temperature (°C): "))
            print("\nAvailable Modes:")
            for k, v in MODES.items():
                print(f"  {k}: {v}")
            mode = int(input("Enter mode (5 for room, 6 for heating element): "))
            asyncio.run(set_target_temperature(temp, mode))
        elif action == "q":
            print("Exiting...")
            break
        else:
            print("Invalid action. Try again.")
