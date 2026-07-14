# Notion API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$NOTION_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `NOTION_API_URL` | Base URL for all requests |

## Blocks

```bash
curl -s "$NOTION_API_URL/v1/blocks/<block_id>/children"
curl -s -X PATCH "$NOTION_API_URL/v1/blocks/<block_id>/children" -H 'Content-Type: application/json' -d '{}'
curl -s -X PATCH "$NOTION_API_URL/v1/blocks/<block_id>" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$NOTION_API_URL/v1/blocks/<block_id>"
```

## Comments

```bash
curl -s "$NOTION_API_URL/v1/comments"
curl -s -X POST "$NOTION_API_URL/v1/comments" -H 'Content-Type: application/json' -d '{}'
```

## Databases

```bash
curl -s "$NOTION_API_URL/v1/databases/<database_id>"
curl -s -X POST "$NOTION_API_URL/v1/databases/<database_id>/query" -H 'Content-Type: application/json' -d '{}'
```

## Pages

```bash
curl -s "$NOTION_API_URL/v1/pages/<page_id>"
curl -s -X POST "$NOTION_API_URL/v1/pages" -H 'Content-Type: application/json' -d '{}'
curl -s -X PATCH "$NOTION_API_URL/v1/pages/<page_id>" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$NOTION_API_URL/v1/pages/<page_id>"
```

## Search

```bash
curl -s -X POST "$NOTION_API_URL/v1/search" -H 'Content-Type: application/json' -d '{}'
```

## Users

```bash
curl -s "$NOTION_API_URL/v1/users"
curl -s "$NOTION_API_URL/v1/users/me"
curl -s "$NOTION_API_URL/v1/users/<user_id>"
```

## Workspace

```bash
curl -s "$NOTION_API_URL/v1/workspace"
```

The audit log of every call is available at `$NOTION_API_URL/audit/requests` (used for grading).
