# Zillow API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$ZILLOW_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `ZILLOW_API_URL` | Base URL for all requests |

## Agents

```bash
curl -s "$ZILLOW_API_URL/v1/agents"
curl -s "$ZILLOW_API_URL/v1/agents/<agent_id>"
```

## Properties

```bash
curl -s "$ZILLOW_API_URL/v1/properties/search"
curl -s "$ZILLOW_API_URL/v1/properties/<zpid>"
curl -s "$ZILLOW_API_URL/v1/properties/<zpid>/zestimate"
curl -s "$ZILLOW_API_URL/v1/properties/<zpid>/price-history"
```

## Saved Searches

```bash
curl -s -X DELETE "$ZILLOW_API_URL/v1/saved-searches/<search_id>"
```

## Users

```bash
curl -s "$ZILLOW_API_URL/v1/users/<user_id>/saved-searches"
curl -s -X POST "$ZILLOW_API_URL/v1/users/<user_id>/saved-searches" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$ZILLOW_API_URL/audit/requests` (used for grading).
