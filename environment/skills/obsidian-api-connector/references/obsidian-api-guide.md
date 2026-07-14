# Obsidian API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$OBSIDIAN_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `OBSIDIAN_API_URL` | Base URL for all requests |

## Vault

```bash
curl -s "$OBSIDIAN_API_URL/vault"
curl -s "$OBSIDIAN_API_URL/vault/notes"
curl -s "$OBSIDIAN_API_URL/vault/notes/<path:path>"
curl -s -X POST "$OBSIDIAN_API_URL/vault/notes" -H 'Content-Type: application/json' -d '{}'
curl -s -X PUT "$OBSIDIAN_API_URL/vault/notes/<path:path>" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$OBSIDIAN_API_URL/vault/notes/<path:path>"
curl -s "$OBSIDIAN_API_URL/vault/search"
curl -s "$OBSIDIAN_API_URL/vault/backlinks/<path:path>"
curl -s "$OBSIDIAN_API_URL/vault/daily/<date_str>"
```

The audit log of every call is available at `$OBSIDIAN_API_URL/audit/requests` (used for grading).
