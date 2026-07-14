# Google Classroom API - Full Test Results

Total tests: 57

## 1. GET /health (Health check)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/health
```

HTTP Status: 200

```json
{
  "status": "ok"
}
```

## 2. GET /v1/courses (List all courses)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses
```

HTTP Status: 200

```json
{
  "courses": [
    {
      "id": "course_001",
      "name": "AP Computer Science A",
      "section": "Period 2",
      "descriptionHeading": "Welcome to AP CS A",
      "description": "Rigorous college-level course covering Java programming fundamentals including object-oriented design data structures and algorithms. Prepares students for the AP Computer Science A exam.",
      "room": "Room 214",
      "ownerId": "teacher_001",
      "courseState": "ACTIVE",
      "creationTime": "2025-01-06T08:00:00Z",
      "updateTime": "2025-04-25T14:30:00Z",
      "enrollmentCode": "apcsa25",
      "alternateLink": "https://classroom.google.com/c/course_001",
      "guardiansEnabled": false,
      "calendarId": "calendar_001"
    },
    {
      "id": "course_002",
      "name": "Intro to Web Development",
      "section": "Period 4",
      "descriptionHeading": "Welcome to Web Dev",
      "description": "Learn to build modern websites using HTML CSS and JavaScript. Project-based course covering responsive design DOM manipulation and basic web application architecture.",
      "room": "Room 214",
      "ownerId": "teacher_001",
      "courseState": "ACTIVE",
      "creationTime": "2025-01-06T08:00:00Z",
      "updateTime": "2025-04-26T09:15:00Z",
      "enrollmentCode": "webdev25",
      "alternateLink": "https://classroom.google.com/c/course_002",
      "guardiansEnabled": false,
      "calendarId": "calendar_002"
    },
    {
      "id": "course_003",
      "name": "AP Computer Science Principles",
      "section": "Period 6",
      "descriptionHeading": "Welcome to AP CSP",
      "description": "Explore the foundational concepts of computer science including abstraction algorithms data and the internet. Emphasizes creative problem-solving and real-world applications.",
      "room": "Room 214",
      "ownerId": "teacher_001",
      "courseState": "ACTIVE",
      "creationTime": "2025-01-06T08:00:00Z",
      "updateTime": "2025-04-24T16:45:00Z",
      "enrollmentCode": "apcsp25",
      "alternateLink": "https://classroom.google.com/c/course_003",
      "guardiansEnabled": false,
      "calendarId": "calendar_003"
    },
    {
      "id": "course_004",
      "name": "Intro to Python (Fall 2024)",
      "section": "Period 3",
      "descriptionHeading": "Welcome to Python",
      "description": "Introduction to programming using Python. Covers variables loops functions and basic data structures. No prior coding experience required.",
      "room": "Room 214",
      "ownerId": "teacher_001",
      "courseState": "ARCHIVED",
      "creationTime": "2024-08-19T08:00:00Z",
      "updateTime": "2024-12-20T15:00:00Z",
      "enrollmentCode": "python24",
      "alternateLink": "https://classroom.google.com/c/course_004",
      "guardiansEnabled": false,
      "calendarId": "calendar_004"
    }
  ]
}
```

## 3. GET /v1/courses?courseStates=ACTIVE (List active courses)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses?courseStates=ACTIVE
```

HTTP Status: 200

```json
{
  "courses": [
    {
      "id": "course_001",
      "name": "AP Computer Science A",
      "section": "Period 2",
      "descriptionHeading": "Welcome to AP CS A",
      "description": "Rigorous college-level course covering Java programming fundamentals including object-oriented design data structures and algorithms. Prepares students for the AP Computer Science A exam.",
      "room": "Room 214",
      "ownerId": "teacher_001",
      "courseState": "ACTIVE",
      "creationTime": "2025-01-06T08:00:00Z",
      "updateTime": "2025-04-25T14:30:00Z",
      "enrollmentCode": "apcsa25",
      "alternateLink": "https://classroom.google.com/c/course_001",
      "guardiansEnabled": false,
      "calendarId": "calendar_001"
    },
    {
      "id": "course_002",
      "name": "Intro to Web Development",
      "section": "Period 4",
      "descriptionHeading": "Welcome to Web Dev",
      "description": "Learn to build modern websites using HTML CSS and JavaScript. Project-based course covering responsive design DOM manipulation and basic web application architecture.",
      "room": "Room 214",
      "ownerId": "teacher_001",
      "courseState": "ACTIVE",
      "creationTime": "2025-01-06T08:00:00Z",
      "updateTime": "2025-04-26T09:15:00Z",
      "enrollmentCode": "webdev25",
      "alternateLink": "https://classroom.google.com/c/course_002",
      "guardiansEnabled": false,
      "calendarId": "calendar_002"
    },
    {
      "id": "course_003",
      "name": "AP Computer Science Principles",
      "section": "Period 6",
      "descriptionHeading": "Welcome to AP CSP",
      "description": "Explore the foundational concepts of computer science including abstraction algorithms data and the internet. Emphasizes creative problem-solving and real-world applications.",
      "room": "Room 214",
      "ownerId": "teacher_001",
      "courseState": "ACTIVE",
      "creationTime": "2025-01-06T08:00:00Z",
      "updateTime": "2025-04-24T16:45:00Z",
      "enrollmentCode": "apcsp25",
      "alternateLink": "https://classroom.google.com/c/course_003",
      "guardiansEnabled": false,
      "calendarId": "calendar_003"
    }
  ]
}
```

## 4. GET /v1/courses?courseStates=ARCHIVED (List archived courses)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses?courseStates=ARCHIVED
```

HTTP Status: 200

```json
{
  "courses": [
    {
      "id": "course_004",
      "name": "Intro to Python (Fall 2024)",
      "section": "Period 3",
      "descriptionHeading": "Welcome to Python",
      "description": "Introduction to programming using Python. Covers variables loops functions and basic data structures. No prior coding experience required.",
      "room": "Room 214",
      "ownerId": "teacher_001",
      "courseState": "ARCHIVED",
      "creationTime": "2024-08-19T08:00:00Z",
      "updateTime": "2024-12-20T15:00:00Z",
      "enrollmentCode": "python24",
      "alternateLink": "https://classroom.google.com/c/course_004",
      "guardiansEnabled": false,
      "calendarId": "calendar_004"
    }
  ]
}
```

## 5. GET /v1/courses/course_001 (Get course valid)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001
```

HTTP Status: 200

```json
{
  "course": {
    "id": "course_001",
    "name": "AP Computer Science A",
    "section": "Period 2",
    "descriptionHeading": "Welcome to AP CS A",
    "description": "Rigorous college-level course covering Java programming fundamentals including object-oriented design data structures and algorithms. Prepares students for the AP Computer Science A exam.",
    "room": "Room 214",
    "ownerId": "teacher_001",
    "courseState": "ACTIVE",
    "creationTime": "2025-01-06T08:00:00Z",
    "updateTime": "2025-04-25T14:30:00Z",
    "enrollmentCode": "apcsa25",
    "alternateLink": "https://classroom.google.com/c/course_001",
    "guardiansEnabled": false,
    "calendarId": "calendar_001"
  }
}
```

## 6. GET /v1/courses/course_999 (Get course 404)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_999
```

