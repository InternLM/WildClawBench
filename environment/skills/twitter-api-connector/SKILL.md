---
name: twitter-api-connector
description: >
  Twitter/X API v2 (Mock) mock HTTP API. Base URL is provided via the
  `TWITTER_API_URL` environment variable. 13 endpoint(s) across DELETE, GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Twitter/X API v2 (Mock)

Mock HTTP API. **All requests go to the base URL in `$TWITTER_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TWITTER_API_URL` | Base URL for all requests (e.g. `http://twitter-api:8061`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/2/users/me` |
| GET | `/2/users/by/username/{username}` |
| GET | `/2/users/{user_id}` |
| GET | `/2/users/{user_id}/tweets` |
| GET | `/2/users/{user_id}/followers` |
| GET | `/2/users/{user_id}/following` |
| GET | `/2/tweets` |
| GET | `/2/tweets/search/recent` |
| GET | `/2/tweets/{tweet_id}` |
| POST | `/2/tweets` |
| DELETE | `/2/tweets/{tweet_id}` |
| POST | `/2/users/{user_id}/likes` |
| POST | `/2/users/{user_id}/retweets` |

## Usage

```bash
# GET example
curl -s "$TWITTER_API_URL/2/users/me"

# POST example
curl -s -X POST "$TWITTER_API_URL/2/users/me" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$TWITTER_API_URL/audit/requests` (used for grading).
