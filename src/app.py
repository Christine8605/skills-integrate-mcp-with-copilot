"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Load activities from activities.json
import json
ACTIVITIES_FILE = os.path.join(current_dir, "activities.json")

def load_activities():
    with open(ACTIVITIES_FILE, "r") as f:
        return json.load(f)

def save_activities(activities):
    with open(ACTIVITIES_FILE, "w") as f:
        json.dump(activities, f, indent=2)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(category: str = None, search: str = None):
    activities = load_activities()
    # Filtering by category
    if category:
        activities = [a for a in activities if a.get("category", "").lower() == category.lower()]
    # Free text search
    if search:
        activities = [a for a in activities if search.lower() in a["name"].lower() or search.lower() in a["description"].lower()]
    return {a["name"]: a for a in activities}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    activities = load_activities()
    for activity in activities:
        if activity["name"] == activity_name:
            if email in activity["participants"]:
                raise HTTPException(status_code=400, detail="Student is already signed up")
            if len(activity["participants"]) >= activity["max_participants"]:
                raise HTTPException(status_code=400, detail="Activity is full")
            activity["participants"].append(email)
            save_activities(activities)
            return {"message": f"Signed up {email} for {activity_name}"}
    raise HTTPException(status_code=404, detail="Activity not found")


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    activities = load_activities()
    for activity in activities:
        if activity["name"] == activity_name:
            if email not in activity["participants"]:
                raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
            activity["participants"].remove(email)
            save_activities(activities)
            return {"message": f"Unregistered {email} from {activity_name}"}
    raise HTTPException(status_code=404, detail="Activity not found")
