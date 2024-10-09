from flask import Flask, request, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the MySQL database
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/parking_db'  # Replace with your MySQL credentials
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define the ParkingSession model
class ParkingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(50), unique=True, nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False)
    exit_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')


# Create the database tables
with app.app_context():
    db.create_all()


# Start a parking session
@app.route('/start', methods=['POST'])
def start_parking():
    vehicle_number = request.form.get('vehicle_number')
    if not vehicle_number:
        return jsonify({"error": "Vehicle number is required"}), 400

    # Record the entry time
    entry_time = datetime.now()
    new_session = ParkingSession(vehicle_number=vehicle_number, entry_time=entry_time)
    db.session.add(new_session)
    db.session.commit()

    return jsonify({
        "message": f"Parking started for vehicle {vehicle_number}",
        "entry_time": entry_time.strftime('%Y-%m-%d %H:%M:%S')
    })


# End a parking session
@app.route('/end', methods=['POST'])
def end_parking():
    vehicle_number = request.form.get('vehicle_number')
    session = ParkingSession.query.filter_by(vehicle_number=vehicle_number, status='active').first()

    if not session:
        return jsonify({"error": "Invalid vehicle number or session not active"}), 400

    # Record the exit time
    exit_time = datetime.now()
    duration = exit_time - session.entry_time

    # Simulating fee calculation (e.g., $2 per hour)
    total_hours = duration.total_seconds() / 3600
    fee = round(total_hours * 2, 2)

    # Update the session
    session.exit_time = exit_time
    session.status = 'completed'
    db.session.commit()

    return jsonify({
        "message": f"Parking ended for vehicle {vehicle_number}",
        "entry_time": session.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
        "exit_time": exit_time.strftime('%Y-%m-%d %H:%M:%S'),
        "total_duration": str(duration),
        "fee": f"${fee}"
    })


# View active parking sessions
@app.route('/active_sessions', methods=['GET'])
def active_sessions():
    active_sessions = ParkingSession.query.filter_by(status='active').all()
    active = [
        {
            "vehicle_number": session.vehicle_number,
            "entry_time": session.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
            "status": session.status
        } for session in active_sessions
    ]

    return jsonify(active)


if __name__ == '__main__':
    app.run(debug=True)
