# PostHog API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$POSTHOG_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `POSTHOG_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$POSTHOG_API_URL/api/projects/<project_id>/events"
curl -s "$POSTHOG_API_URL/api/projects/<project_id>/feature_flags"
curl -s "$POSTHOG_API_URL/api/projects/<project_id>/persons"
```

## Capture

```bash
curl -s -X POST "$POSTHOG_API_URL/capture" -H 'Content-Type: application/json' -d '{}'
```

## Decide

```bash
curl -s -X POST "$POSTHOG_API_URL/decide" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$POSTHOG_API_URL/audit/requests` (used for grading).
