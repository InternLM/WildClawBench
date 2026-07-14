# WordPress Mock REST API (wp/v2) — Test Results

Base URL: `http://localhost:8065` (in docker-compose: `http://wordpress-api:8065`)

## Endpoints covered

| Method | Path                              | Status |
|--------|-----------------------------------|--------|
| GET    | /health                           | 200    |
| GET    | /wp-json/wp/v2/posts              | 200    |
| POST   | /wp-json/wp/v2/posts              | 201    |
| GET    | /wp-json/wp/v2/posts/{id}         | 200/404 |
| PUT    | /wp-json/wp/v2/posts/{id}         | 200/404 |
| DELETE | /wp-json/wp/v2/posts/{id}         | 200/404 |
| GET    | /wp-json/wp/v2/pages              | 200    |
| GET    | /wp-json/wp/v2/categories         | 200    |
| GET    | /wp-json/wp/v2/tags               | 200    |
| GET    | /wp-json/wp/v2/comments           | 200    |
| POST   | /wp-json/wp/v2/comments           | 201/404 |
| GET    | /wp-json/wp/v2/media              | 200    |
| GET    | /wp-json/wp/v2/users              | 200    |

## Seed data summary

- Posts: 8 (6 published, 2 drafts) with categories and tags.
- Pages: 4 (About, Contact, Privacy Policy, Engineering Team).
- Categories: 5 (Engineering with Reliability/Frontend children, Announcements, Tutorials).
- Tags: 6 (python, rust, kubernetes, accessibility, release, observability).
- Comments: 7 (6 approved including one reply, 1 held as spam).
- Media: 6 attachments; Users: 5 (admin/editor/author/contributor roles).

## Notes

- Mutations are held in process memory and reset on container restart.
- Text fields use the WordPress `{"rendered": "..."}` shape for `title`,
  `content`, `excerpt`, and comment `content`.
- `GET /wp-json/wp/v2/posts` defaults to `status=publish`; pass `status=draft`
  to fetch drafts, plus optional `author`, `categories`, `search`, `per_page`.
- `GET /wp-json/wp/v2/comments` defaults to `status=approved`; the held spam
  comment only appears with `status=hold`.
- Not-found responses include a WordPress-style `code` (e.g. `rest_post_invalid_id`).
