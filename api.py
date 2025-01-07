from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample endpoint to set temperature
@app.route('/set-temp', methods=['POST'])
def set_temperature():
    data = request.json
    temp = data.get('temperature')

    if not temp or not isinstance(temp, (int, float)):
        return jsonify({"error": "Invalid temperature value"}), 400

    # Logic to set temperature (placeholder)
    print(f"Setting temperature to {temp}°C")

    return jsonify({"message": f"Temperature set to {temp}°C"}), 200

# Sample endpoint to set mode
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
