from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# In-memory data store for active parking sessions
parking_sessions = {}

# Start a parking session
@app.route('/start', methods=['POST'])
def start_parking():
    vehicle_number = request.form.get('vehicle_number')
    if not vehicle_number:
        return jsonify({"error": "Vehicle number is required"}), 400

    # Record the entry time
    entry_time = datetime.now()
    parking_sessions[vehicle_number] = {
        'entry_time': entry_time,
        'exit_time': None,
        'status': 'active'
    }

    return jsonify({
        "message": f"Parking started for vehicle {vehicle_number}",
        "entry_time": entry_time.strftime('%Y-%m-%d %H:%M:%S')
    })

# End a parking session
@app.route('/end', methods=['POST'])
def end_parking():
    vehicle_number = request.form.get('vehicle_number')
    if not vehicle_number or vehicle_number not in parking_sessions:
        return jsonify({"error": "Invalid vehicle number"}), 400

    # Record the exit time
    exit_time = datetime.now()
    entry_time = parking_sessions[vehicle_number]['entry_time']
    duration = exit_time - entry_time

    # Simulating fee calculation (e.g., $2 per hour)
    total_hours = duration.total_seconds() / 3600
    fee = round(total_hours * 2, 2)

    # Update the session
    parking_sessions[vehicle_number]['exit_time'] = exit_time
    parking_sessions[vehicle_number]['status'] = 'completed'

    return jsonify({
        "message": f"Parking ended for vehicle {vehicle_number}",
        "entry_time": entry_time.strftime('%Y-%m-%d %H:%M:%S'),
        "exit_time": exit_time.strftime('%Y-%m-%d %H:%M:%S'),
        "total_duration": str(duration),
        "fee": f"${fee}"
    })

# View active parking sessions
@app.route('/active_sessions', methods=['GET'])
def active_sessions():
    active = {
        vehicle: data for vehicle, data in parking_sessions.items()
        if data['status'] == 'active'
    }

    return jsonify(active)

if __name__ == '__main__':
    app.run(debug=True)
