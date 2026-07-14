# Amadeus Mock API — Test Results

Base URL: `http://localhost:8076` (in docker-compose: `http://amadeus-api:8076`)

## Endpoints covered

| Method | Path                                          | Status  |
|--------|-----------------------------------------------|---------|
| GET    | /health                                       | 200     |
| GET    | /v2/shopping/flight-offers                    | 200     |
| POST   | /v1/shopping/flight-offers/pricing            | 200/400 |
| GET    | /v1/reference-data/locations                  | 200     |
| GET    | /v1/reference-data/locations/{location_id}    | 200/404 |
| GET    | /v1/reference-data/airlines                   | 200     |

## Seed data summary

- Airports: 12 (JFK, LAX, LHR, CDG, FRA, DXB, SIN, NRT, SFO, BOS, ORD, AMS) with IATA code, city, country, lat/lng, timezone.
- Airlines: 10 (AA, DL, UA, BA, AF, LH, EK, SQ, NH, KL).
- Flight offers: 8 routes (e.g. JFK->LHR, LAX->NRT, SFO->SIN) with itineraries, segments (carrier, flightNumber, dep/arr times), price and duration.

## Notes

- `/v2/shopping/flight-offers` filters seeded offers by `originLocationCode`,
  `destinationLocationCode`, and optional `departureDate`; price scales by `adults`.
- Location ids are prefixed: airports `A<IATA>` (e.g. `AJFK`), cities `C<cityCode>`.
- Pricing echoes the seeded offer when a matching `id` is posted, else the posted offer.
- Mutations are held in process memory and reset on container restart.
