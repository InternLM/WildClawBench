# Figma API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$FIGMA_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `FIGMA_API_URL` | Base URL for all requests |

## Files

```bash
curl -s "$FIGMA_API_URL/v1/files/<file_key>"
curl -s "$FIGMA_API_URL/v1/files/<file_key>/nodes"
curl -s "$FIGMA_API_URL/v1/files/<file_key>/comments"
curl -s -X POST "$FIGMA_API_URL/v1/files/<file_key>/comments" -H 'Content-Type: application/json' -d '{}'
curl -s "$FIGMA_API_URL/v1/files/<file_key>/components"
```

## Me

```bash
curl -s "$FIGMA_API_URL/v1/me"
```

## Projects

```bash
curl -s "$FIGMA_API_URL/v1/projects/<project_id>/files"
```

## Teams

```bash
curl -s "$FIGMA_API_URL/v1/teams/<team_id>/projects"
```

The audit log of every call is available at `$FIGMA_API_URL/audit/requests` (used for grading).
