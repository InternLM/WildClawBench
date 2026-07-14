# Kubernetes API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$KUBERNETES_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `KUBERNETES_API_URL` | Base URL for all requests |

## Api

```bash
curl -s "$KUBERNETES_API_URL/api/v1/namespaces"
curl -s "$KUBERNETES_API_URL/api/v1/namespaces/<ns>/pods"
curl -s "$KUBERNETES_API_URL/api/v1/namespaces/<ns>/pods/<name>"
curl -s -X DELETE "$KUBERNETES_API_URL/api/v1/namespaces/<ns>/pods/<name>"
curl -s "$KUBERNETES_API_URL/api/v1/namespaces/<ns>/services"
curl -s "$KUBERNETES_API_URL/api/v1/nodes"
```

## Apis

```bash
curl -s "$KUBERNETES_API_URL/apis/apps/v1/namespaces/<ns>/deployments"
curl -s "$KUBERNETES_API_URL/apis/apps/v1/namespaces/<ns>/deployments/<name>"
curl -s -X PATCH "$KUBERNETES_API_URL/apis/apps/v1/namespaces/<ns>/deployments/<name>/scale" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$KUBERNETES_API_URL/audit/requests` (used for grading).
