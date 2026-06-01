# Salesforce REST Mock API — Test Results

Base URL: `http://localhost:8044` (in docker-compose: `http://salesforce-api:8044`)
All paths are prefixed with `/services/data/v59.0`.

## Endpoints covered

| Method | Path                                           | Status  |
|--------|------------------------------------------------|---------|
| GET    | /health                                        | 200     |
| GET    | /sobjects/{sObject}                            | 200/404 |
| GET    | /sobjects/{sObject}/{id}                       | 200/404 |
| POST   | /sobjects/{sObject}                            | 201/404 |
| PATCH  | /sobjects/{sObject}/{id}                       | 204/404 |
| GET    | /query?q=<SOQL>                                | 200/400/404 |

`{sObject}` is one of `Account`, `Contact`, `Lead`, `Opportunity`.

## Seed data summary

- Accounts: 5 (Retail, Technology, Manufacturing, Healthcare, Transportation)
- Contacts: 8 (linked to accounts via `AccountId`)
- Leads: 5 (mixed statuses and ratings)
- Opportunities: 6 across stages (Prospecting, Proposal/Price Quote,
  Negotiation/Review, Qualification, Closed Won, Closed Lost)

## Notes

- IDs use Salesforce-style 18-character identifiers (e.g. `001Ax000001AAAAAA1`),
  with object key-prefixes 001=Account, 003=Contact, 00Q=Lead, 006=Opportunity.
- Mutations are held in process memory and reset on container restart.
- `POST` accepts either a flat field object (`{"Name": "..."}`) or
  `{"fields": {...}}`; it returns `{"id", "success", "errors"}`.
- `PATCH` returns HTTP 204 No Content on success (Salesforce convention).
- The `/query` endpoint supports a simplified SOQL grammar:
  `SELECT <fields|*> FROM <Object> [WHERE <field> = '<value>']`.
- Unknown sObject types return 404; malformed SOQL returns 400.
