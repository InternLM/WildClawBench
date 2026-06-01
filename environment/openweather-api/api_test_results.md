# OpenWeather Mock API — Test Results

Base URL: `http://localhost:8035` (in docker-compose: `http://openweather-api:8035`)

## Endpoints covered

| Method | Path                   | Status      |
|--------|------------------------|-------------|
| GET    | /health                | 200         |
| GET    | /data/2.5/weather      | 200/400/404 |
| GET    | /data/2.5/forecast     | 200/400/404 |
| GET    | /geo/1.0/direct        | 200         |

## Seed data summary

- Cities: 6 (New York, London, Paris, Tokyo, Sydney, Chicago) with id, country,
  lat/lon, and timezone offset.
- Current weather: one record per city (temp, feels_like, humidity, pressure,
  wind, clouds, visibility, weather main/description/icon).
- Forecast: 4 three-hourly rows per city (24 total) with temp, humidity, wind,
  weather, and precipitation probability (`pop`).

## Notes

- `/data/2.5/weather` accepts `q=City` (or `q=City,CC`) or `lat`+`lon`; missing
  both returns cod 400, an unknown city returns cod 404.
- Coordinate lookups snap to the nearest seeded city.
- `/data/2.5/forecast` returns a `list` of 3-hourly entries plus a `city` block.
- Responses follow OpenWeather shapes (`weather[]`, `main`, `wind`, `clouds`,
  `name`, `cod`).
- `/geo/1.0/direct` resolves a city name to lat/lon entries.
- This service is read-only; no mutations.
