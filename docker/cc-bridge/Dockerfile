FROM python:3.12-slim

RUN pip install --no-cache-dir --disable-pip-version-check \
    "fastapi==0.115.5" \
    "uvicorn==0.32.1" \
    "httpx==0.27.2" \
    "pydantic==2.10.3"

WORKDIR /app

COPY src/utils/claude_oauth /app/claude_oauth

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    WCB_CC_BRIDGE_HOST=0.0.0.0 \
    WCB_CC_BRIDGE_PORT=8765

EXPOSE 8765

ENTRYPOINT ["python", "-m", "claude_oauth"]
CMD ["--host", "0.0.0.0", "--port", "8765"]
