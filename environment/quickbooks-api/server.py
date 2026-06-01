"""FastAPI server wrapping quickbooks_data module as REST endpoints."""

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

import quickbooks_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="QuickBooks Online API (Mock)", version="3.0")
install_tracker(app)

REALM_ID = quickbooks_data.REALM_ID


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Company Info ---

@app.get("/v3/company/{realm_id}/companyinfo/{company_id}")
def get_company_info(realm_id: str, company_id: str):
    return quickbooks_data.get_company_info()


# --- Customers ---

@app.get("/v3/company/{realm_id}/customer/{customer_id}")
def get_customer(realm_id: str, customer_id: str):
    result = quickbooks_data.get_customer(customer_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CustomerBody(BaseModel):
    Id: Optional[str] = None
    DisplayName: Optional[str] = None
    GivenName: Optional[str] = None
    FamilyName: Optional[str] = None
    CompanyName: Optional[str] = None
    PrimaryEmailAddr: Optional[Dict[str, str]] = None
    PrimaryPhone: Optional[Dict[str, str]] = None
    BillAddr: Optional[Dict[str, str]] = None
    Active: Optional[bool] = None
    Notes: Optional[str] = None
    SyncToken: Optional[str] = None


@app.post("/v3/company/{realm_id}/customer")
def create_or_update_customer(realm_id: str, body: CustomerBody):
    if body.Id:
        data = {k: v for k, v in body.model_dump().items() if v is not None and k not in ("Id", "SyncToken")}
        result = quickbooks_data.update_customer(body.Id, data)
        if "error" in result:
            return JSONResponse(status_code=404, content=result)
        return result
    else:
        result = quickbooks_data.create_customer(body.model_dump())
        return JSONResponse(status_code=201, content=result)


# --- Vendors ---

@app.get("/v3/company/{realm_id}/vendor/{vendor_id}")
def get_vendor(realm_id: str, vendor_id: str):
    result = quickbooks_data.get_vendor(vendor_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class VendorBody(BaseModel):
    Id: Optional[str] = None
    DisplayName: Optional[str] = None
    CompanyName: Optional[str] = None
    PrimaryEmailAddr: Optional[Dict[str, str]] = None
    PrimaryPhone: Optional[Dict[str, str]] = None
    BillAddr: Optional[Dict[str, str]] = None
    Active: Optional[bool] = None
    AcctNum: Optional[str] = None
    Vendor1099: Optional[bool] = None
    SyncToken: Optional[str] = None


@app.post("/v3/company/{realm_id}/vendor")
def create_or_update_vendor(realm_id: str, body: VendorBody):
    if body.Id:
        data = {k: v for k, v in body.model_dump().items() if v is not None and k not in ("Id", "SyncToken")}
        result = quickbooks_data.update_vendor(body.Id, data)
        if "error" in result:
            return JSONResponse(status_code=404, content=result)
        return result
    else:
        result = quickbooks_data.create_vendor(body.model_dump())
        return JSONResponse(status_code=201, content=result)


# --- Items ---

@app.get("/v3/company/{realm_id}/item/{item_id}")
def get_item(realm_id: str, item_id: str):
    result = quickbooks_data.get_item(item_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ItemBody(BaseModel):
    Id: Optional[str] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    Type: Optional[str] = None
    UnitPrice: Optional[float] = None
    IncomeAccountRef: Optional[Dict[str, str]] = None
    Active: Optional[bool] = None
    Taxable: Optional[bool] = None
    SyncToken: Optional[str] = None


@app.post("/v3/company/{realm_id}/item")
def create_or_update_item(realm_id: str, body: ItemBody):
    if body.Id:
        data = {k: v for k, v in body.model_dump().items() if v is not None and k not in ("Id", "SyncToken")}
        result = quickbooks_data.update_item(body.Id, data)
        if "error" in result:
            return JSONResponse(status_code=404, content=result)
        return result
    else:
        result = quickbooks_data.create_item(body.model_dump())
        return JSONResponse(status_code=201, content=result)


# --- Accounts ---

@app.get("/v3/company/{realm_id}/account/{account_id}")
def get_account(realm_id: str, account_id: str):
    result = quickbooks_data.get_account(account_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Invoices ---

@app.get("/v3/company/{realm_id}/invoice/{invoice_id}")
def get_invoice(realm_id: str, invoice_id: str):
    result = quickbooks_data.get_invoice(invoice_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v3/company/{realm_id}/invoice/{invoice_id}/pdf")
def get_invoice_pdf(realm_id: str, invoice_id: str):
    result = quickbooks_data.get_invoice_pdf(invoice_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class InvoiceBody(BaseModel):
    Id: Optional[str] = None
    CustomerRef: Optional[Dict[str, str]] = None
    Line: Optional[List[Dict[str, Any]]] = None
    TxnDate: Optional[str] = None
    DueDate: Optional[str] = None
    BillEmail: Optional[Dict[str, str]] = None
    PrintStatus: Optional[str] = None
    EmailStatus: Optional[str] = None
    SyncToken: Optional[str] = None


@app.post("/v3/company/{realm_id}/invoice")
def create_or_update_invoice(realm_id: str, body: InvoiceBody):
    if body.Id:
        data = {k: v for k, v in body.model_dump().items() if v is not None and k not in ("Id", "SyncToken")}
        result = quickbooks_data.update_invoice(body.Id, data)
        if "error" in result:
            return JSONResponse(status_code=404, content=result)
        return result
    else:
        result = quickbooks_data.create_invoice(body.model_dump())
        return JSONResponse(status_code=201, content=result)


@app.post("/v3/company/{realm_id}/invoice/{invoice_id}")
def void_or_send_invoice(
    realm_id: str,
    invoice_id: str,
    operation: Optional[str] = Query(default=None),
    include: Optional[str] = Query(default=None),
):
    if operation == "delete" or operation == "void":
        result = quickbooks_data.void_invoice(invoice_id)
        if "error" in result:
            return JSONResponse(status_code=404, content=result)
        return result
    if include == "send" or operation == "send":
        result = quickbooks_data.send_invoice(invoice_id)
        if "error" in result:
            return JSONResponse(status_code=404, content=result)
        return result
    return JSONResponse(status_code=400, content={"error": "Invalid operation. Use ?operation=void or ?include=send"})


# --- Bills ---

@app.get("/v3/company/{realm_id}/bill/{bill_id}")
def get_bill(realm_id: str, bill_id: str):
    result = quickbooks_data.get_bill(bill_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class BillCreateBody(BaseModel):
    VendorRef: Dict[str, str]
    Line: List[Dict[str, Any]]
    TxnDate: Optional[str] = None
    DueDate: Optional[str] = None
    DocNumber: Optional[str] = None


@app.post("/v3/company/{realm_id}/bill", status_code=201)
def create_bill(realm_id: str, body: BillCreateBody):
    result = quickbooks_data.create_bill(body.model_dump())
    return result


@app.post("/v3/company/{realm_id}/bill/{bill_id}")
def pay_bill(realm_id: str, bill_id: str, operation: Optional[str] = Query(default=None)):
    if operation == "pay":
        result = quickbooks_data.pay_bill(bill_id)
        if "error" in result:
            return JSONResponse(status_code=404, content=result)
        return result
    return JSONResponse(status_code=400, content={"error": "Invalid operation. Use ?operation=pay"})


# --- Payments ---

@app.get("/v3/company/{realm_id}/payment/{payment_id}")
def get_payment(realm_id: str, payment_id: str):
    result = quickbooks_data.get_payment(payment_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class PaymentCreateBody(BaseModel):
    CustomerRef: Dict[str, str]
    TotalAmt: float
    Line: List[Dict[str, Any]]
    TxnDate: Optional[str] = None


@app.post("/v3/company/{realm_id}/payment", status_code=201)
def create_payment(realm_id: str, body: PaymentCreateBody):
    result = quickbooks_data.create_payment(body.model_dump())
    return result


# --- Estimates ---

@app.get("/v3/company/{realm_id}/estimate/{estimate_id}")
def get_estimate(realm_id: str, estimate_id: str):
    result = quickbooks_data.get_estimate(estimate_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class EstimateCreateBody(BaseModel):
    CustomerRef: Dict[str, str]
    Line: List[Dict[str, Any]]
    TxnDate: Optional[str] = None
    ExpirationDate: Optional[str] = None


@app.post("/v3/company/{realm_id}/estimate", status_code=201)
def create_estimate(realm_id: str, body: EstimateCreateBody):
    result = quickbooks_data.create_estimate(body.model_dump())
    return result


@app.post("/v3/company/{realm_id}/estimate/{estimate_id}")
def convert_estimate(realm_id: str, estimate_id: str, operation: Optional[str] = Query(default=None)):
    if operation == "convert":
        result = quickbooks_data.convert_estimate_to_invoice(estimate_id)
        if "error" in result:
            return JSONResponse(status_code=400, content=result)
        return result
    return JSONResponse(status_code=400, content={"error": "Invalid operation. Use ?operation=convert"})


# --- Expenses (Purchases) ---

@app.get("/v3/company/{realm_id}/purchase/{expense_id}")
def get_expense(realm_id: str, expense_id: str):
    result = quickbooks_data.get_expense(expense_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ExpenseCreateBody(BaseModel):
    AccountRef: Dict[str, str]
    PaymentType: Optional[str] = "CreditCard"
    Line: List[Dict[str, Any]]
    TxnDate: Optional[str] = None


@app.post("/v3/company/{realm_id}/purchase", status_code=201)
def create_expense(realm_id: str, body: ExpenseCreateBody):
    result = quickbooks_data.create_expense(body.model_dump())
    return result


# --- Query ---

@app.get("/v3/company/{realm_id}/query")
def query_entities(realm_id: str, query: str = Query(...)):
    result = quickbooks_data.execute_query(query)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Reports ---

@app.get("/v3/company/{realm_id}/reports/ProfitAndLoss")
def report_profit_and_loss(
    realm_id: str,
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
):
    return quickbooks_data.profit_and_loss(start_date, end_date)


@app.get("/v3/company/{realm_id}/reports/BalanceSheet")
def report_balance_sheet(
    realm_id: str,
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
):
    return quickbooks_data.balance_sheet(start_date, end_date)


@app.get("/v3/company/{realm_id}/reports/AgedReceivableDetail")
def report_ar_aging(realm_id: str):
    return quickbooks_data.accounts_receivable_aging()


@app.get("/v3/company/{realm_id}/reports/AgedPayableDetail")
def report_ap_aging(realm_id: str):
    return quickbooks_data.accounts_payable_aging()
