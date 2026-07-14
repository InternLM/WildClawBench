# Twilio Mock API — Test Results

Base URL: `http://localhost:8026` (in docker-compose: `http://twilio-api:8026`)

Account SID: `ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

## Endpoints covered

| Method | Path                                                       | Status  |
|--------|------------------------------------------------------------|---------|
| GET    | /health                                                    | 200     |
| GET    | /2010-04-01/Accounts/{AccountSid}/Messages.json            | 200     |
| POST   | /2010-04-01/Accounts/{AccountSid}/Messages.json            | 201/400 |
| GET    | /2010-04-01/Accounts/{AccountSid}/Messages/{Sid}.json      | 200/404 |
| GET    | /2010-04-01/Accounts/{AccountSid}/Calls.json               | 200     |
| POST   | /2010-04-01/Accounts/{AccountSid}/Calls.json               | 201/400 |
| GET    | /2010-04-01/Accounts/{AccountSid}/IncomingPhoneNumbers.json| 200     |
| GET    | /v1/PhoneNumbers/{PhoneNumber}                             | 200     |

## Seed data summary

- Account: 1 (`AC9f4b2e...`, Orbit Labs Messaging)
- Incoming phone numbers: 4 (US support, US marketing, UK, AU)
- Messages: 10 (outbound + inbound; statuses delivered/received/sent/queued/undelivered/failed)
- Calls: 6 (outbound + inbound; completed/no-answer/busy/in-progress)

## Notes

- Mutations are held in process memory and reset on container restart.
- SIDs use Twilio prefixes: messages `SM...`, calls `CA...`, phone numbers `PN...`,
  account `AC...`. New SIDs are generated as `<prefix><uuid4hex>`.
- `create_message` / `create_call` accept `To` / `From` (and `Body`) as query params on
  the POST URL and always return `status = "queued"`.
- List endpoints support optional `To`, `From`, `Status` and `PageSize` filters.
- Lookup returns country code, validity and (if owned) the caller name.
