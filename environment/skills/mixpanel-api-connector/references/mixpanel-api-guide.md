# Mixpanel API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$MIXPANEL_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `MIXPANEL_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$MIXPANEL_API_URL/api/2.0/events"
curl -s "$MIXPANEL_API_URL/api/2.0/funnels/list"
curl -s "$MIXPANEL_API_URL/api/2.0/funnels"
curl -s "$MIXPANEL_API_URL/api/2.0/segmentation"
curl -s "$MIXPANEL_API_URL/api/2.0/engage"
```

## Track

```bash
curl -s -X POST "$MIXPANEL_API_URL/track" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$MIXPANEL_API_URL/audit/requests` (used for grading).
