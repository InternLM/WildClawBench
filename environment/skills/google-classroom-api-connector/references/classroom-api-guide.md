# Google Classroom API Guide

Detailed patterns and examples for working with the Google Classroom teacher API.

## Base URL

Set via the `GOOGLE_CLASSROOM_API_URL` environment variable (e.g. `http://google-classroom-api:8002`).

## Health

```bash
curl "$GOOGLE_CLASSROOM_API_URL/health"
```

## Courses

```bash
# List all courses
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses"

# List active courses only
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses?courseStates=ACTIVE"

# List archived courses
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses?courseStates=ARCHIVED"

# Get a specific course
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001"

# Create a new course
curl -X POST "$GOOGLE_CLASSROOM_API_URL/v1/courses" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Data Structures (Spring 2025)",
    "section": "Period 7",
    "description": "Advanced data structures using Java",
    "room": "Room 214"
  }'

# Update a course
curl -X PATCH "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001" \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated: Rigorous college-level Java course with AP exam focus."}'

# Archive a course
curl -X POST "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_004:archive"
```

## Course Work (Assignments & Questions)

```bash
# List all coursework for a course
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork"

# Filter by topic
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork?topicId=topic_104"

# Order by due date descending
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork?orderBy=dueDate%20desc"

# Get a specific coursework item
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_101"

# Create an assignment
curl -X POST "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Recursion Challenge",
    "description": "Implement recursive solutions for factorial, fibonacci, and tower of hanoi.",
    "workType": "ASSIGNMENT",
    "maxPoints": 75,
    "topicId": "topic_107",
    "dueDate": {"year": 2025, "month": 5, "day": 9},
    "dueTime": {"hours": 23, "minutes": 59}
  }'

# Create a short answer question
curl -X POST "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_002/courseWork" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "CSS Box Model Quiz",
    "description": "What is the difference between content-box and border-box?",
    "workType": "SHORT_ANSWER_QUESTION",
    "maxPoints": 10,
    "topicId": "topic_202"
  }'

# Update coursework (extend due date, increase points)
curl -X PATCH "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_109" \
  -H "Content-Type: application/json" \
  -d '{"dueDate": {"year": 2025, "month": 5, "day": 5}, "maxPoints": 120}'

# Delete coursework
curl -X DELETE "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_103"
```

## Topics

```bash
# List topics for a course
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/topics"

# Get a specific topic
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/topics/topic_101"

# Create a topic
curl -X POST "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/topics" \
  -H "Content-Type: application/json" \
  -d '{"name": "Unit 8: 2D Arrays"}'

# Update a topic
curl -X PATCH "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/topics/topic_101" \
  -H "Content-Type: application/json" \
  -d '{"name": "Unit 1: Primitive Types & Expressions"}'

# Delete a topic
curl -X DELETE "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/topics/topic_107"
```

## Student Submissions

```bash
# List all submissions for an assignment
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_101/studentSubmissions"

# Filter by state (find submissions awaiting grading)
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_108/studentSubmissions?states=TURNED_IN"

# Filter for returned (graded) submissions
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_101/studentSubmissions?states=RETURNED"

# Filter for late submissions
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_101/studentSubmissions?late=true"

# Get a specific submission
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_101/studentSubmissions/sub_001"

# Grade a submission
curl -X PATCH "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_024" \
  -H "Content-Type: application/json" \
  -d '{"assignedGrade": 45, "draftGrade": 45}'

# Return a graded submission to the student
curl -X POST "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_024:return"

# Reclaim a submission (student takes it back)
curl -X POST "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_025:reclaim"
```

## Students

```bash
# List students in a course
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/students"

# Paginate (page 2 with 10 per page)
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_002/students?pageSize=10&pageToken=10"

# Get a specific student
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/students/student_001"

# Invite a student by email
curl -X POST "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/students" \
  -H "Content-Type: application/json" \
  -d '{"emailAddress": "newstudent@westlake.edu", "fullName": "New Student"}'

# Remove a student
curl -X DELETE "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/students/student_048"
```

