---
name: youtube-api-connector
description: >
  YouTube Data API v3 HTTP endpoints for channel management, video operations,
  playlists, comment moderation, search, and analytics reporting.
---

# YouTube Data API v3

## Base URL

| Variable | Purpose |
|----------|---------|
| `YOUTUBE_API_URL` | Base URL for all requests |

All paths below are relative to `YOUTUBE_API_URL`.

---

## Health

```
GET /health
```

Returns `{"status": "ok"}`.

---

## Channels

### Get channel

Returns channel metadata including snippet (title, description, thumbnails), content details (related playlists), statistics (subscriber count, video count, view count), and branding settings. When no `id` is specified, returns the authenticated channel.

```
GET /youtube/v3/channels
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `id` | string | query | no | Channel ID. Defaults to the authenticated channel. |
| `part` | string | query | no | Comma-separated resource parts to include: `snippet`, `contentDetails`, `statistics`, `brandingSettings`. Default: all parts. |

---

## Videos

### List videos

Returns a list of videos matching the specified filters. Each video resource includes snippet (title, description, tags, thumbnails, publish date), content details (duration, definition, caption availability), statistics (views, likes, comments), and status (privacy, embeddable, license). Supports filtering by specific video IDs or by channel.

```
GET /youtube/v3/videos
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `id` | string | query | no | Comma-separated video IDs to retrieve |
| `channelId` | string | query | no | Filter videos by channel ID |
| `part` | string | query | no | Comma-separated resource parts: `snippet`, `contentDetails`, `statistics`, `status`. Default: all parts. |
| `maxResults` | integer | query | no | Maximum results, 1-50. Default: 25 |
| `pageToken` | string | query | no | Pagination token from a previous response |

### Update video

Updates the metadata and/or status of an existing video. The video `id` is required in the request body. Only the provided resource parts are modified. Returns the updated video resource.

```
PUT /youtube/v3/videos
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Video ID to update |
| `snippet` | object | no | `{"title": "string", "description": "string", "tags": ["string"], "categoryId": "string"}` |
| `status` | object | no | `{"privacyStatus": "public\|unlisted\|private", "embeddable": boolean}` |

### Delete video

Permanently deletes a video from the channel. This action cannot be undone.

```
DELETE /youtube/v3/videos
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `id` | string | query | yes | Video ID to delete |

---

## Playlists

### List playlists

Returns a list of playlists matching the specified filters. Each playlist includes snippet (title, description, thumbnails), content details (item count), and status (privacy setting). Supports filtering by specific playlist IDs or by channel.

```
GET /youtube/v3/playlists
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `id` | string | query | no | Comma-separated playlist IDs |
| `channelId` | string | query | no | Filter playlists by channel ID |
| `part` | string | query | no | Comma-separated resource parts: `snippet`, `contentDetails`, `status`. Default: all parts. |
| `maxResults` | integer | query | no | Maximum results, 1-50. Default: 25 |
| `pageToken` | string | query | no | Pagination token |

### Create playlist

Creates a new playlist on the authenticated channel. Returns the created playlist resource with a server-generated ID.

```
POST /youtube/v3/playlists
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `snippet` | object | yes | `{"title": "string", "description": "string"}` |
| `status` | object | no | `{"privacyStatus": "public\|unlisted\|private"}` |

### Update playlist

Updates an existing playlist's title, description, or privacy status. The playlist `id` is required. Returns the updated playlist resource.

```
PUT /youtube/v3/playlists
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Playlist ID to update |
| `snippet` | object | no | `{"title": "string", "description": "string"}` |
| `status` | object | no | `{"privacyStatus": "public\|unlisted\|private"}` |

### Delete playlist

Permanently deletes a playlist and removes all item associations. The videos themselves are not deleted.

```
DELETE /youtube/v3/playlists
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `id` | string | query | yes | Playlist ID to delete |

---

## Playlist Items

### List playlist items

Returns the videos contained in a specified playlist, ordered by position. Each item includes the video resource ID, position index, title, description, and thumbnails.

```
GET /youtube/v3/playlistItems
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `playlistId` | string | query | yes | Playlist ID to list items from |
| `part` | string | query | no | Comma-separated resource parts: `snippet`, `contentDetails`. Default: all parts. |
| `maxResults` | integer | query | no | Maximum results, 1-50. Default: 25 |
| `pageToken` | string | query | no | Pagination token |

### Insert playlist item

Adds a video to a playlist at the specified position. If no position is given, the video is appended to the end. Returns the created playlist item resource.

```
POST /youtube/v3/playlistItems
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `snippet` | object | yes | `{"playlistId": "string", "resourceId": {"kind": "youtube#video", "videoId": "string"}, "position": integer}`. `position` is optional. |

### Update playlist item

Updates the position of an existing item within a playlist. Returns the updated playlist item resource.

```
PUT /youtube/v3/playlistItems
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Playlist item ID |
| `snippet` | object | yes | `{"position": integer}` |

### Delete playlist item

Removes a video from a playlist. The video itself is not deleted.

```
DELETE /youtube/v3/playlistItems
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `id` | string | query | yes | Playlist item ID to remove |

---

## Comment Threads

### List comment threads

Returns top-level comment threads for a video or channel. Each thread includes the top-level comment (author, text, like count, publish date) and optionally its replies. Threads can be filtered by moderation status to find comments awaiting review.

