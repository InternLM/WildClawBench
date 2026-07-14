# jira-api

This API runs only inside the umbrella mock_stack container.

To debug locally:
```
cd environment/
PYTHONPATH=. python -m uvicorn server:app --app-dir jira-api --port 8029
```
