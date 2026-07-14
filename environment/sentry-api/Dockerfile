FROM python:3.12-slim@sha256:090ba77e2958f6af52a5341f788b50b032dd4ca28377d2893dcf1ecbdfdfe203
RUN groupadd -r app && useradd -r -g app -d /app -s /usr/sbin/nologin app
WORKDIR /app
COPY requirements.txt requirements-locked.txt ./
RUN pip install --no-cache-dir --require-hashes -r requirements-locked.txt
COPY . .
RUN chown -R app:app /app
EXPOSE 8047
USER app
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8047"]
