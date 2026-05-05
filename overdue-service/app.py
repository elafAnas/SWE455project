from flask import Flask, request
from flask_cors import CORS
import requests
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

API_URL = os.environ.get("ASSIGNMENT_API_URL")


@app.route("/", methods=["GET"])
def health_check():
    return {
        "message": "Overdue service is running",
        "assignment_api_url": API_URL
    }, 200


@app.route("/assignment-created", methods=["POST"])
def assignment_created():
    assignment = request.get_json()

    if not API_URL:
        return {"error": "ASSIGNMENT_API_URL is not set"}, 500

    if not assignment:
        return {"error": "No data provided"}, 400

    if "id" not in assignment or "due_date" not in assignment or "status" not in assignment:
        return {"error": "Missing required assignment fields"}, 400

    due_date = datetime.strptime(assignment["due_date"], "%Y-%m-%d").date()
    today = datetime.now().date()

    if due_date < today and assignment["status"] not in ["completed", "late"]:
        response = requests.put(
            f"{API_URL}/assignments/{assignment['id']}",
            json={"status": "overdue"},
            timeout=5
        )

        if response.status_code != 200:
            return {
                "error": "Failed to update assignment",
                "status_code": response.status_code
            }, 500

        return {
            "message": "Assignment marked as overdue",
            "assignment_id": assignment["id"]
        }, 200

    return {
        "message": "Assignment is not overdue",
        "assignment_id": assignment["id"]
    }, 200


@app.route("/check-overdue", methods=["GET", "POST"])
def check_overdue():
    if not API_URL:
        return {"error": "ASSIGNMENT_API_URL is not set"}, 500

    try:
        response = requests.get(f"{API_URL}/assignments", timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return {"error": "Assignment API is not available"}, 500

    data = response.json()
    assignments = data.get("assignments", [])
    updated = []

    today = datetime.now().date()

    for assignment in assignments:
        due_date = datetime.strptime(assignment["due_date"], "%Y-%m-%d").date()

        if due_date < today and assignment["status"] not in ["completed", "late"]:
            update_response = requests.put(
                f"{API_URL}/assignments/{assignment['id']}",
                json={"status": "overdue"},
                timeout=5
            )

            if update_response.status_code == 200:
                updated.append(assignment["id"])

    return {
        "message": "Overdue check done",
        "updated": updated
    }, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)