# NASA Open API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$NASA_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `NASA_API_URL` | Base URL for all requests |

## Epic

```bash
curl -s "$NASA_API_URL/EPIC/api/natural"
```

## Mars Photos

```bash
curl -s "$NASA_API_URL/mars-photos/api/v1/rovers/<rover>/photos"
curl -s "$NASA_API_URL/mars-photos/api/v1/rovers/<rover>"
```

## Neo

```bash
curl -s "$NASA_API_URL/neo/rest/v1/feed"
curl -s "$NASA_API_URL/neo/rest/v1/neo/<neo_id>"
```

## Planetary

```bash
curl -s "$NASA_API_URL/planetary/apod"
```

The audit log of every call is available at `$NASA_API_URL/audit/requests` (used for grading).
