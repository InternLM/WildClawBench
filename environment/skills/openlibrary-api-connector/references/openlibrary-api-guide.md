# Open Library API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$OPENLIBRARY_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `OPENLIBRARY_API_URL` | Base URL for all requests |

## Authors

```bash
curl -s "$OPENLIBRARY_API_URL/authors/<author_id>.json"
curl -s "$OPENLIBRARY_API_URL/authors/<author_id>/works.json"
```

## Isbn

```bash
curl -s "$OPENLIBRARY_API_URL/isbn/<isbn>.json"
```

## Search.Json

```bash
curl -s "$OPENLIBRARY_API_URL/search.json"
```

## Subjects

```bash
curl -s "$OPENLIBRARY_API_URL/subjects/<subject>.json"
```

## Works

```bash
curl -s "$OPENLIBRARY_API_URL/works/<work_id>.json"
curl -s "$OPENLIBRARY_API_URL/works/<work_id>/editions.json"
```

The audit log of every call is available at `$OPENLIBRARY_API_URL/audit/requests` (used for grading).
