import time
import bluetooth

def control_heater():
    print("Scanning for Bluetooth devices...")
    devices = bluetooth.discover_devices(duration=5, lookup_names=True)

    for addr, name in devices:
        print(f"Found device {name} with address {addr}")

    print("Heater control executed!")

if __name__ == "__main__":
    control_heater()
