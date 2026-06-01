---
name: docusign-api-connector
description: >
  DocuSign eSignature API (Mock) mock HTTP API. Base URL is provided via the
  `DOCUSIGN_API_URL` environment variable. 7 endpoint(s) across GET, POST, PUT.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# DocuSign eSignature API (Mock)

Mock HTTP API. **All requests go to the base URL in `$DOCUSIGN_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `DOCUSIGN_API_URL` | Base URL for all requests (e.g. `http://docusign-api:8053`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/restapi/v2.1/accounts/{accountId}/envelopes` |
| POST | `/restapi/v2.1/accounts/{accountId}/envelopes` |
| GET | `/restapi/v2.1/accounts/{accountId}/envelopes/{envelopeId}` |
| PUT | `/restapi/v2.1/accounts/{accountId}/envelopes/{envelopeId}` |
| GET | `/restapi/v2.1/accounts/{accountId}/envelopes/{envelopeId}/recipients` |
| GET | `/restapi/v2.1/accounts/{accountId}/envelopes/{envelopeId}/documents` |
| GET | `/restapi/v2.1/accounts/{accountId}/templates` |

## Usage

```bash
# GET example
curl -s "$DOCUSIGN_API_URL/restapi/v2.1/accounts/{accountId}/envelopes"

# POST example
curl -s -X POST "$DOCUSIGN_API_URL/restapi/v2.1/accounts/{accountId}/envelopes" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$DOCUSIGN_API_URL/audit/requests` (used for grading).
