"""
CodeCraftHub - A simple personalized learning platform
------------------------------------------------------
This Flask REST API lets developers track courses they want to learn.
Data is stored in a JSON file (courses.json) instead of a database.
"""

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Path to the JSON file
DATA_FILE = "courses.json"

# Allowed status values
VALID_STATUSES = ["Not Started", "In Progress", "Completed"]


# ---------------------------
# Utility functions
# ---------------------------

def load_courses():
    """Load courses from the JSON file. Create file if missing."""
    if not os.path.exists(DATA_FILE):
        # Initialize with an empty list if file doesn't exist
        save_courses([])
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # Handle corrupted or unreadable file
        return []


def save_courses(courses):
    """Save courses to the JSON file safely."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(courses, f, indent=4)
    except IOError:
        raise ValueError("Error writing to courses.json")


def generate_new_id(courses):
    """Generate a new auto-incremented ID starting from 1."""
    if not courses:
        return 1
    return max(course["id"] for course in courses) + 1


# ---------------------------
# REST API Endpoints
# ---------------------------

@app.route("/api/courses", methods=["POST"])
def add_course():
    """Add a new course."""
    data = request.get_json()

    # Validate required fields
    required_fields = ["name", "description", "target_date", "status"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Validate status
    if data["status"] not in VALID_STATUSES:
        return jsonify({"error": "Invalid status value"}), 400

    # Validate target_date format
    try:
        datetime.strptime(data["target_date"], "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "target_date must be in YYYY-MM-DD format"}), 400

    courses = load_courses()
    new_course = {
        "id": generate_new_id(courses),
        "name": data["name"],
        "description": data["description"],
        "target_date": data["target_date"],
        "status": data["status"],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    courses.append(new_course)
    save_courses(courses)

    return jsonify(new_course), 201


@app.route("/api/courses", methods=["GET"])
def get_courses():
    """Get all courses."""
    courses = load_courses()
    return jsonify(courses)


@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    """Get a specific course by ID."""
    courses = load_courses()
    course = next((c for c in courses if c["id"] == course_id), None)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    return jsonify(course)


@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    """Update an existing course."""
    data = request.get_json()
    courses = load_courses()
    course = next((c for c in courses if c["id"] == course_id), None)

    if not course:
        return jsonify({"error": "Course not found"}), 404

    # Update fields if provided
    if "name" in data:
        course["name"] = data["name"]
    if "description" in data:
        course["description"] = data["description"]
    if "target_date" in data:
        try:
            datetime.strptime(data["target_date"], "%Y-%m-%d")
            course["target_date"] = data["target_date"]
        except ValueError:
            return jsonify({"error": "target_date must be in YYYY-MM-DD format"}), 400
    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return jsonify({"error": "Invalid status value"}), 400
        course["status"] = data["status"]

    save_courses(courses)
    return jsonify(course)


@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    """Delete a course by ID."""
    courses = load_courses()
    course = next((c for c in courses if c["id"] == course_id), None)

    if not course:
        return jsonify({"error": "Course not found"}), 404

    courses = [c for c in courses if c["id"] != course_id]
    save_courses(courses)
    return jsonify({"message": "Course deleted successfully"}), 200


# ---------------------------
# Run the app
# ---------------------------

if __name__ == "__main__":
    app.run(debug=True)
