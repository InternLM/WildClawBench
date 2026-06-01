# Gusto Payroll API Mock — Test Results

Base URL: `http://localhost:8074` (in docker-compose: `http://gusto-api:8074`)

## Endpoints covered

| Method | Path                                          | Status  |
|--------|-----------------------------------------------|---------|
| GET    | /health                                       | 200     |
| GET    | /v1/companies/{company_id}                    | 200/404 |
| GET    | /v1/companies/{company_id}/employees          | 200/404 |
| GET    | /v1/employees/{id}                            | 200/404 |
| GET    | /v1/companies/{company_id}/payrolls           | 200/404 |
| GET    | /v1/payrolls/{id}                             | 200/404 |
| POST   | /v1/companies/{company_id}/payrolls           | 201/404/400 |
| PUT    | /v1/payrolls/{id}/submit                      | 200/404/400 |
| GET    | /v1/companies/{company_id}/contractors        | 200/404 |

## Seed data summary

- Company: Orbit Labs Inc. (`comp-001`), semimonthly pay schedule
- Employees: 8 (with linked compensation rate + payment_unit)
- Compensations: 8 (Year salaries and one Hourly)
- Payrolls: 4 (3 processed with gross/net totals, 1 unprocessed `pay-404`)
- Contractors: 4 (2 individuals hourly, 2 businesses fixed)

## Notes

- `GET /v1/companies/{company_id}/employees` embeds each employee's compensation.
- `POST /v1/companies/{company_id}/payrolls` creates an unprocessed payroll draft.
- `PUT /v1/payrolls/{id}/submit` computes gross pay from a semimonthly slice of
  each active employee's annual/hourly comp and sets net pay at ~72.6% of gross;
  resubmitting an already-processed payroll returns 400.
- `payrolls` list supports a `processed` boolean filter.
- Mutations are held in process memory and reset on container restart.
