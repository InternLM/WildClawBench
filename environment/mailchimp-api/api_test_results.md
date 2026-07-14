# Mailchimp Mock API — Test Results

Base URL: `http://localhost:8081` (in docker-compose: `http://mailchimp-api:8081`)

## Endpoints covered

| Method | Path                                                  | Status  |
|--------|-------------------------------------------------------|---------|
| GET    | /health                                               | 200     |
| GET    | /3.0/lists                                            | 200     |
| GET    | /3.0/lists/{list_id}                                  | 200/404 |
| GET    | /3.0/lists/{list_id}/members                          | 200/404 |
| POST   | /3.0/lists/{list_id}/members                          | 201/400/404 |
| GET    | /3.0/lists/{list_id}/members/{subscriber_hash}        | 200/404 |
| PATCH  | /3.0/lists/{list_id}/members/{subscriber_hash}        | 200/404 |
| GET    | /3.0/campaigns                                         | 200     |
| POST   | /3.0/campaigns                                         | 201/404 |
| GET    | /3.0/campaigns/{id}                                   | 200/404 |
| POST   | /3.0/campaigns/{id}/actions/send                      | 200/400/404 |
| GET    | /3.0/reports/{campaign_id}                            | 200/404 |

## Seed data summary

- Lists / audiences: 2 (`list-newsletter` 5 members, `list-product` 4 members)
- Members: 9 (statuses subscribed / unsubscribed / cleaned)
- Campaigns: 4 (3 sent, 1 draft `camp-nov-draft` with status `save`)
- Reports: 3 (one per sent campaign) with opens/clicks/unsubscribed/bounces

## Notes

- A member's `id` is the `subscriber_hash` = MD5 of the lowercased email.
  `GET`/`PATCH` accept either the hash or the raw email address.
- `POST /campaigns/{id}/actions/send` flips status to `sent`, sets
  `emails_sent` to the audience member count, stamps `send_time`, and seeds an
  empty report. Re-sending an already-sent campaign returns 400.
- `GET /campaigns` and `GET /members` support an optional `status` filter.
- Mutations are held in process memory and reset on container restart.
