# LinkedIn API v2 (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$LINKEDIN_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `LINKEDIN_API_URL` | Base URL for all requests |

## Connections

```bash
curl -s "$LINKEDIN_API_URL/v2/connections"
```

## Jobs

```bash
curl -s "$LINKEDIN_API_URL/v2/jobs"
curl -s "$LINKEDIN_API_URL/v2/jobs/<job_id>"
```

## Me

```bash
curl -s "$LINKEDIN_API_URL/v2/me"
```

## Organizations

```bash
curl -s "$LINKEDIN_API_URL/v2/organizations/<org_id>"
```

## Posts

```bash
curl -s "$LINKEDIN_API_URL/v2/posts"
curl -s -X POST "$LINKEDIN_API_URL/v2/posts" -H 'Content-Type: application/json' -d '{}'
curl -s "$LINKEDIN_API_URL/v2/posts/<post_id>"
```

The audit log of every call is available at `$LINKEDIN_API_URL/audit/requests` (used for grading).
