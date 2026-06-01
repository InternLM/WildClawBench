# Ring API Guide

Detailed patterns and examples for working with the Ring home security API.

## Base URL

Set via the `RING_API_URL` environment variable (e.g. `http://ring-api:8008`).

## Devices

```bash
# List all devices (doorbots, stickup_cams, chimes)
curl "$RING_API_URL/clients_api/ring_devices"

# Get a specific device
curl "$RING_API_URL/clients_api/doorbots/987001"

# Get device health (battery, WiFi signal)
curl "$RING_API_URL/clients_api/doorbots/987005/health"

# Update device settings (motion sensitivity)
curl -X PUT "$RING_API_URL/clients_api/doorbots/987001/settings" \
  -H "Content-Type: application/json" \
  -d '{"motion_sensitivity": 9}'

# Toggle LED off
curl -X PUT "$RING_API_URL/clients_api/doorbots/987004/settings" \
  -H "Content-Type: application/json" \
  -d '{"led_status": "off"}'

# Enable people detection
curl -X PUT "$RING_API_URL/clients_api/doorbots/987003/settings" \
  -H "Content-Type: application/json" \
  -d '{"people_detection_enabled": true}'
```

## Locations

```bash
# Get location info
curl "$RING_API_URL/clients_api/locations/loc_martinez_001"

# List devices at a location
curl "$RING_API_URL/clients_api/locations/loc_martinez_001/devices"

# Get current security mode
curl "$RING_API_URL/clients_api/locations/loc_martinez_001/mode"

# Set mode to "away"
curl -X PUT "$RING_API_URL/clients_api/locations/loc_martinez_001/mode" \
  -H "Content-Type: application/json" \
  -d '{"mode": "away"}'

# Set mode to "home"
curl -X PUT "$RING_API_URL/clients_api/locations/loc_martinez_001/mode" \
  -H "Content-Type: application/json" \
  -d '{"mode": "home"}'

# Set mode to "disarmed"
curl -X PUT "$RING_API_URL/clients_api/locations/loc_martinez_001/mode" \
  -H "Content-Type: application/json" \
  -d '{"mode": "disarmed"}'
```

## Active Dings

```bash
# List currently active alerts (live doorbell rings, motion events)
curl "$RING_API_URL/clients_api/dings/active"
```

## Event History

```bash
# List all events for the front door doorbell
curl "$RING_API_URL/clients_api/doorbots/987001/history"

# Filter by event type (ding = doorbell press)
curl "$RING_API_URL/clients_api/doorbots/987001/history?kind=ding"

# Filter by motion events only
curl "$RING_API_URL/clients_api/doorbots/987001/history?kind=motion"

# Filter by package detection
curl "$RING_API_URL/clients_api/doorbots/987001/history?kind=package_detected"

# Date range filter (today only)
curl "$RING_API_URL/clients_api/doorbots/987001/history?date_from=2025-04-28T00:00:00.000Z&date_to=2025-04-28T23:59:59.000Z"

# Last 24 hours
curl "$RING_API_URL/clients_api/doorbots/987001/history?date_from=2025-04-27T14:30:00.000Z"

# Pagination
curl "$RING_API_URL/clients_api/doorbots/987001/history?limit=5&offset=0"

# Driveway cam events
curl "$RING_API_URL/clients_api/doorbots/987003/history"

# Backyard cam events
curl "$RING_API_URL/clients_api/doorbots/987002/history"

# Get a single event
curl "$RING_API_URL/clients_api/dings/7001"

# Get recording URL for an event
curl "$RING_API_URL/clients_api/dings/7001/recording"
```

## Recordings

```bash
# List all recordings for the doorbell
curl "$RING_API_URL/clients_api/doorbots/987001/recordings"

# List recordings for the driveway cam
curl "$RING_API_URL/clients_api/doorbots/987003/recordings"

# Filter recordings by date range
curl "$RING_API_URL/clients_api/doorbots/987001/recordings?date_from=2025-04-25T00:00:00.000Z&date_to=2025-04-26T23:59:59.000Z"
```

## Shared Users

```bash
# List all users with access
curl "$RING_API_URL/clients_api/locations/loc_martinez_001/users"

# Get specific user (owner)
curl "$RING_API_URL/clients_api/locations/loc_martinez_001/users/100001"

# Get guest user
curl "$RING_API_URL/clients_api/locations/loc_martinez_001/users/100003"
```

## Chime Settings

