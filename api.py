from flask import Flask, request, jsonify
import json
import asyncio
import control_heater

# Load rooms configuration
with open("rooms.json", "r") as file:
    rooms = json.load(file)

app = Flask(__name__)

@app.route('/set-temp', methods=['POST'])
def set_temperature():
    try:
        # Extract and validate data
        data = request.get_json(force=True)
        room = data.get('room')  # Room name
        target_temp = float(data.get('temperature'))  # Target temperature

        # Validate input
        if room not in rooms:
            return jsonify({"error": f"Room '{room}' not found"}), 400

        if not (30 <= target_temp <= 60):  # Check heating element range
            return jsonify({"error": "Temperature out of range (30–60°C)"}), 400

        # Call function to set temperature
        asyncio.run(control_heater.set_room_temperature(room, target_temp, target_type="heater"))

        return jsonify({"status": "success", "room": room, "temperature": target_temp}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Get rooms to dynamically populate HA dropdown
@app.route('/rooms', methods=['GET'])
def get_rooms():
    try:
        room_list = list(rooms.keys())  # Extract room names
        return jsonify({"rooms": room_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Sample endpoint to set modes
@app.route('/set-mode', methods=['POST'])
def set_mode():
    data = request.json
    mode = data.get('mode')

    valid_modes = ["off", "manual_room", "manual_heating_element"]
    if mode not in valid_modes:
        return jsonify({"error": "Invalid mode"}), 400

    # Logic to set mode (placeholder)
    print(f"Setting mode to {mode}")

    return jsonify({"message": f"Mode set to {mode}"}), 200

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "API is running"}), 200

# Flask route to fetch all BLE fields
@app.route('/get-all-fields', methods=['GET'])
def get_all_fields():
    try:
        # Extract the BLE address from the request
        address = request.args.get('address')

        if not address:
            return jsonify({"error": "The 'address' parameter is required."}), 400

        # Call the BLE function to get all fields
        import asyncio
        fields = asyncio.run(control_heater.get_all_ble_fields(address))

        # Return the fields as a response
        return jsonify({"address": address, "fields": fields})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
