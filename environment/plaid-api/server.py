"""FastAPI server wrapping plaid_data module as REST endpoints.

Mirrors the Plaid API: reads are POST requests with a JSON body (the real Plaid
API authenticates via client_id/secret/access_token, which the mock accepts but
ignores). Pagination on /transactions/get uses count + offset under `options`.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import plaid_data
try:
    from tracking_middleware import install_tracker
    from admin_plane import install_admin_plane
except ModuleNotFoundError as _shared_plane_err:  # standalone run without the shared module on sys.path
    import logging as _logging
    _logging.error("SHARED PLANE MISSING - audit + admin disabled: %s", _shared_plane_err)
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

    def install_admin_plane(app, store=None, one_shot_registry=None):
        return None

app = FastAPI(title="Plaid API (Mock)", version="2020-09-14")
install_tracker(app)
install_admin_plane(app, store=plaid_data._store)


@app.get("/health")
def health():
    return {"status": "ok"}


# Shared auth fields accepted (and ignored) on every request, like real Plaid.
class _BaseRequest(BaseModel):
    client_id: Optional[str] = None
    secret: Optional[str] = None
    access_token: Optional[str] = None


class AccountsOptions(BaseModel):
    account_ids: Optional[List[str]] = None


class AccountsGetBody(_BaseRequest):
    options: Optional[AccountsOptions] = None


@app.post("/accounts/get")
def accounts_get(body: AccountsGetBody):
    account_ids = body.options.account_ids if body.options else None
    return plaid_data.get_accounts(account_ids=account_ids)


@app.post("/accounts/balance/get")
def accounts_balance_get(body: AccountsGetBody):
    account_ids = body.options.account_ids if body.options else None
    return plaid_data.get_balances(account_ids=account_ids)


class TransactionsOptions(BaseModel):
    account_ids: Optional[List[str]] = None
    count: Optional[int] = 100
    offset: Optional[int] = 0


class TransactionsGetBody(_BaseRequest):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    options: Optional[TransactionsOptions] = None


@app.post("/transactions/get")
def transactions_get(body: TransactionsGetBody):
    opts = body.options or TransactionsOptions()
    return plaid_data.get_transactions(
        start_date=body.start_date,
        end_date=body.end_date,
        account_ids=opts.account_ids,
        count=opts.count if opts.count is not None else 100,
        offset=opts.offset if opts.offset is not None else 0,
    )


class InstitutionGetByIdBody(_BaseRequest):
    institution_id: str
    country_codes: Optional[List[str]] = None


@app.post("/institutions/get_by_id")
def institutions_get_by_id(body: InstitutionGetByIdBody):
    result = plaid_data.get_institution_by_id(body.institution_id)
    if "error_code" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class IdentityGetBody(_BaseRequest):
    options: Optional[AccountsOptions] = None


@app.post("/identity/get")
def identity_get(body: IdentityGetBody):
    account_ids = body.options.account_ids if body.options else None
    return plaid_data.get_identity(account_ids=account_ids)
