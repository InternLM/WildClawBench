# DocuSign Mock API — Test Results

Base URL: `http://localhost:8053` (in docker-compose: `http://docusign-api:8053`)

All envelope routes are namespaced under `/restapi/v2.1/accounts/{accountId}/...`.

## Endpoints covered

| Method | Path                                              | Status  |
|--------|---------------------------------------------------|---------|
| GET    | /health                                           | 200     |
| GET    | /envelopes                                         | 200     |
| POST   | /envelopes                                         | 201     |
| GET    | /envelopes/{envelopeId}                            | 200/404 |
| PUT    | /envelopes/{envelopeId}                            | 200/404 |
| GET    | /envelopes/{envelopeId}/recipients                | 200/404 |
| GET    | /envelopes/{envelopeId}/documents                 | 200/404 |
| GET    | /templates                                         | 200     |

## Seed data summary

- Envelopes: 5 (sent, delivered, completed, voided, completed)
- Recipients: 9 signers with routingOrder + status (sent / delivered / completed)
- Documents: 6 across the envelopes
- Templates: 3 (MSA, Mutual NDA, Vendor Onboarding)

## Notes

- `accountId` is accepted as a path segment but not validated (any value works).
- `POST /envelopes` accepts `recipients.signers[]` and `documents[]`; status
  `sent` stamps `sentDateTime`. Returns `{envelopeId, status, uri}`.
- `PUT /envelopes/{envelopeId}` updates status (e.g. `voided` / `sent`);
  `completed` stamps `completedDateTime`.
- Mutations are held in process memory and reset on container restart.
