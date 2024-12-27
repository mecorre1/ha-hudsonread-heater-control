from bleak import BleakClient
import asyncio

# 2024-12-26T21:03:06.291629861Z Found device: Terma Wireless, Address: CC:22:37:11:30:EC
# 2024-12-26T21:03:06.291661582Z Found device: Terma Wireless, Address: CC:22:37:11:5D:02
# 2024-12-26T21:03:06.291725433Z Found device: Terma Wireless, Address: CC:22:37:11:1E:84
# 2024-12-26T21:03:06.291819395Z Found device: Terma Wireless, Address: CC:22:37:11:26:4F
# 2024-12-26T21:03:06.291847246Z Found device: Terma Wireless, Address: CC:22:37:11:1E:40


# Heater Bluetooth Address (Replace this with your device address)
DEVICE_ADDRESS = "CC:22:37:11:26:4F"

# UUIDs for characteristics
ROOM_TEMP_UUID = "D97352B1-D19E-11E2-9E96-0800200C9A66"
HEAT_TEMP_UUID = "D97352B2-D19E-11E2-9E96-0800200C9A66"
MODE_UUID = "D97352B3-D19E-11E2-9E96-0800200C9A66"

# Modes
MODES = {
    0: "Off",
    5: "Manual (Room Temp)",
    6: "Manual (Heating Element Temp)",
    7: "Schedule (Room Temp)",
    8: "Schedule (Heating Element Temp)"
}

# --- Helper Functions ---

# Encode temperature to 4 bytes
def encode_temperature(temp):
    value = int(temp * 10)
    return value.to_bytes(2, 'big')

# Decode 4-byte temperature response
def decode_temperature(data):
    current_temp = ((data[0] * 256) + data[1]) / 10
    target_temp = ((data[2] * 256) + data[3]) / 10
    return current_temp, target_temp


# --- Control Functions ---

# Read current settings
async def read_heater_settings():
    async with BleakClient(DEVICE_ADDRESS) as client:
        print("Connected to heater")

        # Read current mode
        mode = await client.read_gatt_char(MODE_UUID)
        mode = int.from_bytes(mode, byteorder='little')
        print(f"Current Mode: {MODES.get(mode, 'Unknown')}")

        # Read room temperature
        room_temp = await client.read_gatt_char(ROOM_TEMP_UUID)
        current_temp, target_temp = decode_temperature(room_temp)
        print(f"Room Temp - Current: {current_temp}°C, Target: {target_temp}°C")

        # Read heating element temperature
        heat_temp = await client.read_gatt_char(HEAT_TEMP_UUID)
        current_temp, target_temp = decode_temperature(heat_temp)
        print(f"Heating Element - Current: {current_temp}°C, Target: {target_temp}°C")

# Set operating mode
async def set_mode(mode):
    async with BleakClient(DEVICE_ADDRESS) as client:
        await client.write_gatt_char(MODE_UUID, mode.to_bytes(1, 'little'))
        print(f"Mode set to {MODES.get(mode, 'Unknown')}")

# Set target temperature
async def set_target_temperature(temp, mode):
    async with BleakClient(DEVICE_ADDRESS) as client:
        encoded_temp = b'\x00\x00' + encode_temperature(temp)
        if mode == 5:  # Room temp mode
            await client.write_gatt_char(ROOM_TEMP_UUID, encoded_temp)
        elif mode == 6:  # Heating element temp mode
            await client.write_gatt_char(HEAT_TEMP_UUID, encoded_temp)
        print(f"Set target temperature to {temp}°C in mode {MODES.get(mode, 'Unknown')}")

# --- Main Menu ---
if __name__ == "__main__":
    action = input("Choose action - read (r), set mode (m), or set temperature (t): ").strip().lower()
    if action == "r":
        asyncio.run(read_heater_settings())
    elif action == "m":
        mode = int(input(f"Enter mode ({MODES}): "))
        asyncio.run(set_mode(mode))
    elif action == "t":
        mode = int(input(f"Enter mode ({MODES}): "))
        temp = float(input("Enter target temperature: "))
        asyncio.run(set_target_temperature(temp, mode))
    else:
        print("Invalid action.")
