---
name: instagram-api-connector
description: >
  Instagram Graph API HTTP endpoints for Business/Creator account management,
  media operations, comments, stories, insights, hashtags, mentions, and
  content publishing.
---

# Instagram Graph API

## Base URL

| Variable | Purpose |
|----------|---------|
| `INSTAGRAM_API_URL` | Base URL for all requests |

All paths below are relative to `INSTAGRAM_API_URL`.

---

## Health

```
GET /health
```

Returns `{"status": "ok"}`.

---

## Users

### Get user profile

Returns the full profile for a Business or Creator account, including the account's username, display name, biography, profile picture URL, follower and following counts, and total media count. Supports field selection to limit the returned properties.

```
GET /{user_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `user_id` | string | path | yes | User ID |
| `fields` | string | query | no | Comma-separated fields (e.g. `id,username,name,biography,followers_count,follows_count,media_count`) |

### Search users

Searches across all user accounts by username and display name. Performs a case-insensitive partial match against both fields. Returns an array of matching user profile objects, each containing the user's ID, username, name, biography, account type, and media count.

```
GET /ig_user_search
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `q` | string | query | yes | Search query. Matches against username and name. Partial match, case-insensitive. |

### Update user profile

Modifies mutable profile fields on a Business or Creator account. Accepts any combination of biography, website URL, and display name. Returns the updated user profile object. At least one field must be provided in the request body; otherwise returns a 400 error.

```
PUT /{user_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `user_id` | string | path | yes | User ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `biography` | string | no | Profile biography text |
| `website` | string | no | Profile website URL |
| `name` | string | no | Display name |

At least one field must be provided.

---

## Media

### List user media

Returns a paginated list of media objects published by the specified user. Each media object includes the media ID, type (IMAGE, VIDEO, or CAROUSEL_ALBUM), caption, permalink, timestamp, like count, and comments count. Supports filtering by media type and field selection.

```
GET /{user_id}/media
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `user_id` | string | path | yes | User ID |
| `media_type` | string | query | no | Filter by type: `IMAGE`, `VIDEO`, `CAROUSEL_ALBUM` |
| `fields` | string | query | no | Comma-separated fields to return |
| `limit` | integer | query | no | Max results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get media

Returns the full details of a single media object, including its ID, type, caption, media URL, permalink, timestamp, like count, comments count, and owner information. Supports field selection to limit the returned properties.

