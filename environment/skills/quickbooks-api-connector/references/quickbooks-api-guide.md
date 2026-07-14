# QuickBooks Online API v3 Guide

Detailed patterns and examples for working with the QuickBooks Online accounting API.

## Base URL

Set via the `QUICKBOOKS_API_URL` environment variable (e.g. `http://localhost:8007`).
Company realm ID: `4620816365272861350`

## Company Info

```bash
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/companyinfo/1"
```

## Customers

```bash
# Query all customers
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Customer"

# Get single customer
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/customer/1"

# Create customer
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/customer" \
  -H "Content-Type: application/json" \
  -d '{
    "DisplayName": "New Customer LLC",
    "GivenName": "Jane",
    "FamilyName": "Smith",
    "PrimaryEmailAddr": {"Address": "jane@example.com"},
    "PrimaryPhone": {"FreeFormNumber": "(704) 555-9999"}
  }'

# Update customer
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/customer" \
  -H "Content-Type: application/json" \
  -d '{"Id": "1", "DisplayName": "Updated Name", "SyncToken": "0"}'

# Query active customers
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Customer%20WHERE%20Active%20%3D%20true"
```

## Vendors

```bash
# Query all vendors
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Vendor"

# Get single vendor
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/vendor/1"

# Create vendor
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/vendor" \
  -H "Content-Type: application/json" \
  -d '{"DisplayName": "New Vendor Co", "CompanyName": "New Vendor Co"}'

# Update vendor
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/vendor" \
  -H "Content-Type: application/json" \
  -d '{"Id": "1", "DisplayName": "Updated Vendor", "SyncToken": "0"}'
```

## Items (Products/Services)

```bash
# Query all items
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Item"

# Get single item
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/item/1"

# Create item
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/item" \
  -H "Content-Type: application/json" \
  -d '{"Name": "Snow Removal", "Type": "Service", "UnitPrice": 150.00}'

# Update item price
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/item" \
  -H "Content-Type: application/json" \
  -d '{"Id": "1", "UnitPrice": 85.00, "SyncToken": "0"}'
```

## Accounts (Chart of Accounts)

```bash
# Query all accounts
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Account"

# Get single account
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/account/3"
```

## Invoices

```bash
# Query all invoices
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Invoice"

# Query unpaid invoices
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Invoice%20WHERE%20Balance%20%3E%20'0'"

# Query paid invoices
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Invoice%20WHERE%20Status%20%3D%20'Paid'"

# Query overdue invoices
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Invoice%20WHERE%20Status%20%3D%20'Overdue'"

# Get single invoice
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/invoice/1001"

# Get invoice PDF link
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/invoice/1001/pdf"

# Create invoice with line items
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/invoice" \
  -H "Content-Type: application/json" \
  -d '{
    "CustomerRef": {"value": "1", "name": "Mark Thompson"},
    "Line": [
      {
        "Amount": 150.00,
        "DetailType": "SalesItemLineDetail",
        "Description": "Weekly lawn mowing (2 visits)",
        "SalesItemLineDetail": {
          "ItemRef": {"value": "1", "name": "Weekly Lawn Mowing"},
          "UnitPrice": 75.00,
          "Qty": 2
        }
      }
    ],
    "TxnDate": "2025-05-01",
    "DueDate": "2025-05-31"
  }'

# Update invoice due date
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/invoice" \
  -H "Content-Type: application/json" \
  -d '{"Id": "1001", "DueDate": "2025-06-15", "SyncToken": "1"}'

# Void an invoice
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/invoice/1001?operation=void"

# Send invoice via email
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/invoice/1001?include=send"
```

## Bills (Vendor Bills)

```bash
# Query all bills
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Bill"

# Query open/unpaid bills
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Bill%20WHERE%20Balance%20%3E%20'0'"

# Get single bill
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/bill/2001"

# Create bill
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/bill" \
  -H "Content-Type: application/json" \
  -d '{
    "VendorRef": {"value": "1", "name": "Charlotte Fuel Depot"},
    "Line": [
      {
        "Amount": 380.00,
        "DetailType": "AccountBasedExpenseLineDetail",
        "Description": "Diesel fuel - weekly fill",
        "AccountBasedExpenseLineDetail": {
          "AccountRef": {"value": "7", "name": "Fuel Expense"}
        }
      }
    ],
    "TxnDate": "2025-05-01",
    "DueDate": "2025-05-31"
  }'

# Mark bill as paid
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/bill/2001?operation=pay"
```

## Payments

```bash
# Query all payments
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Payment"

# Get single payment
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/payment/3001"

# Record payment against an invoice
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/payment" \
  -H "Content-Type: application/json" \
  -d '{
    "CustomerRef": {"value": "4", "name": "Patricia Nguyen"},
    "TotalAmt": 150.00,
    "Line": [
      {
        "Amount": 150.00,
        "LinkedTxn": [{"TxnId": "1009", "TxnType": "Invoice"}]
      }
    ],
    "TxnDate": "2025-05-01"
  }'
```

## Estimates

```bash
# Query all estimates
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Estimate"

# Get single estimate
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/estimate/4001"

# Create estimate
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/estimate" \
  -H "Content-Type: application/json" \
  -d '{
    "CustomerRef": {"value": "18", "name": "Daniel Harris"},
    "Line": [
      {
        "Amount": 500.00,
        "DetailType": "SalesItemLineDetail",
        "Description": "Spring cleanup and mulching",
        "SalesItemLineDetail": {
          "ItemRef": {"value": "4", "name": "Spring Cleanup"},
          "UnitPrice": 250.00,
          "Qty": 2
        }
      }
    ],
    "TxnDate": "2025-05-01",
    "ExpirationDate": "2025-05-31"
  }'

# Convert estimate to invoice
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/estimate/4004?operation=convert"
```

## Expenses (Purchases)

```bash
# Query all expenses
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Purchase"

# Get single expense
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/purchase/5001"

# Create expense
curl -X POST "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/purchase" \
  -H "Content-Type: application/json" \
  -d '{
    "AccountRef": {"value": "7", "name": "Fuel Expense"},
    "PaymentType": "Cash",
    "Line": [
      {
        "Amount": 45.00,
        "DetailType": "AccountBasedExpenseLineDetail",
        "Description": "Gas for handheld equipment",
        "AccountBasedExpenseLineDetail": {
          "AccountRef": {"value": "7", "name": "Fuel Expense"}
        }
      }
    ],
    "TxnDate": "2025-05-01"
  }'
```

## Reports

```bash
# Profit & Loss with date range
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/reports/ProfitAndLoss?start_date=2025-01-01&end_date=2025-04-30"

# Profit & Loss (all time)
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/reports/ProfitAndLoss"

# Balance Sheet
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/reports/BalanceSheet?start_date=2025-01-01&end_date=2025-04-30"

# Accounts Receivable Aging
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/reports/AgedReceivableDetail"

# Accounts Payable Aging
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/reports/AgedPayableDetail"
```

## Query Endpoint

The query endpoint accepts simplified SQL-like syntax:

```bash
# All invoices
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Invoice"

# Filter by field value
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Invoice%20WHERE%20Status%20%3D%20'Paid'"

# Numeric comparison
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Invoice%20WHERE%20Balance%20%3E%20'0'"

# Boolean filter
curl "$QUICKBOOKS_API_URL/v3/company/4620816365272861350/query?query=SELECT%20*%20FROM%20Customer%20WHERE%20Active%20%3D%20true"
```

Supported entities: `Customer`, `Vendor`, `Item`, `Account`, `Invoice`, `Bill`, `Payment`, `Estimate`, `Purchase`