```bash
# Get chime settings
curl "$RING_API_URL/clients_api/chimes/987006/settings"

# Link chime to a doorbell
curl -X PUT "$RING_API_URL/clients_api/chimes/987006/link" \
  -H "Content-Type: application/json" \
  -d '{"doorbell_id": 987001}'

# Unlink chime from a doorbell
curl -X PUT "$RING_API_URL/clients_api/chimes/987006/unlink" \
  -H "Content-Type: application/json" \
  -d '{"doorbell_id": 987001}'
```

## Motion Zones

```bash
# List motion zones for the doorbell
curl "$RING_API_URL/clients_api/doorbots/987001/motion_zones"

# List motion zones for the driveway cam
curl "$RING_API_URL/clients_api/doorbots/987003/motion_zones"
```

## Notification Preferences

```bash
# List all notification preferences
curl "$RING_API_URL/clients_api/notifications"

# Get preferences for a specific device
curl "$RING_API_URL/clients_api/notifications/987001"

# Get preferences for living room (alerts disabled)
curl "$RING_API_URL/clients_api/notifications/987004"

# Toggle motion alerts off for backyard cam
curl -X PUT "$RING_API_URL/clients_api/notifications/987002" \
  -H "Content-Type: application/json" \
  -d '{"motion_alerts": false}'

# Enable motion alerts for living room
curl -X PUT "$RING_API_URL/clients_api/notifications/987004" \
  -H "Content-Type: application/json" \
  -d '{"motion_alerts": true}'
```

## Siren Control

```bash
# Activate siren on driveway cam (15 seconds)
curl -X POST "$RING_API_URL/clients_api/doorbots/987003/siren_on" \
  -H "Content-Type: application/json" \
  -d '{"duration_seconds": 15}'

# Deactivate siren
curl -X POST "$RING_API_URL/clients_api/doorbots/987003/siren_off"
```

## Floodlight Control

```bash
# Turn floodlight on
curl -X PUT "$RING_API_URL/clients_api/doorbots/987003/floodlight_light_on" \
  -H "Content-Type: application/json" \
  -d '{"on": true}'

# Turn floodlight off
curl -X PUT "$RING_API_URL/clients_api/doorbots/987003/floodlight_light_on" \
  -H "Content-Type: application/json" \
  -d '{"on": false}'
```

## Common Patterns

### Investigate a Suspicious Nighttime Event

```python
import json
import os
import urllib.request

BASE = os.environ["RING_API_URL"]

def api_get(path, params=None):
    url = f"{BASE}{path}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())

def api_put(path, data):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# Check nighttime events on all outdoor cameras
for device_id in [987001, 987003, 987005]:
    events = api_get(f"/clients_api/doorbots/{device_id}/history",
                     {"date_from": "2025-04-28T00:00:00.000Z", "date_to": "2025-04-28T06:00:00.000Z"})
    for event in events.get("results", []):
        rec = api_get(f"/clients_api/dings/{event['id']}/recording")
        print(f"[{event['created_at']}] {event['kind']} on device {device_id} - {rec['recording_url']}")
```

### Morning Security Status Check

```python
# Get overall system status
location = api_get("/clients_api/locations/loc_martinez_001")
mode = api_get("/clients_api/locations/loc_martinez_001/mode")
print(f"Mode: {mode['mode']}")

# Check device health across all devices
devices = api_get("/clients_api/ring_devices")
all_devices = devices.get("doorbots", []) + devices.get("stickup_cams", []) + devices.get("chimes", [])
for dev in all_devices:
    health = api_get(f"/clients_api/doorbots/{dev['id']}/health")
    h = health["device_health"]
    battery = h.get("battery_life")
    wifi = h.get("wifi_signal_category", "unknown")
    status = "OK"
    if battery is not None and battery < 30:
        status = f"LOW BATTERY ({battery}%)"
    if wifi == "poor":
        status = f"WEAK WIFI ({h.get('wifi_signal_strength')}dBm)"
    print(f"  {dev['description']}: {status}")
```

### Set Away Mode and Increase Sensitivity

```python
# Family leaving — switch to away mode and boost sensitivity
api_put("/clients_api/locations/loc_martinez_001/mode", {"mode": "away"})

# Increase sensitivity on outdoor cameras
for device_id in [987001, 987003, 987005]:
    api_put(f"/clients_api/doorbots/{device_id}/settings", {"motion_sensitivity": 9})

# Verify mode changed
mode = api_get("/clients_api/locations/loc_martinez_001/mode")
print(f"System armed: mode={mode['mode']}")
```