```
GET /media/{media_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `media_id` | string | path | yes | Media ID |
| `fields` | string | query | no | Comma-separated fields to return |

### Delete media

Permanently removes a media object. Returns a success confirmation on deletion. Returns a 404 error if the media ID does not exist.

```
DELETE /media/{media_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `media_id` | string | path | yes | Media ID |

### Get carousel children

Returns the ordered list of child media items belonging to a CAROUSEL_ALBUM media object. Each child includes its own ID, media type, media URL, and timestamp. Returns a 404 error if the media ID does not exist or is not a carousel.

```
GET /media/{media_id}/children
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `media_id` | string | path | yes | Media ID (must be `CAROUSEL_ALBUM` type) |
| `fields` | string | query | no | Comma-separated fields to return |

---

## Comments

### List comments on media

Returns a paginated list of top-level comments on a media object. Each comment includes the comment ID, text, username of the commenter, timestamp, like count, and reply count. Results are ordered chronologically. Supports field selection and pagination.

```
GET /media/{media_id}/comments
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `media_id` | string | path | yes | Media ID |
| `fields` | string | query | no | Comma-separated fields to return |
| `limit` | integer | query | no | Max results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get comment

Returns the full details of a single comment, including the comment ID, text, username, timestamp, like count, reply count, and hidden status. Supports field selection.

```
GET /comment/{comment_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `comment_id` | string | path | yes | Comment ID |
| `fields` | string | query | no | Comma-separated fields to return |

### Get comment replies

Returns a paginated list of replies to a specific comment. Each reply includes its ID, text, username, timestamp, and like count. Results are ordered chronologically. Supports field selection and pagination.

```
GET /comment/{comment_id}/replies
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `comment_id` | string | path | yes | Comment ID |
| `fields` | string | query | no | Comma-separated fields to return |
| `limit` | integer | query | no | Max results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Create comment

Creates a new comment on a media object. If `parent_id` is provided, the comment is created as a reply to an existing comment. Returns the newly created comment object with its assigned ID and timestamp.

```
POST /media/{media_id}/comments
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `media_id` | string | path | yes | Media ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | yes | Comment text |
| `parent_id` | string | no | Parent comment ID (for replies) |

### Delete comment

Permanently removes a comment from a media object. Returns a success confirmation on deletion. Returns a 404 error if the media or comment ID does not exist.

```
DELETE /media/{media_id}/comments/{comment_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `media_id` | string | path | yes | Media ID |
| `comment_id` | string | path | yes | Comment ID |

### Hide/unhide comment

Toggles the visibility of a comment on a media object. Hidden comments are not visible to the public but remain accessible via the API. Returns the updated comment object with the new hidden status.

```
PUT /media/{media_id}/comments/{comment_id}/hide
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `media_id` | string | path | yes | Media ID |
| `comment_id` | string | path | yes | Comment ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `hide` | boolean | yes | `true` to hide, `false` to unhide |

---

## Stories

### List user stories

Returns the current stories for a user account. Each story object includes its ID, media type, media URL, caption, and timestamp. Stories are ephemeral and only available for their active duration. Supports field selection.

```
GET /{user_id}/stories
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `user_id` | string | path | yes | User ID |
| `fields` | string | query | no | Comma-separated fields to return |

### Get story

Returns the full details of a single story object, including its ID, media type, media URL, caption, and timestamp. Returns a 404 error if the story ID does not exist or has expired.

```
GET /stories/{story_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `story_id` | string | path | yes | Story ID |
| `fields` | string | query | no | Comma-separated fields to return |

---

## Insights

### Get user insights

Returns engagement and audience metrics for a user account over a specified period. Available metrics include impressions, reach, follower count, profile views, and website clicks. Each metric is returned with its name, period, values array, and title.

```
GET /{user_id}/insights
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `user_id` | string | path | yes | User ID |
| `metric` | string | query | no | Comma-separated metrics: `impressions`, `reach`, `follower_count`, `profile_views`, `website_clicks` |
| `period` | string | query | no | Time period: `day`, `week`, `days_28`, `lifetime`. Default: `day` |

### Get media insights

Returns performance metrics for a single media object. Available metrics include impressions, reach, engagement, saved count, shares, profile visits, and follows attributed to the media. Each metric is returned with its name, period, and values array.

```
GET /media/{media_id}/insights
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `media_id` | string | path | yes | Media ID |
| `metric` | string | query | no | Comma-separated metrics: `impressions`, `reach`, `engagement`, `saved`, `shares`, `profile_visits`, `follows` |

---

## Hashtags

### Search hashtags

Searches for hashtag objects by name. Returns an array of matching hashtag objects, each containing the hashtag ID and name. The query is matched against the hashtag name string.

```
GET /ig_hashtag_search
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `q` | string | query | yes | Search query |

### Get hashtag

Returns the details of a single hashtag object, including its ID, name, and total media count (the number of media objects tagged with this hashtag). Supports field selection.

```
GET /hashtag/{hashtag_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `hashtag_id` | string | path | yes | Hashtag ID |
| `fields` | string | query | no | Comma-separated fields to return |

### Get hashtag recent media

Returns a paginated list of the most recently published media objects tagged with a specific hashtag. Each media object includes its ID, type, caption, permalink, and timestamp. Requires a `user_id` parameter identifying the account performing the lookup. Supports field selection.

```
GET /hashtag/{hashtag_id}/recent_media
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `hashtag_id` | string | path | yes | Hashtag ID |
| `user_id` | string | query | yes | User ID performing the search |
| `fields` | string | query | no | Comma-separated fields to return |
| `limit` | integer | query | no | Max results, 1-50. Default: 25 |

---

## Mentions

### List tagged media

Returns a paginated list of media objects in which the specified user has been tagged (mentioned). Each media object includes its ID, type, caption, permalink, and the tagger's information. Supports field selection and pagination.

```
GET /{user_id}/tags
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `user_id` | string | path | yes | User ID |
| `fields` | string | query | no | Comma-separated fields to return |
| `limit` | integer | query | no | Max results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

---

## Content Publishing

### Create media container

Creates a media container that stages content for publishing. For IMAGE type, provide `image_url`. For VIDEO type, provide `video_url`. For CAROUSEL_ALBUM type, provide an array of previously created child container IDs in `children`. Returns the container object with its assigned ID and a status of `IN_PROGRESS`.

```
POST /{user_id}/media
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `user_id` | string | path | yes | User ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `media_type` | string | no | `IMAGE`, `VIDEO`, or `CAROUSEL_ALBUM`. Default: `IMAGE` |
| `image_url` | string | no | Image URL (for `IMAGE` type) |
| `video_url` | string | no | Video URL (for `VIDEO` type) |
| `caption` | string | no | Post caption |
| `children` | array of strings | no | Child container IDs (for `CAROUSEL_ALBUM` type) |

### Get container status

Returns the current status of a media container. The status field indicates the container's publishing readiness: `IN_PROGRESS`, `FINISHED`, or `ERROR`. If the status is `ERROR`, the `status_code` field contains the error reason.

```
GET /container/{container_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `container_id` | string | path | yes | Container ID |

### Publish media container

Publishes a finished media container as a live media object on the user's profile. The container must have a status of `FINISHED` before publishing. Returns the newly created media object with its permanent media ID.

```
POST /{user_id}/media_publish
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `user_id` | string | path | yes | User ID |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `creation_id` | string | yes | Container ID to publish |

---

## Errors

Error responses follow this format:

```json
{
  "error": {
    "message": "Description of the error",
    "type": "IGApiException",
    "code": 100
  }
}
```

Common HTTP status codes:

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid parameters) |
| 404 | Resource not found |
