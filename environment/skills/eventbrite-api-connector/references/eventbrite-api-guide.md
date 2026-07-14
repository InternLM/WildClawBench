# Eventbrite API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$EVENTBRITE_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `EVENTBRITE_API_URL` | Base URL for all requests |

## Attendees

```bash
curl -s -X POST "$EVENTBRITE_API_URL/v3/attendees/<attendee_id>/check_in" -H 'Content-Type: application/json' -d '{}'
```

## Events

```bash
curl -s "$EVENTBRITE_API_URL/v3/events/search"
curl -s "$EVENTBRITE_API_URL/v3/events/<event_id>"
curl -s -X POST "$EVENTBRITE_API_URL/v3/events" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$EVENTBRITE_API_URL/v3/events/<event_id>/publish" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$EVENTBRITE_API_URL/v3/events/<event_id>/cancel" -H 'Content-Type: application/json' -d '{}'
curl -s "$EVENTBRITE_API_URL/v3/events/<event_id>/ticket_classes"
curl -s -X POST "$EVENTBRITE_API_URL/v3/events/<event_id>/ticket_classes" -H 'Content-Type: application/json' -d '{}'
curl -s "$EVENTBRITE_API_URL/v3/events/<event_id>/attendees"
curl -s -X POST "$EVENTBRITE_API_URL/v3/events/<event_id>/attendees" -H 'Content-Type: application/json' -d '{}'
```

## Organizations

```bash
curl -s "$EVENTBRITE_API_URL/v3/organizations/<org_id>"
curl -s "$EVENTBRITE_API_URL/v3/organizations/<org_id>/events"
```

## Users

```bash
curl -s "$EVENTBRITE_API_URL/v3/users/me/organizations"
```

## Venues

```bash
curl -s "$EVENTBRITE_API_URL/v3/venues"
curl -s "$EVENTBRITE_API_URL/v3/venues/<venue_id>"
```

The audit log of every call is available at `$EVENTBRITE_API_URL/audit/requests` (used for grading).
