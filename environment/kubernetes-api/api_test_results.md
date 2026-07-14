# Kubernetes Mock API — Test Results

Base URL: `http://localhost:8051` (in docker-compose: `http://kubernetes-api:8051`)

## Endpoints covered

| Method | Path                                                        | Status |
|--------|-------------------------------------------------------------|--------|
| GET    | /health                                                     | 200    |
| GET    | /api/v1/namespaces                                          | 200    |
| GET    | /api/v1/namespaces/{ns}/pods                                | 200/404 |
| GET    | /api/v1/namespaces/{ns}/pods/{name}                         | 200/404 |
| DELETE | /api/v1/namespaces/{ns}/pods/{name}                         | 200/404 |
| GET    | /apis/apps/v1/namespaces/{ns}/deployments                  | 200/404 |
| GET    | /apis/apps/v1/namespaces/{ns}/deployments/{name}           | 200/404 |
| PATCH  | /apis/apps/v1/namespaces/{ns}/deployments/{name}/scale     | 200/404 |
| GET    | /api/v1/namespaces/{ns}/services                           | 200/404 |
| GET    | /api/v1/nodes                                               | 200    |

## Seed data summary

- Namespaces: 3 (default, kube-system, prod) — all Active
- Pods: 9 (Running, Pending, CrashLoopBackOff) across namespaces
- Deployments: 5 (with replicas / availableReplicas / readyReplicas)
- Services: 5 (ClusterIP and LoadBalancer types)
- Nodes: 4 (1 control-plane + 3 workers), all Ready

## Notes

- Responses use k8s-style list envelopes `{"kind":"PodList","apiVersion":"v1","items":[...]}`
  and object metadata `{"metadata":{...},"spec":{...},"status":{...}}`.
- `PATCH .../scale` accepts `{"spec":{"replicas":N}}`; the mock converges
  available/ready/updated replicas to the requested count.
- Mutations are held in process memory and reset on container restart.
