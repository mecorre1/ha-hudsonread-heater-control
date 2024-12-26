import asyncio
import bleak
from bleak import BleakClient, BleakScanner
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define service and characteristic UUIDs
SERVICE_UUID = "D97352XX-D19E-11E2-9E96-0800200C9A66"  # Replace XX if known
TEMP_CHARACTERISTICS = {
    "Room Temperature": "D97352B1-D19E-11E2-9E96-0800200C9A66",
    "Heating Element Temperature": "D97352B2-D19E-11E2-9E96-0800200C9A66",
}

# Heater data structure
class Heater:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.client = None

    async def connect(self):
        try:
            self.client = BleakClient(self.address)
            await self.client.connect()
            logger.info(f"Connected to {self.name} ({self.address})")
            return True
        except bleak.exc.BleakError as e:
            logger.error(f"Connection error to {self.name} ({self.address}): {e}")
            return False
        except Exception as e:
            logger.exception(f"An unexpected error occurred during connection to {self.name} ({self.address}): {e}")
            return False

    async def disconnect(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            logger.info(f"Disconnected from {self.name} ({self.address})")
            self.client = None

    async def read_temperature(self, characteristic_uuid):
        if not self.client or not self.client.is_connected:
            logger.warning(f"Not connected to {self.name}. Cannot read temperature.")
            return None
        try:
            data = await self.client.read_characteristic(characteristic_uuid)
            current_temp = ((data[0] * 255) + data[1]) / 10
            target_temp = ((data[2] * 255) + data[3]) / 10
            return current_temp, target_temp
        except Exception as e:
            logger.error(f"Error reading from {self.name} - {characteristic_uuid}: {e}")
            return None

    async def set_target_temperature(self, characteristic_uuid, target_temp):
        if not self.client or not self.client.is_connected:
            logger.warning(f"Not connected to {self.name}. Cannot set temperature.")
            return
        try:
            data = celsius_to_bytes(target_temp)
            await self.client.write_characteristic(characteristic_uuid, data, without_response=True)
            logger.info(f"Target temperature for {self.name} - {characteristic_uuid.split('-')[0]} set to {target_temp:.1f}°C")
        except Exception as e:
            logger.error(f"Error writing to {self.name} - {characteristic_uuid}: {e}")

# Function to convert temperature from Celsius to bytes
def celsius_to_bytes(temp):
    if temp < 15 or temp > 60:
        raise ValueError("Target temperature out of range (15-60°C)")
    value = int(temp * 10)
    return value.to_bytes(2, byteorder="big") + value.to_bytes(2, byteorder="big")

async def main():
    heaters = [
        Heater("Heater 1", "XX:XX:XX:XX:XX:X1"),  # Replace with actual addresses
        Heater("Heater 2", "XX:XX:XX:XX:XX:X2"),
        # Add more heaters here
    ]

    for heater in heaters:
        if not await heater.connect():
            logger.error(f"Failed to connect to {heater.name}. Skipping.")
            continue

        for name, uuid in TEMP_CHARACTERISTICS.items():
            temps = await heater.read_temperature(uuid)
            if temps:
                current_temp, target_temp = temps
                logger.info(f"{heater.name} - {name}: Current: {current_temp:.1f}°C, Target: {target_temp:.1f}°C")

        await heater.set_target_temperature(TEMP_CHARACTERISTICS["Room Temperature"], 22.5) #Example

        await heater.disconnect()

if __name__ == "__main__":
    asyncio.run(main())