# PagerDuty API (Mock) Guide

Worked `curl` examples for every endpoint. **All requests target the base URL in `$PAGERDUTY_API_URL`.** Auth headers are mocked (any token is accepted) and responses are deterministic fixtures.

## Base URL

| Variable | Purpose |
|----------|---------|
| `PAGERDUTY_API_URL` | Base URL for all requests |

## Escalation_Policies

```bash
curl -s "$PAGERDUTY_API_URL/escalation_policies"
```

## Incidents

```bash
curl -s "$PAGERDUTY_API_URL/incidents"
curl -s "$PAGERDUTY_API_URL/incidents/<incident_id>"
curl -s -X POST "$PAGERDUTY_API_URL/incidents" -H 'Content-Type: application/json' -d '{}'
curl -s -X PUT "$PAGERDUTY_API_URL/incidents/<incident_id>" -H 'Content-Type: application/json' -d '{}'
curl -s "$PAGERDUTY_API_URL/incidents/<incident_id>/notes"
curl -s -X POST "$PAGERDUTY_API_URL/incidents/<incident_id>/notes" -H 'Content-Type: application/json' -d '{}'
```

## Oncalls

```bash
curl -s "$PAGERDUTY_API_URL/oncalls"
```

## Schedules

```bash
curl -s "$PAGERDUTY_API_URL/schedules"
```

## Services

```bash
curl -s "$PAGERDUTY_API_URL/services"
curl -s "$PAGERDUTY_API_URL/services/<service_id>"
```

## Users

```bash
curl -s "$PAGERDUTY_API_URL/users"
```

The audit log of every call is available at `$PAGERDUTY_API_URL/audit/requests` (used for grading).
