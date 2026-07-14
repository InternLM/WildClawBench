# Gmail API Mock — Test Results

Base URL: `http://localhost:8017` (docker-compose: `http://gmail-api:8017`)

## Endpoints

| Method | Path                                              | Status   |
|--------|---------------------------------------------------|----------|
| GET    | /health                                           | 200      |
| GET    | /gmail/v1/users/me/profile                        | 200      |
| GET    | /gmail/v1/users/me/labels                         | 200      |
| GET    | /gmail/v1/users/me/labels/{label_id}              | 200/404  |
| POST   | /gmail/v1/users/me/labels                         | 201/409  |
| GET    | /gmail/v1/users/me/messages                       | 200      |
| GET    | /gmail/v1/users/me/messages/{id}                  | 200/404  |
| POST   | /gmail/v1/users/me/messages/send                  | 201      |
| POST   | /gmail/v1/users/me/messages/{id}/modify           | 200/404  |
| POST   | /gmail/v1/users/me/messages/{id}/trash            | 200/404  |
| DELETE | /gmail/v1/users/me/messages/{id}                  | 200/404  |
| GET    | /gmail/v1/users/me/threads                        | 200      |
| GET    | /gmail/v1/users/me/threads/{id}                   | 200/404  |
| GET    | /gmail/v1/users/me/drafts                         | 200      |
| GET    | /gmail/v1/users/me/drafts/{id}                    | 200/404  |
| POST   | /gmail/v1/users/me/drafts                         | 201      |
| POST   | /gmail/v1/users/me/drafts/{id}/send               | 200/404  |

## Search query operators

- `from:`, `to:`, `subject:`, `label:` (by display name), `is:unread`, `is:starred`
- Bare keywords match against subject, body, and snippet.

## Seed data

- 7 messages across 6 threads (INBOX, SENT, SPAM, with system and user labels)
- 1 draft
- 8 labels (5 system + 3 user)
