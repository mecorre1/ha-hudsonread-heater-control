import json
import asyncio
import logging
from bleak import BleakClient

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# UUIDs for heater characteristics
ROOM_TEMP_UUID = "d97352b1-d19e-11e2-9e96-0800200c9a66"
HEAT_TEMP_UUID = "d97352b2-d19e-11e2-9e96-0800200c9a66"
MODE_UUID = "d97352b3-d19e-11e2-9e96-0800200c9a66"

# Modes Mapping
MODES = {
    0: "Off",
    33: "On - Manual (Heating Element Temp)"
}

# Mode Encodings
MODE_ENCODINGS = {
    "Off": bytes([0x00, 0x00, 0x00, 0x00]),
    "On - Manual (Heating Element Temp)": bytes([0x21, 0x00, 0x00, 0x00])
}

# Load rooms configuration
with open("rooms.json", "r") as file:
    rooms = json.load(file)

# Helper: Decode temperature values
def decode_temperature(data):
    logging.debug(f"Decoding temperature data: {data}")
    current_temp = ((data[1] << 8) | data[0]) / 10
    target_temp = ((data[3] << 8) | data[2]) / 10
    return round(current_temp, 1), round(target_temp, 1)

# Helper: Encode target temperature
def encode_temperature(target_temp):
    logging.debug(f"Encoding target temperature: {target_temp}")
    temp_value = int(target_temp * 10)
    return temp_value.to_bytes(2, 'little')

# Helper: Read mode
async def read_mode(client):
    data = await client.read_gatt_char(MODE_UUID)
    mode = int.from_bytes(data, byteorder='little')
    logging.debug(f"Read mode: {data} (decoded: {mode})")
    return MODES.get(mode, f"Unknown ({mode})")

# Helper: Read temperatures
async def read_temperatures(client):
    logging.debug("Reading temperatures...")
    room_temp_data = await client.read_gatt_char(ROOM_TEMP_UUID)
    heat_temp_data = await client.read_gatt_char(HEAT_TEMP_UUID)

    room_temp = decode_temperature(room_temp_data)
    heat_temp = decode_temperature(heat_temp_data)
    return room_temp, heat_temp

# Helper: Set mode
async def set_mode(client, mode):
    logging.debug(f"Setting mode to: {mode}")
    if mode in MODE_ENCODINGS:
        await client.write_gatt_char(MODE_UUID, MODE_ENCODINGS[mode])
        logging.info(f"Mode successfully set to: {mode}")
    else:
        logging.error("Invalid mode")

# Helper: Set temperature
async def set_temperature(client, target_temp, mode_uuid):
    logging.debug(f"Setting temperature to {target_temp}°C on UUID {mode_uuid}")
    await set_mode(client, "On - Manual (Heating Element Temp)")
    encoded_temp = b'\x00\x00' + encode_temperature(target_temp)
    await client.write_gatt_char(mode_uuid, encoded_temp)
    logging.info(f"Temperature successfully set to: {target_temp}°C")

# Multi-Heater Actions
async def read_room_settings(room):
    if room not in rooms:
        logging.error(f"Room '{room}' not found.")
        return

    for heater in rooms[room]:
        logging.debug(f"Connecting to heater: {heater}")
        async with BleakClient(heater) as client:
            mode = await read_mode(client)
            room_temp, heat_temp = await read_temperatures(client)
            logging.info(f"Heater {heater}: Mode={mode}, Room Temp={room_temp}, Heat Temp={heat_temp}")

async def set_room_temperature(room, target_temp, target_type):
    if room not in rooms:
        logging.error(f"Room '{room}' not found.")
        return

    uuid = ROOM_TEMP_UUID if target_type == "room" else HEAT_TEMP_UUID
    for heater in rooms[room]:
        logging.debug(f"Connecting to heater: {heater}")
        async with BleakClient(heater) as client:
            try:
                await set_temperature(client, target_temp, uuid)
            except Exception as e:
                logging.error(f"Error setting temperature for heater {heater}: {e}")

async def get_all_ble_fields(address):
    logging.debug(f"Fetching all BLE fields for {address}")
    async with BleakClient(address) as client:
        try:
            services = await client.get_services()
            fields = {}
            for service in services:
                for characteristic in service.characteristics:
                    if "read" in characteristic.properties:
                        try:
                            value = await client.read_gatt_char(characteristic.uuid)
                            fields[characteristic.uuid] = {
                                "value": value.hex(),
                                "description": characteristic.description,
                                "service": service.uuid
                            }
                        except Exception as e:
                            fields[characteristic.uuid] = {"error": str(e)}
            return fields
        except Exception as e:
            logging.error(f"Error fetching BLE fields: {e}")
            return {"error": str(e)}

# # ------------------------------------
# # Main Menu
# # ------------------------------------

# async def main():
#     while True:
#         print("\nOptions:")
#         print("  r - Read room settings")
#         print("  m - Set room mode")
#         print("  t - Set room temperature")
#         print("  q - Quit")
#         action = input("Choose action: ").strip().lower()

#         if action == "r":
#             room = input("Enter room name: ").strip().lower()
#             await read_room_settings(room)

#         elif action == "m":
#             room = input("Enter room name: ").strip().lower()
#             mode = input("Enter mode (Off, Manual (Room Temp), Manual (Heating Element Temp)): ").strip()
#             await set_room_mode(room, mode)

#         elif action == "t":
#             room = input("Enter room name: ").strip().lower()
#             target_temp = float(input("Enter target temperature (°C): ").strip())
#             target_type = input("Target type? (room/heater): ").strip().lower()
#             await set_room_temperature(room, target_temp, target_type)

#         elif action == "q":
#             break

#         else:
#             print("Invalid action. Try again.")

# # ------------------------------------

# if __name__ == "__main__":
#     asyncio.run(main())