## Teachers

```bash
# List teachers in a course
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/teachers"

# Get a specific teacher
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/teachers/teacher_001"
```

## Announcements

```bash
# List announcements for a course
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/announcements"

# Get a specific announcement
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/announcements/ann_001"

# Create an announcement
curl -X POST "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/announcements" \
  -H "Content-Type: application/json" \
  -d '{"text": "Extra credit opportunity: attend the CS guest speaker event this Thursday at 3pm in the auditorium."}'

# Update an announcement
curl -X PATCH "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/announcements/ann_002" \
  -H "Content-Type: application/json" \
  -d '{"text": "UPDATED: Unit 2 test moved to Monday. Extra review session Friday after school."}'

# Delete an announcement
curl -X DELETE "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/announcements/ann_004"
```

## Course Work Materials

```bash
# List materials for a course
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWorkMaterials"

# Get a specific material
curl "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWorkMaterials/mat_001"

# Create a material (link resource)
curl -X POST "$GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWorkMaterials" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "ArrayList Tutorial Video",
    "description": "Comprehensive video tutorial on Java ArrayList operations",
    "topicId": "topic_107",
    "materials": [{"link": {"url": "https://youtube.com/watch?v=example", "title": "ArrayList Tutorial"}}]
  }'
```

## Common Patterns

### Grade All Pending Submissions for an Assignment

```python
import json
import os
import urllib.request

BASE = os.environ["GOOGLE_CLASSROOM_API_URL"]
COURSE = "course_001"
COURSEWORK = "cw_108"

def api_get(path):
    with urllib.request.urlopen(f"{BASE}{path}") as r:
        return json.loads(r.read())

def api_patch(path, data):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def api_post(path):
    req = urllib.request.Request(f"{BASE}{path}", data=b"", method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

subs = api_get(f"/v1/courses/{COURSE}/courseWork/{COURSEWORK}/studentSubmissions?states=TURNED_IN")
for sub in subs.get("studentSubmissions", []):
    sid = sub["id"]
    grade = 42  # your grading logic here
    api_patch(f"/v1/courses/{COURSE}/courseWork/{COURSEWORK}/studentSubmissions/{sid}", {"assignedGrade": grade, "draftGrade": grade})
    api_post(f"/v1/courses/{COURSE}/courseWork/{COURSEWORK}/studentSubmissions/{sid}:return")
    print(f"Graded and returned {sid} with score {grade}")
```

### Check for Late Submissions Across All Assignments

```python
courses = api_get("/v1/courses?courseStates=ACTIVE")
for course in courses.get("courses", []):
    cid = course["id"]
    cw_list = api_get(f"/v1/courses/{cid}/courseWork?pageSize=100")
    for cw in cw_list.get("courseWork", []):
        subs = api_get(f"/v1/courses/{cid}/courseWork/{cw['id']}/studentSubmissions?late=true")
        for sub in subs.get("studentSubmissions", []):
            print(f"Late: {sub['userId']} in {course['name']} / {cw['title']}")
```

### Generate a Grading Summary Report

```python
COURSE = "course_001"
cw_list = api_get(f"/v1/courses/{COURSE}/courseWork?pageSize=100")
for cw in cw_list.get("courseWork", []):
    subs = api_get(f"/v1/courses/{COURSE}/courseWork/{cw['id']}/studentSubmissions?pageSize=100")
    all_subs = subs.get("studentSubmissions", [])
    graded = [s for s in all_subs if s.get("assignedGrade") is not None]
    turned_in = [s for s in all_subs if s["state"] == "TURNED_IN"]
    if graded:
        avg = sum(s["assignedGrade"] for s in graded) / len(graded)
        print(f"{cw['title']}: {len(graded)} graded (avg {avg:.1f}/{cw['maxPoints']}), {len(turned_in)} awaiting grading")
    else:
        print(f"{cw['title']}: {len(turned_in)} submissions awaiting grading, none graded yet")
```
