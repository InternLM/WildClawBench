# Open Library Mock API — Test Results

Base URL: `http://localhost:8078` (in docker-compose: `http://openlibrary-api:8078`)

## Endpoints covered

| Method | Path                              | Status  |
|--------|-----------------------------------|---------|
| GET    | /health                           | 200     |
| GET    | /search.json                      | 200     |
| GET    | /works/{work_id}.json             | 200/404 |
| GET    | /works/{work_id}/editions.json    | 200/404 |
| GET    | /authors/{author_id}.json         | 200/404 |
| GET    | /authors/{author_id}/works.json   | 200/404 |
| GET    | /subjects/{subject}.json          | 200     |
| GET    | /isbn/{isbn}.json                 | 200/404 |

## Seed data summary

- Authors: 6 (Tolkien, Le Guin, Asimov, Jemisin, Herbert, Butler) with Open Library `OL...A` keys.
- Works: 8 (e.g. `OL893415W` Dune, `OL46125W` Foundation) with title, author, first_publish_year, subjects.
- Editions: 9 with ISBN-13/ISBN-10, publisher, page count, language.
- Subjects: 6 (science_fiction, fantasy, robots, time_travel, magic, adventure).

## Notes

- `/search.json` accepts `q`, `author`, and/or `title`; returns `{numFound, docs: [...]}`
  with Open Library style `key` (`/works/OL...W`) and `author_key`/`author_name`.
- ISBN lookup accepts ISBN-13 or ISBN-10 (hyphens stripped).
- Subjects match against the work `subjects` list with spaces normalized to underscores.
- Mutations are held in process memory and reset on container restart (this mock is read-only).
