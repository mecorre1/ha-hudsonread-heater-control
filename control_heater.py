from bleak import BleakScanner
import asyncio

async def scan_devices():
    print("Scanning for Bluetooth devices...")
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Found device: {device.name}, Address: {device.address}")
    print("Scan complete.")

if __name__ == "__main__":
    asyncio.run(scan_devices())

# this is a change, just to test the cronssss