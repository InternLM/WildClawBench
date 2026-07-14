# eventbrite-api

This API runs only inside the umbrella mock_stack container.

To debug locally:
```
cd environment/
PYTHONPATH=. python -m uvicorn server:app --app-dir eventbrite-api --port 8020
```
