# Plaid API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$PLAID_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `PLAID_API_URL` | Base URL for all requests |

## Accounts

```bash
curl -s -X POST "$PLAID_API_URL/accounts/get" -H 'Content-Type: application/json' -d '{}'
curl -s -X POST "$PLAID_API_URL/accounts/balance/get" -H 'Content-Type: application/json' -d '{}'
```

## Identity

```bash
curl -s -X POST "$PLAID_API_URL/identity/get" -H 'Content-Type: application/json' -d '{}'
```

## Institutions

```bash
curl -s -X POST "$PLAID_API_URL/institutions/get_by_id" -H 'Content-Type: application/json' -d '{}'
```

## Transactions

```bash
curl -s -X POST "$PLAID_API_URL/transactions/get" -H 'Content-Type: application/json' -d '{}'
```

The audit log of every call is available at `$PLAID_API_URL/audit/requests` (used for grading).
