# Okta Mock API — Test Results

Base URL: `http://localhost:8049` (docker-compose: `http://okta-api:8049`)

## Endpoints

| Method | Path                                          | Status      |
|--------|-----------------------------------------------|-------------|
| GET    | /health                                       | 200         |
| GET    | /api/v1/users                                 | 200         |
| POST   | /api/v1/users                                 | 201         |
| GET    | /api/v1/users/{id}                            | 200/404     |
| POST   | /api/v1/users/{id}/lifecycle/activate         | 200/403/404 |
| POST   | /api/v1/users/{id}/lifecycle/suspend          | 200/403/404 |
| POST   | /api/v1/users/{id}/lifecycle/deactivate       | 200/404     |
| GET    | /api/v1/groups                                | 200         |
| GET    | /api/v1/groups/{id}                           | 200/404     |
| GET    | /api/v1/groups/{id}/users                     | 200/404     |
| GET    | /api/v1/apps                                  | 200         |

## Seed data

- 6 users (statuses ACTIVE / SUSPENDED / PROVISIONED)
- 4 groups (Engineering, Platform Team, Administrators, Everyone)
- 13 group memberships
- 4 apps (3 active, 1 inactive) with 6 user assignments

## Notes

- Mutations are held in process memory and reset on container restart.
- Lifecycle transitions are validated: activate requires STAGED/PROVISIONED/DEPROVISIONED,
  suspend requires ACTIVE; an invalid transition returns 403 while an unknown user returns 404.
- User responses use the Okta nested `profile` shape.
- User list supports `status` and `q` (name/email substring) query params.
