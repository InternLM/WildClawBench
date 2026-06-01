---
name: kubernetes-api-connector
description: >
  Kubernetes API (Mock) mock HTTP API. Base URL is provided via the
  `KUBERNETES_API_URL` environment variable. 9 endpoint(s) across DELETE, GET, PATCH.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Kubernetes API (Mock)

Mock HTTP API. **All requests go to the base URL in `$KUBERNETES_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `KUBERNETES_API_URL` | Base URL for all requests (e.g. `http://kubernetes-api:8051`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/api/v1/namespaces` |
| GET | `/api/v1/namespaces/{ns}/pods` |
| GET | `/api/v1/namespaces/{ns}/pods/{name}` |
| DELETE | `/api/v1/namespaces/{ns}/pods/{name}` |
| GET | `/apis/apps/v1/namespaces/{ns}/deployments` |
| GET | `/apis/apps/v1/namespaces/{ns}/deployments/{name}` |
| PATCH | `/apis/apps/v1/namespaces/{ns}/deployments/{name}/scale` |
| GET | `/api/v1/namespaces/{ns}/services` |
| GET | `/api/v1/nodes` |

## Usage

```bash
# GET example
curl -s "$KUBERNETES_API_URL/api/v1/namespaces"

# POST example
curl -s -X POST "$KUBERNETES_API_URL/api/v1/namespaces" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$KUBERNETES_API_URL/audit/requests` (used for grading).
