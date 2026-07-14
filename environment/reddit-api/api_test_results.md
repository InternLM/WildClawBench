# Reddit Mock API — Test Results

Base URL: `http://localhost:8058` (in docker-compose: `http://reddit-api:8058`)

## Endpoints covered

| Method | Path                        | Status |
|--------|-----------------------------|--------|
| GET    | /health                     | 200    |
| GET    | /r/{subreddit}/about        | 200/404 |
| GET    | /r/{subreddit}/hot          | 200/404 |
| GET    | /r/{subreddit}/new          | 200/404 |
| GET    | /comments/{post_id}         | 200/404 |
| POST   | /api/submit                 | 200/400 |
| POST   | /api/vote                   | 200/400/404 |
| GET    | /user/{username}/about      | 200/404 |

## Seed data summary

- Subreddits: 3 (`programming`, `homelab`, `gardening`), fullnames `t5_*`.
- Posts: 6 link/self posts with scores, fullnames `t3_*`.
- Comments: 11 across the posts, threaded via `parent_id`, fullnames `t1_*`.
- Users: 6 accounts with link/comment karma, fullnames `t2_*`.

## Notes

- Listings use the standard envelope `{"kind":"Listing","data":{"children":[{"kind":"t3","data":{...}}]}}`.
- `/comments/{post_id}` returns a two-element array: `[post Listing (t3), comment Listing (t1)]`.
- `/r/.../hot` sorts by score; `/r/.../new` sorts by `created_utc` descending.
- `/api/vote` `dir` of `1`/`-1`/`0` adjusts the thing's score relative to the prior vote
  (per-process); a fresh upvote on a seed post adds +1.
- `/api/submit` `kind` of `self` uses `text`; `link` uses `url`. New posts start at score 1.
- Mutations are held in process memory and reset on container restart.