HTTP Status: 404

```json
{
  "error": "Course course_999 not found"
}
```

## 7. POST /v1/courses (Create course)

```
curl -s -X POST -H 'Content-Type: application/json' -d '{"name": "Data Structures (Spring 2025)", "section": "Period 7", "description": "Advanced DS", "room": "Room 214"}' $GOOGLE_CLASSROOM_API_URL/v1/courses
```

HTTP Status: 201

```json
{
  "course": {
    "id": "course_005",
    "name": "Data Structures (Spring 2025)",
    "section": "Period 7",
    "descriptionHeading": null,
    "description": "Advanced DS",
    "room": "Room 214",
    "ownerId": null,
    "courseState": "ACTIVE",
    "creationTime": "2026-05-06T18:44:02Z",
    "updateTime": "2026-05-06T18:44:02Z",
    "enrollmentCode": "code5",
    "alternateLink": "https://classroom.google.com/c/course_005",
    "guardiansEnabled": false,
    "calendarId": "calendar_005"
  }
}
```

## 8. PATCH /v1/courses/course_001 (Update course)

```
curl -s -X PATCH -H 'Content-Type: application/json' -d '{"description": "Updated AP CS A description"}' $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001
```

HTTP Status: 200

```json
{
  "course": {
    "id": "course_001",
    "name": "AP Computer Science A",
    "section": "Period 2",
    "descriptionHeading": "Welcome to AP CS A",
    "description": "Updated AP CS A description",
    "room": "Room 214",
    "ownerId": "teacher_001",
    "courseState": "ACTIVE",
    "creationTime": "2025-01-06T08:00:00Z",
    "updateTime": "2026-05-06T18:44:02Z",
    "enrollmentCode": "apcsa25",
    "alternateLink": "https://classroom.google.com/c/course_001",
    "guardiansEnabled": false,
    "calendarId": "calendar_001"
  }
}
```

## 9. POST /v1/courses/course_004:archive (Archive course)

```
curl -s -X POST $GOOGLE_CLASSROOM_API_URL/v1/courses/course_004:archive
```

HTTP Status: 200

```json
{
  "course": {
    "id": "course_004",
    "name": "Intro to Python (Fall 2024)",
    "section": "Period 3",
    "descriptionHeading": "Welcome to Python",
    "description": "Introduction to programming using Python. Covers variables loops functions and basic data structures. No prior coding experience required.",
    "room": "Room 214",
    "ownerId": "teacher_001",
    "courseState": "ARCHIVED",
    "creationTime": "2024-08-19T08:00:00Z",
    "updateTime": "2026-05-06T18:44:02Z",
    "enrollmentCode": "python24",
    "alternateLink": "https://classroom.google.com/c/course_004",
    "guardiansEnabled": false,
    "calendarId": "calendar_004"
  }
}
```

