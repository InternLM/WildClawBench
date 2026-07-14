# Twitter/X API v2 (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$TWITTER_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TWITTER_API_URL` | Base URL for all requests |

## 2

```bash
curl -s "$TWITTER_API_URL/2/users/me"
curl -s "$TWITTER_API_URL/2/users/by/username/<username>"
curl -s "$TWITTER_API_URL/2/users/<user_id>"
curl -s "$TWITTER_API_URL/2/users/<user_id>/tweets"
curl -s "$TWITTER_API_URL/2/users/<user_id>/followers"
curl -s "$TWITTER_API_URL/2/users/<user_id>/following"
curl -s "$TWITTER_API_URL/2/tweets"
curl -s "$TWITTER_API_URL/2/tweets/search/recent"
curl -s "$TWITTER_API_URL/2/tweets/<tweet_id>"
curl -s -X POST "$TWITTER_API_URL/2/tweets" -H 'Content-Type: application/json' -d '{}'
curl -s -X DELETE "$TWITTER_API_URL/2/tweets/<tweet_id>"
curl -s -X POST "$TWITTER_API_URL/2/users/<user_id>/likes" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$TWITTER_API_URL/2/users/<user_id>/retweets" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$TWITTER_API_URL/audit/requests` (used for grading).
