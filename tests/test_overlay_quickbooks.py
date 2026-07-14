"""Overlay-logic edge cases applied to the ``quickbooks-api`` data module.

``test_overlay_edge_cases.py`` pins the contract for ``read_seed_with_ctx``
in isolation and end-to-end through ``figma-api`` / ``instagram-api``. The
quickbooks-api wiring is meaningfully different and deserves its own pin:

* ``invoices`` / ``bills`` / ``payments`` / ``estimates`` / ``expenses`` —
  use ``_load`` directly (pure overlay; raw rows enter the store).
* ``items`` — ``_load`` followed by ``_coerce_items`` (the JSON file is
  already in flat-row, CSV-friendly shape with columns like
  ``IncomeAccountRef_value`` / ``IncomeAccountRef_name``).
* ``customers`` / ``vendors`` / ``accounts`` — ``_load_qbo_or_csv``, a
  table-specific wrapper that:
    1. peeks for a sibling ``.csv``; if present, routes the CSV through
       ``_load`` (i.e. ``read_seed_with_ctx``) and feeds the result to a
       coercer that re-builds the nested QBO envelope shape;
    2. otherwise, unwraps a baked ``QueryResponse.<EnvelopeKey>`` array
       from the JSON via ``_load_json`` (which bypasses the overlay
       dispatcher entirely).
* ``company_info`` / ``company_raw`` / ``bill_payments`` /
  ``corporate_expense_ledger`` / ``reimbursement_policy`` /
  ``break_even_analysis`` — ``register_document`` + ``_load_json``. These
  intentionally bypass ``read_seed_with_ctx``; an author cannot overlay
  them with a CSV. We pin this as a *negative* property so a refactor
  that "helpfully" routes documents through the overlay dispatcher would
  fail loudly here.

All tests sandbox the real ``environment/quickbooks-api/`` directory under
``tmp_path`` and re-import ``quickbooks_data`` with strict sys.modules /
``_STORES`` isolation. The fixture mirrors the one in
``test_overlay_edge_cases.py``.
"""

from __future__ import annotations

import csv
import importlib
import json
import shutil
import sys
from pathlib import Path

import pytest

# Repo-root + environment/ on sys.path so ``_mutable_store`` resolves whether
# pytest is invoked from the repo root or from ``tests/``.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "environment"))

from _mutable_store import CoerceError  # noqa: E402

_ENV_DIR = Path(__file__).resolve().parents[1] / "environment"
_API = "quickbooks-api"
_MODULE = "quickbooks_data"


# ---------------------------------------------------------------------------
# Shared sandbox + isolation helpers (mirror test_overlay_edge_cases.py).
# ---------------------------------------------------------------------------


def _sandbox_qb(tmp_path: Path) -> Path:
    """Copy environment/quickbooks-api to tmp_path for non-destructive
    overlay authoring."""
    sandbox = tmp_path / "quickbooks-api"
    shutil.copytree(_ENV_DIR / "quickbooks-api", sandbox)
    return sandbox


@pytest.fixture()
def isolated_qb_import(monkeypatch):
    """Yields an importer that loads ``quickbooks_data`` from a sandbox dir
    with isolated sys.path / sys.modules / ``_STORES`` and tears everything
    down afterwards. Does NOT evict ``_mutable_store`` itself (would re-bind
    ``CoerceError`` and break identity in interleaved tests).
    """
    import _mutable_store as _ms

    bookmarks: list[str] = []

    def _import(sandbox: Path):
        _ms._STORES.pop(_API, None)
        sys.modules.pop(_MODULE, None)
        # environment/ first so the data module's ``from _mutable_store ...``
        # resolves to the canonical module; sandbox last so it wins for the
        # data module itself.
        monkeypatch.syspath_prepend(str(_ENV_DIR))
        monkeypatch.syspath_prepend(str(sandbox))
        bookmarks.append(_MODULE)
        return importlib.import_module(_MODULE)

    yield _import

    import _mutable_store as _ms2
    for module_name in bookmarks:
        _ms2._STORES.pop(_API, None)
        sys.modules.pop(module_name, None)


def _write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------------------
# Baseline: no overlay -> store loads cleanly from the baked JSON files.
# Pinning the pristine counts lets us prove later that a sibling-table
# overlay does NOT perturb the rest of the fleet.
# ---------------------------------------------------------------------------


