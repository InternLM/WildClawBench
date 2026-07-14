"""FastAPI server wrapping wordpress_data module as REST endpoints.

Implements a subset of the WordPress REST API. Base path: /wp-json/wp/v2
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import wordpress_data
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

app = FastAPI(title="WordPress REST API (Mock)", version="wp/v2")
install_tracker(app)
install_admin_plane(app, store=wordpress_data._store)
BASE = "/wp-json/wp/v2"


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Posts ---

@app.get(f"{BASE}/posts")
def list_posts(status: Optional[str] = None, author: Optional[int] = None,
               search: Optional[str] = None, categories: Optional[int] = None,
               per_page: int = Query(10, ge=1, le=100)):
    return wordpress_data.list_posts(status=status, author=author, search=search,
                                     category=categories, per_page=per_page)


class PostCreateBody(BaseModel):
    title: str
    content: str = ""
    status: str = "draft"
    author: int = 1
    excerpt: str = ""
    categories: Optional[List[int]] = None
    tags: Optional[List[int]] = None


@app.post(f"{BASE}/posts", status_code=201)
def create_post(body: PostCreateBody):
    return wordpress_data.create_post(
        title=body.title, content=body.content, status=body.status,
        author=body.author, excerpt=body.excerpt,
        categories=body.categories, tags=body.tags,
    )


@app.get(f"{BASE}/posts/{{post_id}}")
def get_post(post_id: int):
    result = wordpress_data.get_post(post_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class PostUpdateBody(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    excerpt: Optional[str] = None
    categories: Optional[List[int]] = None
    tags: Optional[List[int]] = None


@app.put(f"{BASE}/posts/{{post_id}}")
def update_post(post_id: int, body: PostUpdateBody):
    result = wordpress_data.update_post(
        post_id, title=body.title, content=body.content, status=body.status,
        excerpt=body.excerpt, categories=body.categories, tags=body.tags,
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete(f"{BASE}/posts/{{post_id}}")
def delete_post(post_id: int):
    result = wordpress_data.delete_post(post_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Pages ---

@app.get(f"{BASE}/pages")
def list_pages(status: str = "publish", per_page: int = Query(10, ge=1, le=100)):
    return wordpress_data.list_pages(status=status, per_page=per_page)


# --- Taxonomies ---

@app.get(f"{BASE}/categories")
def list_categories():
    return wordpress_data.list_categories()


@app.get(f"{BASE}/tags")
def list_tags():
    return wordpress_data.list_tags()


# --- Comments ---

@app.get(f"{BASE}/comments")
def list_comments(post: Optional[int] = None, status: str = "approved"):
    return wordpress_data.list_comments(post=post, status=status)


class CommentCreateBody(BaseModel):
    post: int
    author_name: str
    author_email: str
    content: str
    parent: int = 0


@app.post(f"{BASE}/comments", status_code=201)
def create_comment(body: CommentCreateBody):
    result = wordpress_data.create_comment(
        post=body.post, author_name=body.author_name,
        author_email=body.author_email, content=body.content, parent=body.parent,
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Media / users ---

@app.get(f"{BASE}/media")
def list_media():
    return wordpress_data.list_media()


@app.get(f"{BASE}/users")
def list_users():
    return wordpress_data.list_users()
