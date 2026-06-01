---
name: quickbooks-api-connector
description: >
  QuickBooks Online API v3 HTTP endpoints for accounting operations including
  invoicing, payments, expenses, customers, vendors, and financial reports.
---

# QuickBooks Online API v3

## Base URL

| Variable | Purpose |
|----------|---------|
| `QUICKBOOKS_API_URL` | Base URL for all requests |
| `REALM_ID` | QuickBooks company realm ID |

All paths below are relative to `QUICKBOOKS_API_URL`. Replace `{realmId}` with the company's realm ID.

---

## Health

```
GET /health
```

Returns `{"status": "ok"}`.

---

## Company Info

### Get company info

Returns the full company profile for the specified realm, including company name, legal name, address, email, phone, fiscal year start month, and industry type.

```
GET /v3/company/{realmId}/companyinfo/{companyId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `companyId` | string | path | yes | Company entity ID |

---

## Customers

### Get customer

Returns the full details of a single customer record, including display name, given/family name, company name, email, phone, billing address, active status, balance, notes, and sync token.

```
GET /v3/company/{realmId}/customer/{customerId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `customerId` | string | path | yes | Customer entity ID |

### Create customer

Creates a new customer record. Returns the created customer object with a server-generated `Id` and `SyncToken`. The customer is set to active by default.

```
POST /v3/company/{realmId}/customer
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `DisplayName` | string | yes | Full display name (must be unique) |
| `GivenName` | string | no | First name |
| `FamilyName` | string | no | Last name |
| `CompanyName` | string | no | Company or business name |
| `PrimaryEmailAddr` | object | no | Email as `{"Address": "string"}` |
| `PrimaryPhone` | object | no | Phone as `{"FreeFormNumber": "string"}` |
| `BillAddr` | object | no | Billing address as `{"Line1": "string", "City": "string", "CountrySubDivisionCode": "string", "PostalCode": "string"}` |
| `Active` | boolean | no | Whether the customer is active. Default: `true` |
| `Notes` | string | no | Free-text notes |

### Update customer

Updates an existing customer record. Requires the `Id` and current `SyncToken` in the request body. Only the fields included in the body are modified. Returns the updated customer with an incremented `SyncToken`.

```
POST /v3/company/{realmId}/customer
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Id` | string | yes | Customer entity ID (presence indicates update) |
| `SyncToken` | string | yes | Concurrency control token from the existing record |
| `DisplayName` | string | no | Updated display name |
| `GivenName` | string | no | Updated first name |
| `FamilyName` | string | no | Updated last name |
| `CompanyName` | string | no | Updated company name |
| `PrimaryEmailAddr` | object | no | Updated email |
| `PrimaryPhone` | object | no | Updated phone |
| `BillAddr` | object | no | Updated billing address |
| `Active` | boolean | no | Updated active status |
| `Notes` | string | no | Updated notes |

---

## Vendors

### Get vendor

Returns the full details of a single vendor record, including display name, company name, email, phone, billing address, account number, 1099 eligibility flag, active status, balance, and sync token.

```
GET /v3/company/{realmId}/vendor/{vendorId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `vendorId` | string | path | yes | Vendor entity ID |

### Create or update vendor

Creates a new vendor if no `Id` is present in the body; updates an existing vendor if `Id` and `SyncToken` are provided. Returns the vendor object.

```
POST /v3/company/{realmId}/vendor
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Id` | string | no | Vendor ID (include for update, omit for create) |
| `SyncToken` | string | no | Required for update |
| `DisplayName` | string | yes (create) | Full display name (must be unique) |
| `GivenName` | string | no | First name |
| `FamilyName` | string | no | Last name |
| `CompanyName` | string | no | Company name |
| `PrimaryEmailAddr` | object | no | Email as `{"Address": "string"}` |
| `PrimaryPhone` | object | no | Phone as `{"FreeFormNumber": "string"}` |
| `BillAddr` | object | no | Billing address |
| `AcctNum` | string | no | Vendor account number |
| `Vendor1099` | boolean | no | Whether vendor receives 1099 forms |
| `Active` | boolean | no | Whether the vendor is active |
| `Notes` | string | no | Free-text notes |

---

## Items

### Get item

Returns the full details of a product or service item, including name, description, type, unit price, income account reference, active status, taxable flag, and sync token.

```
GET /v3/company/{realmId}/item/{itemId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `itemId` | string | path | yes | Item entity ID |

### Create or update item

Creates a new product/service item if no `Id` is present; updates an existing item if `Id` and `SyncToken` are provided. Returns the item object.

```
POST /v3/company/{realmId}/item
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Id` | string | no | Item ID (include for update, omit for create) |
| `SyncToken` | string | no | Required for update |
| `Name` | string | yes (create) | Item name |
| `Description` | string | no | Item description |
| `Type` | string | no | Item type: `Service`, `Inventory`, `NonInventory` |
| `UnitPrice` | number | no | Default unit price |
| `IncomeAccountRef` | object | no | Income account as `{"value": "id", "name": "display name"}` |
| `Active` | boolean | no | Whether the item is active |
| `Taxable` | boolean | no | Whether the item is taxable |

---

## Accounts

### Get account

Returns the details of a single chart of accounts entry, including account name, type, sub-type, current balance, and classification.

```
GET /v3/company/{realmId}/account/{accountId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `accountId` | string | path | yes | Account entity ID |

---

## Invoices

### Get invoice

Returns the full details of a single invoice, including customer reference, line items, dates, amounts, balance, email/print status, and sync token.

```
GET /v3/company/{realmId}/invoice/{invoiceId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `invoiceId` | string | path | yes | Invoice entity ID |

### Get invoice PDF

Returns the invoice rendered as a PDF document.

```
GET /v3/company/{realmId}/invoice/{invoiceId}/pdf
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `invoiceId` | string | path | yes | Invoice entity ID |

### Create or update invoice

Creates a new invoice if no `Id` is present; updates an existing invoice if `Id` and `SyncToken` are provided. Line items use a `DetailType` discriminator to determine line structure. Returns the invoice object.

```
POST /v3/company/{realmId}/invoice
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Id` | string | no | Invoice ID (include for update) |
| `SyncToken` | string | no | Required for update |
| `CustomerRef` | object | yes (create) | Customer as `{"value": "id", "name": "display name"}` |
| `Line` | array | yes (create) | Array of line items. Each: `{"Amount": number, "DetailType": "SalesItemLineDetail", "Description": "string", "SalesItemLineDetail": {"ItemRef": {"value": "id", "name": "name"}, "UnitPrice": number, "Qty": number}}` |
| `TxnDate` | string | no | Transaction date (YYYY-MM-DD) |
| `DueDate` | string | no | Payment due date (YYYY-MM-DD) |
| `BillEmail` | object | no | Email address as `{"Address": "string"}` |
| `PrintStatus` | string | no | Print status |
| `EmailStatus` | string | no | Email status |

### Void invoice

Voids an existing invoice, zeroing out its balance while preserving the transaction record for audit purposes.

```
POST /v3/company/{realmId}/invoice/{invoiceId}?operation=void
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `invoiceId` | string | path | yes | Invoice entity ID |

### Send invoice

Sends the invoice to the customer via email. The invoice's `EmailStatus` is updated to reflect the send action.

```
POST /v3/company/{realmId}/invoice/{invoiceId}?include=send
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `invoiceId` | string | path | yes | Invoice entity ID |

---

## Bills

### Get bill

Returns the full details of a vendor bill, including vendor reference, line items, transaction date, due date, document number, balance, and sync token.

```
GET /v3/company/{realmId}/bill/{billId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `billId` | string | path | yes | Bill entity ID |

### Create bill

Creates a new vendor bill. Line items use `AccountBasedExpenseLineDetail` to specify the expense account. Returns the created bill object.

```
POST /v3/company/{realmId}/bill
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `VendorRef` | object | yes | Vendor as `{"value": "id", "name": "display name"}` |
| `Line` | array | yes | Array of line items. Each: `{"Amount": number, "DetailType": "AccountBasedExpenseLineDetail", "Description": "string", "AccountBasedExpenseLineDetail": {"AccountRef": {"value": "id", "name": "name"}}}` |
| `TxnDate` | string | no | Transaction date (YYYY-MM-DD) |
| `DueDate` | string | no | Payment due date (YYYY-MM-DD) |
| `DocNumber` | string | no | Document/reference number |

### Pay bill

Records a payment against an existing bill. Reduces the bill's outstanding balance.

```
POST /v3/company/{realmId}/bill/{billId}?operation=pay
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `billId` | string | path | yes | Bill entity ID |

---

## Payments

### Get payment

Returns the full details of a customer payment, including customer reference, total amount, linked transactions (invoices), transaction date, and sync token.

```
GET /v3/company/{realmId}/payment/{paymentId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `paymentId` | string | path | yes | Payment entity ID |

### Create payment

Records a customer payment. Payments can be linked to one or more invoices via the `Line` array. The payment reduces the outstanding balance on the linked invoices.

```
POST /v3/company/{realmId}/payment
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `CustomerRef` | object | yes | Customer as `{"value": "id", "name": "display name"}` |
| `TotalAmt` | number | yes | Total payment amount |
| `Line` | array | no | Linked transactions. Each: `{"Amount": number, "LinkedTxn": [{"TxnId": "id", "TxnType": "Invoice"}]}` |
| `TxnDate` | string | no | Payment date (YYYY-MM-DD) |

---

## Estimates

### Get estimate

Returns the full details of a customer estimate/quote, including customer reference, line items, transaction date, expiration date, total amount, and status.

```
GET /v3/company/{realmId}/estimate/{estimateId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `estimateId` | string | path | yes | Estimate entity ID |

### Create estimate

Creates a new estimate/quote for a customer. The estimate can later be converted to an invoice. Returns the created estimate object.

```
POST /v3/company/{realmId}/estimate
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `CustomerRef` | object | yes | Customer as `{"value": "id", "name": "display name"}` |
| `Line` | array | yes | Line items (same structure as invoice lines) |
| `TxnDate` | string | no | Estimate date (YYYY-MM-DD) |
| `ExpirationDate` | string | no | Estimate expiration date (YYYY-MM-DD) |

### Convert estimate to invoice

Converts an accepted estimate into an invoice. The new invoice inherits the estimate's customer, line items, and amounts. Returns the created invoice object.

```
POST /v3/company/{realmId}/estimate/{estimateId}?operation=convert
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `estimateId` | string | path | yes | Estimate entity ID |

---

## Expenses

### Get expense

Returns the full details of a purchase/expense record, including the payment account, payment type, line items, transaction date, total amount, and sync token.

```
GET /v3/company/{realmId}/purchase/{purchaseId}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `purchaseId` | string | path | yes | Purchase entity ID |

### Create expense

Records a new expense/purchase transaction. Line items specify the accounts to which the expense is charged. Returns the created purchase object.

```
POST /v3/company/{realmId}/purchase
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `AccountRef` | object | yes | Payment account as `{"value": "id", "name": "display name"}` |
| `PaymentType` | string | yes | Payment method: `Cash`, `Check`, `CreditCard` |
| `Line` | array | yes | Line items. Each: `{"Amount": number, "DetailType": "AccountBasedExpenseLineDetail", "Description": "string", "AccountBasedExpenseLineDetail": {"AccountRef": {"value": "id", "name": "name"}}}` |
| `TxnDate` | string | no | Transaction date (YYYY-MM-DD) |

---

## Query

### Query entities

Executes a SQL-like query against the specified entity type. Supports `SELECT`, `WHERE`, `ORDER BY`, and comparison operators. Returns a `QueryResponse` object containing the matched entities, start position, max results, and total count.

```
GET /v3/company/{realmId}/query
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `query` | string | query | yes | SQL-like query string. Supported entities: `Customer`, `Vendor`, `Item`, `Account`, `Invoice`, `Bill`, `Payment`, `Estimate`, `Purchase` |

Query syntax examples:
- `SELECT * FROM Invoice`
- `SELECT * FROM Customer WHERE Active = true`
- `SELECT * FROM Invoice WHERE Balance > '0'`
- `SELECT * FROM Invoice WHERE Status = 'Overdue'`

---

## Reports

### Profit and Loss report

Returns a profit and loss (income statement) report for the specified date range. The report includes income, cost of goods sold, gross profit, expenses, and net income broken down by account.

```
GET /v3/company/{realmId}/reports/ProfitAndLoss
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `start_date` | string | query | no | Report start date (YYYY-MM-DD) |
| `end_date` | string | query | no | Report end date (YYYY-MM-DD) |

### Balance Sheet report

Returns a balance sheet report as of the specified date range. The report includes assets, liabilities, and equity broken down by account with current balances.

```
GET /v3/company/{realmId}/reports/BalanceSheet
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |
| `start_date` | string | query | no | Report start date (YYYY-MM-DD) |
| `end_date` | string | query | no | Report end date (YYYY-MM-DD) |

### Aged Receivable Detail report

Returns an aged accounts receivable detail report. Lists all outstanding customer invoices grouped by aging bucket (current, 1-30, 31-60, 61-90, 91+ days past due).

```
GET /v3/company/{realmId}/reports/AgedReceivableDetail
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |

### Aged Payable Detail report

Returns an aged accounts payable detail report. Lists all outstanding vendor bills grouped by aging bucket (current, 1-30, 31-60, 61-90, 91+ days past due).

```
GET /v3/company/{realmId}/reports/AgedPayableDetail
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `realmId` | string | path | yes | Company realm ID |

---

## General Conventions

- All entity endpoints follow the pattern: `/v3/company/{realmId}/{entityName}`
- Field names use PascalCase: `TxnDate`, `TotalAmt`, `DueDate`, `DocNumber`
- Reference fields follow the pattern `{Name}Ref` with structure `{"value": "id", "name": "display name"}`
- Create and update use the same `POST` path — the presence of `Id` in the body indicates an update
- Single read response: `{"Entity": {…}}`
- Query response: `{"QueryResponse": {"Entity": [...], "startPosition": N, "maxResults": N, "totalCount": N}}`
- Line items use a `Line` array with `DetailType` discriminator (`SalesItemLineDetail` for sales, `AccountBasedExpenseLineDetail` for expenses)

---

## Errors

Error responses follow this format:

```json
{
  "Fault": {
    "Error": [{"Message": "Description of the error", "code": "6240"}],
    "type": "ValidationFault"
  }
}
```

Common HTTP status codes:

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid parameters or malformed body) |
| 404 | Resource not found |
| 409 | Stale object (SyncToken mismatch) |
