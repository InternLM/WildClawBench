# Zoom Mock API — Test Results

Base URL: `http://localhost:8028` (in docker-compose: `http://zoom-api:8028`)

## Endpoints covered

| Method | Path                                       | Status  |
|--------|--------------------------------------------|---------|
| GET    | /health                                    | 200     |
| GET    | /v2/users/me                               | 200     |
| GET    | /v2/users/{userId}/meetings                | 200/404 |
| POST   | /v2/users/{userId}/meetings                | 201/404 |
| GET    | /v2/meetings/{meetingId}                    | 200/404 |
| PATCH  | /v2/meetings/{meetingId}                    | 200/404 |
| DELETE | /v2/meetings/{meetingId}                    | 204/404 |
| GET    | /v2/meetings/{meetingId}/recordings         | 200/404 |
| GET    | /v2/meetings/{meetingId}/registrants        | 200/404 |

## Seed data summary

- User: 1 (`u-amelia-9f4b2e8d`, Owner). `me` resolves to this user.
- Meetings: 6 (3 scheduled/`waiting`, 3 finished/past)
- Recordings: 4 files across the 3 past meetings (MP4/M4A)
- Registrants: 7 across upcoming + past meetings (approved/pending)

## Notes

- Mutations are held in process memory and reset on container restart.
- `userId` accepts the literal `me` or the seeded user id.
- `type` query on the meetings list: `scheduled` -> `waiting` meetings,
  `previous_meetings` -> `finished` meetings.
- Meeting ids are 11-digit numbers; newly created meetings get a random unused id
  and `status = "waiting"`.
- `recordings` returns 404 with code 3301 for meetings that have no recording files.
