import threading
import time
import random
from .shared_data import doctor_schedule, log_list
from .locks import reader_semaphore, mutex, read_count, read_count_lock

DAYS = list(doctor_schedule.keys())



def patient_thread(patient_id):
    global read_count
    while True:
        time.sleep(random.uniform(1, 3))
        reader_semaphore.acquire()

        with read_count_lock:
            read_count += 1
            if read_count == 1:
                mutex.acquire()

        log_list.append(f"Patient {patient_id} is viewing the schedule.")
        time.sleep(1)  # Simulate reading
        reader_semaphore.release()

        with read_count_lock:
            read_count -= 1
            if read_count == 0:
                mutex.release()

def receptionist_thread(receptionist_id):
    while True:
        time.sleep(random.uniform(4, 6))
        with mutex:
            day = random.choice(DAYS)
            if doctor_schedule[day]["status"] == "Available":
                # Find first available time slot
                for time_slot, patient in doctor_schedule[day]["appointments"].items():
                    if patient is None:
                        patient_name = f"Patient-{random.randint(100, 999)}"
                        doctor_schedule[day]["appointments"][time_slot] = patient_name
                        log_list.append(
                            f"Receptionist {receptionist_id} booked {patient_name} "
                            f"on {day} at {time_slot}"
                        )
                        break
                else:
                    doctor_schedule[day]["status"] = "Fully Booked"
                    log_list.append(f"Receptionist {receptionist_id} marked {day} as fully booked")

        time.sleep(2)  # Simulate booking time

def start_simulation(num_patients, num_receptionists):
    for i in range(int(num_patients)):
        threading.Thread(target=patient_thread, args=(i + 1,), daemon=True).start()

    for i in range(int(num_receptionists)):
        threading.Thread(target=receptionist_thread, args=(i + 1,), daemon=True).start()