def test_baseline_no_overlay_loads_all_tables_and_documents(
    tmp_path, isolated_qb_import
):
    sandbox = _sandbox_qb(tmp_path)
    qb = isolated_qb_import(sandbox)
    store = qb._store

    # Every registered table loads without error.
    for table_name in (
        "customers", "vendors", "items", "accounts",
        "invoices", "bills", "payments", "estimates", "expenses",
    ):
        rows = store.table(table_name).rows()
        assert isinstance(rows, list), f"table {table_name} did not load"
        assert len(rows) > 0, f"table {table_name} unexpectedly empty"

    # Documents resolve too.
    for doc_name in (
        "company_info", "company_raw", "bill_payments",
        "corporate_expense_ledger", "reimbursement_policy",
        "break_even_analysis",
    ):
        doc = store.document(doc_name)
        assert doc is not None, f"document {doc_name} did not resolve"


# ---------------------------------------------------------------------------
# Section A — pure ``_load`` overlay tables (invoices/bills/payments/...)
#
# These call ``read_seed_with_ctx`` directly with NO coercer. A CSV overlay
# returns rows verbatim; downstream consumers must tolerate whatever shape
# the CSV declared.
# ---------------------------------------------------------------------------


def test_invoices_csv_overlay_replaces_baked_json(tmp_path, isolated_qb_import):
    """Drop a single-row ``invoices.csv`` next to ``invoices.json`` and the
    store's ``invoices`` table reflects ONLY the CSV row (26 baked invoices
    are shadowed)."""
    sandbox = _sandbox_qb(tmp_path)
    overlay = {
        "Id": "OVR-001",
        "DocNumber": "INV-OVERLAY-1",
        "TxnDate": "2026-12-01",
        "DueDate": "2026-12-15",
        "TotalAmt": "100.00",
        "Balance": "100.00",
        "Status": "Open",
    }
    _write_csv(sandbox / "invoices.csv", [overlay], list(overlay.keys()))

    qb = isolated_qb_import(sandbox)
    rows = qb._store.table("invoices").rows()

    assert len(rows) == 1
    assert rows[0]["Id"] == "OVR-001"
    assert rows[0]["DocNumber"] == "INV-OVERLAY-1"
    # Context keys injected by ``read_csv_with_ctx`` survive into the store
    # because the invoices loader does not strip them.
    assert rows[0]["__api__"] == _API
    assert rows[0]["__table__"] == "invoices"
    assert rows[0]["__file__"].endswith("invoices.csv")


def test_empty_invoices_csv_overlay_blanks_the_table(tmp_path, isolated_qb_import):
    """Header-only ``invoices.csv`` is a valid "blank out" overlay -- the
    store reports zero invoices, distinct from "no overlay" (26 rows)."""
    sandbox = _sandbox_qb(tmp_path)
    # Header-only with the minimum columns needed for the file to parse.
    with open(sandbox / "invoices.csv", "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(
            f, fieldnames=["Id", "DocNumber", "TxnDate", "DueDate", "TotalAmt"]
        ).writeheader()

    qb = isolated_qb_import(sandbox)
    assert qb._store.table("invoices").rows() == []


def test_bills_csv_overlay_does_not_perturb_other_overlay_tables(
    tmp_path, isolated_qb_import
):
    """Selective-overlay invariant: overlaying ``bills.csv`` must not change
    invoices / payments / estimates / expenses counts -- a globbed overlay
    collector that accidentally replaces every table would fail this."""
    sandbox = _sandbox_qb(tmp_path)
    baseline = isolated_qb_import(sandbox)
    n_invoices = len(baseline._store.table("invoices").rows())
    n_payments = len(baseline._store.table("payments").rows())
    n_estimates = len(baseline._store.table("estimates").rows())
    n_expenses = len(baseline._store.table("expenses").rows())

    # Author overlay -> re-import (fixture cleans up between imports).
    overlay = {
        "Id": "BILL-OVR-1",
        "DocNumber": "BILL-OVERLAY",
        "TxnDate": "2026-12-02",
        "TotalAmt": "250.00",
        "Balance": "250.00",
    }
    _write_csv(sandbox / "bills.csv", [overlay], list(overlay.keys()))

    qb = isolated_qb_import(sandbox)
    assert len(qb._store.table("bills").rows()) == 1
    # Sibling overlay-capable tables intact.
    assert len(qb._store.table("invoices").rows()) == n_invoices
    assert len(qb._store.table("payments").rows()) == n_payments
    assert len(qb._store.table("estimates").rows()) == n_estimates
    assert len(qb._store.table("expenses").rows()) == n_expenses


