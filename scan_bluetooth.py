import asyncio
import bleak
from bleak import BleakScanner
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def scan_and_log_devices():
    try:
        logger.info("Scanning for Bluetooth devices...")
        devices = await BleakScanner.discover(timeout=10.0) # set a timeout to avoid indefinite blocking
        if devices:
            for device in devices:
                logger.info(f"Found device: Name: {device.name}, Address: {device.address}, RSSI: {device.rssi}")
        else:
            logger.info("No Bluetooth devices found within timeout.")
    except bleak.exc.BleakError as e:
        logger.error(f"Bleak error during scanning: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred during scanning: {e}")

async def main():
    await scan_and_log_devices()

if __name__ == "__main__":
    asyncio.run(main())