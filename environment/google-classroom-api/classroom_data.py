"""Data access module for Google Classroom API simulation."""

import csv
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_courses(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "section": r["section"],
            "descriptionHeading": r["descriptionHeading"],
            "description": r["description"],
            "room": r["room"],
            "ownerId": r["ownerId"],
            "courseState": r["courseState"],
            "creationTime": r["creationTime"],
            "updateTime": r["updateTime"],
            "enrollmentCode": r["enrollmentCode"],
            "alternateLink": r["alternateLink"],
            "guardiansEnabled": r["guardiansEnabled"].lower() == "true",
            "calendarId": r["calendarId"],
        })
    return out


def _coerce_coursework(rows):
    out = []
    for r in rows:
        cw = {
            "courseId": r["courseId"],
            "id": r["id"],
            "title": r["title"],
            "description": r["description"],
            "state": r["state"],
            "maxPoints": float(r["maxPoints"]) if r["maxPoints"] else None,
            "workType": r["workType"],
            "topicId": r["topicId"] if r["topicId"] else None,
            "creationTime": r["creationTime"],
            "updateTime": r["updateTime"],
            "alternateLink": r["alternateLink"],
        }
        # Build dueDate and dueTime objects if present
        if r.get("dueDate_year") and r["dueDate_year"]:
            cw["dueDate"] = {
                "year": int(r["dueDate_year"]),
                "month": int(r["dueDate_month"]),
                "day": int(r["dueDate_day"]),
            }
        else:
            cw["dueDate"] = None
        if r.get("dueTime_hours") and r["dueTime_hours"]:
            cw["dueTime"] = {
                "hours": int(r["dueTime_hours"]),
                "minutes": int(r["dueTime_minutes"]),
            }
        else:
            cw["dueTime"] = None
        out.append(cw)
    return out


def _coerce_topics(rows):
    out = []
    for r in rows:
        out.append({
            "courseId": r["courseId"],
            "topicId": r["topicId"],
            "name": r["name"],
            "updateTime": r["updateTime"],
        })
    return out


def _coerce_students(rows):
    out = []
    for r in rows:
        out.append({
            "courseId": r["courseId"],
            "userId": r["userId"],
            "profile": {
                "id": r["userId"],
                "name": {"fullName": r["fullName"]},
                "emailAddress": r["emailAddress"],
                "photoUrl": r["photoUrl"],
            },
        })
    return out


def _coerce_teachers(rows):
    out = []
    for r in rows:
        out.append({
            "courseId": r["courseId"],
            "userId": r["userId"],
            "profile": {
                "id": r["userId"],
                "name": {"fullName": r["fullName"]},
                "emailAddress": r["emailAddress"],
                "photoUrl": r["photoUrl"],
            },
        })
    return out


def _coerce_submissions(rows):
    out = []
    for r in rows:
        sub = {
            "courseId": r["courseId"],
            "courseWorkId": r["courseWorkId"],
            "id": r["id"],
            "userId": r["userId"],
            "state": r["state"],
            "late": r["late"].lower() == "true",
            "creationTime": r["creationTime"],
            "updateTime": r["updateTime"],
            "alternateLink": r["alternateLink"],
        }
        sub["assignedGrade"] = float(r["assignedGrade"]) if r.get("assignedGrade") and r["assignedGrade"] else None
        sub["draftGrade"] = float(r["draftGrade"]) if r.get("draftGrade") and r["draftGrade"] else None
        out.append(sub)
    return out


def _coerce_announcements(rows):
    out = []
    for r in rows:
        out.append({
            "courseId": r["courseId"],
            "id": r["id"],
            "text": r["text"],
            "state": r["state"],
            "creationTime": r["creationTime"],
            "updateTime": r["updateTime"],
            "creatorUserId": r["creatorUserId"],
            "alternateLink": r["alternateLink"],
        })
    return out


def _coerce_materials(rows):
    out = []
    for r in rows:
        out.append({
            "courseId": r["courseId"],
            "id": r["id"],
            "title": r["title"],
            "description": r["description"],
            "state": r["state"],
            "creationTime": r["creationTime"],
            "updateTime": r["updateTime"],
            "creatorUserId": r["creatorUserId"],
            "topicId": r["topicId"] if r["topicId"] else None,
            "alternateLink": r["alternateLink"],
            "materials": [{"link": {"url": r["materialUrl"], "title": r["title"]}}] if r.get("materialUrl") else [],
        })
    return out


