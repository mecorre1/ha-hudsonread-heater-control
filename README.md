
# Heater Control with Python, Docker, and Bluetooth

This project enables **smart control of Terma MOA Blue heaters** using **Python**, **Docker**, and **Bluetooth Low Energy (BLE)**. It integrates seamlessly with **Home Assistant (HA)** for remote monitoring and temperature management.

---

## Overview

- **Control Heating Modes and Temperatures**: Supports manual operation based on **room** or **heating element temperature**.
- **Multi-Heater Support**: Handles multiple heaters grouped by **rooms**.
- **Automated Bluetooth Pairing Script**: A **bash script** automates pairing and reconnecting heaters.
- **Fault Handling**: Logs connection errors and alerts when re-pairing is required.

---

## Blog Posts - Step-by-Step Guide

This project is detailed in a series of blog posts on **dev.to**:
- [**Part 1: Building a Smart Heater Controller with Python, Docker, and Bluetooth**](https://dev.to/mecorre1/building-a-smart-heater-controller-with-python-docker-and-bluetooth-1-44c7)
- **More to come!**

Follow these posts for **in-depth explanations**, **troubleshooting tips**, and a complete **walkthrough** of the setup.

---

## Features

1. **Python API for Heater Control**:
   - Reads and sets temperatures.
   - Changes operating modes.

2. **Dockerized Setup**:
   - Ensures a portable and stable runtime environment.

3. **Multi-Heater Configuration**:
   - Define heaters by **room** in `rooms.json`.

4. **Automated Pairing Script**:
   - Handles Bluetooth pairing, retries, and manual confirmations when required.
   - Outputs **logs** and a **summary** of pairing results.

5. **HA Integration**:
   - Connects heaters to **Home Assistant** for centralized control.

---

## Getting Started

### 1. Clone the Repository
```
git clone git@github.com:mecorre1/ha-hudsonread-heater-control.git
cd ha-hudsonread-heater-control
```

### 2. Install Docker
Follow the instructions to install Docker and Docker Compose:
- [Docker Setup Guide](https://docs.docker.com/engine/install/)

### 3. Build the Docker Image
```
docker build -t heater-controller .
```

### 4. Run the Heater Controller
```
docker run -it --net=host --privileged -v /var/run/dbus:/var/run/dbus heater-controller
```

### 5. Automate Bluetooth Pairing
```
chmod +x pair_heaters.sh
./pair_heaters.sh
```

---

## Configuration

### rooms.json Example:
```json
{
  "kitchen": ["CC:22:37:11:26:4F"],
  "living_room": ["CC:22:37:11:5D:02"],
  "bedroom_1": ["CC:22:37:11:30:EC"],
  "bedroom_2": ["CC:22:37:11:1E:84"]
}
```

### Python API
- Supports **reading** and **writing** temperature and mode settings.
- Error logs indicate when re-pairing is needed.

---

## Known Issues and Debugging Tips

1. **Pairing Mode Reset**:
   - If the heater loses connection, it must be manually set to **pairing mode** (hold button for 5 seconds until blinking).

2. **Re-run the Pairing Script**:
   - If HA actions fail, rerun the `pair_heaters.sh` script.

3. **Multi-Room Control**:
   - Ensure `rooms.json` reflects the correct **addresses** for each heater.

---

## Contributing

Contributions are welcome!

- Fork the repository.
- Create a new branch for your feature or bug fix.
- Submit a **pull request**.

---

## Credits

This project was built by **[mecorre1](https://github.com/mecorre1)** in collaboration with **ChatGPT**. Special thanks to the **Home Assistant community** for insights shared in [this forum post](https://community.home-assistant.io/t/terma-blue-line-bluetooth-radiators-and-heating-elements/81325/24).
