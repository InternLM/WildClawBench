# Greenhouse Harvest API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$GREENHOUSE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GREENHOUSE_API_URL` | Base URL for all requests |

## Applications

```bash
curl -s "$GREENHOUSE_API_URL/v1/applications"
curl -s "$GREENHOUSE_API_URL/v1/applications/<application_id>"
curl -s -X POST "$GREENHOUSE_API_URL/v1/applications/<application_id>/advance" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$GREENHOUSE_API_URL/v1/applications/<application_id>/reject" -H 'Content-Type: application/json' -d '{}'
```

## Candidates

```bash
curl -s "$GREENHOUSE_API_URL/v1/candidates"
curl -s "$GREENHOUSE_API_URL/v1/candidates/<candidate_id>"
curl -s -X POST "$GREENHOUSE_API_URL/v1/candidates" -H 'Content-Type: application/json' -d '{}'
```

## Jobs

```bash
curl -s "$GREENHOUSE_API_URL/v1/jobs"
curl -s "$GREENHOUSE_API_URL/v1/jobs/<job_id>"
```

## Scorecards

```bash
curl -s "$GREENHOUSE_API_URL/v1/scorecards"
```

The audit log of every call is available at `$GREENHOUSE_API_URL/audit/requests` (used for grading).