```
GET /youtube/v3/commentThreads
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `videoId` | string | query | no | Filter threads by video ID |
| `channelId` | string | query | no | Filter threads by channel ID |
| `part` | string | query | no | Comma-separated resource parts: `snippet`, `replies`. Default: all parts. |
| `maxResults` | integer | query | no | Maximum results, 1-100. Default: 20 |
| `moderationStatus` | string | query | no | Filter by status: `published`, `heldForReview`, `rejected` |
| `pageToken` | string | query | no | Pagination token |

### Create comment thread

Creates a new top-level comment on a video. Returns the created comment thread resource.

```
POST /youtube/v3/commentThreads
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `snippet` | object | yes | `{"videoId": "string", "topLevelComment": {"snippet": {"textOriginal": "string"}}}` |

---

## Comments

### List replies

Returns replies to a specific parent comment. Each reply includes the author display name, text content, like count, and publish date.

```
GET /youtube/v3/comments
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `parentId` | string | query | yes | Parent comment ID to retrieve replies for |
| `part` | string | query | no | Comma-separated resource parts: `snippet`. Default: `snippet`. |
| `maxResults` | integer | query | no | Maximum results, 1-100. Default: 20 |
| `pageToken` | string | query | no | Pagination token |

### Create reply

Posts a reply to an existing comment. The reply appears as a nested response under the parent comment. Returns the created comment resource.

```
POST /youtube/v3/comments
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `snippet` | object | yes | `{"parentId": "string", "textOriginal": "string"}` |

### Update comment

Edits the text content of an existing comment or reply. Returns the updated comment resource.

```
PUT /youtube/v3/comments
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Comment ID to update |
| `snippet` | object | yes | `{"textOriginal": "string"}` |

### Delete comment

Permanently deletes a comment or reply. This action cannot be undone.

```
DELETE /youtube/v3/comments
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `id` | string | query | yes | Comment ID to delete |

### Set moderation status

Changes the moderation status of a comment. Transitions a comment between published, held for review, and rejected states.

```
POST /youtube/v3/comments/setModerationStatus
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `id` | string | query | yes | Comment ID |
| `moderationStatus` | string | query | yes | Target status: `published`, `heldForReview`, `rejected` |

---

## Search

### Search content

Executes a text search across the channel's or platform's video content. Returns matching results ranked by the specified sort order. Each result includes the resource kind, ID, and snippet (title, description, thumbnails, publish date, channel info).

```
GET /youtube/v3/search
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `q` | string | query | no | Search query keyword |
| `channelId` | string | query | no | Restrict results to a specific channel |
| `part` | string | query | no | Resource parts: `snippet`. Default: `snippet`. |
| `order` | string | query | no | Sort order: `relevance`, `date`, `viewCount`, `rating`. Default: `relevance` |
| `maxResults` | integer | query | no | Maximum results, 1-50. Default: 25 |
| `pageToken` | string | query | no | Pagination token |
| `type` | string | query | no | Resource type filter: `video`, `channel`, `playlist`. Default: `video` |

---

## Video Categories

### List video categories

Returns the list of video categories available in a specified region. Each category includes its ID, title, and whether it is assignable to videos.

```
GET /youtube/v3/videoCategories
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `regionCode` | string | query | no | ISO 3166-1 alpha-2 country code. Default: `US` |
| `part` | string | query | no | Resource parts: `snippet`. Default: `snippet`. |

---

## Captions

### List captions

Returns the list of caption tracks available for a specific video. Each caption includes the track language, name, type (standard, ASR, forced), and whether it is a draft.

```
GET /youtube/v3/captions
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `videoId` | string | query | yes | Video ID to list captions for |
| `part` | string | query | no | Resource parts: `snippet`. Default: `snippet`. |

---

## Channel Sections

### List channel sections

Returns the sections configured on a channel's homepage. Each section defines a content grouping (e.g., recent uploads, popular uploads, playlists) with a title, position, and type.

```
GET /youtube/v3/channelSections
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `channelId` | string | query | yes | Channel ID |
| `part` | string | query | no | Comma-separated resource parts: `snippet`, `contentDetails`. Default: all parts. |

---

## Analytics

### Get analytics report

Returns analytics data for a channel or specific video over a date range. Supports multiple metrics and dimensional breakdowns. The response contains column headers and data rows matching the requested metrics.

```
GET /youtube/analytics/v2/reports
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `ids` | string | query | no | Channel identifier in format `channel=={channelId}` |
| `filters` | string | query | no | Filter expression, e.g. `video=={videoId}` |
| `metrics` | string | query | no | Comma-separated metrics: `views`, `estimatedMinutesWatched`, `likes`, `dislikes`, `comments`, `subscribersGained`, `subscribersLost`, `averageViewDuration` |
| `dimensions` | string | query | no | Comma-separated dimensions: `day`, `video`, `country` |
| `startDate` | string | query | no | Start date (YYYY-MM-DD) |
| `endDate` | string | query | no | End date (YYYY-MM-DD) |

---

## Errors

Error responses follow this format:

```json
{
  "error": {
    "code": 404,
    "message": "Video not found",
    "errors": [{"domain": "youtube.video", "reason": "videoNotFound"}]
  }
}
```

Common HTTP status codes:

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid parameters or malformed body) |
| 404 | Resource not found |
| 409 | Conflict (duplicate resource) |
