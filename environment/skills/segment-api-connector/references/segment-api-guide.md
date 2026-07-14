# Segment API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$SEGMENT_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `SEGMENT_API_URL` | Base URL for all requests |

## Batch

```bash
curl -s -X POST "$SEGMENT_API_URL/v1/batch" -H 'Content-Type: application/json' -d '{}'
```

## Destinations

```bash
curl -s "$SEGMENT_API_URL/v1/destinations"
```

## Events

```bash
curl -s "$SEGMENT_API_URL/v1/events"
```

## Identify

```bash
curl -s -X POST "$SEGMENT_API_URL/v1/identify" -H 'Content-Type: application/json' -d '{}'
```

## Page

```bash
curl -s -X POST "$SEGMENT_API_URL/v1/page" -H 'Content-Type: application/json' -d '{}'
```

## Sources

```bash
curl -s "$SEGMENT_API_URL/v1/sources"
```

## Track

```bash
curl -s -X POST "$SEGMENT_API_URL/v1/track" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$SEGMENT_API_URL/audit/requests` (used for grading).
