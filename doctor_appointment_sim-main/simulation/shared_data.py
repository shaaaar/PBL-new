from collections import defaultdict
from datetime import datetime, timedelta
import threading

class DoctorSchedule:
    def __init__(self, doctor_id):
        self.lock = threading.Lock()
        self.schedule = {
            (datetime.now() + timedelta(days=i)).date(): {
                "status": "available",
                "slots": {
                    f"{h:02d}:{m:02d}": None for h in range(8, 18) 
                    for m in [0, 30] if h != 12
                }
            } for i in range(14)  # 2-week rolling schedule
        }

    def book_slot(self, date, time, patient_id):
        with self.lock:
            if self.schedule[date]['slots'][time] is None:
                self.schedule[date]['slots'][time] = patient_id
                return True
            return False

class Clinic:
    def __init__(self):
        self.doctors = {
            "cardio": DoctorSchedule("dr_smith"),
            "neuro": DoctorSchedule("dr_jones")
        }
        self.patients = {}
        self.appointment_log = []
        self.emergency_slots = threading.Lock()

clinic = Clinic()

# Sample structure for simulation
doctor_schedule = {
    "dr_smith": {
        "schedule": {
            "2025-05-09": {
                "slots": {
                    "09:00": None,
                    "10:00": None,
                    "11:00": None
                }
            },
            "2025-05-10": {
                "slots": {
                    "09:00": None,
                    "10:00": None,
                    "11:00": None
                }
            }
        }
    }
}

log_list = []

patient_records = {
    "p123": {"id": "p123", "name": "Alice", "contact": "alice@example.com"},
    "p456": {"id": "p456", "name": "Bob", "contact": "bob@example.com"},
    "p789": {"id": "p789", "name": "Charlie", "contact": "charlie@example.com"}
}
