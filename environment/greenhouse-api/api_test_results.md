# Greenhouse Harvest API Mock — Test Results

Base URL: `http://localhost:8073` (in docker-compose: `http://greenhouse-api:8073`)

## Endpoints covered

| Method | Path                                  | Status  |
|--------|---------------------------------------|---------|
| GET    | /health                               | 200     |
| GET    | /v1/candidates                        | 200     |
| POST   | /v1/candidates                        | 201/400 |
| GET    | /v1/candidates/{id}                   | 200/404 |
| GET    | /v1/jobs                              | 200     |
| GET    | /v1/jobs/{id}                         | 200/404 |
| GET    | /v1/applications                      | 200     |
| GET    | /v1/applications/{id}                 | 200/404 |
| POST   | /v1/applications/{id}/advance         | 200/404/400 |
| POST   | /v1/applications/{id}/reject          | 200/404 |
| GET    | /v1/scorecards                        | 200     |

## Seed data summary

- Candidates: 8
- Jobs: 6 (5 open, 1 closed)
- Applications: 8 across stages Application Review / Interview / Offer (7 active, 1 rejected)
- Scorecards: 6 with overall recommendations and ratings 1-5

## Notes

- The hiring pipeline stages, in order, are: Application Review, Interview, Offer, Hired.
- `POST /v1/applications/{id}/advance` moves an active application to the next stage;
  advancing past Offer marks the application `hired`. Non-active applications return 400.
- `POST /v1/applications/{id}/reject` accepts an optional `{"reason": "..."}` body.
- `/v1/applications` supports `job_id`, `candidate_id`, and `status` filters;
  `/v1/jobs` supports a `status` filter; `/v1/scorecards` supports
  `application_id` and `candidate_id` filters.
- Mutations are held in process memory and reset on container restart.
