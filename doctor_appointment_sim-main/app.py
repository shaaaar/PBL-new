from flask import Flask, render_template, request, jsonify
from threading import Thread, Lock
import time
import datetime

app = Flask(__name__)

# ------------------------------
# In-Memory Data Storage
# ------------------------------
appointments = []
logs = []
doctor_schedule = {
    "Monday": "Available",
    "Tuesday": "Available",
    "Wednesday": "Available",
    "Thursday": "Available",
    "Friday": "Available"
}
lock = Lock()

# Emoji queues for simulation visuals
patients_queue = []
receptionist_queue = []

# ------------------------------
# Routes
# ------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/book", methods=["POST"])
def book_appointment():
    data = request.json
    name = data.get("name")
    day = data.get("day")
    time_slot = data.get("time")

    if not name or not day or not time_slot:
        return jsonify({"status": "error", "message": "Missing appointment data."}), 400

    with lock:
        appointments.append({"name": name, "day": day, "time": time_slot})
        logs.append(f"[{timestamp()}] Appointment booked for {name} on {day} at {time_slot}")
        patients_queue.append("🧑‍🤝‍🧑")

    return jsonify({"status": "success", "message": "Appointment booked!"})


@app.route("/appointments")
def get_appointments():
    with lock:
        return jsonify(appointments)


@app.route("/schedule")
def get_schedule():
    return jsonify(doctor_schedule)


@app.route("/logs")
def get_logs():
    with lock:
        return jsonify(logs)


@app.route("/queue")
def get_queue():
    with lock:
        return jsonify({
            "patients": patients_queue,
            "receptionists": receptionist_queue
        })


@app.route("/start_simulation", methods=["POST"])
def start_simulation():
    data = request.json
    num_patients = int(data.get("patients", 5))
    num_receptionists = int(data.get("receptionists", 1))
    speed = float(data.get("speed", 1))

    def simulate():
        with lock:
            receptionist_queue.clear()
            patients_queue.clear()
        logs.append(f"[{timestamp()}] 🟢 Simulation started with {num_patients} patients, {num_receptionists} receptionist(s), speed {speed}x")

        # Add receptionists
        with lock:
            receptionist_queue.extend(["👩‍💼"] * num_receptionists)

        # Simulate patient arrivals
        for i in range(num_patients):
            time.sleep(1 / speed)
            with lock:
                patient_name = f"SimPatient{i+1}"
                appointments.append({
                    "name": patient_name,
                    "day": "Monday",
                    "time": f"{9 + i}:00"
                })
                logs.append(f"[{timestamp()}] 🧑 Patient {patient_name} added to Monday at {9 + i}:00")
                patients_queue.append("🧑‍🤝‍🧑")

        logs.append(f"[{timestamp()}] ✅ Simulation completed.")

    sim_thread = Thread(target=simulate)
    sim_thread.start()

    return jsonify({"status": "started", "message": "Simulation running"})


@app.route("/emergency_slot", methods=["POST"])
def emergency_slot():
    with lock:
        emergency_patient = {
            "name": "🚨 Emergency Patient",
            "day": "Today",
            "time": datetime.datetime.now().strftime("%H:%M")
        }
        appointments.insert(0, emergency_patient)
        logs.append(f"[{timestamp()}] 🚨 Emergency slot added immediately at {emergency_patient['time']}")
        patients_queue.insert(0, "🚨")

    return jsonify({"status": "success", "message": "Emergency slot assigned"})


# ------------------------------
# Utility
# ------------------------------
def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ------------------------------
# Run the App
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