def test_ragged_invoices_csv_overlay_surfaces_coerce_error(
    tmp_path, isolated_qb_import
):
    """A malformed CSV overlay (extra unquoted comma) must surface as
    ``CoerceError`` at store-load time naming the api+table+file, not as
    a downstream KeyError when an agent eventually hits ``GET /invoice/``.
    """
    sandbox = _sandbox_qb(tmp_path)
    # 5 declared columns; row has 6 fields -> ragged row.
    (sandbox / "invoices.csv").write_text(
        "Id,DocNumber,TxnDate,TotalAmt,Status\n"
        "OVR-1,INV-X,2026-12-01,100.00, extra, Open\n",
        encoding="utf-8",
    )
    # NOTE: match CoerceError by class NAME, not by the top-level-imported
    # class object. quickbooks_data resolves _mutable_store (and thus its
    # CoerceError) freshly at re-import time; if an earlier test in the session
    # evicted _mutable_store from sys.modules (test_drift_plane_smoke.py does),
    # the re-imported CoerceError is a DISTINCT class and pytest.raises keyed
    # on the stale top-level import would not catch it. Name+message matching
    # pins the same contract robustly regardless of import order.
    with pytest.raises(Exception) as excinfo:
        isolated_qb_import(sandbox)
    assert type(excinfo.value).__name__ == "CoerceError", (
        f"expected CoerceError, got {type(excinfo.value).__name__}: {excinfo.value}"
    )
    msg = str(excinfo.value)
    assert "ragged row" in msg
    assert _API in msg
    assert "invoices" in msg


# ---------------------------------------------------------------------------
# Section B — ``items`` table: ``_load`` + ``_coerce_items``.
# This is the cleanest overlay path because the baked items.json is already
# a flat array of CSV-friendly rows; a CSV overlay can be coerced end-to-end.
# ---------------------------------------------------------------------------


def test_items_csv_overlay_flows_through_coercer(tmp_path, isolated_qb_import):
    sandbox = _sandbox_qb(tmp_path)
    overlay = {
        "Id": "ITEM-OVR-1",
        "Name": "Overlay Widget",
        "Description": "Authored via CSV overlay",
        "Type": "Service",
        "UnitPrice": "199.99",
        "IncomeAccountRef_value": "82",
        "IncomeAccountRef_name": "Services",
        "Active": "true",
        "Taxable": "false",
    }
    _write_csv(sandbox / "items.csv", [overlay], list(overlay.keys()))

    qb = isolated_qb_import(sandbox)
    rows = qb._store.table("items").rows()

    assert len(rows) == 1
    item = rows[0]
    # Coercer rebuilt the nested IncomeAccountRef dict from the flat CSV columns.
    assert item["Id"] == "ITEM-OVR-1"
    assert item["Name"] == "Overlay Widget"
    assert item["IncomeAccountRef"] == {"value": "82", "name": "Services"}
    # Boolean coercion applied.
    assert item["Active"] is True
    assert item["Taxable"] is False
    # Float coercion applied.
    assert item["UnitPrice"] == 199.99


def test_items_csv_overlay_with_missing_column_fails_in_coercer(
    tmp_path, isolated_qb_import
):
    """Dispatcher is a dumb pipe -- the CSV is read fine, but the coercer
    references ``IncomeAccountRef_value`` which is missing. A future author
    who silently drops a column in their overlay must get a clear failure
    (KeyError today) rather than a successful load with phantom data.
    """
    sandbox = _sandbox_qb(tmp_path)
    overlay = {
        "Id": "ITEM-OVR-2",
        "Name": "Broken Overlay",
        "Description": "",
        "Type": "Service",
        "UnitPrice": "1.00",
        # ``IncomeAccountRef_value`` and ``IncomeAccountRef_name`` deliberately
        # omitted.
        "Active": "true",
        "Taxable": "false",
    }
    _write_csv(sandbox / "items.csv", [overlay], list(overlay.keys()))

    # The dispatcher returns rows successfully; the coercer raises KeyError
    # when it tries to read the missing column. Either error class is a
    # legitimate "loud failure"; we accept both, but require the load to
    # NOT silently succeed.
    with pytest.raises((KeyError, CoerceError)):
        isolated_qb_import(sandbox)


# ---------------------------------------------------------------------------
# Section C — ``_load_qbo_or_csv`` tables (customers / vendors / accounts).
#
# These have a custom CSV-sibling check in addition to the dispatcher's:
# ``_load_qbo_or_csv`` peeks ``.with_suffix('.csv').exists()``; if True it
# routes through ``_load`` (i.e. ``read_seed_with_ctx``) on the CSV file
# DIRECTLY, then coerces. If False it falls through to ``_load_json`` on
# the JSON and unwraps the ``QueryResponse.<Key>`` envelope. So *adding a
# CSV* still triggers overlay-wins via the dispatcher.
# ---------------------------------------------------------------------------


