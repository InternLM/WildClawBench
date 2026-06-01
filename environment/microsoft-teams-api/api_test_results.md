# Microsoft Teams Mock API — Test Results

Base URL: `http://localhost:8086` (in docker-compose: `http://microsoft-teams-api:8086`)

## Endpoints covered

| Method | Path                                                              | Status      |
|--------|------------------------------------------------------------------|-------------|
| GET    | /health                                                          | 200         |
| GET    | /v1.0/me/joinedTeams                                             | 200         |
| GET    | /v1.0/teams/{team_id}                                            | 200/404     |
| GET    | /v1.0/teams/{team_id}/channels                                   | 200/404     |
| GET    | /v1.0/teams/{team_id}/channels/{channel_id}/messages            | 200/404     |
| POST   | /v1.0/teams/{team_id}/channels/{channel_id}/messages            | 201/400/404 |

## Seed data summary

- Teams: 6 (Engineering, Product, Marketing, Sales, All Company, Architecture Guild — one archived) with displayName, visibility, and members.
- Channels: 9 across the teams (General defaults plus topic channels), standard and private.
- Messages: 10 channel posts with from-user, importance, and 2026-05 timestamps.

## Notes

- Collection responses are wrapped in `{"value": [...]}` to match Microsoft Graph.
- `/v1.0/me/joinedTeams` returns non-archived teams the signed-in user (`user-001`) belongs to.
- `POST .../messages` accepts a Graph chatMessage body (`{"body": {"contentType","content"}, "importance"}`); a missing `content` returns 400, an unknown channel 404.
- Mutations are held in process memory and reset on container restart.
