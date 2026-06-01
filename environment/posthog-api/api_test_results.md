# PostHog Mock API — Test Results

Base URL: `http://localhost:8092` (in docker-compose: `http://posthog-api:8092`)

## Endpoints covered

| Method | Path                                          | Status |
|--------|-----------------------------------------------|--------|
| GET    | /health                                       | 200    |
| POST   | /capture                                      | 200    |
| POST   | /decide                                       | 200    |
| GET    | /api/projects/{project_id}/events             | 200    |
| GET    | /api/projects/{project_id}/feature_flags      | 200    |
| GET    | /api/projects/{project_id}/persons            | 200    |

## Seed data summary

- Events: 10 seeded events across projects 1 and 2 ($pageview, purchase, etc.), dated 2026-05.
- Feature flags: 5 flags (new-onboarding, beta-dashboard, dark-mode, fast-checkout, referral-program).
- Persons: 5 persons with distinct_id, name, email, created_at.

## Notes

- `/capture` accepts a JSON event and appends to the in-memory event store, returning `{"status": 1}`.
- `/decide` returns `featureFlags` (key -> enabled bool) for the given project + distinct_id.
- List endpoints wrap results as `{"results": [...], "count": N}` and are scoped by `project_id`.
- `/events` is filterable by `event` and `distinct_id`.
- Captured events are held in process memory and reset on container restart.
