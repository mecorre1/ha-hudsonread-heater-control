import json
import asyncio
from bleak import BleakClient

# UUIDs for heater characteristics
ROOM_TEMP_UUID = "d97352b1-d19e-11e2-9e96-0800200c9a66"
HEAT_TEMP_UUID = "d97352b2-d19e-11e2-9e96-0800200c9a66"
MODE_UUID = "d97352b3-d19e-11e2-9e96-0800200c9a66"

# Modes Mapping
MODES = {
    0: "Off",
    5: "Manual (Room Temp)",
    6: "Manual (Heating Element Temp)",
    33: "Manual (Heating Element Temp - Verified)"
}
MODE_ENCODINGS = {
    "Off": bytes([0x00]),
    "Manual (Room Temp)": bytes([0x05]),
    "Manual (Heating Element Temp)": bytes([0x06])
}

# Load rooms configuration
with open("rooms.json", "r") as file:
    rooms = json.load(file)

# ------------------------------------
# Helper Functions
# ------------------------------------

# Helper: Decode temperature values
def decode_temperature(data):
    current_temp = ((data[1] << 8) | data[0]) / 10
    target_temp = ((data[3] << 8) | data[2]) / 10
    return round(current_temp, 1), round(target_temp, 1)

# Helper: Encode target temperature
def encode_temperature(target_temp):
    temp_value = int(target_temp * 10)
    return temp_value.to_bytes(2, 'little')

# Helper: Read mode
async def read_mode(client):
    data = await client.read_gatt_char(MODE_UUID)
    mode = int.from_bytes(data, byteorder='little')
    return MODES.get(mode, f"Unknown ({mode})")

# Helper: Read temperatures
async def read_temperatures(client):
    room_temp_data = await client.read_gatt_char(ROOM_TEMP_UUID)
    heat_temp_data = await client.read_gatt_char(HEAT_TEMP_UUID)

    room_temp = decode_temperature(room_temp_data)
    heat_temp = decode_temperature(heat_temp_data)
    return room_temp, heat_temp

# Helper: Set mode
async def set_mode(client, mode):
    if mode in MODE_ENCODINGS:
        await client.write_gatt_char(MODE_UUID, MODE_ENCODINGS[mode])
        print(f"Mode set to: {mode}")
    else:
        print("Invalid mode")

# Helper: Set temperature
async def set_temperature(client, target_temp, mode_uuid):
    encoded_temp = b'\x00\x00' + encode_temperature(target_temp)
    await client.write_gatt_char(mode_uuid, encoded_temp)
    print(f"Temperature set to: {target_temp}°C")

# ------------------------------------
# Multi-Heater Actions
# ------------------------------------

# Read settings for all heaters in a room
async def read_room_settings(room):
    if room not in rooms:
        print(f"Room '{room}' not found.")
        return

    for heater in rooms[room]:
        print(f"Connecting to heater: {heater}")
        async with BleakClient(heater) as client:
            mode = await read_mode(client)
            room_temp, heat_temp = await read_temperatures(client)

            print(f"Heater {heater}")
            print(f"  Mode: {mode}")
            print(f"  Room Temp - Current: {room_temp[0]}°C, Target: {room_temp[1]}°C")
            print(f"  Heating Element - Current: {heat_temp[0]}°C, Target: {heat_temp[1]}°C")
            print()

# Set mode for all heaters in a room
async def set_room_mode(room, mode):
    if room not in rooms:
        print(f"Room '{room}' not found.")
        return

    for heater in rooms[room]:
        print(f"Connecting to heater: {heater}")
        async with BleakClient(heater) as client:
            await set_mode(client, mode)

# Set temperature for all heaters in a room
async def set_room_temperature(room, target_temp, target_type):
    if room not in rooms:
        print(f"Room '{room}' not found.")
        return

    uuid = ROOM_TEMP_UUID if target_type == "room" else HEAT_TEMP_UUID
    for heater in rooms[room]:
        print(f"Connecting to heater: {heater}")
        async with BleakClient(heater) as client:
            await set_temperature(client, target_temp, uuid)

# ------------------------------------
# Main Menu
# ------------------------------------

async def main():
    while True:
        print("\nOptions:")
        print("  r - Read room settings")
        print("  m - Set room mode")
        print("  t - Set room temperature")
        print("  q - Quit")
        action = input("Choose action: ").strip().lower()

        if action == "r":
            room = input("Enter room name: ").strip().lower()
            await read_room_settings(room)

        elif action == "m":
            room = input("Enter room name: ").strip().lower()
            mode = input("Enter mode (Off, Manual (Room Temp), Manual (Heating Element Temp)): ").strip()
            await set_room_mode(room, mode)

        elif action == "t":
            room = input("Enter room name: ").strip().lower()
            target_temp = float(input("Enter target temperature (°C): ").strip())
            target_type = input("Target type? (room/heater): ").strip().lower()
            await set_room_temperature(room, target_temp, target_type)

        elif action == "q":
            break

        else:
            print("Invalid action. Try again.")

# ------------------------------------

if __name__ == "__main__":
    asyncio.run(main())
