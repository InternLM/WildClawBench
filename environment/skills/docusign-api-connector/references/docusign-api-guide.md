# DocuSign eSignature API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$DOCUSIGN_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `DOCUSIGN_API_URL` | Base URL for all requests |

## Restapi

```bash
curl -s "$DOCUSIGN_API_URL/restapi/v2.1/accounts/<accountId>/envelopes"
curl -s -X POST "$DOCUSIGN_API_URL/restapi/v2.1/accounts/<accountId>/envelopes" -H 'Content-Type: application/json' -d '{}'
curl -s "$DOCUSIGN_API_URL/restapi/v2.1/accounts/<accountId>/envelopes/<envelopeId>"
curl -s -X PUT "$DOCUSIGN_API_URL/restapi/v2.1/accounts/<accountId>/envelopes/<envelopeId>" -H 'Content-Type: application/json' -d '{}'
curl -s "$DOCUSIGN_API_URL/restapi/v2.1/accounts/<accountId>/envelopes/<envelopeId>/recipients"
curl -s "$DOCUSIGN_API_URL/restapi/v2.1/accounts/<accountId>/envelopes/<envelopeId>/documents"
curl -s "$DOCUSIGN_API_URL/restapi/v2.1/accounts/<accountId>/templates"
```

The audit log of every call is available at `$DOCUSIGN_API_URL/audit/requests` (used for grading).
