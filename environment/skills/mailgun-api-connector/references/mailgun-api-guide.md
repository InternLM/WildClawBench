# Mailgun API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$MAILGUN_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `MAILGUN_API_URL` | Base URL for all requests |

## Events

```bash
curl -s "$MAILGUN_API_URL/v3/<domain>/events"
```

## Lists

```bash
curl -s "$MAILGUN_API_URL/v3/lists/<address>/members"
```

## Messages

```bash
curl -s -X POST "$MAILGUN_API_URL/v3/<domain>/messages" -H 'Content-Type: application/json' -d '{}'
```

## Stats

```bash
curl -s "$MAILGUN_API_URL/v3/<domain>/stats/total"
```

The audit log of every call is available at `$MAILGUN_API_URL/audit/requests` (used for grading).
