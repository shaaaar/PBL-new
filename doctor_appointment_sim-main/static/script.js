// LIVE CLOCK
function updateClock() {
  const now = new Date();
  const timeString = now.toLocaleTimeString();
  document.getElementById("live-clock").textContent = timeString;
}
setInterval(updateClock, 1000);
updateClock();

// POPULATE DAYS & TIMES IN MODAL
document.addEventListener("DOMContentLoaded", () => {
  const daySelect = document.getElementById("appointment-day");
  const timeSelect = document.getElementById("appointment-time");

  const weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  weekdays.forEach(day => {
    const option = document.createElement("option");
    option.value = day;
    option.textContent = day;
    daySelect.appendChild(option);
  });

  for (let hour = 9; hour <= 17; hour++) {
    const option = document.createElement("option");
    option.value = `${hour}:00`;
    option.textContent = `${hour}:00`;
    timeSelect.appendChild(option);
  }
});


// BOOK APPOINTMENT
document.getElementById("appointment-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = e.target.querySelector("input").value;
  const day = e.target.querySelector("#appointment-day").value;
  const time = e.target.querySelector("#appointment-time").value;

  const response = await fetch("/book", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, day, time })
  });

  const result = await response.json();
  alert(result.message);
  document.getElementById("appointment-modal").classList.remove("show");
  document.querySelector(".modal-backdrop")?.remove();
  e.target.reset();
  loadAppointments();
});

// SIMULATION START
document.getElementById("start-simulation").addEventListener("click", async () => {
  const patients = document.getElementById("num-patients").value;
  const receptionists = document.getElementById("num-receptionists").value;
  const speed = document.getElementById("speed-slider").value;

  await fetch("/start_simulation", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ patients, receptionists, speed })
  });

  updateStats();
  fetchQueues();
  fetchLogs();
});

// EMERGENCY SLOT
document.getElementById("emergency-override").addEventListener("click", async () => {
  const response = await fetch("/emergency_slot", { method: "POST" });
  const result = await response.json();
  alert(result.message);
  loadAppointments();
});

// SLIDER UPDATE
document.getElementById("speed-slider").addEventListener("input", (e) => {
  document.getElementById("speed-label").textContent = `${e.target.value}x`;
});

// FETCH & RENDER FUNCTIONS
async function loadAppointments() {
  const res = await fetch("/appointments");
  const data = await res.json();
  document.getElementById("today-appointments").textContent = data.length;

  const calendar = document.getElementById("calendar");
  calendar.innerHTML = "";
  data.forEach(app => {
    const entry = document.createElement("div");
    entry.textContent = `${app.day} - ${app.time} : ${app.name}`;
    calendar.appendChild(entry);
  });
}

async function updateStats() {
  const res = await fetch("/appointments");
  const data = await res.json();
  document.getElementById("today-appointments").textContent = data.length;
  document.getElementById("active-patients").textContent = data.length;
}

async function fetchLogs() {
  const res = await fetch("/logs");
  const data = await res.json();
  const logList = document.getElementById("log-list");
  logList.innerHTML = "";
  data.slice().reverse().forEach(log => {
    const item = document.createElement("li");
    item.className = "list-group-item";
    item.textContent = log;
    logList.appendChild(item);
  });
}

async function fetchQueues() {
  const res = await fetch("/queue");
  const data = await res.json();
  document.getElementById("patients-emoji").textContent = data.patients.join(" ");
  document.getElementById("receptionist-emoji").textContent = data.receptionists.join(" ");
}

// INIT
loadAppointments();
updateStats();
fetchLogs();
fetchQueues();
setInterval(fetchQueues, 2000);
setInterval(fetchLogs, 5000);