## 10. GET /v1/courses/course_001/courseWork (List coursework)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork
```

HTTP Status: 200

```json
{
  "courseWork": [
    {
      "courseId": "course_001",
      "id": "cw_101",
      "title": "Variables and Data Types Lab",
      "description": "Write a Java program that demonstrates the use of int double boolean and String variables. Include type casting examples.",
      "state": "PUBLISHED",
      "maxPoints": 25.0,
      "workType": "ASSIGNMENT",
      "topicId": "topic_101",
      "creationTime": "2025-01-13T09:00:00Z",
      "updateTime": "2025-01-13T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101",
      "dueDate": {
        "year": 2025,
        "month": 1,
        "day": 20
      },
      "dueTime": {
        "hours": 23,
        "minutes": 59
      }
    },
    {
      "courseId": "course_001",
      "id": "cw_102",
      "title": "String Methods Practice",
      "description": "Complete the StringExercises.java file implementing 5 string manipulation methods using charAt substring and indexOf.",
      "state": "PUBLISHED",
      "maxPoints": 50.0,
      "workType": "ASSIGNMENT",
      "topicId": "topic_102",
      "creationTime": "2025-01-29T09:00:00Z",
      "updateTime": "2025-01-29T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_102",
      "dueDate": {
        "year": 2025,
        "month": 2,
        "day": 5
      },
      "dueTime": {
        "hours": 23,
        "minutes": 59
      }
    },
    {
      "courseId": "course_001",
      "id": "cw_103",
      "title": "Scanner Input Quiz",
      "description": "What method of the Scanner class is used to read an integer from the user?",
      "state": "PUBLISHED",
      "maxPoints": 10.0,
      "workType": "SHORT_ANSWER_QUESTION",
      "topicId": "topic_102",
      "creationTime": "2025-02-03T09:00:00Z",
      "updateTime": "2025-02-03T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_103",
      "dueDate": {
        "year": 2025,
        "month": 2,
        "day": 3
      },
      "dueTime": {
        "hours": 23,
        "minutes": 59
      }
    },
    {
      "courseId": "course_001",
      "id": "cw_104",
      "title": "If-Else Decision Making",
      "description": "Write a GradeCalculator program that takes a numeric score and outputs the letter grade using if-else chains.",
      "state": "PUBLISHED",
      "maxPoints": 50.0,
      "workType": "ASSIGNMENT",
      "topicId": "topic_103",
      "creationTime": "2025-02-12T09:00:00Z",
      "updateTime": "2025-02-12T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_104",
      "dueDate": {
        "year": 2025,
        "month": 2,
        "day": 19
      },
      "dueTime": {
        "hours": 23,
        "minutes": 59
      }
    },
    {
      "courseId": "course_001",
      "id": "cw_105",
      "title": "While Loop Patterns",
      "description": "Create programs that use while loops to generate number patterns: pyramid triangle and diamond shapes in the console.",
      "state":
```

## 11. GET /v1/courses/course_001/courseWork?topicId=topic_104 (List coursework by topic)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork?topicId=topic_104
```

HTTP Status: 200

```json
{
  "courseWork": [
    {
      "courseId": "course_001",
      "id": "cw_105",
      "title": "While Loop Patterns",
      "description": "Create programs that use while loops to generate number patterns: pyramid triangle and diamond shapes in the console.",
      "state": "PUBLISHED",
      "maxPoints": 50.0,
      "workType": "ASSIGNMENT",
      "topicId": "topic_104",
      "creationTime": "2025-02-26T09:00:00Z",
      "updateTime": "2025-02-26T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_105",
      "dueDate": {
        "year": 2025,
        "month": 3,
        "day": 5
      },
      "dueTime": {
        "hours": 23,
        "minutes": 59
      }
    },
    {
      "courseId": "course_001",
      "id": "cw_106",
      "title": "For Loop Array Traversal",
      "description": "Implement methods that use for loops to find min max sum and average of integer arrays.",
      "state": "PUBLISHED",
      "maxPoints": 100.0,
      "workType": "ASSIGNMENT",
      "topicId": "topic_104",
      "creationTime": "2025-03-03T09:00:00Z",
      "updateTime": "2025-03-03T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_106",
      "dueDate": {
        "year": 2025,
        "month": 3,
        "day": 12
      },
      "dueTime": {
        "hours": 23,
        "minutes": 59
      }
    }
  ]
}
```

## 12. GET /v1/courses/course_001/courseWork?orderBy=dueDate%20desc (List coursework ordered by dueDate desc)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork?orderBy=dueDate%20desc
```

HTTP Status: 200

```json
{
  "courseWork": [
    {
      "courseId": "course_001",
      "id": "cw_109",
      "title": "AP Practice: FRQ Set 1",
      "description": "Complete Free Response Questions 1-3 from the 2023 AP CS A exam practice set. Show all work.",
      "state": "PUBLISHED",
      "maxPoints": 100.0,
      "workType": "ASSIGNMENT",
      "topicId": "topic_107",
      "creationTime": "2025-04-21T09:00:00Z",
      "updateTime": "2025-04-21T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_109",
      "dueDate": {
        "year": 2025,
        "month": 5,
        "day": 2
      },
      "dueTime": {
        "hours": 23,
        "minutes": 59
      }
    },
    {
      "courseId": "course_001",
      "id": "cw_108",
      "title": "ArrayList Operations",
      "description": "Implement a StudentRoster program using ArrayList with add remove search and sort operations.",
      "state": "PUBLISHED",
      "maxPoints": 50.0,
      "workType": "ASSIGNMENT",
      "topicId": "topic_107",
      "creationTime": "2025-04-09T09:00:00Z",
      "updateTime": "2025-04-09T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_108",
      "dueDate": {
        "year": 2025,
        "month": 4,
        "day": 18
      },
      "dueTime": {
        "hours": 23,
        "minutes": 59
      }
    },
    {
      "courseId": "course_001",
      "id": "cw_107",
      "title": "Class Design: BankAccount",
      "description": "Design and implement a BankAccount class with instance variables constructor deposit withdraw and getBalance methods.",
      "state": "PUBLISHED",
      "maxPoints": 100.0,
      "workType": "ASSIGNMENT",
      "topicId": "topic_105",
      "creationTime": "2025-03-12T09:00:00Z",
      "updateTime": "2025-03-12T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_107",
      "dueDate": {
        "year": 2025,
        "month": 3,
        "day": 21
      },
      "dueTime": {
        "hours": 23,
        "minutes": 59
      }
    },
    {
      "courseId": "course_001",
      "id": "cw_106",
      "title": "For Loop Array Traversal",
      "description": "Implement methods that use for loops to find min max sum and average of integer arrays.",
      "state": "PUBLISHED",
      "maxPoints": 100.0,
      "workType": "ASSIGNMENT",
      "topicId": "topic_104",
      "creationTime": "2025-03-03T09:00:00Z",
      "updateTime": "2025-03-03T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_106",
      "dueDate": {
        "year": 2025,
        "month": 3,
        "day": 12
      },
      "dueTime": {
        "hours": 23,
        "minutes": 59
      }
    },
    {
      "courseId": "course_001",
      "id": "cw_105",
      "title": "While Loop Patterns",
      "description": "Create programs that use while loops to generate number patterns: pyramid triangle and diamond shapes in the console.",
      "state": "PUBLISHED",
      "maxPoints": 50.0,
 
```

## 13. GET /v1/courses/course_001/courseWork/cw_101 (Get coursework valid)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_101
```

HTTP Status: 200

```json
{
  "courseWork": {
    "courseId": "course_001",
    "id": "cw_101",
    "title": "Variables and Data Types Lab",
    "description": "Write a Java program that demonstrates the use of int double boolean and String variables. Include type casting examples.",
    "state": "PUBLISHED",
    "maxPoints": 25.0,
    "workType": "ASSIGNMENT",
    "topicId": "topic_101",
    "creationTime": "2025-01-13T09:00:00Z",
    "updateTime": "2025-01-13T09:00:00Z",
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101",
    "dueDate": {
      "year": 2025,
      "month": 1,
      "day": 20
    },
    "dueTime": {
      "hours": 23,
      "minutes": 59
    }
  }
}
```

## 14. GET /v1/courses/course_001/courseWork/cw_999 (Get coursework 404)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_999
```

HTTP Status: 404

```json
{
  "error": "CourseWork cw_999 not found in course course_001"
}
```

## 15. POST /v1/courses/course_001/courseWork (Create coursework assignment)

```
curl -s -X POST -H 'Content-Type: application/json' -d '{"title": "Recursion Challenge", "description": "Recursive solutions", "workType": "ASSIGNMENT", "maxPoints": 75, "topicId": "topic_107", "dueDate": {"year": 2025, "month": 5, "day": 9}, "dueTime": {"hours": 23, "minutes": 59}}' $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork
```

HTTP Status: 201

```json
{
  "courseWork": {
    "courseId": "course_001",
    "id": "cw_400",
    "title": "Recursion Challenge",
    "description": "Recursive solutions",
    "state": null,
    "maxPoints": 75.0,
    "workType": "ASSIGNMENT",
    "topicId": "topic_107",
    "creationTime": "2026-05-06T18:44:02Z",
    "updateTime": "2026-05-06T18:44:02Z",
    "dueDate": {
      "year": 2025,
      "month": 5,
      "day": 9
    },
    "dueTime": {
      "hours": 23,
      "minutes": 59
    },
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_400"
  }
}
```

## 16. POST /v1/courses/course_002/courseWork (Create coursework question)

```
curl -s -X POST -H 'Content-Type: application/json' -d '{"title": "CSS Box Model Quiz", "description": "What is border-box?", "workType": "SHORT_ANSWER_QUESTION", "maxPoints": 10, "topicId": "topic_202"}' $GOOGLE_CLASSROOM_API_URL/v1/courses/course_002/courseWork
```

HTTP Status: 201

```json
{
  "courseWork": {
    "courseId": "course_002",
    "id": "cw_401",
    "title": "CSS Box Model Quiz",
    "description": "What is border-box?",
    "state": null,
    "maxPoints": 10.0,
    "workType": "SHORT_ANSWER_QUESTION",
    "topicId": "topic_202",
    "creationTime": "2026-05-06T18:44:02Z",
    "updateTime": "2026-05-06T18:44:02Z",
    "dueDate": null,
    "dueTime": null,
    "alternateLink": "https://classroom.google.com/c/course_002/a/cw_401"
  }
}
```

## 17. PATCH /v1/courses/course_001/courseWork/cw_109 (Update coursework due date and points)

```
curl -s -X PATCH -H 'Content-Type: application/json' -d '{"dueDate": {"year": 2025, "month": 5, "day": 5}, "maxPoints": 120}' $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_109
```

HTTP Status: 200

```json
{
  "courseWork": {
    "courseId": "course_001",
    "id": "cw_109",
    "title": "AP Practice: FRQ Set 1",
    "description": "Complete Free Response Questions 1-3 from the 2023 AP CS A exam practice set. Show all work.",
    "state": "PUBLISHED",
    "maxPoints": 120.0,
    "workType": "ASSIGNMENT",
    "topicId": "topic_107",
    "creationTime": "2025-04-21T09:00:00Z",
    "updateTime": "2026-05-06T18:44:02Z",
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_109",
    "dueDate": {
      "year": 2025,
      "month": 5,
      "day": 5
    },
    "dueTime": {
      "hours": 23,
      "minutes": 59
    }
  }
}
```

## 18. DELETE /v1/courses/course_001/courseWork/cw_103 (Delete coursework)

```
curl -s -X DELETE $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_103
```

HTTP Status: 200

```json
{
  "deleted": true
}
```

## 19. DELETE /v1/courses/course_001/courseWork/cw_999 (Delete coursework 404)

```
curl -s -X DELETE $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_999
```

HTTP Status: 404

```json
{
  "error": "CourseWork cw_999 not found in course course_001"
}
```

## 20. GET /v1/courses/course_001/topics (List topics)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/topics
```

HTTP Status: 200

```json
{
  "topic": [
    {
      "courseId": "course_001",
      "topicId": "topic_101",
      "name": "Unit 1: Primitive Types",
      "updateTime": "2025-01-10T08:00:00Z"
    },
    {
      "courseId": "course_001",
      "topicId": "topic_102",
      "name": "Unit 2: Using Objects",
      "updateTime": "2025-01-27T08:00:00Z"
    },
    {
      "courseId": "course_001",
      "topicId": "topic_103",
      "name": "Unit 3: Boolean Expressions and if Statements",
      "updateTime": "2025-02-10T08:00:00Z"
    },
    {
      "courseId": "course_001",
      "topicId": "topic_104",
      "name": "Unit 4: Iteration",
      "updateTime": "2025-02-24T08:00:00Z"
    },
    {
      "courseId": "course_001",
      "topicId": "topic_105",
      "name": "Unit 5: Writing Classes",
      "updateTime": "2025-03-10T08:00:00Z"
    },
    {
      "courseId": "course_001",
      "topicId": "topic_106",
      "name": "Unit 6: Arrays",
      "updateTime": "2025-03-24T08:00:00Z"
    },
    {
      "courseId": "course_001",
      "topicId": "topic_107",
      "name": "Unit 7: ArrayList",
      "updateTime": "2025-04-07T08:00:00Z"
    }
  ]
}
```

## 21. GET /v1/courses/course_002/topics (List topics course_002)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_002/topics
```

HTTP Status: 200

```json
{
  "topic": [
    {
      "courseId": "course_002",
      "topicId": "topic_201",
      "name": "Unit 1: HTML Fundamentals",
      "updateTime": "2025-01-10T08:00:00Z"
    },
    {
      "courseId": "course_002",
      "topicId": "topic_202",
      "name": "Unit 2: CSS Styling",
      "updateTime": "2025-01-27T08:00:00Z"
    },
    {
      "courseId": "course_002",
      "topicId": "topic_203",
      "name": "Unit 3: CSS Layout (Flexbox and Grid)",
      "updateTime": "2025-02-10T08:00:00Z"
    },
    {
      "courseId": "course_002",
      "topicId": "topic_204",
      "name": "Unit 4: JavaScript Basics",
      "updateTime": "2025-02-24T08:00:00Z"
    },
    {
      "courseId": "course_002",
      "topicId": "topic_205",
      "name": "Unit 5: DOM Manipulation",
      "updateTime": "2025-03-10T08:00:00Z"
    },
    {
      "courseId": "course_002",
      "topicId": "topic_206",
      "name": "Unit 6: APIs and Fetch",
      "updateTime": "2025-03-31T08:00:00Z"
    }
  ]
}
```

## 22. GET /v1/courses/course_001/topics/topic_101 (Get topic valid)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/topics/topic_101
```

HTTP Status: 200

```json
{
  "topic": {
    "courseId": "course_001",
    "topicId": "topic_101",
    "name": "Unit 1: Primitive Types",
    "updateTime": "2025-01-10T08:00:00Z"
  }
}
```

## 23. GET /v1/courses/course_001/topics/topic_999 (Get topic 404)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/topics/topic_999
```

HTTP Status: 404

```json
{
  "error": "Topic topic_999 not found in course course_001"
}
```

## 24. POST /v1/courses/course_001/topics (Create topic)

```
curl -s -X POST -H 'Content-Type: application/json' -d '{"name": "Unit 8: 2D Arrays"}' $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/topics
```

HTTP Status: 201

```json
{
  "topic": {
    "courseId": "course_001",
    "topicId": "topic_400",
    "name": "Unit 8: 2D Arrays",
    "updateTime": "2026-05-06T18:44:02Z"
  }
}
```

## 25. PATCH /v1/courses/course_001/topics/topic_101 (Update topic)

```
curl -s -X PATCH -H 'Content-Type: application/json' -d '{"name": "Unit 1: Primitive Types & Expressions"}' $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/topics/topic_101
```

HTTP Status: 200

```json
{
  "topic": {
    "courseId": "course_001",
    "topicId": "topic_101",
    "name": "Unit 1: Primitive Types & Expressions",
    "updateTime": "2026-05-06T18:44:02Z"
  }
}
```

## 26. DELETE /v1/courses/course_001/topics/topic_107 (Delete topic)

```
curl -s -X DELETE $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/topics/topic_107
```

HTTP Status: 200

```json
{
  "deleted": true
}
```

## 27. GET /v1/courses/course_001/courseWork/cw_101/studentSubmissions (List submissions)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_101/studentSubmissions
```

HTTP Status: 200

```json
{
  "studentSubmissions": [
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_001",
      "userId": "student_001",
      "state": "RETURNED",
      "late": false,
      "creationTime": "2025-01-14T10:00:00Z",
      "updateTime": "2025-01-22T14:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_001",
      "assignedGrade": 23.0,
      "draftGrade": 23.0
    },
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_002",
      "userId": "student_002",
      "state": "RETURNED",
      "late": false,
      "creationTime": "2025-01-15T08:30:00Z",
      "updateTime": "2025-01-22T14:05:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_002",
      "assignedGrade": 25.0,
      "draftGrade": 25.0
    },
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_003",
      "userId": "student_003",
      "state": "RETURNED",
      "late": false,
      "creationTime": "2025-01-18T22:45:00Z",
      "updateTime": "2025-01-22T14:10:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_003",
      "assignedGrade": 20.0,
      "draftGrade": 20.0
    },
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_004",
      "userId": "student_004",
      "state": "RETURNED",
      "late": true,
      "creationTime": "2025-01-21T11:00:00Z",
      "updateTime": "2025-01-23T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_004",
      "assignedGrade": 18.0,
      "draftGrade": 18.0
    },
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_005",
      "userId": "student_005",
      "state": "RETURNED",
      "late": false,
      "creationTime": "2025-01-19T15:20:00Z",
      "updateTime": "2025-01-22T14:15:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_005",
      "assignedGrade": 22.0,
      "draftGrade": 22.0
    }
  ]
}
```

## 28. GET /v1/courses/course_001/courseWork/cw_108/studentSubmissions?states=TURNED_IN (List submissions TURNED_IN filter)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_108/studentSubmissions?states=TURNED_IN
```

HTTP Status: 200

```json
{
  "studentSubmissions": [
    {
      "courseId": "course_001",
      "courseWorkId": "cw_108",
      "id": "sub_024",
      "userId": "student_001",
      "state": "TURNED_IN",
      "late": false,
      "creationTime": "2025-04-15T10:00:00Z",
      "updateTime": "2025-04-15T10:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_108/submissions/sub_024",
      "assignedGrade": null,
      "draftGrade": null
    },
    {
      "courseId": "course_001",
      "courseWorkId": "cw_108",
      "id": "sub_025",
      "userId": "student_002",
      "state": "TURNED_IN",
      "late": false,
      "creationTime": "2025-04-16T08:00:00Z",
      "updateTime": "2025-04-16T08:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_108/submissions/sub_025",
      "assignedGrade": null,
      "draftGrade": null
    },
    {
      "courseId": "course_001",
      "courseWorkId": "cw_108",
      "id": "sub_026",
      "userId": "student_003",
      "state": "TURNED_IN",
      "late": false,
      "creationTime": "2025-04-17T22:30:00Z",
      "updateTime": "2025-04-17T22:30:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_108/submissions/sub_026",
      "assignedGrade": null,
      "draftGrade": null
    }
  ]
}
```

## 29. GET /v1/courses/course_001/courseWork/cw_101/studentSubmissions?states=RETURNED (List submissions RETURNED filter)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_101/studentSubmissions?states=RETURNED
```

HTTP Status: 200

```json
{
  "studentSubmissions": [
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_001",
      "userId": "student_001",
      "state": "RETURNED",
      "late": false,
      "creationTime": "2025-01-14T10:00:00Z",
      "updateTime": "2025-01-22T14:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_001",
      "assignedGrade": 23.0,
      "draftGrade": 23.0
    },
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_002",
      "userId": "student_002",
      "state": "RETURNED",
      "late": false,
      "creationTime": "2025-01-15T08:30:00Z",
      "updateTime": "2025-01-22T14:05:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_002",
      "assignedGrade": 25.0,
      "draftGrade": 25.0
    },
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_003",
      "userId": "student_003",
      "state": "RETURNED",
      "late": false,
      "creationTime": "2025-01-18T22:45:00Z",
      "updateTime": "2025-01-22T14:10:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_003",
      "assignedGrade": 20.0,
      "draftGrade": 20.0
    },
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_004",
      "userId": "student_004",
      "state": "RETURNED",
      "late": true,
      "creationTime": "2025-01-21T11:00:00Z",
      "updateTime": "2025-01-23T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_004",
      "assignedGrade": 18.0,
      "draftGrade": 18.0
    },
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_005",
      "userId": "student_005",
      "state": "RETURNED",
      "late": false,
      "creationTime": "2025-01-19T15:20:00Z",
      "updateTime": "2025-01-22T14:15:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_005",
      "assignedGrade": 22.0,
      "draftGrade": 22.0
    }
  ]
}
```

## 30. GET /v1/courses/course_001/courseWork/cw_101/studentSubmissions?late=true (List submissions late filter)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_101/studentSubmissions?late=true
```

HTTP Status: 200

```json
{
  "studentSubmissions": [
    {
      "courseId": "course_001",
      "courseWorkId": "cw_101",
      "id": "sub_004",
      "userId": "student_004",
      "state": "RETURNED",
      "late": true,
      "creationTime": "2025-01-21T11:00:00Z",
      "updateTime": "2025-01-23T09:00:00Z",
      "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_004",
      "assignedGrade": 18.0,
      "draftGrade": 18.0
    }
  ]
}
```

## 31. GET /v1/courses/course_001/courseWork/cw_101/studentSubmissions/sub_001 (Get submission valid)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_101/studentSubmissions/sub_001
```

HTTP Status: 200

```json
{
  "studentSubmission": {
    "courseId": "course_001",
    "courseWorkId": "cw_101",
    "id": "sub_001",
    "userId": "student_001",
    "state": "RETURNED",
    "late": false,
    "creationTime": "2025-01-14T10:00:00Z",
    "updateTime": "2025-01-22T14:00:00Z",
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_101/submissions/sub_001",
    "assignedGrade": 23.0,
    "draftGrade": 23.0
  }
}
```

## 32. GET /v1/courses/course_001/courseWork/cw_101/studentSubmissions/sub_999 (Get submission 404)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_101/studentSubmissions/sub_999
```

HTTP Status: 404

```json
{
  "error": "Submission sub_999 not found"
}
```

## 33. PATCH /v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_024 (Grade submission)

```
curl -s -X PATCH -H 'Content-Type: application/json' -d '{"assignedGrade": 45, "draftGrade": 45}' $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_024
```

HTTP Status: 200

```json
{
  "studentSubmission": {
    "courseId": "course_001",
    "courseWorkId": "cw_108",
    "id": "sub_024",
    "userId": "student_001",
    "state": "TURNED_IN",
    "late": false,
    "creationTime": "2025-04-15T10:00:00Z",
    "updateTime": "2026-05-06T18:44:02Z",
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_108/submissions/sub_024",
    "assignedGrade": 45.0,
    "draftGrade": 45.0
  }
}
```

## 34. POST /v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_024:return (Return submission)

```
curl -s -X POST $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_024:return
```

HTTP Status: 200

```json
{
  "studentSubmission": {
    "courseId": "course_001",
    "courseWorkId": "cw_108",
    "id": "sub_024",
    "userId": "student_001",
    "state": "RETURNED",
    "late": false,
    "creationTime": "2025-04-15T10:00:00Z",
    "updateTime": "2026-05-06T18:44:02Z",
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_108/submissions/sub_024",
    "assignedGrade": 45.0,
    "draftGrade": 45.0
  }
}
```

## 35. POST /v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_025:reclaim (Reclaim submission)

```
curl -s -X POST $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWork/cw_108/studentSubmissions/sub_025:reclaim
```

HTTP Status: 200

```json
{
  "studentSubmission": {
    "courseId": "course_001",
    "courseWorkId": "cw_108",
    "id": "sub_025",
    "userId": "student_002",
    "state": "RECLAIMED_BY_STUDENT",
    "late": false,
    "creationTime": "2025-04-16T08:00:00Z",
    "updateTime": "2026-05-06T18:44:02Z",
    "alternateLink": "https://classroom.google.com/c/course_001/a/cw_108/submissions/sub_025",
    "assignedGrade": null,
    "draftGrade": null
  }
}
```

## 36. GET /v1/courses/course_001/students (List students)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/students
```

HTTP Status: 200

```json
{
  "students": [
    {
      "courseId": "course_001",
      "userId": "student_001",
      "profile": {
        "id": "student_001",
        "name": {
          "fullName": "Ethan Nakamura"
        },
        "emailAddress": "enakamura@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student001"
      }
    },
    {
      "courseId": "course_001",
      "userId": "student_002",
      "profile": {
        "id": "student_002",
        "name": {
          "fullName": "Sofia Patel"
        },
        "emailAddress": "spatel@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student002"
      }
    },
    {
      "courseId": "course_001",
      "userId": "student_003",
      "profile": {
        "id": "student_003",
        "name": {
          "fullName": "Marcus Johnson"
        },
        "emailAddress": "mjohnson@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student003"
      }
    },
    {
      "courseId": "course_001",
      "userId": "student_004",
      "profile": {
        "id": "student_004",
        "name": {
          "fullName": "Olivia Kim"
        },
        "emailAddress": "okim@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student004"
      }
    },
    {
      "courseId": "course_001",
      "userId": "student_005",
      "profile": {
        "id": "student_005",
        "name": {
          "fullName": "Liam O'Brien"
        },
        "emailAddress": "lobrien@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student005"
      }
    },
    {
      "courseId": "course_001",
      "userId": "student_006",
      "profile": {
        "id": "student_006",
        "name": {
          "fullName": "Aisha Rahman"
        },
        "emailAddress": "arahman@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student006"
      }
    },
    {
      "courseId": "course_001",
      "userId": "student_007",
      "profile": {
        "id": "student_007",
        "name": {
          "fullName": "Diego Herrera"
        },
        "emailAddress": "dherrera@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student007"
      }
    },
    {
      "courseId": "course_001",
      "userId": "student_008",
      "profile": {
        "id": "student_008",
        "name": {
          "fullName": "Emma Wilson"
        },
        "emailAddress": "ewilson@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student008"
      }
    },
    {
      "courseId": "course_001",
      "userId": "student_009",
      "profile": {
        "id": "student_009",
        "name": {
          "fullName": "Ryan Choi"
        },
        "emailAddress": "rchoi@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student009"
      }
    },
    {
      "courseId": "course_001",
      "userId": "student_030",
      "profile": {
        "id": "student_030",
        "name": {
          "fullN
```

## 37. GET /v1/courses/course_002/students?pageSize=10&pageToken=10 (List students page 2)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_002/students?pageSize=10&pageToken=10
```

HTTP Status: 200

```json
{
  "students": [
    {
      "courseId": "course_002",
      "userId": "student_050",
      "profile": {
        "id": "student_050",
        "name": {
          "fullName": "Rachel Green"
        },
        "emailAddress": "rgreen@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student050"
      }
    },
    {
      "courseId": "course_002",
      "userId": "student_051",
      "profile": {
        "id": "student_051",
        "name": {
          "fullName": "David Park"
        },
        "emailAddress": "dpark@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student051"
      }
    },
    {
      "courseId": "course_002",
      "userId": "student_052",
      "profile": {
        "id": "student_052",
        "name": {
          "fullName": "Grace Nguyen"
        },
        "emailAddress": "gnguyen@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student052"
      }
    },
    {
      "courseId": "course_002",
      "userId": "student_053",
      "profile": {
        "id": "student_053",
        "name": {
          "fullName": "Owen Phillips"
        },
        "emailAddress": "ophillips@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student053"
      }
    },
    {
      "courseId": "course_002",
      "userId": "student_054",
      "profile": {
        "id": "student_054",
        "name": {
          "fullName": "Lily Campbell"
        },
        "emailAddress": "lcampbell@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student054"
      }
    },
    {
      "courseId": "course_002",
      "userId": "student_055",
      "profile": {
        "id": "student_055",
        "name": {
          "fullName": "Jack Roberts"
        },
        "emailAddress": "jroberts@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student055"
      }
    },
    {
      "courseId": "course_002",
      "userId": "student_056",
      "profile": {
        "id": "student_056",
        "name": {
          "fullName": "Chloe Evans"
        },
        "emailAddress": "cevans@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student056"
      }
    },
    {
      "courseId": "course_002",
      "userId": "student_057",
      "profile": {
        "id": "student_057",
        "name": {
          "fullName": "Andrew Turner"
        },
        "emailAddress": "aturner@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student057"
      }
    },
    {
      "courseId": "course_002",
      "userId": "student_058",
      "profile": {
        "id": "student_058",
        "name": {
          "fullName": "Sofia Mitchell"
        },
        "emailAddress": "smitchell@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/student058"
      }
    },
    {
      "courseId": "course_002",
      "userId": "student_059",
      "profile": {
        "id": "student_059",
        "name": {
       
```

## 38. GET /v1/courses/course_001/students/student_001 (Get student valid)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/students/student_001
```

HTTP Status: 200

```json
{
  "student": {
    "courseId": "course_001",
    "userId": "student_001",
    "profile": {
      "id": "student_001",
      "name": {
        "fullName": "Ethan Nakamura"
      },
      "emailAddress": "enakamura@westlake.edu",
      "photoUrl": "https://lh3.googleusercontent.com/a/student001"
    }
  }
}
```

## 39. GET /v1/courses/course_001/students/student_999 (Get student 404)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/students/student_999
```

HTTP Status: 404

```json
{
  "error": "Student student_999 not found in course course_001"
}
```

## 40. POST /v1/courses/course_001/students (Invite student)

```
curl -s -X POST -H 'Content-Type: application/json' -d '{"emailAddress": "newstudent@westlake.edu", "fullName": "New Student"}' $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/students
```

HTTP Status: 201

```json
{
  "student": {
    "courseId": "course_001",
    "userId": "student_new_85",
    "profile": {
      "id": "student_new_85",
      "name": {
        "fullName": "New Student"
      },
      "emailAddress": "newstudent@westlake.edu",
      "photoUrl": "https://lh3.googleusercontent.com/a/student_new_85"
    }
  }
}
```

## 41. DELETE /v1/courses/course_001/students/student_048 (Remove student)

```
curl -s -X DELETE $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/students/student_048
```

HTTP Status: 200

```json
{
  "deleted": true
}
```

## 42. GET /v1/courses/course_001/teachers (List teachers)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/teachers
```

HTTP Status: 200

```json
{
  "teachers": [
    {
      "courseId": "course_001",
      "userId": "teacher_001",
      "profile": {
        "id": "teacher_001",
        "name": {
          "fullName": "Rachel Torres"
        },
        "emailAddress": "rtorres@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/teacher001"
      }
    }
  ]
}
```

## 43. GET /v1/courses/course_002/teachers (List teachers course_002)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_002/teachers
```

HTTP Status: 200

```json
{
  "teachers": [
    {
      "courseId": "course_002",
      "userId": "teacher_001",
      "profile": {
        "id": "teacher_001",
        "name": {
          "fullName": "Rachel Torres"
        },
        "emailAddress": "rtorres@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/teacher001"
      }
    },
    {
      "courseId": "course_002",
      "userId": "teacher_002",
      "profile": {
        "id": "teacher_002",
        "name": {
          "fullName": "Marcus Chen"
        },
        "emailAddress": "mchen@westlake.edu",
        "photoUrl": "https://lh3.googleusercontent.com/a/teacher002"
      }
    }
  ]
}
```

## 44. GET /v1/courses/course_001/teachers/teacher_001 (Get teacher valid)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/teachers/teacher_001
```

HTTP Status: 200

```json
{
  "teacher": {
    "courseId": "course_001",
    "userId": "teacher_001",
    "profile": {
      "id": "teacher_001",
      "name": {
        "fullName": "Rachel Torres"
      },
      "emailAddress": "rtorres@westlake.edu",
      "photoUrl": "https://lh3.googleusercontent.com/a/teacher001"
    }
  }
}
```

## 45. GET /v1/courses/course_001/teachers/teacher_999 (Get teacher 404)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/teachers/teacher_999
```

HTTP Status: 404

```json
{
  "error": "Teacher teacher_999 not found in course course_001"
}
```

## 46. GET /v1/courses/course_001/announcements (List announcements)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/announcements
```

HTTP Status: 200

```json
{
  "announcements": [
    {
      "courseId": "course_001",
      "id": "ann_004",
      "text": "No class Thursday due to PSAT testing day. Use the time to work on your BankAccount project.",
      "state": "PUBLISHED",
      "creationTime": "2025-03-17T08:00:00Z",
      "updateTime": "2025-03-17T08:00:00Z",
      "creatorUserId": "teacher_001",
      "alternateLink": "https://classroom.google.com/c/course_001/p/ann_004"
    },
    {
      "courseId": "course_001",
      "id": "ann_003",
      "text": "AP Exam registration deadline is next Monday March 3. Sign up in the counseling office if you haven't already.",
      "state": "PUBLISHED",
      "creationTime": "2025-02-24T08:00:00Z",
      "updateTime": "2025-02-24T08:00:00Z",
      "creatorUserId": "teacher_001",
      "alternateLink": "https://classroom.google.com/c/course_001/p/ann_003"
    },
    {
      "courseId": "course_001",
      "id": "ann_002",
      "text": "Reminder: Unit 2 test on Friday. Review String methods and Scanner input. Office hours Tuesday and Thursday after school.",
      "state": "PUBLISHED",
      "creationTime": "2025-02-03T08:00:00Z",
      "updateTime": "2025-02-03T08:00:00Z",
      "creatorUserId": "teacher_001",
      "alternateLink": "https://classroom.google.com/c/course_001/p/ann_002"
    },
    {
      "courseId": "course_001",
      "id": "ann_001",
      "text": "Welcome to AP Computer Science A! Please review the syllabus linked in Materials and complete the intro survey by Friday.",
      "state": "PUBLISHED",
      "creationTime": "2025-01-06T09:00:00Z",
      "updateTime": "2025-01-06T09:00:00Z",
      "creatorUserId": "teacher_001",
      "alternateLink": "https://classroom.google.com/c/course_001/p/ann_001"
    }
  ]
}
```

## 47. GET /v1/courses/course_002/announcements (List announcements course_002)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_002/announcements
```

HTTP Status: 200

```json
{
  "announcements": [
    {
      "courseId": "course_002",
      "id": "ann_007",
      "text": "Reminder: Weather API project due Wednesday. Make sure your API key is working. See me if you need help with fetch.",
      "state": "PUBLISHED",
      "creationTime": "2025-04-14T11:00:00Z",
      "updateTime": "2025-04-14T11:00:00Z",
      "creatorUserId": "teacher_001",
      "alternateLink": "https://classroom.google.com/c/course_002/p/ann_007"
    },
    {
      "courseId": "course_002",
      "id": "ann_006",
      "text": "Great work on the portfolio projects everyone! I've posted some exemplary examples in Materials for inspiration.",
      "state": "PUBLISHED",
      "creationTime": "2025-01-27T11:00:00Z",
      "updateTime": "2025-01-27T11:00:00Z",
      "creatorUserId": "teacher_001",
      "alternateLink": "https://classroom.google.com/c/course_002/p/ann_006"
    },
    {
      "courseId": "course_002",
      "id": "ann_005",
      "text": "Welcome to Web Dev! Make sure you have VS Code installed and a GitHub account created before next class.",
      "state": "PUBLISHED",
      "creationTime": "2025-01-06T11:00:00Z",
      "updateTime": "2025-01-06T11:00:00Z",
      "creatorUserId": "teacher_001",
      "alternateLink": "https://classroom.google.com/c/course_002/p/ann_005"
    }
  ]
}
```

## 48. GET /v1/courses/course_001/announcements/ann_001 (Get announcement valid)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/announcements/ann_001
```

HTTP Status: 200

```json
{
  "announcement": {
    "courseId": "course_001",
    "id": "ann_001",
    "text": "Welcome to AP Computer Science A! Please review the syllabus linked in Materials and complete the intro survey by Friday.",
    "state": "PUBLISHED",
    "creationTime": "2025-01-06T09:00:00Z",
    "updateTime": "2025-01-06T09:00:00Z",
    "creatorUserId": "teacher_001",
    "alternateLink": "https://classroom.google.com/c/course_001/p/ann_001"
  }
}
```

## 49. GET /v1/courses/course_001/announcements/ann_999 (Get announcement 404)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/announcements/ann_999
```

HTTP Status: 404

```json
{
  "error": "Announcement ann_999 not found in course course_001"
}
```

## 50. POST /v1/courses/course_001/announcements (Create announcement)

```
curl -s -X POST -H 'Content-Type: application/json' -d '{"text": "Extra credit: CS guest speaker Thursday 3pm"}' $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/announcements
```

HTTP Status: 201

```json
{
  "announcement": {
    "courseId": "course_001",
    "id": "ann_020",
    "text": "Extra credit: CS guest speaker Thursday 3pm",
    "state": null,
    "creationTime": "2026-05-06T18:44:02Z",
    "updateTime": "2026-05-06T18:44:02Z",
    "creatorUserId": "teacher_001",
    "alternateLink": "https://classroom.google.com/c/course_001/p/ann_020"
  }
}
```

## 51. PATCH /v1/courses/course_001/announcements/ann_002 (Update announcement)

```
curl -s -X PATCH -H 'Content-Type: application/json' -d '{"text": "UPDATED: Unit 2 test moved to Monday"}' $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/announcements/ann_002
```

HTTP Status: 200

```json
{
  "announcement": {
    "courseId": "course_001",
    "id": "ann_002",
    "text": "UPDATED: Unit 2 test moved to Monday",
    "state": "PUBLISHED",
    "creationTime": "2025-02-03T08:00:00Z",
    "updateTime": "2026-05-06T18:44:02Z",
    "creatorUserId": "teacher_001",
    "alternateLink": "https://classroom.google.com/c/course_001/p/ann_002"
  }
}
```

## 52. DELETE /v1/courses/course_001/announcements/ann_004 (Delete announcement)

```
curl -s -X DELETE $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/announcements/ann_004
```

HTTP Status: 200

```json
{
  "deleted": true
}
```

## 53. GET /v1/courses/course_001/courseWorkMaterials (List materials)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWorkMaterials
```

HTTP Status: 200

```json
{
  "courseWorkMaterial": [
    {
      "courseId": "course_001",
      "id": "mat_001",
      "title": "AP CS A Syllabus",
      "description": "Course syllabus with schedule grading policy and required materials.",
      "state": "PUBLISHED",
      "creationTime": "2025-01-06T08:30:00Z",
      "updateTime": "2025-01-06T08:30:00Z",
      "creatorUserId": "teacher_001",
      "topicId": "topic_101",
      "alternateLink": "https://classroom.google.com/c/course_001/m/mat_001",
      "materials": [
        {
          "link": {
            "url": "https://docs.google.com/document/d/apcs-syllabus-2025",
            "title": "AP CS A Syllabus"
          }
        }
      ]
    },
    {
      "courseId": "course_001",
      "id": "mat_002",
      "title": "Java Style Guide",
      "description": "Coding standards and naming conventions for all Java assignments in this class.",
      "state": "PUBLISHED",
      "creationTime": "2025-01-10T09:00:00Z",
      "updateTime": "2025-01-10T09:00:00Z",
      "creatorUserId": "teacher_001",
      "topicId": "topic_101",
      "alternateLink": "https://classroom.google.com/c/course_001/m/mat_002",
      "materials": [
        {
          "link": {
            "url": "https://docs.google.com/document/d/java-style-guide",
            "title": "Java Style Guide"
          }
        }
      ]
    },
    {
      "courseId": "course_001",
      "id": "mat_003",
      "title": "AP CS A Exam Reference Sheet",
      "description": "Official reference sheet provided during the AP exam. Familiarize yourself with it.",
      "state": "PUBLISHED",
      "creationTime": "2025-03-01T09:00:00Z",
      "updateTime": "2025-03-01T09:00:00Z",
      "creatorUserId": "teacher_001",
      "topicId": "topic_107",
      "alternateLink": "https://classroom.google.com/c/course_001/m/mat_003",
      "materials": [
        {
          "link": {
            "url": "https://apcentral.collegeboard.org/media/pdf/ap-computer-science-a-java-quick-reference.pdf",
            "title": "AP CS A Exam Reference Sheet"
          }
        }
      ]
    }
  ]
}
```

## 54. GET /v1/courses/course_002/courseWorkMaterials (List materials course_002)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_002/courseWorkMaterials
```

HTTP Status: 200

```json
{
  "courseWorkMaterial": [
    {
      "courseId": "course_002",
      "id": "mat_004",
      "title": "VS Code Setup Guide",
      "description": "Step-by-step instructions for installing VS Code and recommended extensions for web development.",
      "state": "PUBLISHED",
      "creationTime": "2025-01-06T11:30:00Z",
      "updateTime": "2025-01-06T11:30:00Z",
      "creatorUserId": "teacher_001",
      "topicId": "topic_201",
      "alternateLink": "https://classroom.google.com/c/course_002/m/mat_004",
      "materials": [
        {
          "link": {
            "url": "https://docs.google.com/document/d/vscode-setup",
            "title": "VS Code Setup Guide"
          }
        }
      ]
    },
    {
      "courseId": "course_002",
      "id": "mat_005",
      "title": "MDN Web Docs Reference",
      "description": "Mozilla Developer Network - your go-to reference for HTML CSS and JavaScript documentation.",
      "state": "PUBLISHED",
      "creationTime": "2025-01-10T11:00:00Z",
      "updateTime": "2025-01-10T11:00:00Z",
      "creatorUserId": "teacher_001",
      "topicId": "topic_201",
      "alternateLink": "https://classroom.google.com/c/course_002/m/mat_005",
      "materials": [
        {
          "link": {
            "url": "https://developer.mozilla.org/en-US/",
            "title": "MDN Web Docs Reference"
          }
        }
      ]
    }
  ]
}
```

## 55. GET /v1/courses/course_001/courseWorkMaterials/mat_001 (Get material valid)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWorkMaterials/mat_001
```

HTTP Status: 200

```json
{
  "courseWorkMaterial": {
    "courseId": "course_001",
    "id": "mat_001",
    "title": "AP CS A Syllabus",
    "description": "Course syllabus with schedule grading policy and required materials.",
    "state": "PUBLISHED",
    "creationTime": "2025-01-06T08:30:00Z",
    "updateTime": "2025-01-06T08:30:00Z",
    "creatorUserId": "teacher_001",
    "topicId": "topic_101",
    "alternateLink": "https://classroom.google.com/c/course_001/m/mat_001",
    "materials": [
      {
        "link": {
          "url": "https://docs.google.com/document/d/apcs-syllabus-2025",
          "title": "AP CS A Syllabus"
        }
      }
    ]
  }
}
```

## 56. GET /v1/courses/course_001/courseWorkMaterials/mat_999 (Get material 404)

```
curl -s -X GET $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWorkMaterials/mat_999
```

HTTP Status: 404

```json
{
  "error": "Material mat_999 not found in course course_001"
}
```

## 57. POST /v1/courses/course_001/courseWorkMaterials (Create material)

```
curl -s -X POST -H 'Content-Type: application/json' -d '{"title": "ArrayList Tutorial Video", "description": "Video tutorial", "topicId": "topic_107", "materials": [{"link": {"url": "https://youtube.com/example", "title": "Tutorial"}}]}' $GOOGLE_CLASSROOM_API_URL/v1/courses/course_001/courseWorkMaterials
```

HTTP Status: 201

```json
{
  "courseWorkMaterial": {
    "courseId": "course_001",
    "id": "mat_010",
    "title": "ArrayList Tutorial Video",
    "description": "Video tutorial",
    "state": "PUBLISHED",
    "creationTime": "2026-05-06T18:44:02Z",
    "updateTime": "2026-05-06T18:44:02Z",
    "creatorUserId": "teacher_001",
    "topicId": "topic_107",
    "alternateLink": "https://classroom.google.com/c/course_001/m/mat_010",
    "materials": [
      {
        "link": {
          "url": "https://youtube.com/example",
          "title": "Tutorial"
        }
      }
    ]
  }
}
```

