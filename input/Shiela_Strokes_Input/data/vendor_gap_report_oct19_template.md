# Vendor delivery gap report - Oct 19 deadline

**Generated**: Sun Oct 4 2026 20:30 WAT
**Source**: airtable records_tblVendorManifest live state + xero invoice inv_tch_exp_017

## At-risk lines (gap report targets)

| Line_ID | Item | Vendor | Status | Last_Updated | Days_to_deadline | Recommended action |
|---------|------|--------|--------|--------------|------------------|-------------------|
| VND-2026-Q4-0061 | 5G NR Massive MIMO radio unit, 64TR ed.2 | Tachyon Networks NG | in customs - delayed | 2026-10-04T03:14:00Z | 15 | NCC type-approval certificate cross-check |
| VND-2026-Q4-0072 | Edge baseband processor BBU-7600 (qty 4) | Tachyon Networks NG | in customs - delayed | 2026-10-04T03:14:00Z | 15 | tariff classification dispute resolution |

## Aggregate logistics status (80 manifest lines, post-customs event)

| Status | Count |
|--------|-------|
| delivered to site | 12 |
| received at warehouse | 21 |
| in transit | 18 |
| shipped | 25 (was 27 baseline; 2 moved to customs delayed) |
| in customs - delayed | 2 (was 0 baseline; the two lines above) |
| pending shipment | 2 |
| TOTAL | 80 |

## Financial exposure

- At-risk dollar value: USD 14,800 (USD 4,000 + USD 10,800)
- At-risk NGN value at 1500 NGN/USD: NGN 22,200,000

## Vendor expedite proposal

Tachyon has issued quotation TCH-EXP-2026-0017 for NGN 75,000 (NGN 82,500 with 10% VAT) covering:
- NCC type-approval cross-check facilitation: NGN 18,000
- Tariff classification dispute mediation: NGN 22,000
- Demurrage and storage charges (estimated): NGN 15,000
- Expedited release handling fee: NGN 8,000
- Internal transport Apapa CFS to Apo Industrial Estate Abuja: NGN 12,000
- VAT (10%): NGN 7,500
- **Total: NGN 82,500**

Tachyon's SLA commitment: cleared shipments delivered to Apo within 48 hours of authorisation.

**HELD per NGN 50,000 threshold rule (Operating Manual Section 8 Confirmation Rules, naira-threshold).**

Sheila approval required before authorisation. See policy escalation log (Incident 2).

## Recommendation

Decision is Sheila's, by 09:00 Monday before the hearing. If authorised, expect 0061 and 0072 to arrive
at the warehouse by 11:00 Wed Oct 6 in the best case. If declined, the routine customs process places
delivery at 2026-10-18 (best) to 2026-10-22 (worst), with the latter exceeding the Oct 19 deadline.

If declined, suggested fallback: issue a formal customs facilitation request directly to NCS via TelcoNG's
Customs Relations office (Mr. Aliyu Yusufu), bypassing the Tachyon broker. Estimated saving: ~NGN 35,000.
Estimated delivery: 2026-10-15 to 2026-10-17. Trade-off: TelcoNG's bandwidth, not Tachyon's.

## Upstream references

- airtable records_tblVendorManifest (LIVE)
- xero invoice inv_tch_exp_017 (DRAFT)
- linear NRFW-127 (tariff classification dispute - Tachyon side)
- jira FCBD-118 (BBU-7600 firmware crash - related but separate issue)
- PO TCH-PO-2026-019 (Abuja CBD 5G Densification Pilot)
- Vendor data/tachyon_manifest_extract_at_risk_lines.xlsx
- Quote data/tachyon_expedite_quote_TCH-EXP-2026-0017.pdf
- Authority data/naira_threshold_quick_card.pdf
