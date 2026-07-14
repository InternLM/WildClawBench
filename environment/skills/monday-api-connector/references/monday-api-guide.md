# monday.com API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$MONDAY_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `MONDAY_API_URL` | Base URL for all requests |

## Boards

```bash
curl -s "$MONDAY_API_URL/v2/boards"
curl -s "$MONDAY_API_URL/v2/boards/<board_id>"
curl -s "$MONDAY_API_URL/v2/boards/<board_id>/items"
```

## Items

```bash
curl -s "$MONDAY_API_URL/v2/items"
curl -s -X POST "$MONDAY_API_URL/v2/items" -H 'Content-Type: application/json' -d '{}'
curl -s "$MONDAY_API_URL/v2/items/<item_id>"
curl -s -X PUT "$MONDAY_API_URL/v2/items/<item_id>" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$MONDAY_API_URL/v2/items/<item_id>"
```

## Users

```bash
curl -s "$MONDAY_API_URL/v2/users"
```

## Workspaces

```bash
curl -s "$MONDAY_API_URL/v2/workspaces"
```

The audit log of every call is available at `$MONDAY_API_URL/audit/requests` (used for grading).
