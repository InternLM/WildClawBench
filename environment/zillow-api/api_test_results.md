# Zillow Mock API — Test Results

Base URL: `http://localhost:8011` (docker-compose: `http://zillow-api:8011`)

## Endpoints

| Method | Path                                       | Status   |
|--------|--------------------------------------------|----------|
| GET    | /health                                    | 200      |
| GET    | /v1/properties/search                      | 200      |
| GET    | /v1/properties/{zpid}                      | 200/404  |
| GET    | /v1/properties/{zpid}/zestimate            | 200/404  |
| GET    | /v1/properties/{zpid}/price-history        | 200/404  |
| GET    | /v1/agents                                 | 200      |
| GET    | /v1/agents/{agent_id}                      | 200/404  |
| GET    | /v1/users/{user_id}/saved-searches         | 200      |
| POST   | /v1/users/{user_id}/saved-searches         | 201      |
| DELETE | /v1/saved-searches/{search_id}             | 200/404  |

## Seed data

- Properties: 10 (Bellevue / Redmond / Seattle / Issaquah / Kirkland / Mercer Island / Sammamish)
- Price history events: 16
- Agents: 3
- Saved searches: 3
