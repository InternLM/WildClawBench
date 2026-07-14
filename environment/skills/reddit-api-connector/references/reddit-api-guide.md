# Reddit API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$REDDIT_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `REDDIT_API_URL` | Base URL for all requests |

## Api

```bash
curl -s -X POST "$REDDIT_API_URL/api/submit" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$REDDIT_API_URL/api/vote" -H 'Content-Type: application/json' -d '{}'
```

## Comments

```bash
curl -s "$REDDIT_API_URL/comments/<post_id>"
```

## R

```bash
curl -s "$REDDIT_API_URL/r/<subreddit>/about"
curl -s "$REDDIT_API_URL/r/<subreddit>/hot"
curl -s "$REDDIT_API_URL/r/<subreddit>/new"
```

## User

```bash
curl -s "$REDDIT_API_URL/user/<username>/about"
```

The audit log of every call is available at `$REDDIT_API_URL/audit/requests` (used for grading).
