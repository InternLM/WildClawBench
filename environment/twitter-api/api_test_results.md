# Twitter/X Mock API v2 — Test Results

Base URL: `http://localhost:8061` (in docker-compose: `http://twitter-api:8061`)

## Endpoints covered

| Method | Path                                  | Status |
|--------|---------------------------------------|--------|
| GET    | /health                               | 200    |
| GET    | /2/users/me                           | 200    |
| GET    | /2/users/{id}                         | 200/404 |
| GET    | /2/users/by/username/{username}       | 200/404 |
| GET    | /2/users/{id}/tweets                  | 200/404 |
| GET    | /2/users/{id}/followers               | 200/404 |
| GET    | /2/users/{id}/following               | 200/404 |
| GET    | /2/tweets                             | 200    |
| GET    | /2/tweets/{id}                        | 200/404 |
| POST   | /2/tweets                             | 201/400 |
| DELETE | /2/tweets/{id}                        | 200/404 |
| GET    | /2/tweets/search/recent               | 200    |
| POST   | /2/users/{id}/likes                   | 200/404 |
| POST   | /2/users/{id}/retweets                | 200/404 |

## Seed data summary

- Users: 6 (maya_dev, orbit_labs, jonas_p, helena_park, rohit_b, noor_codes). The authenticated "me" user is `2001` (maya_dev).
- Tweets: 10 (including one reply `3007` -> `3005`); each carries `public_metrics` (like/retweet/reply/quote counts).
- Follows: 12 follower/following edges.
- Likes: 6 seed likes; Retweets: 4 seed retweets.

## Notes

- Mutations are held in process memory and reset on container restart.
- Responses follow the v2 envelope: single objects under `data`, collections under `data` with a `meta.result_count`.
- `GET /2/users/me` returns user `2001`.
- `POST /2/tweets` accepts `text`, optional `author_id` (defaults to `me`) and `reply_to_tweet_id`; replying bumps the parent's `reply_count`.
- Likes/retweets are idempotent and increment the target tweet's `public_metrics`.
- `search/recent` does a case-insensitive substring match on tweet text.
