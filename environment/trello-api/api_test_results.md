# Trello Mock API — Test Results

Base URL: `http://localhost:8030` (in docker-compose: `http://trello-api:8030`)

## Endpoints covered

| Method | Path                              | Status  |
|--------|-----------------------------------|---------|
| GET    | /health                           | 200     |
| GET    | /1/members/me/boards              | 200     |
| GET    | /1/boards/{id}                    | 200/404 |
| GET    | /1/boards/{id}/lists              | 200/404 |
| GET    | /1/lists/{id}/cards               | 200/404 |
| POST   | /1/cards                          | 200/404 |
| PUT    | /1/cards/{id}                     | 200/404 |
| DELETE | /1/cards/{id}                     | 200/404 |
| GET    | /1/cards/{id}/checklists          | 200/404 |
| POST   | /1/checklists                     | 200/404 |

## Seed data summary

- Members: 4 (`me` resolves to Amelia Ortega)
- Boards: 2 (Product Roadmap, Marketing Campaigns)
- Lists: 6 (Product: To Do / Doing / Done; Marketing: Backlog / In Review / Published)
- Cards: 10 distributed across the lists, with members, labels and some due dates
- Checklists: 3 (with check items in complete/incomplete states)

## Notes

- Mutations are held in process memory and reset on container restart.
- Like the real Trello API, write fields are passed as query params
  (e.g. `POST /1/cards?idList=...&name=...`, `PUT /1/cards/{id}?idList=...`).
- `PUT /1/cards/{id}` with `idList` moves a card to another list (and re-homes its
  `idBoard`); `closed=true` archives the card.
- Ids use Trello-style 24-char hex strings; created entities get a fresh random hex id.
- `DELETE /1/cards/{id}` also removes the card's checklists.
