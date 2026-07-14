# Sentry API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$SENTRY_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SENTRY_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$SENTRY_API_URL/api/0/organizations/<org_slug>/projects/"
curl -s "$SENTRY_API_URL/api/0/projects/<org_slug>/<project_slug>/issues/"
curl -s "$SENTRY_API_URL/api/0/organizations/<org_slug>/issues/<issue_id>/"
curl -s -X PUT "$SENTRY_API_URL/api/0/organizations/<org_slug>/issues/<issue_id>/" -H 'Content-Type: application/json' -d '{}'
curl -s "$SENTRY_API_URL/api/0/organizations/<org_slug>/issues/<issue_id>/events/"
curl -s "$SENTRY_API_URL/api/0/organizations/<org_slug>/releases/"
```

The audit log of every call is available at `$SENTRY_API_URL/audit/requests` (used for grading).
