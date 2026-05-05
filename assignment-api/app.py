from flask import Flask, request
from flask_cors import CORS
import uuid
import requests
import os
from google.cloud import firestore

app = Flask(__name__)
CORS(app)

db = firestore.Client()
collection_name = "assignments"

OVERDUE_SERVICE_URL = os.environ.get("OVERDUE_SERVICE_URL")


@app.route("/", methods=["GET"])
def health_check():
    return {"message": "Assignment API is running with Firestore"}, 200


@app.route("/assignments", methods=["POST"])
def create_assignment():
    data = request.get_json()

    if not data:
        return {"error": "No data provided"}, 400

    if "course" not in data or "title" not in data or "due_date" not in data:
        return {"error": "Missing required fields"}, 400

    new_assignment = {
        "id": str(uuid.uuid4()),
        "course": data["course"],
        "title": data["title"],
        "due_date": data["due_date"],
        "status": "pending"
    }

    db.collection(collection_name).document(new_assignment["id"]).set(new_assignment)

    if OVERDUE_SERVICE_URL:
        try:
            requests.post(
                f"{OVERDUE_SERVICE_URL}/assignment-created",
                json=new_assignment,
                timeout=5
            )
        except requests.exceptions.RequestException:
            print("Warning: overdue-service is not available")
    else:
        print("Warning: OVERDUE_SERVICE_URL is not set")

    return new_assignment, 201


@app.route("/assignments", methods=["GET"])
def get_assignments():
    docs = db.collection(collection_name).stream()
    assignments = []

    for doc in docs:
        assignments.append(doc.to_dict())

    return {"assignments": assignments}, 200


@app.route("/assignments/<string:assignment_id>", methods=["PUT"])
def update_assignment(assignment_id):
    data = request.get_json()

    if not data:
        return {"error": "No data provided"}, 400

    doc_ref = db.collection(collection_name).document(assignment_id)
    doc = doc_ref.get()

    if doc.exists:
        doc_ref.update(data)
        return doc_ref.get().to_dict(), 200

    return {"error": "Assignment not found"}, 404


@app.route("/assignments/<string:assignment_id>", methods=["DELETE"])
def delete_assignment(assignment_id):
    doc_ref = db.collection(collection_name).document(assignment_id)
    doc = doc_ref.get()

    if doc.exists:
        deleted_assignment = doc.to_dict()
        doc_ref.delete()
        return deleted_assignment, 200

    return {"error": "Assignment not found"}, 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)