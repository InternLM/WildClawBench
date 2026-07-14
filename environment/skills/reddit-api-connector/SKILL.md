---
name: reddit-api-connector
description: >
  Reddit API (Mock) mock HTTP API. Base URL is provided via the
  `REDDIT_API_URL` environment variable. 7 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Reddit API (Mock)

Mock HTTP API. **All requests go to the base URL in `$REDDIT_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `REDDIT_API_URL` | Base URL for all requests (e.g. `http://reddit-api:8058`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/r/{subreddit}/about` |
| GET | `/r/{subreddit}/hot` |
| GET | `/r/{subreddit}/new` |
| GET | `/comments/{post_id}` |
| POST | `/api/submit` |
| POST | `/api/vote` |
| GET | `/user/{username}/about` |

## Usage

```bash
# GET example
curl -s "$REDDIT_API_URL/r/{subreddit}/about"

# POST example
curl -s -X POST "$REDDIT_API_URL/r/{subreddit}/about" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$REDDIT_API_URL/audit/requests` (used for grading).
