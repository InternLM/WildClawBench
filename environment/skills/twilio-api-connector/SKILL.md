---
name: twilio-api-connector
description: >
  Twilio API (Mock) mock HTTP API. Base URL is provided via the
  `TWILIO_API_URL` environment variable. 7 endpoint(s) across GET, POST.
metadata: {"clawdbot":{"emoji":"🔌"}}
---

# Twilio API (Mock)

Mock HTTP API. **All requests go to the base URL in `$TWILIO_API_URL`.** Auth headers
are mocked (any token is accepted). Responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TWILIO_API_URL` | Base URL for all requests (e.g. `http://twilio-api:8026`) |

## Endpoints

| Method | Path |
|--------|------|
| GET | `/2010-04-01/Accounts/{account_sid}/Messages.json` |
| GET | `/2010-04-01/Accounts/{account_sid}/Messages/{sid}.json` |
| POST | `/2010-04-01/Accounts/{account_sid}/Messages.json` |
| GET | `/2010-04-01/Accounts/{account_sid}/Calls.json` |
| POST | `/2010-04-01/Accounts/{account_sid}/Calls.json` |
| GET | `/2010-04-01/Accounts/{account_sid}/IncomingPhoneNumbers.json` |
| GET | `/v1/PhoneNumbers/{phone_number}` |

## Usage

```bash
# GET example
curl -s "$TWILIO_API_URL/2010-04-01/Accounts/{account_sid}/Messages.json"

# POST example
curl -s -X POST "$TWILIO_API_URL/2010-04-01/Accounts/{account_sid}/Messages.json" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call the agent makes is available at
`$TWILIO_API_URL/audit/requests` (used for grading).
