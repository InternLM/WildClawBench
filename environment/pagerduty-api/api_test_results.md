# PagerDuty Mock API — Test Results

Base URL: `http://localhost:8040` (docker-compose: `http://pagerduty-api:8040`)

## Endpoints

| Method | Path                              | Status   |
|--------|-----------------------------------|----------|
| GET    | /health                           | 200      |
| GET    | /services                         | 200      |
| GET    | /services/{id}                    | 200/404  |
| GET    | /incidents                        | 200      |
| GET    | /incidents/{id}                   | 200/404  |
| POST   | /incidents                        | 201/400  |
| PUT    | /incidents/{id}                   | 200/400/404 |
| GET    | /incidents/{id}/notes             | 200/404  |
| POST   | /incidents/{id}/notes             | 201/404  |
| GET    | /oncalls                          | 200      |
| GET    | /schedules                        | 200      |
| GET    | /escalation_policies              | 200      |
| GET    | /users                            | 200      |

## Seed data

- Services: 3 (auth-api, billing-api, notifications-api)
- Incidents: 6 (2 triggered, 2 acknowledged, 2 resolved) across high/low urgency,
  including an auth-api token-refresh latency incident
- Escalation policies: 2 | Schedules: 3 | Users: 5

## Notes

- Incidents, notes, and status changes are held in process memory and reset on restart.
- `GET /incidents` supports repeated `statuses[]=` query params (e.g.
  `?statuses[]=triggered&statuses[]=acknowledged`), plus `service_id` and `urgency`.
- `PUT /incidents/{id}` accepts a `status` of triggered/acknowledged/resolved;
  resolving stamps `resolved_at`. It may also reassign via `assigned_to`.
- New incidents start in `triggered` and inherit the service's escalation policy.
