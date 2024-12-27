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
    6: "Manual (Heating Element Temp)",  # Hex: 06
    8: "Schedule (Heating Element Temp)"  # Hex: 08
}


# Helper: Decode temperature values
def decode_temperature(data):
    # Decode 4 bytes: [current_temp, target_temp]
    current_temp = ((data[0] * 255) + data[1]) / 10
    target_temp = ((data[2] * 255) + data[3]) / 10
    return round(current_temp, 1), round(target_temp, 1)


# Helper: Encode target temperature
def encode_temperature(temp):
    # Convert Celsius to Terma format (0.1°C scaling)
    temp_value = int(temp * 10)
    first_byte = temp_value // 255
    second_byte = temp_value % 255
    return first_byte.to_bytes(1, 'little') + second_byte.to_bytes(1, 'little')


# Read heater settings
async def read_heater_settings():
    async with BleakClient(DEVICE_ADDRESS) as client:
        print("Connected to heater")

        # Read current mode with bit masking
        mode = await client.read_gatt_char(MODE_UUID)
        print(f"Raw Mode Data: {mode.hex()}")  # Log raw mode bytes
        decoded_mode = int.from_bytes(mode, byteorder='little')
        masked_mode = decoded_mode & 0x0F  # Apply mask for lower 4 bits
        print(f"Decoded Mode Value: {decoded_mode}")
        print(f"Masked Mode Value: {masked_mode}")
        print(f"Current Mode: {MODES.get(masked_mode, f'Unknown ({masked_mode})')}")


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
        await client.write_gatt_char(MODE_UUID, bytes.fromhex("06"))
        print(f"Mode set to {MODES.get(mode, 'Unknown')}")

# Set target temperature and mode
async def set_target_temperature(target_temp, mode):
    async with BleakClient(DEVICE_ADDRESS) as client:
        print("Connected to heater")

        # Encode and write mode first
        if mode == "HEAT":
            await client.write_gatt_char(MODE_UUID, bytes.fromhex("06"))
        elif mode == "AUTO":
            await client.write_gatt_char(MODE_UUID, bytes.fromhex("08"))
        elif mode == "OFF":
            await client.write_gatt_char(MODE_UUID, bytes.fromhex("00"))

        print(f"Mode set to {MODES.get(mode, 'Unknown')}")

        # Encode and write temperature
        encoded_temp = b'\x00\x00' + encode_temperature(target_temp)
        await client.write_gatt_char(HEAT_TEMP_UUID, encoded_temp)
        print(f"Set target temperature to {target_temp}°C in mode {mode}")

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
