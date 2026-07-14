# Twilio API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$TWILIO_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `TWILIO_API_URL` | Base URL for all requests |

## 2010 04 01

```bash
curl -s "$TWILIO_API_URL/2010-04-01/Accounts/<account_sid>/Messages.json"
curl -s "$TWILIO_API_URL/2010-04-01/Accounts/<account_sid>/Messages/<sid>.json"
curl -s -X POST "$TWILIO_API_URL/2010-04-01/Accounts/<account_sid>/Messages.json" -H 'Content-Type: application/json' -d '{}'
curl -s "$TWILIO_API_URL/2010-04-01/Accounts/<account_sid>/Calls.json"
curl -s -X POST "$TWILIO_API_URL/2010-04-01/Accounts/<account_sid>/Calls.json" -H 'Content-Type: application/json' -d '{}'
curl -s "$TWILIO_API_URL/2010-04-01/Accounts/<account_sid>/IncomingPhoneNumbers.json"
```

## Phonenumbers

```bash
curl -s "$TWILIO_API_URL/v1/PhoneNumbers/<phone_number>"
```

The audit log of every call is available at `$TWILIO_API_URL/audit/requests` (used for grading).
