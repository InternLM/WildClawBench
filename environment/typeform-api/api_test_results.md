# Typeform Mock API — Test Results

Base URL: `http://localhost:8055` (in docker-compose: `http://typeform-api:8055`)

## Endpoints covered

| Method | Path                                   | Status  |
|--------|----------------------------------------|---------|
| GET    | /health                                | 200     |
| GET    | /forms                                 | 200     |
| POST   | /forms                                 | 201     |
| GET    | /forms/{form_id}                       | 200/404 |
| PUT    | /forms/{form_id}                       | 200/404 |
| DELETE | /forms/{form_id}                       | 200/404 |
| GET    | /forms/{form_id}/responses             | 200/404 |
| GET    | /forms/{form_id}/insights/summary      | 200/404 |

## Seed data summary

- Forms: 3 (Customer Satisfaction, Product Onboarding Feedback, Event Registration)
- Fields: 10 across forms (short_text, multiple_choice, rating, email)
- Responses: 7 (all completed) with answers keyed by field
- Answers: 20 across the responses

## Notes

- `GET /forms` returns a lightweight list; `GET /forms/{form_id}` returns the
  full form with ordered `fields` (multiple_choice includes `properties.choices`).
- Answers are serialized in Typeform shape: `text` / `email` / `number` (rating)
  / `choice.label` (multiple_choice), each with its `field` reference.
- `GET /forms/{form_id}/insights/summary` aggregates completion rate, rating
  averages, and multiple_choice answer counts.
- `POST /forms` accepts inline `fields[]`. Mutations are held in process memory
  and reset on container restart.