def test_customers_csv_overlay_triggers_load_path_and_coercer(
    tmp_path, isolated_qb_import
):
    sandbox = _sandbox_qb(tmp_path)
    overlay = {
        "Id": "CUST-OVR-1",
        "DisplayName": "Overlay Customer Inc.",
        "GivenName": "Olivia",
        "FamilyName": "Overlay",
        "CompanyName": "Overlay Customer Inc.",
        "PrimaryEmailAddr": "olivia@example.com",
        "PrimaryPhone": "555-0100",
        "BillAddr_Line1": "1 Overlay Way",
        "BillAddr_City": "Testville",
        "BillAddr_CountrySubDivisionCode": "CA",
        "BillAddr_PostalCode": "94000",
        "Balance": "0.00",
        "Active": "true",
        "Job": "false",
        "Notes": "",
    }
    _write_csv(sandbox / "customers.csv", [overlay], list(overlay.keys()))

    qb = isolated_qb_import(sandbox)
    customers = qb._store.table("customers").rows()

    assert len(customers) == 1
    c = customers[0]
    assert c["Id"] == "CUST-OVR-1"
    assert c["DisplayName"] == "Overlay Customer Inc."
    # Coercer rebuilt nested address.
    assert c["BillAddr"] == {
        "Line1": "1 Overlay Way",
        "City": "Testville",
        "CountrySubDivisionCode": "CA",
        "PostalCode": "94000",
    }
    # opt_str -> default "" -> None for empty Notes.
    assert c["Notes"] is None
    # Active coerced from string to bool.
    assert c["Active"] is True
    assert c["Job"] is False


def test_customers_no_csv_overlay_uses_qbo_envelope(tmp_path, isolated_qb_import):
    """Without a sibling ``customers.csv``, ``_load_qbo_or_csv`` unwraps
    ``QueryResponse.Customer`` from the baked JSON. This pins the *fall-
    through* leg: the overlay path is NOT mandatory, the envelope path
    still works.
    """
    sandbox = _sandbox_qb(tmp_path)
    # No customers.csv authored.
    qb = isolated_qb_import(sandbox)
    customers = qb._store.table("customers").rows()

    assert len(customers) > 0
    # Envelope-unwrapped rows preserve baked JSON keys (nested DisplayName /
    # Balance etc.) rather than flat CSV columns.
    first = customers[0]
    assert "DisplayName" in first
    # No __api__ context key because this leg bypasses the dispatcher.
    assert "__api__" not in first
    # And the envelope produced *more* than one row (the baked file has many).
    assert len(customers) > 1


def test_vendors_csv_overlay_replaces_envelope_rows(tmp_path, isolated_qb_import):
    sandbox = _sandbox_qb(tmp_path)
    overlay = {
        "Id": "VEND-OVR-1",
        "DisplayName": "Overlay Vendor LLC",
        "CompanyName": "Overlay Vendor LLC",
        "PrimaryEmailAddr": "billing@overlay-vendor.test",
        "PrimaryPhone": "555-0200",
        "BillAddr_Line1": "2 Vendor Rd",
        "BillAddr_City": "Buyersburg",
        "BillAddr_CountrySubDivisionCode": "NY",
        "BillAddr_PostalCode": "10001",
        "Balance": "0",
        "Active": "true",
        "AcctNum": "",
        "Vendor1099": "false",
    }
    _write_csv(sandbox / "vendors.csv", [overlay], list(overlay.keys()))

    qb = isolated_qb_import(sandbox)
    vendors = qb._store.table("vendors").rows()
    assert len(vendors) == 1
    assert vendors[0]["DisplayName"] == "Overlay Vendor LLC"
    assert vendors[0]["Vendor1099"] is False
    assert vendors[0]["AcctNum"] is None


def test_accounts_csv_overlay_replaces_envelope_rows(tmp_path, isolated_qb_import):
    sandbox = _sandbox_qb(tmp_path)
    overlay = {
        "Id": "ACC-OVR-1",
        "Name": "Overlay Cash",
        "AccountType": "Bank",
        "AccountSubType": "Checking",
        "CurrentBalance": "1234.56",
        "Active": "true",
        "Classification": "Asset",
        "Description": "Overlay account for tests",
    }
    _write_csv(sandbox / "accounts.csv", [overlay], list(overlay.keys()))

    qb = isolated_qb_import(sandbox)
    accounts = qb._store.table("accounts").rows()
    assert len(accounts) == 1
    assert accounts[0]["Name"] == "Overlay Cash"
    assert accounts[0]["CurrentBalance"] == 1234.56


