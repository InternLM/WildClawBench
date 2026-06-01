---
name: pinterest-api-connector
description: >
  Pinterest API v5 HTTP endpoints for business account management, boards,
  board sections, pins, search, media uploads, ad accounts, and analytics.
---

# Pinterest API v5

## Base URL

| Variable | Purpose |
|----------|---------|
| `PINTEREST_API_URL` | Base URL for all requests |

All paths below are relative to `PINTEREST_API_URL`.

---

## Health

```
GET /health
```

Returns `{"status": "ok"}`.

---

## User Account

### Get account profile

Returns the authenticated user's profile information, including account username, display name, bio, profile image URL, website URL, account type, and board and pin counts.

```
GET /v5/user_account
```

### Get account analytics

Returns aggregate analytics for the authenticated user's account over a date range. Metrics include impressions, engagements, pin clicks, outbound clicks, and saves. When date parameters are omitted, returns the most recent available data.

```
GET /v5/user_account/analytics
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `start_date` | string | query | no | Start date (YYYY-MM-DD) |
| `end_date` | string | query | no | End date (YYYY-MM-DD) |

---

## Boards

### List boards

Returns a paginated list of all boards belonging to the authenticated user. Each board object includes its ID, name, description, privacy setting, pin count, follower count, and creation timestamp. Supports filtering by privacy level.

```
GET /v5/boards
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `privacy` | string | query | no | Filter by privacy: `PUBLIC`, `SECRET` |
| `limit` | integer | query | no | Max results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get board

Returns the full details of a single board, including its ID, name, description, privacy setting, pin count, follower count, collaborator count, and creation timestamp. Returns a 404 error if the board ID does not exist.

```
GET /v5/boards/{board_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `board_id` | string | path | yes | Board ID |

### Create board

Creates a new board for the authenticated user. Returns the newly created board object with its assigned ID and default settings. The board name is required; description and privacy level are optional.

```
POST /v5/boards
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Board name |
| `description` | string | no | Board description |
| `privacy` | string | no | `PUBLIC` or `SECRET` |

### Update board

Modifies the properties of an existing board. Accepts any combination of name, description, and privacy setting. Returns the updated board object. Returns a 404 error if the board ID does not exist.

