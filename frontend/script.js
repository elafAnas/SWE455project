
const API_URL = "https://assignment-api-ofb2xhz2nq-uc.a.run.app";
const OVERDUE_URL = "https://overdue-service-ofb2xhz2nq-uc.a.run.app";

const form = document.getElementById("assignmentForm");
const assignmentsList = document.getElementById("assignmentsList");

async function fetchAssignments() {
  const response = await fetch(`${API_URL}/assignments`);
  const data = await response.json();

  assignmentsList.innerHTML = "";

  if (data.assignments.length === 0) {
    assignmentsList.innerHTML = `<p class="empty">No assignments yet.</p>`;
    return;
  }

  data.assignments.forEach((assignment) => {
    const item = document.createElement("div");
    item.className = "assignment-item";

    const displayStatus =
      assignment.status === "completed" ? "done" : assignment.status;

    const isFinished =
      assignment.status === "completed" || assignment.status === "late";

    item.innerHTML = `
      <div class="assignment-info">
        <h3>${assignment.title}</h3>
        <p>Course: ${assignment.course}</p>
        <p>Due: ${assignment.due_date}</p>
        <p>Status: 
          <span class="status ${assignment.status}">
            ${displayStatus}
          </span>
        </p>
      </div>

      <div>
        <button 
          class="done-btn ${isFinished ? "completed" : ""}"
          onclick="markCompleted('${assignment.id}', '${assignment.status}')"
          ${isFinished ? "disabled" : ""}
        >
          Done
        </button>

        <button class="delete-btn" onclick="deleteAssignment('${assignment.id}')">
          Delete
        </button>
      </div>
    `;

    assignmentsList.appendChild(item);
  });
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const assignment = {
    course: document.getElementById("course").value,
    title: document.getElementById("title").value,
    due_date: document.getElementById("due_date").value
  };

  await fetch(`${API_URL}/assignments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(assignment)
  });

  form.reset();
  fetchAssignments();
});

async function deleteAssignment(id) {
  await fetch(`${API_URL}/assignments/${id}`, {
    method: "DELETE"
  });

  fetchAssignments();
}

async function markCompleted(id, currentStatus) {
  let newStatus = "completed";

  if (currentStatus === "overdue") {
    newStatus = "late";
  }

  await fetch(`${API_URL}/assignments/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      status: newStatus
    })
  });

  fetchAssignments();
}

async function runOverdueCheck() {
  try {
    const response = await fetch(`${OVERDUE_URL}/check-overdue`, {
      method: "POST"
    });

    const result = await response.json();

    alert(`Overdue check done! Updated: ${result.updated.length}`);
    fetchAssignments();
  } catch (error) {
    alert("Error running overdue check. Make sure overdue service is running.");
    console.error(error);
  }
}

fetchAssignments();