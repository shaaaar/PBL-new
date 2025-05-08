document.getElementById("start-simulation").addEventListener("click", startSimulation);
document.getElementById("speed-slider").addEventListener("input", updateSpeedLabel);

// Day toggle click
document.querySelectorAll(".day").forEach(dayEl => {
    dayEl.addEventListener("click", () => {
        const dayText = dayEl.querySelector("span");
        if (dayText.textContent === "Available") {
            dayText.textContent = "Blocked";
            dayEl.classList.add("blocked");
        } else {
            dayText.textContent = "Available";
            dayEl.classList.remove("blocked");
        }
    });
});

function updateSpeedLabel() {
    const speed = document.getElementById("speed-slider").value;
    document.getElementById("speed-label").textContent = `${speed}x`;
}

function startSimulation() {
    const numPatients = parseInt(document.getElementById("num-patients").value);
    const numReceptionists = parseInt(document.getElementById("num-receptionists").value);

    // Clear emoji areas
    document.getElementById("patients-emoji").innerHTML = '';
    document.getElementById("receptionist-emoji").innerHTML = '';

    // Animate Patients
    for (let i = 0; i < numPatients; i++) {
        const emoji = document.createElement("div");
        emoji.classList.add("emoji", "patient");
        emoji.textContent = "🧍‍♂️";
        document.getElementById("patients-emoji").appendChild(emoji);
        setTimeout(() => emoji.classList.add("slide-in"), i * 200);
    }

    // Animate Receptionists
    for (let i = 0; i < numReceptionists; i++) {
        const emoji = document.createElement("div");
        emoji.classList.add("emoji", "receptionist");
        emoji.textContent = "🧑‍💼";
        document.getElementById("receptionist-emoji").appendChild(emoji);
        setTimeout(() => emoji.classList.add("slide-in"), i * 400);
    }

    // Send to backend
    fetch('/start_simulation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ num_patients: numPatients, num_receptionists: numReceptionists })
    });

    updateSchedule();
    updateLogs();
}

function updateSchedule() {
    setInterval(() => {
        fetch('/get_schedule')
            .then(response => response.json())
            .then(data => {
                document.getElementById("monday").querySelector("span").textContent = data.Monday;
                document.getElementById("tuesday").querySelector("span").textContent = data.Tuesday;
                document.getElementById("wednesday").querySelector("span").textContent = data.Wednesday;
                document.getElementById("thursday").querySelector("span").textContent = data.Thursday;
                document.getElementById("friday").querySelector("span").textContent = data.Friday;
            });
    }, 1000);
}

function updateLogs() {
    setInterval(() => {
        fetch('/get_logs')
            .then(response => response.json())
            .then(data => {
                const logList = document.getElementById("log-list");
                logList.innerHTML = '';
                data.forEach(log => {
                    const item = document.createElement("li");
                    item.textContent = log;
                    logList.appendChild(item);
                });
            });
    }, 1000);
}
// Initialize calendar
function initCalendar() {
    const calendar = document.getElementById('calendar-view');
    calendar.innerHTML = '';
    
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    days.forEach(day => {
        const dayEl = document.createElement('div');
        dayEl.className = 'calendar-day';
        dayEl.innerHTML = `<strong>${day}</strong>`;
        
        // Add appointment slots
        const slots = ['09:00', '10:00', '11:00', '13:00', '14:00'];
        slots.forEach(slot => {
            const slotEl = document.createElement('div');
            slotEl.className = 'calendar-slot';
            slotEl.textContent = slot;
            dayEl.appendChild(slotEl);
        });
        
        calendar.appendChild(dayEl);
    });
}

// Modal functionality
const modal = document.getElementById('appointment-modal');
const btn = document.getElementById('new-appointment-btn');
const span = document.getElementsByClassName('close')[0];

btn.onclick = () => modal.style.display = 'block';
span.onclick = () => modal.style.display = 'none';
window.onclick = (event) => {
    if (event.target == modal) modal.style.display = 'none';
}

// Form submission
document.getElementById('appointment-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    fetch('/book_appointment', {
        method: 'POST',
        body: JSON.stringify(Object.fromEntries(formData)),
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCalendar();
            modal.style.display = 'none';
        }
    });
});

// Real-time updates
function updateDashboard() {
    fetch('/get_stats')
        .then(res => res.json())
        .then(data => {
            document.getElementById('active-patients').textContent = data.active_patients;
            document.getElementById('today-appointments').textContent = data.today_appointments;
        });
    
    fetch('/get_calendar')
        .then(res => res.json())
        .then(data => renderCalendar(data));
}

// Run every 5 seconds
setInterval(updateDashboard, 5000);
// Initialize FullCalendar with doctor's schedule
document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'timeGridWeek',
      slotMinTime: '08:00:00',
      slotMaxTime: '18:00:00',
      events: '/api/appointments',
      dateClick: function(info) {
        showBookingModal(info.dateStr);
      },
      eventClick: function(info) {
        showAppointmentDetails(info.event);
      }
    });
    calendar.render();
  
    // Refresh calendar every minute
    setInterval(() => calendar.refetchEvents(), 60000);
  });
  
  function showBookingModal(date) {
    // Fetch available slots for the selected date
    fetch(`/api/available-slots?date=${date}`)
      .then(response => response.json())
      .then(slots => {
        // Populate modal with available time slots
        const slotSelect = document.getElementById('timeSlotSelect');
        slotSelect.innerHTML = slots.map(slot => 
          `<option value="${slot}">${slot}</option>`
        ).join('');
        
        // Show modal
        new bootstrap.Modal('#bookingModal').show();
      });
  }
  let calendar;

document.addEventListener('DOMContentLoaded', () => {
    calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {
        initialView: 'timeGridWeek',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay listWeek'
        },
        slotMinTime: '08:00:00',
        slotMaxTime: '18:00:00',
        eventDidMount: function(info) {
            if (info.event.extendedProps.emergency) {
                info.el.style.backgroundColor = '#dc3545';
                info.el.innerHTML += '<i class="fas fa-exclamation-circle ms-2"></i>';
            }
        },
        eventClick: function(info) {
            showAppointmentDetails(info.event);
        },
        events: async function(fetchInfo, successCallback) {
            const response = await fetch(`/api/appointments?start=${fetchInfo.startStr}&end=${fetchInfo.endStr}`);
            const events = await response.json();
            successCallback(events);
        }
    });
    calendar.render();
    
    // Real-time updates
    const eventSource = new EventSource('/api/calendar-updates');
    eventSource.onmessage = e => calendar.refetchEvents();
});

// Emergency slot handling
document.getElementById('emergency-override').addEventListener('click', async () => {
    const { value: formValues } = await Swal.fire({
        title: 'Emergency Override',
        html: `
            <input type="datetime-local" id="emergency-time" class="swal2-input">
            <select id="emergency-doctor" class="swal2-input">
                <option value="cardio">Dr. Smith (Cardiology)</option>
                <option value="neuro">Dr. Jones (Neurology)</option>
            </select>
        `,
        confirmButtonText: 'Create Emergency Slot'
    });
    
    if (formValues) {
        const response = await fetch('/api/emergency-slot', {
            method: 'POST',
            body: JSON.stringify({
                doctor: document.getElementById('emergency-doctor').value,
                time: document.getElementById('emergency-time').value
            })
        });
        handleResponse(response);
    }
});