# Ticketmaster Discovery API Mock — Test Results

Base URL: `http://localhost:8075` (in docker-compose: `http://ticketmaster-api:8075`)

## Endpoints covered

| Method | Path                                    | Status  |
|--------|-----------------------------------------|---------|
| GET    | /health                                 | 200     |
| GET    | /discovery/v2/events                    | 200     |
| GET    | /discovery/v2/events/{id}               | 200/404 |
| GET    | /discovery/v2/venues                    | 200     |
| GET    | /discovery/v2/venues/{id}               | 200/404 |
| GET    | /discovery/v2/attractions               | 200     |
| GET    | /discovery/v2/attractions/{id}          | 200/404 |
| GET    | /discovery/v2/classifications           | 200     |

## Seed data summary

- Events: 10 (music / sports / arts; each with start date, price range, linked venue + attraction)
- Venues: 6 (NY, SF, Chicago, LA, Austin, Seattle)
- Attractions: 7 (bands, musicians, teams, theatre, comedian)
- Classifications: 7 (Music: Rock/Pop/Jazz; Sports: Basketball/Soccer; Arts & Theatre: Theatre/Comedy)

## Notes

- List endpoints return the `{"_embedded": {<key>: [...]}, "page": {...}}` shape.
  Single-item GETs return the object directly.
- `/discovery/v2/events` supports `keyword`, `city`, `classificationName`
  (matches segment / genre / subgenre), and `startDateTime` (events at or after).
- Each event embeds its venue + attraction under `_embedded` and carries a
  `priceRanges` entry and `classifications`.
- Data is read-only; no mutating endpoints in this service.