# Load all data at module init
_courses = _coerce_courses(_load("courses.csv"))
_coursework = _coerce_coursework(_load("coursework.csv"))
_topics = _coerce_topics(_load("topics.csv"))
_students = _coerce_students(_load("students.csv"))
_teachers = _coerce_teachers(_load("teachers.csv"))
_submissions = _coerce_submissions(_load("submissions.csv"))
_announcements = _coerce_announcements(_load("announcements.csv"))
_materials = _coerce_materials(_load("materials.csv"))

# Mutable in-memory stores
_courses_store = deepcopy(_courses)
_coursework_store = deepcopy(_coursework)
_topics_store = deepcopy(_topics)
_students_store = deepcopy(_students)
_teachers_store = deepcopy(_teachers)
_submissions_store = deepcopy(_submissions)
_announcements_store = deepcopy(_announcements)
_materials_store = deepcopy(_materials)

_next_course_id = 5
_next_cw_id = 400
_next_topic_id = 400
_next_sub_id = 100
_next_ann_id = 20
_next_mat_id = 10


# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------

def list_courses(course_states=None, page_size=20, page_token=0):
    results = list(_courses_store)
    if course_states:
        states = [s.strip().upper() for s in course_states.split(",")]
        results = [c for c in results if c["courseState"] in states]

    total = len(results)
    offset = int(page_token) if page_token else 0
    page_results = results[offset: offset + page_size]
    next_token = str(offset + page_size) if offset + page_size < total else None
    resp = {"courses": page_results}
    if next_token:
        resp["nextPageToken"] = next_token
    return resp


def get_course(course_id):
    for c in _courses_store:
        if c["id"] == course_id:
            return {"course": c}
    return {"error": f"Course {course_id} not found"}


def create_course(data):
    global _next_course_id
    required = ["name"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    now = _now()
    course = {
        "id": f"course_{_next_course_id:03d}",
        "name": data["name"],
        "section": data.get("section", ""),
        "descriptionHeading": data.get("descriptionHeading", ""),
        "description": data.get("description", ""),
        "room": data.get("room", ""),
        "ownerId": data.get("ownerId", "teacher_001"),
        "courseState": "ACTIVE",
        "creationTime": now,
        "updateTime": now,
        "enrollmentCode": f"code{_next_course_id}",
        "alternateLink": f"https://classroom.google.com/c/course_{_next_course_id:03d}",
        "guardiansEnabled": False,
        "calendarId": f"calendar_{_next_course_id:03d}",
    }
    _courses_store.append(course)
    _next_course_id += 1
    return {"course": course}


def update_course(course_id, data):
    for i, c in enumerate(_courses_store):
        if c["id"] == course_id:
            updatable = {"name", "section", "descriptionHeading", "description",
                         "room", "courseState", "guardiansEnabled"}
            for k, v in data.items():
                if k in updatable:
                    _courses_store[i][k] = v
            _courses_store[i]["updateTime"] = _now()
            return {"course": _courses_store[i]}
    return {"error": f"Course {course_id} not found"}


def archive_course(course_id):
    for i, c in enumerate(_courses_store):
        if c["id"] == course_id:
            _courses_store[i]["courseState"] = "ARCHIVED"
            _courses_store[i]["updateTime"] = _now()
            return {"course": _courses_store[i]}
    return {"error": f"Course {course_id} not found"}


# ---------------------------------------------------------------------------
# Course Work
# ---------------------------------------------------------------------------

def list_coursework(course_id, topic_id=None, course_work_states=None,
                    order_by=None, page_size=20, page_token=0):
    # Check course exists
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}

    results = [cw for cw in _coursework_store if cw["courseId"] == course_id]

    if topic_id:
        results = [cw for cw in results if cw["topicId"] == topic_id]
    if course_work_states:
        states = [s.strip().upper() for s in course_work_states.split(",")]
        results = [cw for cw in results if cw["state"] in states]

    if order_by:
        if "updateTime" in order_by:
            reverse = "desc" in order_by.lower()
            results = sorted(results, key=lambda x: x["updateTime"], reverse=reverse)
        elif "dueDate" in order_by:
            def due_sort_key(cw):
                if cw.get("dueDate"):
                    return f"{cw['dueDate']['year']:04d}-{cw['dueDate']['month']:02d}-{cw['dueDate']['day']:02d}"
                return "9999-99-99"
            reverse = "desc" in order_by.lower()
            results = sorted(results, key=due_sort_key, reverse=reverse)

    total = len(results)
    offset = int(page_token) if page_token else 0
    page_results = results[offset: offset + page_size]
    next_token = str(offset + page_size) if offset + page_size < total else None
    resp = {"courseWork": page_results}
    if next_token:
        resp["nextPageToken"] = next_token
    return resp


