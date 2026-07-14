# Calendly API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$CALENDLY_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `CALENDLY_API_URL` | Base URL for all requests |

## Event_Types

```bash
curl -s "$CALENDLY_API_URL/event_types"
curl -s "$CALENDLY_API_URL/event_types/<uuid>"
```

## Scheduled_Events

```bash
curl -s "$CALENDLY_API_URL/scheduled_events"
curl -s "$CALENDLY_API_URL/scheduled_events/<uuid>"
curl -s "$CALENDLY_API_URL/scheduled_events/<uuid>/invitees"
curl -s -X POST "$CALENDLY_API_URL/scheduled_events" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$CALENDLY_API_URL/scheduled_events/<uuid>/cancellation" -H 'Content-Type: application/json' -d '{}'
```

## Users

```bash
curl -s "$CALENDLY_API_URL/users/me"
```

The audit log of every call is available at `$CALENDLY_API_URL/audit/requests` (used for grading).
