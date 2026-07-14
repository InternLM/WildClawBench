---
name: google-classroom-api-connector
description: >
  Google Classroom API HTTP endpoints for course management, assignments,
  grading, student rosters, announcements, and course materials.
---

# Google Classroom API

## Base URL

| Variable | Purpose |
|----------|---------|
| `GOOGLE_CLASSROOM_API_URL` | Base URL for all requests |

All paths below are relative to `GOOGLE_CLASSROOM_API_URL`.

---

## Health

```
GET /health
```

Returns `{"status": "ok"}`.

---

## Courses

### List courses

Returns a paginated list of all courses accessible to the authenticated user. Courses can be filtered by their lifecycle state. Results include course metadata such as name, section, description, room, owner, enrollment code, and current state.

```
GET /v1/courses
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseStates` | string | query | no | Filter by lifecycle state: `ACTIVE`, `ARCHIVED`, `PROVISIONED`, `DECLINED`, `SUSPENDED` |
| `pageSize` | integer | query | no | Maximum number of results to return, 1-100. Default: 20 |
| `pageToken` | string | query | no | Pagination token from a previous response's `nextPageToken` field. Interpreted as a numeric offset. |

### Get course

Returns the full details of a single course identified by its course ID. The response includes all course properties: name, section, description heading, description, room, owner ID, enrollment code, course state, creation time, and update time.

```
GET /v1/courses/{courseId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |

### Create course

Creates a new course with the specified properties. The course is created in `ACTIVE` state by default. Returns the newly created course object with a server-generated `id`, `enrollmentCode`, and timestamps.

```
POST /v1/courses
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Course name |
| `section` | string | no | Section/period identifier |
| `descriptionHeading` | string | no | Short heading for course description |
| `description` | string | no | Full course description |
| `room` | string | no | Physical location or room number |
| `ownerId` | string | no | User ID of the course owner |

### Update course

Partially updates an existing course. Only the fields provided in the request body are modified; all other fields remain unchanged. Returns the updated course object.

```
PATCH /v1/courses/{courseId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | no | Course name |
| `section` | string | no | Section/period identifier |
| `descriptionHeading` | string | no | Short heading for course description |
| `description` | string | no | Full course description |
| `room` | string | no | Physical location or room number |
| `courseState` | string | no | Course lifecycle state: `ACTIVE`, `ARCHIVED`, `PROVISIONED`, `DECLINED`, `SUSPENDED` |

### Archive course

Transitions a course to `ARCHIVED` state. Archived courses are read-only — no new coursework, announcements, or enrollments can be created. Returns the updated course object with `courseState` set to `ARCHIVED`.

```
POST /v1/courses/{courseId}:archive
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |

---

## Course Work

### List course work

Returns a paginated list of coursework items (assignments, questions) for a course. Results can be filtered by topic and publication state, and sorted by due date or update time. Each item includes title, description, work type, max points, due date/time, state, topic ID, and timestamps.

