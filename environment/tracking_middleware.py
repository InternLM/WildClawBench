"""
Shared request/response tracking middleware for Kensei2 mock API services.

Usage in any server.py:
    from tracking_middleware import install_tracker
    install_tracker(app)

This installs:
    1. HTTP middleware that captures all requests/responses in-memory
    2. GET /audit/requests - returns all captured request logs
    3. GET /audit/requests/clear - clears the log (useful between runs)
    4. GET /audit/summary - returns counts by method/path/status
"""

import time
import json
from io import BytesIO
from typing import List, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse


_request_log: List[dict] = []
_MAX_BODY_SIZE = 512 * 1024
_MAX_LOG_ENTRIES = 10_000


class RequestTracker(BaseHTTPMiddleware):
    """Captures full request/response data for every HTTP call."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/audit"):
            return await call_next(request)
        if request.url.path.startswith("/admin"):
            return await call_next(request)
        if request.url.path == "/health":
            return await call_next(request)

        start_time = time.time()

        request_body = await request.body()
        request_body_str = None
        if request_body:
            try:
                request_body_str = request_body.decode("utf-8")[:_MAX_BODY_SIZE]
            except UnicodeDecodeError:
                request_body_str = f"<binary {len(request_body)} bytes>"

        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        response_body_str = None
        if hasattr(response, "body_iterator"):
            chunks = []
            async for chunk in response.body_iterator:
                if isinstance(chunk, bytes):
                    chunks.append(chunk)
                else:
                    chunks.append(chunk.encode("utf-8"))
            body_bytes = b"".join(chunks)
            try:
                response_body_str = body_bytes.decode("utf-8")[:_MAX_BODY_SIZE]
            except UnicodeDecodeError:
                response_body_str = f"<binary {len(body_bytes)} bytes>"
            response = Response(
                content=body_bytes,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        query_params = dict(request.query_params) if request.query_params else None

        entry = {
            "timestamp": time.time(),
            "timestamp_iso": time.strftime(
                "%Y-%m-%dT%H:%M:%S", time.gmtime(start_time)
            ),
            "method": request.method,
            "path": request.url.path,
            "query_params": query_params,
            "request_body": request_body_str,
            "status_code": response.status_code,
            "response_body": response_body_str,
            "duration_ms": duration_ms,
        }
        _request_log.append(entry)
        if len(_request_log) > _MAX_LOG_ENTRIES:
            del _request_log[: len(_request_log) - _MAX_LOG_ENTRIES]

        return response


def install_tracker(app):
    """Install tracking middleware and audit endpoints on a FastAPI app."""

    app.add_middleware(RequestTracker)

    @app.get("/audit/requests")
    def get_audit_requests(
        limit: Optional[int] = None,
        offset: int = 0,
        include_body: bool = True,
    ):
        """Return captured request/response logs.

        WARNING: the unpaginated default response embeds a full copy of every
        response body seen this session and grows without bound — late in a
        session it can exceed what client tooling returns intact (long output
        is often silently capped). Prefer `/audit/summary` for an overview, or
        page through with `limit`/`offset` and `include_body=false` (drops the
        bulky `response_body` field; `request_body` is always kept).

        Defaults (no params = full dump, bodies included) are kept for
        compatibility with the grading harness, which reads this endpoint
        parameter-less and asserts on response_body content.
        """
        items = _request_log[offset:offset + limit] if limit is not None \
            else _request_log[offset:]
        if not include_body:
            items = [
                {k: v for k, v in e.items() if k != "response_body"}
                for e in items
            ]
        return {
            "total": len(_request_log),
            "offset": offset,
            "returned": len(items),
            "requests": items,
        }

    @app.get("/audit/requests/clear")
    def clear_audit_requests():
        """Clear the request log. Returns count of cleared entries."""
        count = len(_request_log)
        _request_log.clear()
        return {"cleared": count}

    @app.get("/audit/summary")
    def get_audit_summary():
        """Return aggregated summary of API usage."""
        summary = {}
        for entry in _request_log:
            key = f"{entry['method']} {entry['path']}"
            if key not in summary:
                summary[key] = {"count": 0, "statuses": {}}
            summary[key]["count"] += 1
            status = str(entry["status_code"])
            summary[key]["statuses"][status] = (
                summary[key]["statuses"].get(status, 0) + 1
            )
        return {
            "total_requests": len(_request_log),
            "endpoints": summary,
        }
