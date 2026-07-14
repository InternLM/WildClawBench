# Okta API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$OKTA_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `OKTA_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$OKTA_API_URL/api/v1/users"
curl -s "$OKTA_API_URL/api/v1/users/<user_id>"
curl -s -X POST "$OKTA_API_URL/api/v1/users" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$OKTA_API_URL/api/v1/users/<user_id>/lifecycle/activate" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$OKTA_API_URL/api/v1/users/<user_id>/lifecycle/suspend" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$OKTA_API_URL/api/v1/users/<user_id>/lifecycle/deactivate" -H 'Content-Type: application/json' -d '{}'
curl -s "$OKTA_API_URL/api/v1/groups"
curl -s "$OKTA_API_URL/api/v1/groups/<group_id>"
curl -s "$OKTA_API_URL/api/v1/groups/<group_id>/users"
curl -s "$OKTA_API_URL/api/v1/apps"
```

The audit log of every call is available at `$OKTA_API_URL/audit/requests` (used for grading).