```
GET /v1/courses/{courseId}/courseWork
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `topicId` | string | query | no | Filter by topic ID |
| `courseWorkStates` | string | query | no | Filter by state: `PUBLISHED`, `DRAFT` |
| `orderBy` | string | query | no | Sort order: `dueDate desc`, `updateTime desc` |
| `pageSize` | integer | query | no | Maximum results, 1-100. Default: 20 |
| `pageToken` | string | query | no | Pagination token |

### Get course work

Returns the full details of a single coursework item, including its title, description, work type, max points, due date and time, state, topic association, creation time, and update time.

```
GET /v1/courses/{courseId}/courseWork/{courseWorkId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `courseWorkId` | string | path | yes | Coursework identifier |

### Create course work

Creates a new coursework item in a course. Supports assignments (`ASSIGNMENT`), short-answer questions (`SHORT_ANSWER_QUESTION`), and multiple-choice questions (`MULTIPLE_CHOICE_QUESTION`). The item is created in `PUBLISHED` state by default. Returns the newly created coursework object with a server-generated ID.

```
POST /v1/courses/{courseId}/courseWork
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | yes | Coursework title |
| `description` | string | no | Coursework description or instructions |
| `workType` | string | no | Type of work: `ASSIGNMENT`, `SHORT_ANSWER_QUESTION`, `MULTIPLE_CHOICE_QUESTION`. Default: `ASSIGNMENT` |
| `state` | string | no | Publication state: `PUBLISHED`, `DRAFT` |
| `maxPoints` | number | no | Maximum grade points |
| `topicId` | string | no | Topic ID to associate with |
| `dueDate` | object | no | Due date as `{"year": int, "month": int, "day": int}` |
| `dueTime` | object | no | Due time as `{"hours": int, "minutes": int}` |

### Update course work

Partially updates an existing coursework item. Only the fields provided in the request body are modified. Returns the updated coursework object.

```
PATCH /v1/courses/{courseId}/courseWork/{courseWorkId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `courseWorkId` | string | path | yes | Coursework identifier |

**Request body**

Same fields as Create course work. All fields are optional.

### Delete course work

Permanently deletes a coursework item and all associated student submissions from the course. This action cannot be undone.

```
DELETE /v1/courses/{courseId}/courseWork/{courseWorkId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `courseWorkId` | string | path | yes | Coursework identifier |

---

## Topics

### List topics

Returns a paginated list of topics defined in a course. Topics are organizational units that group coursework items. Each topic includes its ID, name, and course ID.

```
GET /v1/courses/{courseId}/topics
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `pageSize` | integer | query | no | Maximum results, 1-100. Default: 20 |
| `pageToken` | string | query | no | Pagination token |

### Get topic

Returns the details of a single topic, including its ID, name, course ID, and update time.

```
GET /v1/courses/{courseId}/topics/{topicId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `topicId` | string | path | yes | Topic identifier |

### Create topic

Creates a new topic in a course. Returns the newly created topic with a server-generated `topicId`.

```
POST /v1/courses/{courseId}/topics
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Topic name |

### Update topic

Updates the name of an existing topic. Returns the updated topic object.

```
PATCH /v1/courses/{courseId}/topics/{topicId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `topicId` | string | path | yes | Topic identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Updated topic name |

### Delete topic

Permanently deletes a topic from a course. Coursework items previously associated with the deleted topic retain their content but lose their topic grouping.

```
DELETE /v1/courses/{courseId}/topics/{topicId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `topicId` | string | path | yes | Topic identifier |

---

## Student Submissions

### List student submissions

Returns a paginated list of student submissions for a specific coursework item. Results can be filtered by submission state and late status. Each submission includes the student's user ID, submission state, assigned grade, draft grade, late flag, creation time, and update time.

```
GET /v1/courses/{courseId}/courseWork/{courseWorkId}/studentSubmissions
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `courseWorkId` | string | path | yes | Coursework identifier |
| `states` | string | query | no | Filter by state: `NEW`, `CREATED`, `TURNED_IN`, `RETURNED`, `RECLAIMED_BY_STUDENT` |
| `late` | string | query | no | Filter late submissions: `true` or `false` |
| `pageSize` | integer | query | no | Maximum results, 1-100. Default: 20 |
| `pageToken` | string | query | no | Pagination token |

### Get student submission

Returns the full details of a single student submission, including the student's user ID, current state, assigned grade, draft grade, whether it was submitted late, and all timestamps.

```
GET /v1/courses/{courseId}/courseWork/{courseWorkId}/studentSubmissions/{submissionId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `courseWorkId` | string | path | yes | Coursework identifier |
| `submissionId` | string | path | yes | Submission identifier |

### Grade student submission

Updates the grade on a student submission. Both the finalized assigned grade and the provisional draft grade can be set. Returns the updated submission object.

```
PATCH /v1/courses/{courseId}/courseWork/{courseWorkId}/studentSubmissions/{submissionId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `courseWorkId` | string | path | yes | Coursework identifier |
| `submissionId` | string | path | yes | Submission identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `assignedGrade` | number | no | Final grade visible to student |
| `draftGrade` | number | no | Draft grade visible only to teacher |

### Return student submission

Returns a graded submission to the student. Transitions the submission state to `RETURNED`, making the assigned grade visible to the student.

```
POST /v1/courses/{courseId}/courseWork/{courseWorkId}/studentSubmissions/{submissionId}:return
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `courseWorkId` | string | path | yes | Coursework identifier |
| `submissionId` | string | path | yes | Submission identifier |

### Reclaim student submission

Reclaims a submission on behalf of the student. Transitions the submission state from `TURNED_IN` back to `RECLAIMED_BY_STUDENT`, allowing the student to continue editing.

```
POST /v1/courses/{courseId}/courseWork/{courseWorkId}/studentSubmissions/{submissionId}:reclaim
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `courseWorkId` | string | path | yes | Coursework identifier |
| `submissionId` | string | path | yes | Submission identifier |

---

## Students

### List students

Returns a paginated list of students enrolled in a course. Each student record includes the user's profile (ID, name, email) and enrollment metadata.

```
GET /v1/courses/{courseId}/students
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `pageSize` | integer | query | no | Maximum results, 1-100. Default: 20 |
| `pageToken` | string | query | no | Pagination token |

### Get student

Returns the profile and enrollment details of a single student in a course, identified by their user ID.

```
GET /v1/courses/{courseId}/students/{userId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `userId` | string | path | yes | Student user identifier |

### Invite student

Adds a new student to the course by email address. If the student does not already exist, a profile is created with the provided full name. Returns the newly enrolled student object.

```
POST /v1/courses/{courseId}/students
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `emailAddress` | string | yes | Student's email address |
| `fullName` | string | no | Student's display name |

### Remove student

Removes a student from the course. The student's submissions are retained but they lose access to the course. This action cannot be undone.

```
DELETE /v1/courses/{courseId}/students/{userId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `userId` | string | path | yes | Student user identifier |

---

## Teachers

### List teachers

Returns the list of teachers associated with a course. Each teacher record includes the user's profile information (ID, name, email).

```
GET /v1/courses/{courseId}/teachers
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |

### Get teacher

Returns the profile of a single teacher in a course, identified by their user ID.

```
GET /v1/courses/{courseId}/teachers/{userId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `userId` | string | path | yes | Teacher user identifier |

---

## Announcements

### List announcements

Returns a paginated list of announcements posted to a course. Announcements can be filtered by publication state. Each announcement includes its text content, state, creator ID, creation time, and update time.

```
GET /v1/courses/{courseId}/announcements
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `announcementStates` | string | query | no | Filter by state: `PUBLISHED`, `DRAFT` |
| `pageSize` | integer | query | no | Maximum results, 1-100. Default: 20 |
| `pageToken` | string | query | no | Pagination token |

### Get announcement

Returns the full details of a single announcement, including its text, state, creator, and timestamps.

```
GET /v1/courses/{courseId}/announcements/{announcementId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `announcementId` | string | path | yes | Announcement identifier |

### Create announcement

Posts a new announcement to a course. The announcement is created in `PUBLISHED` state by default and becomes visible to all enrolled students.

```
POST /v1/courses/{courseId}/announcements
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | yes | Announcement text content |
| `state` | string | no | Publication state: `PUBLISHED`, `DRAFT`. Default: `PUBLISHED` |

### Update announcement

Partially updates an existing announcement. Only the provided fields are modified. Returns the updated announcement object.

```
PATCH /v1/courses/{courseId}/announcements/{announcementId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `announcementId` | string | path | yes | Announcement identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | no | Updated announcement text |
| `state` | string | no | Updated state: `PUBLISHED`, `DRAFT` |

### Delete announcement

Permanently deletes an announcement from a course. This action cannot be undone.

```
DELETE /v1/courses/{courseId}/announcements/{announcementId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `announcementId` | string | path | yes | Announcement identifier |

---

## Course Work Materials

### List course work materials

Returns a paginated list of supplementary materials shared in a course. Materials can include linked resources (URLs, documents). Each material includes its title, description, topic association, attached materials, and timestamps.

```
GET /v1/courses/{courseId}/courseWorkMaterials
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `pageSize` | integer | query | no | Maximum results, 1-100. Default: 20 |
| `pageToken` | string | query | no | Pagination token |

### Get course work material

Returns the full details of a single course work material, including its title, description, attached materials (links), topic association, and timestamps.

```
GET /v1/courses/{courseId}/courseWorkMaterials/{materialId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |
| `materialId` | string | path | yes | Material identifier |

### Create course work material

Creates a new supplementary material resource in a course. Materials can include link attachments with URLs and titles. Returns the newly created material object.

```
POST /v1/courses/{courseId}/courseWorkMaterials
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `courseId` | string | path | yes | Course identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | yes | Material title |
| `description` | string | no | Material description |
| `topicId` | string | no | Topic ID to associate with |
| `materials` | array | no | Array of material attachments. Each element: `{"link": {"url": "string", "title": "string"}}` |

---

## Errors

Error responses follow this format:

```json
{
  "error": {
    "code": 404,
    "message": "Course not found",
    "status": "NOT_FOUND"
  }
}
```

Common HTTP status codes:

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid parameters or malformed body) |
| 404 | Resource not found |
| 409 | Conflict (duplicate resource) |
