# Trello API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$TRELLO_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TRELLO_API_URL` | Base URL for all requests |

## 1

```bash
curl -s "$TRELLO_API_URL/1/members/me"
curl -s "$TRELLO_API_URL/1/members/me/boards"
curl -s "$TRELLO_API_URL/1/boards/<board_id>"
curl -s "$TRELLO_API_URL/1/boards/<board_id>/lists"
curl -s "$TRELLO_API_URL/1/lists/<list_id>/cards"
curl -s "$TRELLO_API_URL/1/cards/<card_id>"
curl -s -X POST "$TRELLO_API_URL/1/cards" -H 'Content-Type: application/json' -d '{}'
curl -s -X PUT "$TRELLO_API_URL/1/cards/<card_id>" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$TRELLO_API_URL/1/cards/<card_id>"
curl -s "$TRELLO_API_URL/1/cards/<card_id>/checklists"
curl -s -X POST "$TRELLO_API_URL/1/checklists" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$TRELLO_API_URL/audit/requests` (used for grading).
