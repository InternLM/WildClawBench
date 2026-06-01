# Documentation Faithfulness Check

## Source: https://raw.githubusercontent.com/pinterest/api-description/v5.12.0/v5/openapi.yaml
## Additional: https://github.com/pinterest/pinterest-python-generated-api-client/blob/main/docs/PinCreate.md

| # | Endpoint | Our Path | Official Path | Match? | Notes |
|---|----------|----------|---------------|--------|-------|
| 1 | Health | GET /health | N/A (mock only) | N/A | Not in official API; mock convention |
| 2 | Get user account | GET /v5/user_account | GET /v5/user_account | ✓ | |
| 3 | User analytics | GET /v5/user_account/analytics | GET /v5/user_account/analytics | ✓ | Official uses metric_types+start_date+end_date; we simplify to start/end only |
| 4 | List boards | GET /v5/boards | GET /v5/boards | ✓ | Official uses bookmark pagination; we use offset/limit per prompt |
| 5 | Get board | GET /v5/boards/{board_id} | GET /v5/boards/{board_id} | ✓ | |
| 6 | Create board | POST /v5/boards | POST /v5/boards | ✓ | |
| 7 | Update board | PATCH /v5/boards/{board_id} | PATCH /v5/boards/{board_id} | ✓ | |
| 8 | Delete board | DELETE /v5/boards/{board_id} | DELETE /v5/boards/{board_id} | ✓ | |
| 9 | List board pins | GET /v5/boards/{board_id}/pins | GET /v5/boards/{board_id}/pins | ✓ | |
| 10 | List board sections | GET /v5/boards/{board_id}/sections | GET /v5/boards/{board_id}/sections | ✓ | |
| 11 | Create board section | POST /v5/boards/{board_id}/sections | POST /v5/boards/{board_id}/sections | ✓ | |
| 12 | List section pins | GET /v5/boards/{board_id}/sections/{section_id}/pins | GET /v5/boards/{board_id}/sections/{section_id}/pins | ✓ | |
| 13 | List pins | GET /v5/pins | GET /v5/pins | ✓ | Official requires bookmark; we use offset/limit |
| 14 | Get pin | GET /v5/pins/{pin_id} | GET /v5/pins/{pin_id} | ✓ | Official uses `id` field in response; we use `pin_id` for clarity |
| 15 | Create pin | POST /v5/pins | POST /v5/pins | ✓ | |
| 16 | Update pin | PATCH /v5/pins/{pin_id} | PATCH /v5/pins/{pin_id} | ✓ | Official uses PATCH, we match |
| 17 | Delete pin | DELETE /v5/pins/{pin_id} | DELETE /v5/pins/{pin_id} | ✓ | |
| 18 | Pin analytics | GET /v5/pins/{pin_id}/analytics | GET /v5/pins/{pin_id}/analytics | ✓ | |
| 19 | Search pins | GET /v5/search/pins | GET /v5/search/pins | ✓ | Official uses `query` param; we match |
| 20 | Media status | GET /v5/media/{media_id} | GET /v5/media/{media_id} | ✓ | |
| 21 | List ad accounts | GET /v5/ad_accounts | GET /v5/ad_accounts | ✓ | |
| 22 | Get ad account | GET /v5/ad_accounts/{ad_account_id} | GET /v5/ad_accounts/{ad_account_id} | ✓ | |
| 23 | List campaigns | GET /v5/ad_accounts/{ad_account_id}/campaigns | GET /v5/ad_accounts/{ad_account_id}/campaigns | ✓ | |

## Field Name Verification (Pin object)

| Field | Our Name | Official Name | Match? | Notes |
|-------|----------|---------------|--------|-------|
| Pin ID | pin_id | id | ~ | We use descriptive `pin_id` for referential clarity in CSV data |
| Title | title | title | ✓ | |
| Description | description | description | ✓ | |
| Link | link | link | ✓ | |
| Board ID | board_id | board_id | ✓ | |
| Board Section ID | board_section_id | board_section_id | ✓ | |
| Alt text | alt_text | alt_text | ✓ | |
| Dominant color | dominant_color | dominant_color | ✓ | |
| Created at | created_at | created_at | ✓ | |
| Media type | media_type | creative_type (enum) | ~ | Official uses `creative_type`; we simplify to `media_type` (image/video) |

## Board Field Verification

| Field | Our Name | Official Name | Match? |
|-------|----------|---------------|--------|
| Board ID | board_id | id | ~ |
| Name | name | name | ✓ |
| Description | description | description | ✓ |
| Privacy | privacy | privacy | ✓ |
| Pin count | pin_count | pin_count | ✓ |
| Created at | created_at | created_at | ✓ |

## Pagination

| Aspect | Our Mock | Official API | Notes |
|--------|----------|-------------|-------|
| Method | offset/limit | bookmark cursor | Simplified per prompt instruction |
| Response envelope | {"results": [...], "total": N} | {"items": [...], "bookmark": "..."} | Simplified; prompt says to use offset/limit |

## Summary

- **23 endpoints** checked against official Pinterest API v5 OpenAPI spec (v5.12.0)
- **All endpoint paths match** the official documentation
- **Field names match** with two documented simplifications: entity IDs use descriptive names (pin_id vs id), and media_type vs creative_type
- **Pagination simplified** from bookmark to offset/limit as explicitly allowed by the project prompt
- **No issues requiring fixes** — all paths are authentic to the real Pinterest API v5
