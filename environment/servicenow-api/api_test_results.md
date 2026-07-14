# ServiceNow Table API Mock — Test Results

Base URL: `http://localhost:8071` (in docker-compose: `http://servicenow-api:8071`)

## Endpoints covered

| Method | Path                                      | Status  |
|--------|-------------------------------------------|---------|
| GET    | /health                                   | 200     |
| GET    | /api/now/table/incident                   | 200     |
| GET    | /api/now/table/incident/{sys_id}          | 200/404 |
| POST   | /api/now/table/incident                   | 201/400 |
| PATCH  | /api/now/table/incident/{sys_id}          | 200/404 |
| GET    | /api/now/table/change_request             | 200     |
| GET    | /api/now/table/change_request/{sys_id}    | 200/404 |
| GET    | /api/now/table/problem                    | 200     |
| GET    | /api/now/table/problem/{sys_id}           | 200/404 |
| GET    | /api/now/table/sys_user                   | 200     |
| GET    | /api/now/table/sys_user/{sys_id}          | 200/404 |

## Seed data summary

- Incidents: 10 (states New=1, In Progress=2, Resolved=6; priorities 1-5)
- Change requests: 6 (new, assess, scheduled, implement, review, closed)
- Problems: 5 (linked to related incidents)
- Users (sys_user): 8 (7 active, 1 inactive)

## Notes

- All successful responses are wrapped as `{"result": ...}` per the ServiceNow convention.
- `sysparm_query` supports the `^` (AND) separator with `field=value` equality,
  e.g. `state=2^priority=1`. Unknown operators are ignored.
- `sysparm_limit` caps the number of returned rows.
- Incident `state` codes: New=1, In Progress=2, On Hold=3, Resolved=6, Closed=7.
- Mutations are held in process memory and reset on container restart.
