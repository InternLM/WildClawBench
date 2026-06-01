# HubSpot Mock CRM API — Test Results

Base URL: `http://localhost:8024` (in docker-compose: `http://hubspot-api:8024`)

## Endpoints covered

| Method | Path                                  | Status   |
|--------|---------------------------------------|----------|
| GET    | /health                               | 200      |
| GET    | /crm/v3/objects/contacts              | 200      |
| GET    | /crm/v3/objects/contacts/{id}         | 200/404  |
| POST   | /crm/v3/objects/contacts              | 201      |
| PATCH  | /crm/v3/objects/contacts/{id}         | 200/404  |
| GET    | /crm/v3/objects/companies             | 200      |
| GET    | /crm/v3/objects/companies/{id}        | 200/404  |
| GET    | /crm/v3/objects/deals                 | 200      |
| GET    | /crm/v3/objects/deals/{id}            | 200/404  |
| POST   | /crm/v3/objects/deals                 | 201      |
| PATCH  | /crm/v3/objects/deals/{id}            | 200/400/404 |
| GET    | /crm/v3/pipelines/deals               | 200      |

## Seed data summary

- Contacts: 8 (ids 201-208) across lifecycle stages (lead .. customer)
- Companies: 4 (ids 301-304)
- Deals: 6 (ids 401-406) spread across the default pipeline's stages
  (appointmentscheduled, qualifiedtobuy, presentationscheduled,
  decisionmakerboughtin, closedwon, closedlost)
- Pipelines: 1 ("default" Sales Pipeline) with 6 ordered stages

## Notes

- Objects use the HubSpot shape: `{"id", "properties": {...}, "createdAt",
  "updatedAt", "archived"}`. Create/update bodies use `{"properties": {...}}`.
- List endpoints paginate via `limit` + `after` (offset cursor); when more
  results exist the response includes `paging.next.after`.
- `PATCH /crm/v3/objects/deals/{id}` is the way to move a deal between stages.
  Supplying a `dealstage` that is not part of the deal's pipeline returns 400
  with `category: VALIDATION_ERROR`. Unknown deal returns 404.
- `GET /crm/v3/pipelines/deals` returns the pipeline + ordered stage definitions
  (each stage carries `metadata.isClosed` and `metadata.probability`).
- Mutations are held in process memory and reset on container restart.
