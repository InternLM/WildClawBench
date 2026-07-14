# GitHub REST API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$GITHUB_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `GITHUB_API_URL` | Base URL for all requests |

## Orgs

```bash
curl -s "$GITHUB_API_URL/orgs/<owner>/repos"
```

## Repos

```bash
curl -s "$GITHUB_API_URL/repos/<owner>/<repo>"
curl -s "$GITHUB_API_URL/repos/<owner>/<repo>/issues"
curl -s "$GITHUB_API_URL/repos/<owner>/<repo>/issues/<number>"
curl -s -X POST "$GITHUB_API_URL/repos/<owner>/<repo>/issues" -H 'Content-Type: application/json' -d '{}'
curl -s -X PATCH "$GITHUB_API_URL/repos/<owner>/<repo>/issues/<number>" -H 'Content-Type: application/json' -d '{}'
curl -s "$GITHUB_API_URL/repos/<owner>/<repo>/pulls"
curl -s "$GITHUB_API_URL/repos/<owner>/<repo>/pulls/<number>"
curl -s -X PUT "$GITHUB_API_URL/repos/<owner>/<repo>/pulls/<number>/merge" -H 'Content-Type: application/json' -d '{}'
curl -s "$GITHUB_API_URL/repos/<owner>/<repo>/issues/<number>/comments"
curl -s -X POST "$GITHUB_API_URL/repos/<owner>/<repo>/issues/<number>/comments" -H 'Content-Type: application/json' -d '{}'
```

## User

```bash
curl -s "$GITHUB_API_URL/user"
```

## Users

```bash
curl -s "$GITHUB_API_URL/users/<owner>/repos"
```

The audit log of every call is available at `$GITHUB_API_URL/audit/requests` (used for grading).