def get_coursework(course_id, coursework_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for cw in _coursework_store:
        if cw["courseId"] == course_id and cw["id"] == coursework_id:
            return {"courseWork": cw}
    return {"error": f"CourseWork {coursework_id} not found in course {course_id}"}


def create_coursework(course_id, data):
    global _next_cw_id
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}

    required = ["title", "workType"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    now = _now()
    cw = {
        "courseId": course_id,
        "id": f"cw_{_next_cw_id}",
        "title": data["title"],
        "description": data.get("description", ""),
        "state": data.get("state", "PUBLISHED"),
        "maxPoints": float(data["maxPoints"]) if data.get("maxPoints") else None,
        "workType": data["workType"],
        "topicId": data.get("topicId"),
        "creationTime": now,
        "updateTime": now,
        "dueDate": data.get("dueDate"),
        "dueTime": data.get("dueTime"),
        "alternateLink": f"https://classroom.google.com/c/{course_id}/a/cw_{_next_cw_id}",
    }
    _coursework_store.append(cw)
    _next_cw_id += 1
    return {"courseWork": cw}


def update_coursework(course_id, coursework_id, data):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for i, cw in enumerate(_coursework_store):
        if cw["courseId"] == course_id and cw["id"] == coursework_id:
            updatable = {"title", "description", "state", "maxPoints",
                         "dueDate", "dueTime", "topicId"}
            for k, v in data.items():
                if k in updatable:
                    if k == "maxPoints" and v is not None:
                        _coursework_store[i][k] = float(v)
                    else:
                        _coursework_store[i][k] = v
            _coursework_store[i]["updateTime"] = _now()
            return {"courseWork": _coursework_store[i]}
    return {"error": f"CourseWork {coursework_id} not found in course {course_id}"}


def delete_coursework(course_id, coursework_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for i, cw in enumerate(_coursework_store):
        if cw["courseId"] == course_id and cw["id"] == coursework_id:
            _coursework_store.pop(i)
            return {"deleted": True}
    return {"error": f"CourseWork {coursework_id} not found in course {course_id}"}


# ---------------------------------------------------------------------------
# Topics
# ---------------------------------------------------------------------------

def list_topics(course_id, page_size=20, page_token=0):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}

    results = [t for t in _topics_store if t["courseId"] == course_id]
    total = len(results)
    offset = int(page_token) if page_token else 0
    page_results = results[offset: offset + page_size]
    next_token = str(offset + page_size) if offset + page_size < total else None
    resp = {"topic": page_results}
    if next_token:
        resp["nextPageToken"] = next_token
    return resp


def get_topic(course_id, topic_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for t in _topics_store:
        if t["courseId"] == course_id and t["topicId"] == topic_id:
            return {"topic": t}
    return {"error": f"Topic {topic_id} not found in course {course_id}"}


def create_topic(course_id, data):
    global _next_topic_id
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}

    if "name" not in data or not data["name"]:
        return {"error": "Missing required field: name"}

    topic = {
        "courseId": course_id,
        "topicId": f"topic_{_next_topic_id}",
        "name": data["name"],
        "updateTime": _now(),
    }
    _topics_store.append(topic)
    _next_topic_id += 1
    return {"topic": topic}


def update_topic(course_id, topic_id, data):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for i, t in enumerate(_topics_store):
        if t["courseId"] == course_id and t["topicId"] == topic_id:
            if "name" in data:
                _topics_store[i]["name"] = data["name"]
            _topics_store[i]["updateTime"] = _now()
            return {"topic": _topics_store[i]}
    return {"error": f"Topic {topic_id} not found in course {course_id}"}


def delete_topic(course_id, topic_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for i, t in enumerate(_topics_store):
        if t["courseId"] == course_id and t["topicId"] == topic_id:
            _topics_store.pop(i)
            return {"deleted": True}
    return {"error": f"Topic {topic_id} not found in course {course_id}"}


# ---------------------------------------------------------------------------
# Student Submissions
# ---------------------------------------------------------------------------

def list_submissions(course_id, coursework_id, states=None, late=None,
                     page_size=20, page_token=0):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    if not any(cw["courseId"] == course_id and cw["id"] == coursework_id
               for cw in _coursework_store):
        return {"error": f"CourseWork {coursework_id} not found in course {course_id}"}

    results = [s for s in _submissions_store
               if s["courseId"] == course_id and s["courseWorkId"] == coursework_id]

    if states:
        state_list = [s.strip().upper() for s in states.split(",")]
        results = [s for s in results if s["state"] in state_list]
    if late is not None:
        results = [s for s in results if s["late"] == late]

    total = len(results)
    offset = int(page_token) if page_token else 0
    page_results = results[offset: offset + page_size]
    next_token = str(offset + page_size) if offset + page_size < total else None
    resp = {"studentSubmissions": page_results}
    if next_token:
        resp["nextPageToken"] = next_token
    return resp


def get_submission(course_id, coursework_id, submission_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for s in _submissions_store:
        if (s["courseId"] == course_id and s["courseWorkId"] == coursework_id
                and s["id"] == submission_id):
            return {"studentSubmission": s}
    return {"error": f"Submission {submission_id} not found"}


def grade_submission(course_id, coursework_id, submission_id, data):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for i, s in enumerate(_submissions_store):
        if (s["courseId"] == course_id and s["courseWorkId"] == coursework_id
                and s["id"] == submission_id):
            if "assignedGrade" in data and data["assignedGrade"] is not None:
                _submissions_store[i]["assignedGrade"] = float(data["assignedGrade"])
            if "draftGrade" in data and data["draftGrade"] is not None:
                _submissions_store[i]["draftGrade"] = float(data["draftGrade"])
            _submissions_store[i]["updateTime"] = _now()
            return {"studentSubmission": _submissions_store[i]}
    return {"error": f"Submission {submission_id} not found"}


def return_submission(course_id, coursework_id, submission_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for i, s in enumerate(_submissions_store):
        if (s["courseId"] == course_id and s["courseWorkId"] == coursework_id
                and s["id"] == submission_id):
            _submissions_store[i]["state"] = "RETURNED"
            _submissions_store[i]["updateTime"] = _now()
            return {"studentSubmission": _submissions_store[i]}
    return {"error": f"Submission {submission_id} not found"}


def reclaim_submission(course_id, coursework_id, submission_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for i, s in enumerate(_submissions_store):
        if (s["courseId"] == course_id and s["courseWorkId"] == coursework_id
                and s["id"] == submission_id):
            _submissions_store[i]["state"] = "RECLAIMED_BY_STUDENT"
            _submissions_store[i]["updateTime"] = _now()
            return {"studentSubmission": _submissions_store[i]}
    return {"error": f"Submission {submission_id} not found"}


# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------

def list_students(course_id, page_size=30, page_token=0):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}

    results = [s for s in _students_store if s["courseId"] == course_id]
    total = len(results)
    offset = int(page_token) if page_token else 0
    page_results = results[offset: offset + page_size]
    next_token = str(offset + page_size) if offset + page_size < total else None
    resp = {"students": page_results}
    if next_token:
        resp["nextPageToken"] = next_token
    return resp


def get_student(course_id, user_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for s in _students_store:
        if s["courseId"] == course_id and s["userId"] == user_id:
            return {"student": s}
    return {"error": f"Student {user_id} not found in course {course_id}"}


def invite_student(course_id, data):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}

    if "emailAddress" not in data or not data["emailAddress"]:
        return {"error": "Missing required field: emailAddress"}

    # Check if student already enrolled
    email = data["emailAddress"]
    for s in _students_store:
        if s["courseId"] == course_id and s["profile"]["emailAddress"] == email:
            return {"error": f"Student with email {email} already enrolled in course {course_id}"}

    # Generate a new student entry
    user_id = f"student_new_{len(_students_store) + 1}"
    student = {
        "courseId": course_id,
        "userId": user_id,
        "profile": {
            "id": user_id,
            "name": {"fullName": data.get("fullName", email.split("@")[0])},
            "emailAddress": email,
            "photoUrl": f"https://lh3.googleusercontent.com/a/{user_id}",
        },
    }
    _students_store.append(student)
    return {"student": student}


def remove_student(course_id, user_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for i, s in enumerate(_students_store):
        if s["courseId"] == course_id and s["userId"] == user_id:
            _students_store.pop(i)
            return {"deleted": True}
    return {"error": f"Student {user_id} not found in course {course_id}"}


# ---------------------------------------------------------------------------
# Teachers
# ---------------------------------------------------------------------------

def list_teachers(course_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}

    results = [t for t in _teachers_store if t["courseId"] == course_id]
    return {"teachers": results}


def get_teacher(course_id, user_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for t in _teachers_store:
        if t["courseId"] == course_id and t["userId"] == user_id:
            return {"teacher": t}
    return {"error": f"Teacher {user_id} not found in course {course_id}"}


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------

def list_announcements(course_id, announcement_states=None, page_size=20, page_token=0):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}

    results = [a for a in _announcements_store if a["courseId"] == course_id]

    if announcement_states:
        states = [s.strip().upper() for s in announcement_states.split(",")]
        results = [a for a in results if a["state"] in states]

    results = sorted(results, key=lambda x: x["creationTime"], reverse=True)

    total = len(results)
    offset = int(page_token) if page_token else 0
    page_results = results[offset: offset + page_size]
    next_token = str(offset + page_size) if offset + page_size < total else None
    resp = {"announcements": page_results}
    if next_token:
        resp["nextPageToken"] = next_token
    return resp


def get_announcement(course_id, announcement_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for a in _announcements_store:
        if a["courseId"] == course_id and a["id"] == announcement_id:
            return {"announcement": a}
    return {"error": f"Announcement {announcement_id} not found in course {course_id}"}


def create_announcement(course_id, data):
    global _next_ann_id
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}

    if "text" not in data or not data["text"]:
        return {"error": "Missing required field: text"}

    now = _now()
    ann = {
        "courseId": course_id,
        "id": f"ann_{_next_ann_id:03d}",
        "text": data["text"],
        "state": data.get("state", "PUBLISHED"),
        "creationTime": now,
        "updateTime": now,
        "creatorUserId": data.get("creatorUserId", "teacher_001"),
        "alternateLink": f"https://classroom.google.com/c/{course_id}/p/ann_{_next_ann_id:03d}",
    }
    _announcements_store.append(ann)
    _next_ann_id += 1
    return {"announcement": ann}


def update_announcement(course_id, announcement_id, data):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for i, a in enumerate(_announcements_store):
        if a["courseId"] == course_id and a["id"] == announcement_id:
            updatable = {"text", "state"}
            for k, v in data.items():
                if k in updatable:
                    _announcements_store[i][k] = v
            _announcements_store[i]["updateTime"] = _now()
            return {"announcement": _announcements_store[i]}
    return {"error": f"Announcement {announcement_id} not found in course {course_id}"}


def delete_announcement(course_id, announcement_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for i, a in enumerate(_announcements_store):
        if a["courseId"] == course_id and a["id"] == announcement_id:
            _announcements_store.pop(i)
            return {"deleted": True}
    return {"error": f"Announcement {announcement_id} not found in course {course_id}"}


# ---------------------------------------------------------------------------
# Course Work Materials
# ---------------------------------------------------------------------------

def list_materials(course_id, page_size=20, page_token=0):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}

    results = [m for m in _materials_store if m["courseId"] == course_id]
    total = len(results)
    offset = int(page_token) if page_token else 0
    page_results = results[offset: offset + page_size]
    next_token = str(offset + page_size) if offset + page_size < total else None
    resp = {"courseWorkMaterial": page_results}
    if next_token:
        resp["nextPageToken"] = next_token
    return resp


def get_material(course_id, material_id):
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}
    for m in _materials_store:
        if m["courseId"] == course_id and m["id"] == material_id:
            return {"courseWorkMaterial": m}
    return {"error": f"Material {material_id} not found in course {course_id}"}


def create_material(course_id, data):
    global _next_mat_id
    if not any(c["id"] == course_id for c in _courses_store):
        return {"error": f"Course {course_id} not found"}

    if "title" not in data or not data["title"]:
        return {"error": "Missing required field: title"}

    now = _now()
    mat = {
        "courseId": course_id,
        "id": f"mat_{_next_mat_id:03d}",
        "title": data["title"],
        "description": data.get("description", ""),
        "state": data.get("state", "PUBLISHED"),
        "creationTime": now,
        "updateTime": now,
        "creatorUserId": data.get("creatorUserId", "teacher_001"),
        "topicId": data.get("topicId"),
        "alternateLink": f"https://classroom.google.com/c/{course_id}/m/mat_{_next_mat_id:03d}",
        "materials": data.get("materials", []),
    }
    _materials_store.append(mat)
    _next_mat_id += 1
    return {"courseWorkMaterial": mat}
