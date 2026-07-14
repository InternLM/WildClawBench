---
name: ring-api-connector
description: >
  Ring API HTTP endpoints for home security device management, event history,
  recordings, motion settings, location modes, and notification preferences.
---

# Ring API

## Base URL

| Variable | Purpose |
|----------|---------|
| `RING_API_URL` | Base URL for all requests |

All paths below are relative to `RING_API_URL`.

---

## Health

```
GET /health
```

Returns `{"status": "ok"}`.

---

## Devices

### List all devices

Returns a complete inventory of all Ring devices across all locations. Each device includes its ID, type (doorbell, camera, chime, floodlight), description, firmware version, location, battery status, and current settings.

```
GET /clients_api/ring_devices
```

### Get device

Returns the full details of a single device, including its type, description, firmware version, battery level, WiFi signal strength, location association, and all current configuration settings.

```
GET /clients_api/doorbots/{device_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Device identifier |

### Get device health

Returns the health diagnostics for a specific device, including battery percentage, WiFi signal strength (RSSI), firmware version, and last seen timestamp.

```
GET /clients_api/doorbots/{device_id}/health
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Device identifier |

### Update device settings

Modifies the configuration settings for a device. Supports motion detection sensitivity, detection feature toggles, LED behavior, and light scheduling. Returns the updated settings object.

```
PUT /clients_api/doorbots/{device_id}/settings
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Device identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `motion_sensitivity` | integer | no | Motion sensitivity level, 1-10 |
| `motion_detection_enabled` | boolean | no | Enable or disable motion detection |
| `people_detection_enabled` | boolean | no | Enable or disable people-only detection |
| `package_detection_enabled` | boolean | no | Enable or disable package detection |
| `led_status` | string | no | LED indicator: `on` or `off` |
| `light_schedule_enabled` | boolean | no | Enable or disable the light schedule |
| `light_on_duration_seconds` | integer | no | Duration (in seconds) the light stays on after triggering |

---

## Locations

### Get location

Returns the details of a specific location, including its name, address, timezone, geocoordinates, and current security mode.

```
GET /clients_api/locations/{location_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `location_id` | string | path | yes | Location identifier |

### List location devices

Returns all devices associated with a specific location.

```
GET /clients_api/locations/{location_id}/devices
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `location_id` | string | path | yes | Location identifier |

### Get location mode

Returns the current security mode for a location. The mode determines the behavior of all devices at that location (armed, monitoring sensitivity, notification level).

```
GET /clients_api/locations/{location_id}/mode
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `location_id` | string | path | yes | Location identifier |

### Set location mode

Changes the security mode for a location. All devices at the location adjust their behavior according to the new mode. Returns the updated mode.

```
PUT /clients_api/locations/{location_id}/mode
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `location_id` | string | path | yes | Location identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mode` | string | yes | Security mode: `home`, `away`, or `disarmed` |

---

## Active Dings

### List active dings

Returns all currently active doorbell rings and motion events across all devices. Active dings are real-time events that have not yet expired. Each ding includes the device ID, event type, timestamp, and SIP endpoint information.

```
GET /clients_api/dings/active
```

---

## Events

### List event history

Returns a paginated list of historical events for a specific device. Events include doorbell presses, motion detections, person detections, and package detections. Each event includes its ID, type, timestamp, duration, and answered status.

```
GET /clients_api/doorbots/{device_id}/history
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Device identifier |
| `kind` | string | query | no | Filter by event type: `motion`, `ding`, `person_detected`, `package_detected` |
| `date_from` | string | query | no | Filter events from this date (ISO 8601) |
| `date_to` | string | query | no | Filter events until this date (ISO 8601) |
| `limit` | integer | query | no | Maximum results, 1-100. Default: 20 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get event

Returns the full details of a single event, including the event type, device ID, timestamp, duration, answered status, and favorite flag.

```
GET /clients_api/dings/{event_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `event_id` | string | path | yes | Event identifier |

### Get event recording

Returns the recording associated with a specific event. The response includes a pre-signed URL to the video file and its duration.

```
GET /clients_api/dings/{event_id}/recording
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `event_id` | string | path | yes | Event identifier |

---

## Recordings

### List device recordings

Returns a list of recorded video clips for a specific device within an optional date range. Each recording includes its ID, timestamp, duration, and event type.

```
GET /clients_api/doorbots/{device_id}/recordings
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Device identifier |
| `date_from` | string | query | no | Filter recordings from this date (ISO 8601) |
| `date_to` | string | query | no | Filter recordings until this date (ISO 8601) |

---

## Shared Users

### List shared users

Returns the list of users who have shared access to a location. Each user includes their ID, name, email, and permission level.

```
GET /clients_api/locations/{location_id}/users
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `location_id` | string | path | yes | Location identifier |

### Get shared user

Returns the details of a specific shared user, including their name, email, and permission level at the location.

```
GET /clients_api/locations/{location_id}/users/{user_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `location_id` | string | path | yes | Location identifier |
| `user_id` | string | path | yes | Shared user identifier |

---

## Chimes

### Get chime settings

Returns the current settings for a chime device, including linked doorbells, volume level, and chime tone.

```
GET /clients_api/chimes/{device_id}/settings
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Chime device identifier |

### Link chime to doorbell

Associates a chime device with a doorbell so the chime sounds when the doorbell is pressed.

```
PUT /clients_api/chimes/{device_id}/link
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Chime device identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `doorbell_id` | integer | yes | ID of the doorbell to link |

### Unlink chime from doorbell

Removes the association between a chime device and a doorbell.

```
PUT /clients_api/chimes/{device_id}/unlink
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Chime device identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `doorbell_id` | integer | yes | ID of the doorbell to unlink |

---

## Motion Zones

### List motion zones

Returns the configured motion detection zones for a device. Each zone defines a polygonal region within the camera's field of view with independent sensitivity settings.

```
GET /clients_api/doorbots/{device_id}/motion_zones
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Device identifier |

---

## Notifications

### List all notification preferences

Returns the notification preferences for all devices, including which event types trigger push notifications.

```
GET /clients_api/notifications
```

### Get device notification preferences

Returns the notification preferences for a specific device.

```
GET /clients_api/notifications/{device_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Device identifier |

### Update notification preferences

Updates the push notification settings for a specific device. Controls which event types generate alerts. Returns the updated preferences.

```
PUT /clients_api/notifications/{device_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Device identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `motion_alerts` | boolean | no | Enable alerts for motion events |
| `ding_alerts` | boolean | no | Enable alerts for doorbell presses |
| `person_alerts` | boolean | no | Enable alerts for person detections |
| `package_alerts` | boolean | no | Enable alerts for package detections |

---

## Siren

### Activate siren

Activates the siren on a device for the specified duration. The siren automatically deactivates after the duration expires.

```
POST /clients_api/doorbots/{device_id}/siren_on
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Device identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `duration_seconds` | integer | no | Siren duration in seconds. Default: 30 |

### Deactivate siren

Immediately stops the siren on a device.

```
POST /clients_api/doorbots/{device_id}/siren_off
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Device identifier |

---

## Floodlight

### Control floodlight

Turns a device's floodlight on or off.

```
PUT /clients_api/doorbots/{device_id}/floodlight_light_on
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `device_id` | string | path | yes | Device identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `on` | boolean | yes | `true` to turn on, `false` to turn off |

---

## Errors

Error responses follow this format:

```json
{
  "error": "Description of the error",
  "status": 404
}
```

Common HTTP status codes:

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid parameters) |
| 404 | Resource not found |