```
PATCH /v5/boards/{board_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `board_id` | string | path | yes | Board ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | no | Board name |
| `description` | string | no | Board description |
| `privacy` | string | no | `PUBLIC` or `SECRET` |

### Delete board

Permanently removes a board and disassociates all of its pins. Returns a success confirmation on deletion. Returns a 404 error if the board ID does not exist.

```
DELETE /v5/boards/{board_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `board_id` | string | path | yes | Board ID |

### List board pins

Returns a paginated list of all pins saved to a specific board. Each pin object includes its ID, title, description, link, media type, dominant color, alt text, board section ID (if assigned), and creation timestamp. Results include pins from all sections of the board. Returns a 404 error if the board ID does not exist.

```
GET /v5/boards/{board_id}/pins
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `board_id` | string | path | yes | Board ID |
| `limit` | integer | query | no | Max results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

---

## Board Sections

### List board sections

Returns the list of all sections within a specific board. Each section object includes its ID, name, and pin count. Returns a 404 error if the board ID does not exist.

```
GET /v5/boards/{board_id}/sections
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `board_id` | string | path | yes | Board ID |

### Create board section

Creates a new section within an existing board. Returns the newly created section object with its assigned ID. Returns a 400 error if the board does not exist or the section name is missing.

```
POST /v5/boards/{board_id}/sections
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `board_id` | string | path | yes | Board ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Section name |

### List section pins

Returns a paginated list of pins within a specific section of a board. Validates that the section belongs to the specified board before returning results. Returns a 404 error if the board, section, or the section-board association does not exist.

```
GET /v5/boards/{board_id}/sections/{section_id}/pins
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `board_id` | string | path | yes | Board ID |
| `section_id` | string | path | yes | Section ID |
| `limit` | integer | query | no | Max results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

---

## Pins

### List all pins

Returns a paginated list of all pins owned by the authenticated user across all boards. Each pin object includes its ID, title, description, link, board ID, board section ID, media type, dominant color, alt text, and creation timestamp.

```
GET /v5/pins
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `limit` | integer | query | no | Max results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get pin

Returns the full details of a single pin, including its ID, title, description, link, board ID, board section ID, media type, media source, dominant color, alt text, and creation timestamp. Returns a 404 error if the pin ID does not exist.

```
GET /v5/pins/{pin_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `pin_id` | string | path | yes | Pin ID |

### Create pin

Creates a new pin on a specified board. Returns the newly created pin object with its assigned ID. The board ID and title are required; all other fields are optional. If `board_section_id` is provided, the pin is placed within that section of the board.

```
POST /v5/pins
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `board_id` | string | yes | Board ID to pin to |
| `title` | string | yes | Pin title |
| `description` | string | no | Pin description |
| `link` | string | no | Source URL |
| `media_type` | string | no | Media type (e.g. `image`) |
| `board_section_id` | string | no | Board section ID |
| `dominant_color` | string | no | Dominant color hex code |
| `alt_text` | string | no | Image alt text |

### Update pin

Modifies the properties of an existing pin. Accepts any combination of title, description, link, board reassignment, section reassignment, and alt text. Returns the updated pin object. Returns a 404 error if the pin ID does not exist.

```
PATCH /v5/pins/{pin_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `pin_id` | string | path | yes | Pin ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | no | Pin title |
| `description` | string | no | Pin description |
| `link` | string | no | Source URL |
| `board_id` | string | no | Move pin to a different board |
| `board_section_id` | string | no | Move pin to a different section |
| `alt_text` | string | no | Image alt text |

### Delete pin

Permanently removes a pin. Returns a success confirmation on deletion. Returns a 404 error if the pin ID does not exist.

```
DELETE /v5/pins/{pin_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `pin_id` | string | path | yes | Pin ID |

### Get pin analytics

Returns performance analytics for a single pin over an optional date range. Metrics include impressions, saves, pin clicks, outbound clicks, and video views (for video pins). When date parameters are omitted, returns the most recent available data. Returns a 404 error if the pin ID does not exist.

```
GET /v5/pins/{pin_id}/analytics
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `pin_id` | string | path | yes | Pin ID |
| `start_date` | string | query | no | Start date (YYYY-MM-DD) |
| `end_date` | string | query | no | End date (YYYY-MM-DD) |

---

## Search

### Search pins

Performs a full-text search across all pin titles and descriptions. Returns a paginated list of matching pin objects ordered by relevance. The search is case-insensitive and matches partial terms.

```
GET /v5/search/pins
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `query` | string | query | yes | Search term |
| `limit` | integer | query | no | Max results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

---

## Media

### Get media upload status

Returns the processing status of a media upload. The status field indicates the upload's current state. Returns a 404 error if the media ID does not exist.

```
GET /v5/media/{media_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `media_id` | string | path | yes | Media ID |

---

## Ad Accounts

### List ad accounts

Returns a paginated list of all ad accounts accessible to the authenticated user. Each ad account object includes its ID, name, and status.

```
GET /v5/ad_accounts
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `limit` | integer | query | no | Max results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get ad account

Returns the full details of a single ad account, including its ID, name, status, currency, and owner information. Returns a 404 error if the ad account ID does not exist.

```
GET /v5/ad_accounts/{ad_account_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `ad_account_id` | string | path | yes | Ad account ID |

### List campaigns

Returns a paginated list of advertising campaigns within a specific ad account. Each campaign includes its ID, name, status, objective type, daily spend limit, and lifetime spend limit. Supports filtering by campaign status. Returns a 404 error if the ad account ID does not exist.

```
GET /v5/ad_accounts/{ad_account_id}/campaigns
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `ad_account_id` | string | path | yes | Ad account ID |
| `status` | string | query | no | Filter by status: `ACTIVE`, `PAUSED` |
| `limit` | integer | query | no | Max results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

---

## Errors

Error responses follow this format:

```json
{
  "error": {
    "message": "Description of the error",
    "code": 404
  }
}
```

Common HTTP status codes:

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid parameters) |
| 404 | Resource not found |
