"""FastAPI server wrapping google_classroom_data module as REST endpoints."""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import google_classroom_data
try:
    from tracking_middleware import install_tracker
    from admin_plane import install_admin_plane
except ModuleNotFoundError as _shared_plane_err:  # standalone run without the shared module on sys.path
    import logging as _logging
    _logging.error("SHARED PLANE MISSING - audit + admin disabled: %s", _shared_plane_err)
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

    def install_admin_plane(app, store=None, one_shot_registry=None):
        return None

app = FastAPI(title="Google Classroom API (Mock)", version="1.0")
install_tracker(app)
install_admin_plane(app, store=google_classroom_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Courses ---

@app.get("/v1/courses")
def list_courses(
    courseStates: Optional[str] = Query(default=None),
    pageSize: int = Query(default=20, ge=1, le=100),
    pageToken: Optional[str] = Query(default=None),
):
    return google_classroom_data.list_courses(
        course_states=courseStates, page_size=pageSize,
        page_token=int(pageToken) if pageToken else 0,
    )


@app.get("/v1/courses/{course_id}")
def get_course(course_id: str):
    result = google_classroom_data.get_course(course_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CourseCreateBody(BaseModel):
    name: str
    section: Optional[str] = None
    descriptionHeading: Optional[str] = None
    description: Optional[str] = None
    room: Optional[str] = None
    ownerId: Optional[str] = None


@app.post("/v1/courses", status_code=201)
def create_course(body: CourseCreateBody):
    result = google_classroom_data.create_course(body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class CourseUpdateBody(BaseModel):
    name: Optional[str] = None
    section: Optional[str] = None
    descriptionHeading: Optional[str] = None
    description: Optional[str] = None
    room: Optional[str] = None
    courseState: Optional[str] = None


@app.patch("/v1/courses/{course_id}")
def update_course(course_id: str, body: CourseUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = google_classroom_data.update_course(course_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/v1/courses/{course_id}:archive")
def archive_course(course_id: str):
    result = google_classroom_data.archive_course(course_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Course Work ---

@app.get("/v1/courses/{course_id}/courseWork")
def list_coursework(
    course_id: str,
    topicId: Optional[str] = Query(default=None),
    courseWorkStates: Optional[str] = Query(default=None),
    orderBy: Optional[str] = Query(default=None),
    pageSize: int = Query(default=20, ge=1, le=100),
    pageToken: Optional[str] = Query(default=None),
):
    result = google_classroom_data.list_coursework(
        course_id=course_id, topic_id=topicId,
        course_work_states=courseWorkStates, order_by=orderBy,
        page_size=pageSize, page_token=int(pageToken) if pageToken else 0,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/courses/{course_id}/courseWork/{coursework_id}")
def get_coursework(course_id: str, coursework_id: str):
    result = google_classroom_data.get_coursework(course_id, coursework_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class DueDateBody(BaseModel):
    year: int
    month: int
    day: int


class DueTimeBody(BaseModel):
    hours: int
    minutes: int


class CourseWorkCreateBody(BaseModel):
    title: str
    description: Optional[str] = None
    workType: str
    state: Optional[str] = None
    maxPoints: Optional[float] = None
    topicId: Optional[str] = None
    dueDate: Optional[DueDateBody] = None
    dueTime: Optional[DueTimeBody] = None


@app.post("/v1/courses/{course_id}/courseWork", status_code=201)
def create_coursework(course_id: str, body: CourseWorkCreateBody):
    data = body.model_dump()
    if data.get("dueDate"):
        data["dueDate"] = dict(data["dueDate"])
    if data.get("dueTime"):
        data["dueTime"] = dict(data["dueTime"])
    result = google_classroom_data.create_coursework(course_id, data)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class CourseWorkUpdateBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None
    maxPoints: Optional[float] = None
    topicId: Optional[str] = None
    dueDate: Optional[DueDateBody] = None
    dueTime: Optional[DueTimeBody] = None


@app.patch("/v1/courses/{course_id}/courseWork/{coursework_id}")
def update_coursework(course_id: str, coursework_id: str, body: CourseWorkUpdateBody):
    data = {}
    for k, v in body.model_dump().items():
        if v is not None:
            if k in ("dueDate", "dueTime"):
                data[k] = dict(v)
            else:
                data[k] = v
    result = google_classroom_data.update_coursework(course_id, coursework_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v1/courses/{course_id}/courseWork/{coursework_id}")
def delete_coursework(course_id: str, coursework_id: str):
    result = google_classroom_data.delete_coursework(course_id, coursework_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Topics ---

@app.get("/v1/courses/{course_id}/topics")
def list_topics(
    course_id: str,
    pageSize: int = Query(default=20, ge=1, le=100),
    pageToken: Optional[str] = Query(default=None),
):
    result = google_classroom_data.list_topics(
        course_id=course_id, page_size=pageSize,
        page_token=int(pageToken) if pageToken else 0,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/courses/{course_id}/topics/{topic_id}")
def get_topic(course_id: str, topic_id: str):
    result = google_classroom_data.get_topic(course_id, topic_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class TopicCreateBody(BaseModel):
    name: str


@app.post("/v1/courses/{course_id}/topics", status_code=201)
def create_topic(course_id: str, body: TopicCreateBody):
    result = google_classroom_data.create_topic(course_id, body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class TopicUpdateBody(BaseModel):
    name: Optional[str] = None


@app.patch("/v1/courses/{course_id}/topics/{topic_id}")
def update_topic(course_id: str, topic_id: str, body: TopicUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = google_classroom_data.update_topic(course_id, topic_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v1/courses/{course_id}/topics/{topic_id}")
def delete_topic(course_id: str, topic_id: str):
    result = google_classroom_data.delete_topic(course_id, topic_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Student Submissions ---

@app.get("/v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions")
def list_submissions(
    course_id: str,
    coursework_id: str,
    states: Optional[str] = Query(default=None),
    late: Optional[bool] = Query(default=None),
    pageSize: int = Query(default=20, ge=1, le=100),
    pageToken: Optional[str] = Query(default=None),
):
    result = google_classroom_data.list_submissions(
        course_id=course_id, coursework_id=coursework_id,
        states=states, late=late,
        page_size=pageSize, page_token=int(pageToken) if pageToken else 0,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}")
def get_submission(course_id: str, coursework_id: str, submission_id: str):
    result = google_classroom_data.get_submission(course_id, coursework_id, submission_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class GradeSubmissionBody(BaseModel):
    assignedGrade: Optional[float] = None
    draftGrade: Optional[float] = None


@app.patch("/v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}")
def grade_submission(course_id: str, coursework_id: str, submission_id: str, body: GradeSubmissionBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = google_classroom_data.grade_submission(course_id, coursework_id, submission_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}:return")
def return_submission(course_id: str, coursework_id: str, submission_id: str):
    result = google_classroom_data.return_submission(course_id, coursework_id, submission_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}:reclaim")
def reclaim_submission(course_id: str, coursework_id: str, submission_id: str):
    result = google_classroom_data.reclaim_submission(course_id, coursework_id, submission_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}:turnIn")
def turn_in_submission(course_id: str, coursework_id: str, submission_id: str):
    result = google_classroom_data.turn_in_submission(course_id, coursework_id, submission_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ModifyAttachmentsBody(BaseModel):
    # Real Classroom sends {"addAttachments": [ {...} ]}; accept it permissively
    # so any attachment shape the agent supplies is recorded.
    addAttachments: Optional[List[dict]] = None


@app.post("/v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}:modifyAttachments")
def modify_submission_attachments(course_id: str, coursework_id: str, submission_id: str,
                                  body: ModifyAttachmentsBody = ModifyAttachmentsBody()):
    result = google_classroom_data.modify_submission_attachments(
        course_id, coursework_id, submission_id, body.addAttachments or [])
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Students ---

@app.get("/v1/courses/{course_id}/students")
def list_students(
    course_id: str,
    pageSize: int = Query(default=30, ge=1, le=100),
    pageToken: Optional[str] = Query(default=None),
):
    result = google_classroom_data.list_students(
        course_id=course_id, page_size=pageSize,
        page_token=int(pageToken) if pageToken else 0,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/courses/{course_id}/students/{user_id}")
def get_student(course_id: str, user_id: str):
    result = google_classroom_data.get_student(course_id, user_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class InviteStudentBody(BaseModel):
    emailAddress: str
    fullName: Optional[str] = None


@app.post("/v1/courses/{course_id}/students", status_code=201)
def invite_student(course_id: str, body: InviteStudentBody):
    result = google_classroom_data.invite_student(course_id, body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.delete("/v1/courses/{course_id}/students/{user_id}")
def remove_student(course_id: str, user_id: str):
    result = google_classroom_data.remove_student(course_id, user_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Teachers ---

@app.get("/v1/courses/{course_id}/teachers")
def list_teachers(course_id: str):
    result = google_classroom_data.list_teachers(course_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/courses/{course_id}/teachers/{user_id}")
def get_teacher(course_id: str, user_id: str):
    result = google_classroom_data.get_teacher(course_id, user_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Announcements ---

@app.get("/v1/courses/{course_id}/announcements")
def list_announcements(
    course_id: str,
    announcementStates: Optional[str] = Query(default=None),
    pageSize: int = Query(default=20, ge=1, le=100),
    pageToken: Optional[str] = Query(default=None),
):
    result = google_classroom_data.list_announcements(
        course_id=course_id, announcement_states=announcementStates,
        page_size=pageSize, page_token=int(pageToken) if pageToken else 0,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/courses/{course_id}/announcements/{announcement_id}")
def get_announcement(course_id: str, announcement_id: str):
    result = google_classroom_data.get_announcement(course_id, announcement_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class AnnouncementCreateBody(BaseModel):
    text: str
    state: Optional[str] = None


@app.post("/v1/courses/{course_id}/announcements", status_code=201)
def create_announcement(course_id: str, body: AnnouncementCreateBody):
    result = google_classroom_data.create_announcement(course_id, body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class AnnouncementUpdateBody(BaseModel):
    text: Optional[str] = None
    state: Optional[str] = None


@app.patch("/v1/courses/{course_id}/announcements/{announcement_id}")
def update_announcement(course_id: str, announcement_id: str, body: AnnouncementUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = google_classroom_data.update_announcement(course_id, announcement_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v1/courses/{course_id}/announcements/{announcement_id}")
def delete_announcement(course_id: str, announcement_id: str):
    result = google_classroom_data.delete_announcement(course_id, announcement_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Course Work Materials ---

@app.get("/v1/courses/{course_id}/courseWorkMaterials")
def list_materials(
    course_id: str,
    pageSize: int = Query(default=20, ge=1, le=100),
    pageToken: Optional[str] = Query(default=None),
):
    result = google_classroom_data.list_materials(
        course_id=course_id, page_size=pageSize,
        page_token=int(pageToken) if pageToken else 0,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/courses/{course_id}/courseWorkMaterials/{material_id}")
def get_material(course_id: str, material_id: str):
    result = google_classroom_data.get_material(course_id, material_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class MaterialLink(BaseModel):
    url: str
    title: Optional[str] = None


class MaterialItem(BaseModel):
    link: Optional[MaterialLink] = None


class MaterialCreateBody(BaseModel):
    title: str
    description: Optional[str] = None
    topicId: Optional[str] = None
    materials: Optional[List[MaterialItem]] = None


@app.post("/v1/courses/{course_id}/courseWorkMaterials", status_code=201)
def create_material(course_id: str, body: MaterialCreateBody):
    data = body.model_dump()
    if data.get("materials"):
        data["materials"] = [m for m in data["materials"] if m]
    result = google_classroom_data.create_material(course_id, data)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result
