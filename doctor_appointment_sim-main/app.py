import time
import threading
import uuid
from flask import Flask, render_template, jsonify, request, Response
from flask_sse import sse
from simulation.scheduler import start_simulation
from simulation.shared_data import doctor_schedule, log_list, patient_records, clinic
from simulation.locks import reader_semaphore, mutex

app = Flask(__name__)
app.register_blueprint(sse, url_prefix='/stream')

# Threading lock for controlling the simulation threads
simulation_thread = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_logs')
def get_logs():
    """Send the latest logs to the frontend."""
    return jsonify(log_list[-5:])  # Only send the last 5 log entries

@app.route('/get_schedule')
def get_schedule():
    """Send the doctor's schedule to the frontend."""
    return jsonify(doctor_schedule)

@app.route('/start_simulation', methods=['POST'])
def start_simulation_route():
    """Start the simulation with the specified number of patients and receptionists."""
    global simulation_thread

    if simulation_thread and simulation_thread.is_alive():
        return jsonify({"message": "Simulation is already running."})

    num_patients = request.json.get('num_patients', 5)
    num_receptionists = request.json.get('num_receptionists', 1)

    simulation_thread = threading.Thread(target=start_simulation, args=(num_patients, num_receptionists))
    simulation_thread.start()

    return jsonify({"message": "Simulation started"})

@app.route('/api/patients', methods=['GET', 'POST'])
def manage_patients():
    if request.method == 'POST':
        data = request.json
        patient_id = str(uuid.uuid4())
        clinic.patients[patient_id] = {
            'name': data['name'],
            'contact': data['contact'],
            'medical_history': data.get('history', []),
            'insurance': data.get('insurance')
        }
        return jsonify({'id': patient_id})

    query = request.args.get('q', '').lower()
    results = {
        pid: pdata for pid, pdata in clinic.patients.items()
        if query in pdata['name'].lower() or query in pid
    }
    return jsonify(results)

@app.route('/api/calendar-updates')
def calendar_updates():
    def generate():
        last_update = time.time()
        while True:
            if time.time() - last_update > 30:  # Send keep-alive
                yield "data: keepalive\n\n"
                last_update = time.time()

            if clinic.schedule_modified:
                yield "data: update\n\n"
                clinic.schedule_modified = False
            time.sleep(1)

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/appointments-range', methods=['GET'])
def get_appointments_range():
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    events = []
    for doctor_id, schedule in clinic.doctors.items():
        for date, day_schedule in schedule.schedule.items():
            if start_date <= str(date) <= end_date:
                for time_slot, patient_id in day_schedule.slots.items():
                    if patient_id:
                        patient = clinic.patients.get(patient_id, {})
                        events.append({
                            'title': patient.get('name', 'Unknown Patient'),
                            'start': f"{date}T{time_slot}:00",
                            'doctor': doctor_id,
                            'color': '#28a745' if doctor_id == 'cardio' else '#007bff'
                        })
    return jsonify(events)

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    doctor_id = request.args.get("doctor", "dr_smith")
    appointments = []
    for date, schedule in doctor_schedule[doctor_id]['schedule'].items():
        for time_slot, patient in schedule['slots'].items():
            if patient:
                appointments.append({
                    'title': patient['name'],
                    'start': f"{date}T{time_slot}",
                    'extendedProps': {
                        'patientId': patient['id'],
                        'status': patient['status']
                    }
                })
    return jsonify(appointments)

@app.route('/api/available-slots')
def get_available_slots():
    date = request.args.get('date')
    doctor_id = request.args.get('doctor', 'dr_smith')  # Default doctor

    available_slots = [
        time for time, patient
        in doctor_schedule[doctor_id]['schedule'][date]['slots'].items()
        if not patient
    ]
    return jsonify(available_slots)

@app.route('/api/book-appointment', methods=['POST'])
def book_appointment():
    data = request.json
    doctor_id = data['doctor_id']
    date = data['date']
    time_slot = data['time']
    patient_id = data['patient_id']

    with mutex:
        if not doctor_schedule[doctor_id]['schedule'][date]['slots'][time_slot]:
            doctor_schedule[doctor_id]['schedule'][date]['slots'][time_slot] = {
                'id': patient_id,
                'name': patient_records[patient_id]['name'],
                'status': 'booked'
            }
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Slot already booked'}), 400

def send_notification(patient_id, message):
    patient = patient_records.get(patient_id)
    if patient and 'contact' in patient:
        # Implement actual SMS/email sending here
        print(f"Sent to {patient['contact']}: {message}")
        log_list.append(f"Notification sent to {patient['name']}")

@app.route('/api/send-reminder/<patient_id>', methods=['POST'])
def send_reminder(patient_id):
    send_notification(patient_id, "Reminder: Your appointment tomorrow at 10:00 AM")
    return jsonify({'status': 'success'})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
