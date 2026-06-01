# BambooHR API Mock — Test Results

Base URL: `http://localhost:8072` (in docker-compose: `http://bamboohr-api:8072`)

The `{company}` path segment defaults to `orbitlabs` and is accepted but not validated.

## Endpoints covered

| Method | Path                                                       | Status  |
|--------|------------------------------------------------------------|---------|
| GET    | /health                                                    | 200     |
| GET    | /api/gateway.php/{company}/v1/company                      | 200     |
| GET    | /api/gateway.php/{company}/v1/employees/directory          | 200     |
| GET    | /api/gateway.php/{company}/v1/employees/{id}               | 200/404 |
| POST   | /api/gateway.php/{company}/v1/employees                    | 201/400 |
| GET    | /api/gateway.php/{company}/v1/time_off/requests            | 200     |
| POST   | /api/gateway.php/{company}/v1/time_off/requests            | 201/404 |
| PUT    | /api/gateway.php/{company}/v1/time_off/requests/{id}/status| 200/404 |
| GET    | /api/gateway.php/{company}/v1/time_off/whos_out            | 200     |
| GET    | /api/gateway.php/{company}/v1/reports/{id}                 | 200/404 |

## Seed data summary

- Company: Orbit Labs Inc. (subdomain `orbitlabs`)
- Employees: 12 (11 Active, 1 Inactive) across Engineering, People, Sales, Marketing, Executive
- Time-off requests: 10 (approved / requested / denied mix)
- Who's out windows: 5

## Notes

- Time-off status transitions accept `requested`, `approved`, `denied`, `canceled`.
- `time_off/requests` supports filtering by `status` and `employeeId` query params.
- `time_off/whos_out` accepts optional `start` / `end` query params to clip the window.
- Report id `1` synthesizes headcount-by-department from active employees.
- Mutations are held in process memory and reset on container restart.