def test_ragged_customers_csv_overlay_surfaces_coerce_error(
    tmp_path, isolated_qb_import
):
    """``_load_qbo_or_csv`` routes through ``read_seed_with_ctx`` for the
    CSV path, so a ragged CSV must surface the same ``CoerceError`` with
    ``api='quickbooks-api'`` and ``table='customers'`` context."""
    sandbox = _sandbox_qb(tmp_path)
    (sandbox / "customers.csv").write_text(
        "Id,DisplayName,Balance,Active\n"
        "CUST-X,Bad Row,0, extra, true\n",
        encoding="utf-8",
    )
    # NOTE: match CoerceError by class NAME, not the stale top-level-imported
    # class object -- see the invoices ragged test above for the full
    # rationale (import-order-dependent _mutable_store identity via
    # test_drift_plane_smoke.py evicting it from sys.modules).
    with pytest.raises(Exception) as excinfo:
        isolated_qb_import(sandbox)
    assert type(excinfo.value).__name__ == "CoerceError", (
        f"expected CoerceError, got {type(excinfo.value).__name__}: {excinfo.value}"
    )
    msg = str(excinfo.value)
    assert "ragged row" in msg
    assert _API in msg
    assert "customers" in msg


# ---------------------------------------------------------------------------
# Section D — documents bypass the overlay dispatcher (negative property).
# ---------------------------------------------------------------------------


def test_company_info_document_csv_sibling_is_ignored(tmp_path, isolated_qb_import):
    """``register_document`` loaders call ``_load_json`` directly,
    bypassing ``read_seed_with_ctx``. A CSV sibling next to
    ``company_info.json`` must therefore be ignored entirely -- the
    document still resolves from JSON.

    This is the *negative* version of the overlay contract: documents are
    intentionally NOT overlayable. If a future refactor "helpfully" routes
    document loaders through ``read_seed_with_ctx``, this test fails and
    forces the change to be a conscious decision (with API/contract
    implications) rather than silent behavior drift.
    """
    sandbox = _sandbox_qb(tmp_path)
    # A CSV sibling beside the document file should be invisible to the
    # document loader path; this single-column file is a tripwire.
    _write_csv(
        sandbox / "company_info.csv",
        [{"CompanyName": "OVERLAY_SHOULD_NOT_APPLY"}],
        ["CompanyName"],
    )

    qb = isolated_qb_import(sandbox)
    value = qb._store.document("company_info").get()
    assert isinstance(value, dict)
    assert value.get("CompanyName") != "OVERLAY_SHOULD_NOT_APPLY"


def test_break_even_analysis_document_csv_sibling_is_ignored(
    tmp_path, isolated_qb_import
):
    """Mirror of the previous test for a document with a hyphenated name
    (``break-even-analysis``). Hyphens in filenames are a common source of
    suffix-comparison bugs; pin both."""
    sandbox = _sandbox_qb(tmp_path)
    _write_csv(
        sandbox / "break-even-analysis.csv",
        [{"label": "ignored"}],
        ["label"],
    )
    qb = isolated_qb_import(sandbox)
    value = qb._store.document("break_even_analysis").get()
    baseline = json.loads(
        (sandbox / "break-even-analysis.json").read_text(encoding="utf-8")
    )
    assert value == baseline


# ---------------------------------------------------------------------------
# Section E — cross-cutting: __file__ attribution + isolation between imports.
# ---------------------------------------------------------------------------


def test_file_attribution_points_at_overlay_csv(tmp_path, isolated_qb_import):
    """When CSV-overlay-wins, every row carries ``__file__`` pointing at
    the CSV file actually read (not the shadowed JSON). Operators reading
    an error trace must see the file they need to fix.
    """
    sandbox = _sandbox_qb(tmp_path)
    overlay = {
        "Id": "OVR-FA-1",
        "DocNumber": "INV-FA",
        "TxnDate": "2026-12-03",
        "DueDate": "2026-12-13",
        "TotalAmt": "1.00",
    }
    _write_csv(sandbox / "invoices.csv", [overlay], list(overlay.keys()))

    qb = isolated_qb_import(sandbox)
    rows = qb._store.table("invoices").rows()
    assert len(rows) == 1
    assert rows[0]["__file__"].endswith("invoices.csv")
    assert "invoices.json" not in rows[0]["__file__"]
