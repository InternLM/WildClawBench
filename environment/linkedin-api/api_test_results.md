# LinkedIn Mock API v2 — Test Results

Base URL: `http://localhost:8062` (in docker-compose: `http://linkedin-api:8062`)

## Endpoints covered

| Method | Path                              | Status |
|--------|-----------------------------------|--------|
| GET    | /health                           | 200    |
| GET    | /v2/me                            | 200    |
| GET    | /v2/connections                   | 200    |
| GET    | /v2/posts                         | 200    |
| POST   | /v2/posts                         | 201    |
| GET    | /v2/posts/{id}                    | 200/404 |
| GET    | /v2/organizations/{id}            | 200/404 |
| GET    | /v2/jobs                          | 200    |
| GET    | /v2/jobs/{id}                     | 200/404 |

## Seed data summary

- Profile ("me"): Amelia Ortega (`urn:li:person:amelia-ortega`), VP Engineering at Orbit Labs.
- Connections: 8 (colleagues + cross-company contacts).
- Posts: 6 (person + organization authored), each with `socialDetail` reaction/comment/share counts.
- Organizations: 4 (Orbit Labs, Northwind Systems, Helix Analytics, Brightloop).
- Jobs: 6 postings across the seeded organizations.

## Notes

- Mutations are held in process memory and reset on container restart.
- Collections return the LinkedIn-style envelope `{"elements": [...], "paging": {...}}`.
- `GET /v2/me` returns the profile singleton from `profile.json`.
- `GET /v2/jobs` filters by case-insensitive `keywords` (title/description/keyword tags) and `location` substring.
- `POST /v2/posts` defaults the author to the "me" profile and starts all social counts at zero.
