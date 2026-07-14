# Airtable Mock API — Test Results

Base URL: `http://localhost:8032` (in docker-compose: `http://airtable-api:8032`)

## Endpoints covered

| Method | Path                                              | Status  |
|--------|---------------------------------------------------|---------|
| GET    | /health                                           | 200     |
| GET    | /v0/meta/bases                                     | 200     |
| GET    | /v0/meta/bases/{baseId}/tables                     | 200/404 |
| GET    | /v0/{baseId}/{tableIdOrName}                        | 200/404 |
| GET    | /v0/{baseId}/{tableIdOrName}/{recordId}            | 200/404 |
| POST   | /v0/{baseId}/{tableIdOrName}                        | 200/404 |
| PATCH  | /v0/{baseId}/{tableIdOrName}/{recordId}            | 200/404 |
| DELETE | /v0/{baseId}/{tableIdOrName}/{recordId}            | 200/404 |

## Seed data summary

- Base: `appNW1studio0001` (Studio Ops)
- Tables: 3 (Projects, Tasks, Contacts)
- Records: Projects 8, Tasks 10, Contacts 9
- Each non-id / non-createdTime CSV column maps to a record field. Numeric
  fields (Budget, EstimateHours) cast to numbers; checkbox fields (Done) to bool.

## Notes

- Records are modeled as `{id, createdTime, fields:{...}}` to match Airtable.
- Tables can be addressed by id (`tblTasks00000001`) or by name (`Tasks`).
- List supports `pageSize` (max 100) plus `offset` cursor pagination; the
  response includes an `offset` field when more records remain.
- `filterByFormula` supports the simple form `{Field}='Value'`.
- `POST` body is `{"records":[{"fields":{...}}]}` and returns created records.
- Mutations are held in process memory and reset on container restart.
