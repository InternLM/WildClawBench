# Slack Web API Mock — Test Results

Base URL: `http://localhost:8013` (docker-compose: `http://slack-api:8013`)

## Method routes

All responses follow Slack's `{"ok": true/false, ...}` envelope convention.

| Method | Path                              | Notes                              |
|--------|-----------------------------------|------------------------------------|
| GET    | /api/auth.test                    | Returns the first admin user       |
| GET    | /api/team.info                    |                                    |
| GET    | /api/users.list                   |                                    |
| GET    | /api/users.info?user=             | `user_not_found` on miss           |
| POST   | /api/users.setPresence            |                                    |
| GET    | /api/conversations.list           | `types`, `exclude_archived` params |
| GET    | /api/conversations.info?channel=  |                                    |
| POST   | /api/conversations.create         | `name_taken` if duplicate          |
| POST   | /api/conversations.archive        |                                    |
| GET    | /api/conversations.members        |                                    |
| POST   | /api/conversations.invite         | Accepts comma-separated `users`    |
| GET    | /api/conversations.history        | `oldest`, `latest`, `limit`        |
| GET    | /api/conversations.replies        |                                    |
| POST   | /api/chat.postMessage             | Pass `thread_ts` to reply          |
| POST   | /api/chat.update                  |                                    |
| POST   | /api/chat.delete                  |                                    |
| POST   | /api/reactions.add                |                                    |
| GET    | /api/search.messages?query=       |                                    |

## Seed data

- Team: `T01CASCADE` (Cascade Engineering)
- Users: 5 humans + 1 bot
- Channels: 4 public, 1 project, 1 private
- Messages: 8 (with reactions and one thread)
