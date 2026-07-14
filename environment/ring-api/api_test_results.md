# Ring API (Mock) - Full API Test Results


## 1. GET /health (Health Check)


```
curl -s -X GET "http://localhost:8010/health"
```


**Status:** 200


```json
{
  "status": "ok"
}
```


---


## 2. GET /clients_api/ring_devices (List All Devices)


```
curl -s -X GET "http://localhost:8010/clients_api/ring_devices"
```


**Status:** 200


```json
{
  "doorbots": [
    {
      "id": 987001,
      "description": "Front Door",
      "device_id": "doorbell_front",
      "address": "4821 Ridgeview Dr",
      "kind": "lpd_v2",
      "firmware_version": "3.22.8",
      "battery_life": 82,
      "external_connection": true,
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "motions_enabled": true,
        "show_recordings": true,
        "advanced_motion_enabled": true,
        "people_only_enabled": true,
        "shadow_correction_enabled": true,
        "motion_message_enabled": false
      },
      "motion_snooze": null,
      "ring_snooze": null,
      "owned": true,
      "owner": {
        "id": 100001,
        "first_name": "Carlos",
        "last_name": "Martinez"
      },
      "led_status": "on",
      "night_mode_status": "enabled",
      "settings": {
        "doorbell_volume": 8,
        "chime_settings": {
          "type": "mechanical",
          "enabled": true,
          "duration": 5
        },
        "motion_detection_enabled": true,
        "motion_sensitivity": 7,
        "people_detection_enabled": true,
        "package_detection_enabled": true
      },
      "created_at": "2022-06-20T14:30:00.000Z"
    }
  ],
  "stickup_cams": [
    {
      "id": 987002,
      "description": "Backyard Patio",
      "device_id": "cam_backyard",
      "address": "4821 Ridgeview Dr",
      "kind": "stickup_cam_v4",
      "firmware_version": "3.20.5",
      "battery_life": 67,
      "external_connection": false,
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "motions_enabled": true,
        "show_recordings": true,
        "advanced_motion_enabled": true,
        "people_only_enabled": false,
        "shadow_correction_enabled": true,
        "night_vision_enabled": true,
        "motion_message_enabled": false
      },
      "motion_snooze": null,
      "led_status": "on",
      "night_mode_status": "enabled",
      "owned": true,
      "owner": {
        "id": 100001,
        "first_name": "Carlos",
        "last_name": "Martinez"
      },
      "settings": {
        "motion_detection_enabled": true,
        "motion_sensitivity": 5,
        "people_detection_enabled": false,
        "package_detection_enabled": false
      },
      "created_at": "2022-07-10T09:00:00.000Z"
    },
    {
      "id": 987003,
      "description": "Driveway",
      "device_id": "cam_driveway",
      "address": "4821 Ridgeview Dr",
      "kind": "floodlight_v2",
      "firmware_version": "3.21.1",
      "battery_life": null,
      "external_connection": true,
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "motions_enabled": true,
        "show_recordings": true,
        "advanced_motion_enabled": true,
        "people_only_enabled": true,
        "shadow_correction_enabled": true,
        "night_vision_enabled": true,
        "motion_message_enabled": false
      },
      "motion_snooze": null,
      "led_status": "on",
      "night_mode_status": "enabled",
      "siren_status": {
        "seconds_remaining": 0
      },
      "floodlight_status": {
        "on": false
      },
      "owned": true,
      "owner": {
        "id": 100001,
        "first_name": "Carlos",
        "last_name": "Martinez"
      },
      "settings": {
        "motion_detection_enabled": true,
        "motion_sensitivity": 8,
        "people_detection_enabled": true,
        "package_detection_enabled": false,
        "light_schedule_enabled": true,
        "light_on_duration_seconds": 30
      },
      "wifi_signal_strength": -68,
      "wifi_signal_category": "poor",
      "created_at": "2022-06-20T15:00:00.000Z"
    },
    {
      "id": 987004,
      "description": "Living Room",
      "device_id": "cam_living_room",
      "address": "4821 Ridgeview Dr",
      "kind": "stickup_cam_mini",
      "firmware_version": "3.19.8",
      "battery_life": null,
      "external_connection": true,
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "motions_enabled": true,
        "show_recordings": true,
        "advanced_motion_enabled": false,
        "people_only_enabled": false,
        "shadow_correction_enabled": false,
        "night_vision_enabled": true,
        "motion_message_enabled": false
      },
      "motion_snooze": null,
      "led_status": "off",
      "night_mode_status": "enabled",
      "owned": true,
      "owner": {
        "id": 100001,
        "first_name": "Carlos",
        "last_name": "Martinez"
      },
      "settings": {
        "motion_detection_enabled": true,
        "motion_sensitivity": 3,
        "people_detection_enabled": false,
        "package_detection_enabled": false
      },
      "created_at": "2023-01-05T11:30:00.000Z"
    },
    {
      "id": 987005,
      "description": "Side Gate",
      "device_id": "cam_side_gate",
      "address": "4821 Ridgeview Dr",
      "kind": "spotlight_cam_v2",
      "firmware_version": "3.18.2",
      "battery_life": 23,
      "external_connection": false,
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "motions_enabled": true,
        "show_recordings": true,
        "advanced_motion_enabled": true,
        "people_only_enabled": false,
        "shadow_correction_enabled": true,
        "night_vision_enabled": true,
        "motion_message_enabled": false
      },
      "motion_snooze": null,
      "led_status": "on",
      "night_mode_status": "enabled",
      "siren_status": {
        "seconds_remaining": 0
      },
      "owned": true,
      "owner": {
        "id": 100001,
        "first_name": "Carlos",
        "last_name": "Martinez"
      },
      "settings": {
        "motion_detection_enabled": true,
        "motion_sensitivity": 6,
        "people_detection_enabled": false,
        "package_detection_enabled": false
      },
      "created_at": "2023-03-18T16:45:00.000Z"
    }
  ],
  "chimes": [
    {
      "id": 987006,
      "description": "Hallway Chime",
      "device_id": "chime_hallway",
      "address": "4821 Ridgeview Dr",
      "kind": "chime_pro_v2",
      "firmware_version": "3.16.4",
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "ringtones_enabled": true,
        "wifi_extender_enabled": true
      },
      "owned": true,
      "owner": {
        "id": 100001,
        "first_name": "Carlos",
        "last_name": "Martinez"
      },
      "settings": {
        "volume": 7,
        "ding_audio_id": "ring_default",
        "ding_audio_user_id": null,
        "motion_audio_id": null,
        "motion_audio_user_id": null,
        "linked_doorbots": [
          987001
        ]
      },
      "wifi_signal_strength": -42,
      "wifi_signal_category": "good",
      "created_at": "2022-06-20T14:45:00.000Z"
    }
  ]
}
```


---


## 3. GET /clients_api/doorbots/987001 (Get Device - Doorbell Front)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987001"
```


**Status:** 200


```json
{
  "type": "device",
  "device_type": "doorbots",
  "device": {
    "id": 987001,
    "description": "Front Door",
    "device_id": "doorbell_front",
    "address": "4821 Ridgeview Dr",
    "kind": "lpd_v2",
    "firmware_version": "3.22.8",
    "battery_life": 82,
    "external_connection": true,
    "latitude": 30.2241,
    "longitude": -97.8416,
    "location_id": "loc_martinez_001",
    "time_zone": "America/Chicago",
    "alerts": {
      "connection": "online"
    },
    "features": {
      "motions_enabled": true,
      "show_recordings": true,
      "advanced_motion_enabled": true,
      "people_only_enabled": true,
      "shadow_correction_enabled": true,
      "motion_message_enabled": false
    },
    "motion_snooze": null,
    "ring_snooze": null,
    "owned": true,
    "owner": {
      "id": 100001,
      "first_name": "Carlos",
      "last_name": "Martinez"
    },
    "led_status": "on",
    "night_mode_status": "enabled",
    "settings": {
      "doorbell_volume": 8,
      "chime_settings": {
        "type": "mechanical",
        "enabled": true,
        "duration": 5
      },
      "motion_detection_enabled": true,
      "motion_sensitivity": 7,
      "people_detection_enabled": true,
      "package_detection_enabled": true
    },
    "created_at": "2022-06-20T14:30:00.000Z"
  }
}
```


---


## 4. GET /clients_api/doorbots/987003 (Get Device - Driveway Cam)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987003"
```


**Status:** 200


```json
{
  "type": "device",
  "device_type": "stickup_cams",
  "device": {
    "id": 987003,
    "description": "Driveway",
    "device_id": "cam_driveway",
    "address": "4821 Ridgeview Dr",
    "kind": "floodlight_v2",
    "firmware_version": "3.21.1",
    "battery_life": null,
    "external_connection": true,
    "latitude": 30.2241,
    "longitude": -97.8416,
    "location_id": "loc_martinez_001",
    "time_zone": "America/Chicago",
    "alerts": {
      "connection": "online"
    },
    "features": {
      "motions_enabled": true,
      "show_recordings": true,
      "advanced_motion_enabled": true,
      "people_only_enabled": true,
      "shadow_correction_enabled": true,
      "night_vision_enabled": true,
      "motion_message_enabled": false
    },
    "motion_snooze": null,
    "led_status": "on",
    "night_mode_status": "enabled",
    "siren_status": {
      "seconds_remaining": 0
    },
    "floodlight_status": {
      "on": false
    },
    "owned": true,
    "owner": {
      "id": 100001,
      "first_name": "Carlos",
      "last_name": "Martinez"
    },
    "settings": {
      "motion_detection_enabled": true,
      "motion_sensitivity": 8,
      "people_detection_enabled": true,
      "package_detection_enabled": false,
      "light_schedule_enabled": true,
      "light_on_duration_seconds": 30
    },
    "wifi_signal_strength": -68,
    "wifi_signal_category": "poor",
    "created_at": "2022-06-20T15:00:00.000Z"
  }
}
```


---


## 5. GET /clients_api/doorbots/987005 (Get Device - Side Gate)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987005"
```


**Status:** 200


```json
{
  "type": "device",
  "device_type": "stickup_cams",
  "device": {
    "id": 987005,
    "description": "Side Gate",
    "device_id": "cam_side_gate",
    "address": "4821 Ridgeview Dr",
    "kind": "spotlight_cam_v2",
    "firmware_version": "3.18.2",
    "battery_life": 23,
    "external_connection": false,
    "latitude": 30.2241,
    "longitude": -97.8416,
    "location_id": "loc_martinez_001",
    "time_zone": "America/Chicago",
    "alerts": {
      "connection": "online"
    },
    "features": {
      "motions_enabled": true,
      "show_recordings": true,
      "advanced_motion_enabled": true,
      "people_only_enabled": false,
      "shadow_correction_enabled": true,
      "night_vision_enabled": true,
      "motion_message_enabled": false
    },
    "motion_snooze": null,
    "led_status": "on",
    "night_mode_status": "enabled",
    "siren_status": {
      "seconds_remaining": 0
    },
    "owned": true,
    "owner": {
      "id": 100001,
      "first_name": "Carlos",
      "last_name": "Martinez"
    },
    "settings": {
      "motion_detection_enabled": true,
      "motion_sensitivity": 6,
      "people_detection_enabled": false,
      "package_detection_enabled": false
    },
    "created_at": "2023-03-18T16:45:00.000Z"
  }
}
```


---


## 6. GET /clients_api/doorbots/987006 (Get Device - Chime)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987006"
```


**Status:** 200


```json
{
  "type": "device",
  "device_type": "chimes",
  "device": {
    "id": 987006,
    "description": "Hallway Chime",
    "device_id": "chime_hallway",
    "address": "4821 Ridgeview Dr",
    "kind": "chime_pro_v2",
    "firmware_version": "3.16.4",
    "latitude": 30.2241,
    "longitude": -97.8416,
    "location_id": "loc_martinez_001",
    "time_zone": "America/Chicago",
    "alerts": {
      "connection": "online"
    },
    "features": {
      "ringtones_enabled": true,
      "wifi_extender_enabled": true
    },
    "owned": true,
    "owner": {
      "id": 100001,
      "first_name": "Carlos",
      "last_name": "Martinez"
    },
    "settings": {
      "volume": 7,
      "ding_audio_id": "ring_default",
      "ding_audio_user_id": null,
      "motion_audio_id": null,
      "motion_audio_user_id": null,
      "linked_doorbots": [
        987001
      ]
    },
    "wifi_signal_strength": -42,
    "wifi_signal_category": "good",
    "created_at": "2022-06-20T14:45:00.000Z"
  }
}
```


---


## 7. GET /clients_api/doorbots/999999 (Get Device - Not Found (404))


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/999999"
```


**Status:** 404


```json
{
  "error": "Device 999999 not found"
}
```


---


## 8. GET /clients_api/doorbots/987001/health (Device Health - Doorbell)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987001/health"
```


**Status:** 200


```json
{
  "type": "device_health",
  "device_health": {
    "device_id": 987001,
    "firmware_version": "3.22.8",
    "battery_life": 82,
    "wifi_signal_strength": -45,
    "wifi_signal_category": "good",
    "alerts": {
      "connection": "online"
    },
    "external_connection": true
  }
}
```


---


## 9. GET /clients_api/doorbots/987003/health (Device Health - Driveway (weak WiFi))


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987003/health"
```


**Status:** 200


```json
{
  "type": "device_health",
  "device_health": {
    "device_id": 987003,
    "firmware_version": "3.21.1",
    "battery_life": null,
    "wifi_signal_strength": -68,
    "wifi_signal_category": "poor",
    "alerts": {
      "connection": "online"
    },
    "external_connection": true
  }
}
```


---


## 10. GET /clients_api/doorbots/987005/health (Device Health - Side Gate (low battery))


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987005/health"
```


**Status:** 200


```json
{
  "type": "device_health",
  "device_health": {
    "device_id": 987005,
    "firmware_version": "3.18.2",
    "battery_life": 23,
    "wifi_signal_strength": -45,
    "wifi_signal_category": "good",
    "alerts": {
      "connection": "online"
    },
    "external_connection": false
  }
}
```


---


## 11. GET /clients_api/doorbots/999999/health (Device Health - Not Found (404))


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/999999/health"
```


**Status:** 404


```json
{
  "error": "Device 999999 not found"
}
```


---


## 12. PUT /clients_api/doorbots/987001/settings (Update Settings - Motion Sensitivity)


```
curl -s -X PUT "http://localhost:8010/clients_api/doorbots/987001/settings" -H 'Content-Type: application/json' -d '{"motion_sensitivity": 9}'
```


**Status:** 200


```json
{
  "type": "device",
  "device_type": "doorbots",
  "device": {
    "id": 987001,
    "description": "Front Door",
    "device_id": "doorbell_front",
    "address": "4821 Ridgeview Dr",
    "kind": "lpd_v2",
    "firmware_version": "3.22.8",
    "battery_life": 82,
    "external_connection": true,
    "latitude": 30.2241,
    "longitude": -97.8416,
    "location_id": "loc_martinez_001",
    "time_zone": "America/Chicago",
    "alerts": {
      "connection": "online"
    },
    "features": {
      "motions_enabled": true,
      "show_recordings": true,
      "advanced_motion_enabled": true,
      "people_only_enabled": true,
      "shadow_correction_enabled": true,
      "motion_message_enabled": false
    },
    "motion_snooze": null,
    "ring_snooze": null,
    "owned": true,
    "owner": {
      "id": 100001,
      "first_name": "Carlos",
      "last_name": "Martinez"
    },
    "led_status": "on",
    "night_mode_status": "enabled",
    "settings": {
      "doorbell_volume": 8,
      "chime_settings": {
        "type": "mechanical",
        "enabled": true,
        "duration": 5
      },
      "motion_detection_enabled": true,
      "motion_sensitivity": 9,
      "people_detection_enabled": true,
      "package_detection_enabled": true
    },
    "created_at": "2022-06-20T14:30:00.000Z"
  }
}
```


---


## 13. PUT /clients_api/doorbots/987004/settings (Update Settings - LED Toggle)


```
curl -s -X PUT "http://localhost:8010/clients_api/doorbots/987004/settings" -H 'Content-Type: application/json' -d '{"led_status": "on"}'
```


**Status:** 200


```json
{
  "type": "device",
  "device_type": "stickup_cams",
  "device": {
    "id": 987004,
    "description": "Living Room",
    "device_id": "cam_living_room",
    "address": "4821 Ridgeview Dr",
    "kind": "stickup_cam_mini",
    "firmware_version": "3.19.8",
    "battery_life": null,
    "external_connection": true,
    "latitude": 30.2241,
    "longitude": -97.8416,
    "location_id": "loc_martinez_001",
    "time_zone": "America/Chicago",
    "alerts": {
      "connection": "online"
    },
    "features": {
      "motions_enabled": true,
      "show_recordings": true,
      "advanced_motion_enabled": false,
      "people_only_enabled": false,
      "shadow_correction_enabled": false,
      "night_vision_enabled": true,
      "motion_message_enabled": false
    },
    "motion_snooze": null,
    "led_status": "off",
    "night_mode_status": "enabled",
    "owned": true,
    "owner": {
      "id": 100001,
      "first_name": "Carlos",
      "last_name": "Martinez"
    },
    "settings": {
      "motion_detection_enabled": true,
      "motion_sensitivity": 3,
      "people_detection_enabled": false,
      "package_detection_enabled": false,
      "led_status": "on"
    },
    "created_at": "2023-01-05T11:30:00.000Z"
  }
}
```


---


## 14. PUT /clients_api/doorbots/999999/settings (Update Settings - Not Found (404))


```
curl -s -X PUT "http://localhost:8010/clients_api/doorbots/999999/settings" -H 'Content-Type: application/json' -d '{"motion_sensitivity": 5}'
```


**Status:** 404


```json
{
  "error": "Device 999999 not found"
}
```


---


## 15. GET /clients_api/locations/loc_martinez_001 (Get Location)


```
curl -s -X GET "http://localhost:8010/clients_api/locations/loc_martinez_001"
```


**Status:** 200


```json
{
  "type": "location",
  "location": {
    "location_id": "loc_martinez_001",
    "name": "Martinez Home",
    "address": {
      "street1": "4821 Ridgeview Dr",
      "street2": "",
      "city": "Austin",
      "state": "TX",
      "zip": "78749",
      "country": "US"
    },
    "latitude": 30.2241,
    "longitude": -97.8416,
    "time_zone": "America/Chicago",
    "mode": "home",
    "owner": {
      "id": 100001,
      "first_name": "Carlos",
      "last_name": "Martinez",
      "email": "carlos.martinez@email.com"
    },
    "subscription": {
      "plan": "protect_plus",
      "status": "active",
      "video_history_days": 180
    },
    "created_at": "2022-06-15T10:00:00.000Z",
    "updated_at": "2025-04-28T08:00:00.000Z"
  }
}
```


---


## 16. GET /clients_api/locations/loc_unknown_999 (Get Location - Not Found (404))


```
curl -s -X GET "http://localhost:8010/clients_api/locations/loc_unknown_999"
```


**Status:** 404


```json
{
  "error": "Location loc_unknown_999 not found"
}
```


---


## 17. GET /clients_api/locations/loc_martinez_001/devices (List Location Devices)


```
curl -s -X GET "http://localhost:8010/clients_api/locations/loc_martinez_001/devices"
```


**Status:** 200


```json
{
  "doorbots": [
    {
      "id": 987001,
      "description": "Front Door",
      "device_id": "doorbell_front",
      "address": "4821 Ridgeview Dr",
      "kind": "lpd_v2",
      "firmware_version": "3.22.8",
      "battery_life": 82,
      "external_connection": true,
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "motions_enabled": true,
        "show_recordings": true,
        "advanced_motion_enabled": true,
        "people_only_enabled": true,
        "shadow_correction_enabled": true,
        "motion_message_enabled": false
      },
      "motion_snooze": null,
      "ring_snooze": null,
      "owned": true,
      "owner": {
        "id": 100001,
        "first_name": "Carlos",
        "last_name": "Martinez"
      },
      "led_status": "on",
      "night_mode_status": "enabled",
      "settings": {
        "doorbell_volume": 8,
        "chime_settings": {
          "type": "mechanical",
          "enabled": true,
          "duration": 5
        },
        "motion_detection_enabled": true,
        "motion_sensitivity": 9,
        "people_detection_enabled": true,
        "package_detection_enabled": true
      },
      "created_at": "2022-06-20T14:30:00.000Z"
    }
  ],
  "stickup_cams": [
    {
      "id": 987002,
      "description": "Backyard Patio",
      "device_id": "cam_backyard",
      "address": "4821 Ridgeview Dr",
      "kind": "stickup_cam_v4",
      "firmware_version": "3.20.5",
      "battery_life": 67,
      "external_connection": false,
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "motions_enabled": true,
        "show_recordings": true,
        "advanced_motion_enabled": true,
        "people_only_enabled": false,
        "shadow_correction_enabled": true,
        "night_vision_enabled": true,
        "motion_message_enabled": false
      },
      "motion_snooze": null,
      "led_status": "on",
      "night_mode_status": "enabled",
      "owned": true,
      "owner": {
        "id": 100001,
        "first_name": "Carlos",
        "last_name": "Martinez"
      },
      "settings": {
        "motion_detection_enabled": true,
        "motion_sensitivity": 5,
        "people_detection_enabled": false,
        "package_detection_enabled": false
      },
      "created_at": "2022-07-10T09:00:00.000Z"
    },
    {
      "id": 987003,
      "description": "Driveway",
      "device_id": "cam_driveway",
      "address": "4821 Ridgeview Dr",
      "kind": "floodlight_v2",
      "firmware_version": "3.21.1",
      "battery_life": null,
      "external_connection": true,
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "motions_enabled": true,
        "show_recordings": true,
        "advanced_motion_enabled": true,
        "people_only_enabled": true,
        "shadow_correction_enabled": true,
        "night_vision_enabled": true,
        "motion_message_enabled": false
      },
      "motion_snooze": null,
      "led_status": "on",
      "night_mode_status": "enabled",
      "siren_status": {
        "seconds_remaining": 0
      },
      "floodlight_status": {
        "on": false
      },
      "owned": true,
      "owner": {
        "id": 100001,
        "first_name": "Carlos",
        "last_name": "Martinez"
      },
      "settings": {
        "motion_detection_enabled": true,
        "motion_sensitivity": 8,
        "people_detection_enabled": true,
        "package_detection_enabled": false,
        "light_schedule_enabled": true,
        "light_on_duration_seconds": 30
      },
      "wifi_signal_strength": -68,
      "wifi_signal_category": "poor",
      "created_at": "2022-06-20T15:00:00.000Z"
    },
    {
      "id": 987004,
      "description": "Living Room",
      "device_id": "cam_living_room",
      "address": "4821 Ridgeview Dr",
      "kind": "stickup_cam_mini",
      "firmware_version": "3.19.8",
      "battery_life": null,
      "external_connection": true,
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "motions_enabled": true,
        "show_recordings": true,
        "advanced_motion_enabled": false,
        "people_only_enabled": false,
        "shadow_correction_enabled": false,
        "night_vision_enabled": true,
        "motion_message_enabled": false
      },
      "motion_snooze": null,
      "led_status": "off",
      "night_mode_status": "enabled",
      "owned": true,
      "owner": {
        "id": 100001,
        "first_name": "Carlos",
        "last_name": "Martinez"
      },
      "settings": {
        "motion_detection_enabled": true,
        "motion_sensitivity": 3,
        "people_detection_enabled": false,
        "package_detection_enabled": false,
        "led_status": "on"
      },
      "created_at": "2023-01-05T11:30:00.000Z"
    },
    {
      "id": 987005,
      "description": "Side Gate",
      "device_id": "cam_side_gate",
      "address": "4821 Ridgeview Dr",
      "kind": "spotlight_cam_v2",
      "firmware_version": "3.18.2",
      "battery_life": 23,
      "external_connection": false,
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "motions_enabled": true,
        "show_recordings": true,
        "advanced_motion_enabled": true,
        "people_only_enabled": false,
        "shadow_correction_enabled": true,
        "night_vision_enabled": true,
        "motion_message_enabled": false
      },
      "motion_snooze": null,
      "led_status": "on",
      "night_mode_status": "enabled",
      "siren_status": {
        "seconds_remaining": 0
      },
      "owned": true,
      "owner": {
        "id": 100001,
        "first_name": "Carlos",
        "last_name": "Martinez"
      },
      "settings": {
        "motion_detection_enabled": true,
        "motion_sensitivity": 6,
        "people_detection_enabled": false,
        "package_detection_enabled": false
      },
      "created_at": "2023-03-18T16:45:00.000Z"
    }
  ],
  "chimes": [
    {
      "id": 987006,
      "description": "Hallway Chime",
      "device_id": "chime_hallway",
      "address": "4821 Ridgeview Dr",
      "kind": "chime_pro_v2",
      "firmware_version": "3.16.4",
      "latitude": 30.2241,
      "longitude": -97.8416,
      "location_id": "loc_martinez_001",
      "time_zone": "America/Chicago",
      "alerts": {
        "connection": "online"
      },
      "features": {
        "ringtones_enabled": true,
        "wifi_extender_enabled": true
      },
      "owned": true,
      "owner": {
        "id": 100001,
        "first_name": "Carlos",
        "last_name": "Martinez"
      },
      "settings": {
        "volume": 7,
        "ding_audio_id": "ring_default",
        "ding_audio_user_id": null,
        "motion_audio_id": null,
        "motion_audio_user_id": null,
        "linked_doorbots": [
          987001
        ]
      },
      "wifi_signal_strength": -42,
      "wifi_signal_category": "good",
      "created_at": "2022-06-20T14:45:00.000Z"
    }
  ]
}
```


---


## 18. GET /clients_api/locations/loc_martinez_001/mode (Get Location Mode)


```
curl -s -X GET "http://localhost:8010/clients_api/locations/loc_martinez_001/mode"
```


**Status:** 200


```json
{
  "type": "mode",
  "mode": "home",
  "location_id": "loc_martinez_001"
}
```


---


## 19. PUT /clients_api/locations/loc_martinez_001/mode (Set Mode - Away)


```
curl -s -X PUT "http://localhost:8010/clients_api/locations/loc_martinez_001/mode" -H 'Content-Type: application/json' -d '{"mode": "away"}'
```


**Status:** 200


```json
{
  "type": "mode",
  "mode": "away",
  "location_id": "loc_martinez_001"
}
```


---


## 20. GET /clients_api/locations/loc_martinez_001/mode (Get Mode After Change to Away)


```
curl -s -X GET "http://localhost:8010/clients_api/locations/loc_martinez_001/mode"
```


**Status:** 200


```json
{
  "type": "mode",
  "mode": "away",
  "location_id": "loc_martinez_001"
}
```


---


## 21. PUT /clients_api/locations/loc_martinez_001/mode (Set Mode - Home)


```
curl -s -X PUT "http://localhost:8010/clients_api/locations/loc_martinez_001/mode" -H 'Content-Type: application/json' -d '{"mode": "home"}'
```


**Status:** 200


```json
{
  "type": "mode",
  "mode": "home",
  "location_id": "loc_martinez_001"
}
```


---


## 22. PUT /clients_api/locations/loc_martinez_001/mode (Set Mode - Invalid (400))


```
curl -s -X PUT "http://localhost:8010/clients_api/locations/loc_martinez_001/mode" -H 'Content-Type: application/json' -d '{"mode": "invalid_mode"}'
```


**Status:** 400


```json
{
  "error": "Invalid mode 'invalid_mode'. Must be one of: ['home', 'away', 'disarmed']"
}
```


---


## 23. GET /clients_api/dings/active (List Active Dings)


```
curl -s -X GET "http://localhost:8010/clients_api/dings/active"
```


**Status:** 200


```json
[
  {
    "id": 234567890123456,
    "id_str": "234567890123456",
    "state": "ringing",
    "protocol": "sip",
    "doorbot_id": 987001,
    "doorbot_description": "Front Door",
    "device_kind": "lpd_v2",
    "motion": false,
    "snapshot_url": "",
    "kind": "ding",
    "sip_server_ip": "192.168.1.1",
    "sip_server_port": 15063,
    "sip_server_tls": true,
    "sip_session_id": "r.ms.abc123def456",
    "sip_from": "sip:ring001@ring.com",
    "sip_to": "sip:martinez001@ring.com",
    "sip_endpoints": [],
    "expires_in": 160,
    "now": 1745846100.0,
    "optimization_level": 3,
    "sip_ding_id": "234567890123456",
    "is_sharing": false
  },
  {
    "id": 345678901234567,
    "id_str": "345678901234567",
    "state": "ringing",
    "protocol": "sip",
    "doorbot_id": 987003,
    "doorbot_description": "Driveway",
    "device_kind": "floodlight_v2",
    "motion": true,
    "snapshot_url": "",
    "kind": "motion",
    "sip_server_ip": "192.168.1.1",
    "sip_server_port": 15063,
    "sip_server_tls": true,
    "sip_session_id": "r.ms.xyz789ghi012",
    "sip_from": "sip:ring003@ring.com",
    "sip_to": "sip:martinez001@ring.com",
    "sip_endpoints": [],
    "expires_in": 145,
    "now": 1745846100.0,
    "optimization_level": 3,
    "sip_ding_id": "345678901234567",
    "is_sharing": false
  }
]
```


---


## 24. GET /clients_api/doorbots/987001/history (List Doorbell Events (all))


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987001/history"
```


**Status:** 200


```json
{
  "type": "events",
  "count": 20,
  "total": 41,
  "offset": 0,
  "limit": 20,
  "results": [
    {
      "id": 7001,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-28T13:45:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 12,
      "cv_properties": "person"
    },
    {
      "id": 7003,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-28T11:15:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 22,
      "cv_properties": "person"
    },
    {
      "id": 7004,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-28T10:48:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 15,
      "cv_properties": "package"
    },
    {
      "id": 7007,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-28T07:42:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 9,
      "cv_properties": "person"
    },
    {
      "id": 7009,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-28T07:30:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 5,
      "cv_properties": "person"
    },
    {
      "id": 7012,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T18:22:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 11,
      "cv_properties": "person"
    },
    {
      "id": 7014,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-27T17:48:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "person"
    },
    {
      "id": 7017,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T15:35:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 7,
      "cv_properties": "person"
    },
    {
      "id": 7018,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-27T15:32:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 4,
      "cv_properties": "person"
    },
    {
      "id": 7020,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-27T11:22:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 12,
      "cv_properties": "package"
    },
    {
      "id": 7022,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T11:15:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 6,
      "cv_properties": "person"
    },
    {
      "id": 7023,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T07:38:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 10,
      "cv_properties": "person"
    },
    {
      "id": 7027,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-26T18:40:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 6,
      "cv_properties": "person"
    },
    {
      "id": 7028,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-26T18:38:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "person"
    },
    {
      "id": 7032,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-26T15:40:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 10,
      "cv_properties": "person"
    },
    {
      "id": 7033,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "person_detected",
      "created_at": "2025-04-26T13:10:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 14,
      "cv_properties": "person"
    },
    {
      "id": 7035,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-26T10:55:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 11,
      "cv_properties": "package"
    },
    {
      "id": 7036,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-26T07:40:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "person"
    },
    {
      "id": 7039,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-25T18:55:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 7,
      "cv_properties": "person"
    },
    {
      "id": 7041,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-25T17:15:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 9,
      "cv_properties": "person"
    }
  ]
}
```


---


## 25. GET /clients_api/doorbots/987001/history?kind=ding (Doorbell Events - Dings only)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987001/history?kind=ding"
```


**Status:** 200


```json
{
  "type": "events",
  "count": 13,
  "total": 13,
  "offset": 0,
  "limit": 20,
  "results": [
    {
      "id": 7003,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-28T11:15:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 22,
      "cv_properties": "person"
    },
    {
      "id": 7009,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-28T07:30:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 5,
      "cv_properties": "person"
    },
    {
      "id": 7014,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-27T17:48:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "person"
    },
    {
      "id": 7018,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-27T15:32:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 4,
      "cv_properties": "person"
    },
    {
      "id": 7027,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-26T18:40:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 6,
      "cv_properties": "person"
    },
    {
      "id": 7032,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-26T15:40:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 10,
      "cv_properties": "person"
    },
    {
      "id": 7041,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-25T17:15:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 9,
      "cv_properties": "person"
    },
    {
      "id": 7044,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-25T15:48:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 3,
      "cv_properties": "person"
    },
    {
      "id": 7053,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-24T17:00:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 7,
      "cv_properties": "person"
    },
    {
      "id": 7056,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-24T15:32:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 5,
      "cv_properties": "person"
    },
    {
      "id": 7064,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-23T18:25:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 6,
      "cv_properties": "person"
    },
    {
      "id": 7075,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-22T17:30:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "person"
    },
    {
      "id": 7078,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-22T15:18:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 4,
      "cv_properties": "person"
    }
  ]
}
```


---


## 26. GET /clients_api/doorbots/987001/history?kind=motion (Doorbell Events - Motion only)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987001/history?kind=motion"
```


**Status:** 200


```json
{
  "type": "events",
  "count": 18,
  "total": 18,
  "offset": 0,
  "limit": 20,
  "results": [
    {
      "id": 7001,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-28T13:45:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 12,
      "cv_properties": "person"
    },
    {
      "id": 7007,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-28T07:42:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 9,
      "cv_properties": "person"
    },
    {
      "id": 7012,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T18:22:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 11,
      "cv_properties": "person"
    },
    {
      "id": 7017,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T15:35:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 7,
      "cv_properties": "person"
    },
    {
      "id": 7022,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T11:15:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 6,
      "cv_properties": "person"
    },
    {
      "id": 7023,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T07:38:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 10,
      "cv_properties": "person"
    },
    {
      "id": 7028,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-26T18:38:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "person"
    },
    {
      "id": 7036,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-26T07:40:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "person"
    },
    {
      "id": 7039,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-25T18:55:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 7,
      "cv_properties": "person"
    },
    {
      "id": 7043,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-25T15:50:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 6,
      "cv_properties": "person"
    },
    {
      "id": 7047,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-25T11:05:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 5,
      "cv_properties": "person"
    },
    {
      "id": 7049,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-25T07:22:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "person"
    },
    {
      "id": 7051,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-24T18:10:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 9,
      "cv_properties": "person"
    },
    {
      "id": 7059,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-24T07:45:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "person"
    },
    {
      "id": 7062,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-23T19:00:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "person"
    },
    {
      "id": 7067,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-23T14:50:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 6,
      "cv_properties": "person"
    },
    {
      "id": 7070,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-23T07:35:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 7,
      "cv_properties": "person"
    },
    {
      "id": 7073,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-22T18:45:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 9,
      "cv_properties": "person"
    }
  ]
}
```


---


## 27. GET /clients_api/doorbots/987001/history?kind=package_detected (Doorbell Events - Package detected)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987001/history?kind=package_detected"
```


**Status:** 200


```json
{
  "type": "events",
  "count": 7,
  "total": 7,
  "offset": 0,
  "limit": 20,
  "results": [
    {
      "id": 7004,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-28T10:48:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 15,
      "cv_properties": "package"
    },
    {
      "id": 7020,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-27T11:22:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 12,
      "cv_properties": "package"
    },
    {
      "id": 7035,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-26T10:55:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 11,
      "cv_properties": "package"
    },
    {
      "id": 7046,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-25T11:10:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 13,
      "cv_properties": "package"
    },
    {
      "id": 7058,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-24T10:40:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 14,
      "cv_properties": "package"
    },
    {
      "id": 7069,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-23T10:30:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 11,
      "cv_properties": "package"
    },
    {
      "id": 7080,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-22T10:20:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 10,
      "cv_properties": "package"
    }
  ]
}
```


---


## 28. GET /clients_api/doorbots/987003/history (Driveway Cam Events)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987003/history"
```


**Status:** 200


```json
{
  "type": "events",
  "count": 20,
  "total": 24,
  "offset": 0,
  "limit": 20,
  "results": [
    {
      "id": 7002,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-28T12:30:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "vehicle"
    },
    {
      "id": 7005,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-28T10:20:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 6,
      "cv_properties": "vehicle"
    },
    {
      "id": 7008,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-28T07:35:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 14,
      "cv_properties": "person"
    },
    {
      "id": 7011,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-27T22:10:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 7,
      "cv_properties": "animal"
    },
    {
      "id": 7013,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-27T17:55:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 13,
      "cv_properties": "vehicle"
    },
    {
      "id": 7019,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-27T14:10:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 9,
      "cv_properties": "vehicle"
    },
    {
      "id": 7021,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-27T11:18:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "vehicle"
    },
    {
      "id": 7024,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-27T07:32:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 12,
      "cv_properties": "vehicle"
    },
    {
      "id": 7026,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-26T19:15:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 9,
      "cv_properties": "person"
    },
    {
      "id": 7031,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-26T15:45:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 7,
      "cv_properties": "person"
    },
    {
      "id": 7034,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-26T11:05:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 6,
      "cv_properties": "vehicle"
    },
    {
      "id": 7037,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-26T07:35:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 10,
      "cv_properties": "vehicle"
    },
    {
      "id": 7040,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-25T18:50:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 12,
      "cv_properties": "vehicle"
    },
    {
      "id": 7045,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-25T12:30:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "vehicle"
    },
    {
      "id": 7048,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-25T07:28:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 11,
      "cv_properties": "vehicle"
    },
    {
      "id": 7050,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-25T01:30:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 4,
      "cv_properties": "animal"
    },
    {
      "id": 7052,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-24T18:05:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 13,
      "cv_properties": "vehicle"
    },
    {
      "id": 7057,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-24T13:20:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 7,
      "cv_properties": "vehicle"
    },
    {
      "id": 7060,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-24T07:40:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 11,
      "cv_properties": "vehicle"
    },
    {
      "id": 7063,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-23T18:30:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 10,
      "cv_properties": "vehicle"
    }
  ]
}
```


---


## 29. GET /clients_api/doorbots/987002/history (Backyard Cam Events)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987002/history"
```


**Status:** 200


```json
{
  "type": "events",
  "count": 10,
  "total": 10,
  "offset": 0,
  "limit": 20,
  "results": [
    {
      "id": 7006,
      "doorbot_id": 987002,
      "device_id": "cam_backyard",
      "kind": "motion",
      "created_at": "2025-04-28T09:30:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 10,
      "cv_properties": "animal"
    },
    {
      "id": 7015,
      "doorbot_id": 987002,
      "device_id": "cam_backyard",
      "kind": "motion",
      "created_at": "2025-04-27T16:30:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 20,
      "cv_properties": "person"
    },
    {
      "id": 7016,
      "doorbot_id": 987002,
      "device_id": "cam_backyard",
      "kind": "motion",
      "created_at": "2025-04-27T16:05:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 15,
      "cv_properties": "person"
    },
    {
      "id": 7029,
      "doorbot_id": 987002,
      "device_id": "cam_backyard",
      "kind": "motion",
      "created_at": "2025-04-26T17:20:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 25,
      "cv_properties": "person"
    },
    {
      "id": 7030,
      "doorbot_id": 987002,
      "device_id": "cam_backyard",
      "kind": "motion",
      "created_at": "2025-04-26T17:00:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 18,
      "cv_properties": "person"
    },
    {
      "id": 7042,
      "doorbot_id": 987002,
      "device_id": "cam_backyard",
      "kind": "motion",
      "created_at": "2025-04-25T16:40:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 16,
      "cv_properties": "person"
    },
    {
      "id": 7054,
      "doorbot_id": 987002,
      "device_id": "cam_backyard",
      "kind": "motion",
      "created_at": "2025-04-24T16:15:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 19,
      "cv_properties": "person"
    },
    {
      "id": 7065,
      "doorbot_id": 987002,
      "device_id": "cam_backyard",
      "kind": "motion",
      "created_at": "2025-04-23T17:45:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 22,
      "cv_properties": "person"
    },
    {
      "id": 7066,
      "doorbot_id": 987002,
      "device_id": "cam_backyard",
      "kind": "motion",
      "created_at": "2025-04-23T15:10:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 12,
      "cv_properties": "person"
    },
    {
      "id": 7076,
      "doorbot_id": 987002,
      "device_id": "cam_backyard",
      "kind": "motion",
      "created_at": "2025-04-22T16:50:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 17,
      "cv_properties": "person"
    }
  ]
}
```


---


## 30. GET /clients_api/doorbots/987001/history?date_from=2025-04-28T00:00:00.000Z&date_to=2025-04-28T23:59:59.000Z (Doorbell Events - Today only)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987001/history?date_from=2025-04-28T00:00:00.000Z&date_to=2025-04-28T23:59:59.000Z"
```


**Status:** 200


```json
{
  "type": "events",
  "count": 5,
  "total": 5,
  "offset": 0,
  "limit": 20,
  "results": [
    {
      "id": 7001,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-28T13:45:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 12,
      "cv_properties": "person"
    },
    {
      "id": 7003,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-28T11:15:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 22,
      "cv_properties": "person"
    },
    {
      "id": 7004,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-28T10:48:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 15,
      "cv_properties": "package"
    },
    {
      "id": 7007,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-28T07:42:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 9,
      "cv_properties": "person"
    },
    {
      "id": 7009,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-28T07:30:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 5,
      "cv_properties": "person"
    }
  ]
}
```


---


## 31. GET /clients_api/doorbots/987001/history?date_from=2025-04-27T14:30:00.000Z (Doorbell Events - Last 24h)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987001/history?date_from=2025-04-27T14:30:00.000Z"
```


**Status:** 200


```json
{
  "type": "events",
  "count": 9,
  "total": 9,
  "offset": 0,
  "limit": 20,
  "results": [
    {
      "id": 7001,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-28T13:45:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 12,
      "cv_properties": "person"
    },
    {
      "id": 7003,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-28T11:15:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 22,
      "cv_properties": "person"
    },
    {
      "id": 7004,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-28T10:48:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 15,
      "cv_properties": "package"
    },
    {
      "id": 7007,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-28T07:42:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 9,
      "cv_properties": "person"
    },
    {
      "id": 7009,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-28T07:30:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 5,
      "cv_properties": "person"
    },
    {
      "id": 7012,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T18:22:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 11,
      "cv_properties": "person"
    },
    {
      "id": 7014,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-27T17:48:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "person"
    },
    {
      "id": 7017,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T15:35:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 7,
      "cv_properties": "person"
    },
    {
      "id": 7018,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-27T15:32:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 4,
      "cv_properties": "person"
    }
  ]
}
```


---


## 32. GET /clients_api/doorbots/987001/history?limit=5&offset=0 (Doorbell Events - Page 1)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987001/history?limit=5&offset=0"
```


**Status:** 200


```json
{
  "type": "events",
  "count": 5,
  "total": 41,
  "offset": 0,
  "limit": 5,
  "results": [
    {
      "id": 7001,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-28T13:45:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 12,
      "cv_properties": "person"
    },
    {
      "id": 7003,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-28T11:15:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 22,
      "cv_properties": "person"
    },
    {
      "id": 7004,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-28T10:48:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 15,
      "cv_properties": "package"
    },
    {
      "id": 7007,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-28T07:42:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 9,
      "cv_properties": "person"
    },
    {
      "id": 7009,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-28T07:30:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 5,
      "cv_properties": "person"
    }
  ]
}
```


---


## 33. GET /clients_api/doorbots/987001/history?limit=5&offset=5 (Doorbell Events - Page 2)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987001/history?limit=5&offset=5"
```


**Status:** 200


```json
{
  "type": "events",
  "count": 5,
  "total": 41,
  "offset": 5,
  "limit": 5,
  "results": [
    {
      "id": 7012,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T18:22:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 11,
      "cv_properties": "person"
    },
    {
      "id": 7014,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-27T17:48:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 8,
      "cv_properties": "person"
    },
    {
      "id": 7017,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T15:35:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 7,
      "cv_properties": "person"
    },
    {
      "id": 7018,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-27T15:32:00.000Z",
      "answered": true,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 4,
      "cv_properties": "person"
    },
    {
      "id": 7020,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-27T11:22:00.000Z",
      "answered": false,
      "favorite": false,
      "recording": {
        "status": "ready"
      },
      "snapshot_url": "",
      "duration_seconds": 12,
      "cv_properties": "package"
    }
  ]
}
```


---


## 34. GET /clients_api/dings/7001 (Get Single Event)


```
curl -s -X GET "http://localhost:8010/clients_api/dings/7001"
```


**Status:** 200


```json
{
  "type": "event",
  "event": {
    "id": 7001,
    "doorbot_id": 987001,
    "device_id": "doorbell_front",
    "kind": "motion",
    "created_at": "2025-04-28T13:45:00.000Z",
    "answered": false,
    "favorite": false,
    "recording": {
      "status": "ready"
    },
    "snapshot_url": "",
    "duration_seconds": 12,
    "cv_properties": "person"
  }
}
```


---


## 35. GET /clients_api/dings/99999 (Get Event - Not Found (404))


```
curl -s -X GET "http://localhost:8010/clients_api/dings/99999"
```


**Status:** 404


```json
{
  "error": "Event 99999 not found"
}
```


---


## 36. GET /clients_api/dings/7001/recording (Get Event Recording URL)


```
curl -s -X GET "http://localhost:8010/clients_api/dings/7001/recording"
```


**Status:** 200


```json
{
  "type": "recording",
  "event_id": 7001,
  "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7001.mp4"
}
```


---


## 37. GET /clients_api/dings/99999/recording (Get Recording - Not Found (404))


```
curl -s -X GET "http://localhost:8010/clients_api/dings/99999/recording"
```


**Status:** 404


```json
{
  "error": "Event 99999 not found"
}
```


---


## 38. GET /clients_api/doorbots/987001/recordings (List Recordings - Doorbell)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987001/recordings"
```


**Status:** 200


```json
{
  "type": "recordings",
  "count": 41,
  "results": [
    {
      "event_id": 7001,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-28T13:45:00.000Z",
      "duration_seconds": 12,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7001.mp4"
    },
    {
      "event_id": 7003,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-28T11:15:00.000Z",
      "duration_seconds": 22,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7003.mp4"
    },
    {
      "event_id": 7004,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-28T10:48:00.000Z",
      "duration_seconds": 15,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7004.mp4"
    },
    {
      "event_id": 7007,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-28T07:42:00.000Z",
      "duration_seconds": 9,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7007.mp4"
    },
    {
      "event_id": 7009,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-28T07:30:00.000Z",
      "duration_seconds": 5,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7009.mp4"
    },
    {
      "event_id": 7012,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T18:22:00.000Z",
      "duration_seconds": 11,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7012.mp4"
    },
    {
      "event_id": 7014,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-27T17:48:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7014.mp4"
    },
    {
      "event_id": 7017,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T15:35:00.000Z",
      "duration_seconds": 7,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7017.mp4"
    },
    {
      "event_id": 7018,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-27T15:32:00.000Z",
      "duration_seconds": 4,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7018.mp4"
    },
    {
      "event_id": 7020,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-27T11:22:00.000Z",
      "duration_seconds": 12,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7020.mp4"
    },
    {
      "event_id": 7022,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T11:15:00.000Z",
      "duration_seconds": 6,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7022.mp4"
    },
    {
      "event_id": 7023,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-27T07:38:00.000Z",
      "duration_seconds": 10,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7023.mp4"
    },
    {
      "event_id": 7027,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-26T18:40:00.000Z",
      "duration_seconds": 6,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7027.mp4"
    },
    {
      "event_id": 7028,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-26T18:38:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7028.mp4"
    },
    {
      "event_id": 7032,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-26T15:40:00.000Z",
      "duration_seconds": 10,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7032.mp4"
    },
    {
      "event_id": 7033,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "person_detected",
      "created_at": "2025-04-26T13:10:00.000Z",
      "duration_seconds": 14,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7033.mp4"
    },
    {
      "event_id": 7035,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-26T10:55:00.000Z",
      "duration_seconds": 11,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7035.mp4"
    },
    {
      "event_id": 7036,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-26T07:40:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7036.mp4"
    },
    {
      "event_id": 7039,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-25T18:55:00.000Z",
      "duration_seconds": 7,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7039.mp4"
    },
    {
      "event_id": 7041,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-25T17:15:00.000Z",
      "duration_seconds": 9,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7041.mp4"
    },
    {
      "event_id": 7043,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-25T15:50:00.000Z",
      "duration_seconds": 6,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7043.mp4"
    },
    {
      "event_id": 7044,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-25T15:48:00.000Z",
      "duration_seconds": 3,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7044.mp4"
    },
    {
      "event_id": 7046,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-25T11:10:00.000Z",
      "duration_seconds": 13,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7046.mp4"
    },
    {
      "event_id": 7047,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-25T11:05:00.000Z",
      "duration_seconds": 5,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7047.mp4"
    },
    {
      "event_id": 7049,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-25T07:22:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7049.mp4"
    },
    {
      "event_id": 7051,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-24T18:10:00.000Z",
      "duration_seconds": 9,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7051.mp4"
    },
    {
      "event_id": 7053,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-24T17:00:00.000Z",
      "duration_seconds": 7,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7053.mp4"
    },
    {
      "event_id": 7055,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "person_detected",
      "created_at": "2025-04-24T15:35:00.000Z",
      "duration_seconds": 10,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7055.mp4"
    },
    {
      "event_id": 7056,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-24T15:32:00.000Z",
      "duration_seconds": 5,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7056.mp4"
    },
    {
      "event_id": 7058,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-24T10:40:00.000Z",
      "duration_seconds": 14,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7058.mp4"
    },
    {
      "event_id": 7059,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-24T07:45:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7059.mp4"
    },
    {
      "event_id": 7062,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-23T19:00:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7062.mp4"
    },
    {
      "event_id": 7064,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-23T18:25:00.000Z",
      "duration_seconds": 6,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7064.mp4"
    },
    {
      "event_id": 7067,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-23T14:50:00.000Z",
      "duration_seconds": 6,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7067.mp4"
    },
    {
      "event_id": 7069,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-23T10:30:00.000Z",
      "duration_seconds": 11,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7069.mp4"
    },
    {
      "event_id": 7070,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-23T07:35:00.000Z",
      "duration_seconds": 7,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7070.mp4"
    },
    {
      "event_id": 7073,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-22T18:45:00.000Z",
      "duration_seconds": 9,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7073.mp4"
    },
    {
      "event_id": 7075,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-22T17:30:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7075.mp4"
    },
    {
      "event_id": 7077,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "person_detected",
      "created_at": "2025-04-22T15:20:00.000Z",
      "duration_seconds": 12,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7077.mp4"
    },
    {
      "event_id": 7078,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-22T15:18:00.000Z",
      "duration_seconds": 4,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7078.mp4"
    },
    {
      "event_id": 7080,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-22T10:20:00.000Z",
      "duration_seconds": 10,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7080.mp4"
    }
  ]
}
```


---


## 39. GET /clients_api/doorbots/987003/recordings (List Recordings - Driveway)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987003/recordings"
```


**Status:** 200


```json
{
  "type": "recordings",
  "count": 24,
  "results": [
    {
      "event_id": 7002,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-28T12:30:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7002.mp4"
    },
    {
      "event_id": 7005,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-28T10:20:00.000Z",
      "duration_seconds": 6,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7005.mp4"
    },
    {
      "event_id": 7008,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-28T07:35:00.000Z",
      "duration_seconds": 14,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7008.mp4"
    },
    {
      "event_id": 7011,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-27T22:10:00.000Z",
      "duration_seconds": 7,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7011.mp4"
    },
    {
      "event_id": 7013,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-27T17:55:00.000Z",
      "duration_seconds": 13,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7013.mp4"
    },
    {
      "event_id": 7019,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-27T14:10:00.000Z",
      "duration_seconds": 9,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7019.mp4"
    },
    {
      "event_id": 7021,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-27T11:18:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7021.mp4"
    },
    {
      "event_id": 7024,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-27T07:32:00.000Z",
      "duration_seconds": 12,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7024.mp4"
    },
    {
      "event_id": 7026,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-26T19:15:00.000Z",
      "duration_seconds": 9,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7026.mp4"
    },
    {
      "event_id": 7031,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-26T15:45:00.000Z",
      "duration_seconds": 7,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7031.mp4"
    },
    {
      "event_id": 7034,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-26T11:05:00.000Z",
      "duration_seconds": 6,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7034.mp4"
    },
    {
      "event_id": 7037,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-26T07:35:00.000Z",
      "duration_seconds": 10,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7037.mp4"
    },
    {
      "event_id": 7040,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-25T18:50:00.000Z",
      "duration_seconds": 12,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7040.mp4"
    },
    {
      "event_id": 7045,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-25T12:30:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7045.mp4"
    },
    {
      "event_id": 7048,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-25T07:28:00.000Z",
      "duration_seconds": 11,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7048.mp4"
    },
    {
      "event_id": 7050,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-25T01:30:00.000Z",
      "duration_seconds": 4,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7050.mp4"
    },
    {
      "event_id": 7052,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-24T18:05:00.000Z",
      "duration_seconds": 13,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7052.mp4"
    },
    {
      "event_id": 7057,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-24T13:20:00.000Z",
      "duration_seconds": 7,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7057.mp4"
    },
    {
      "event_id": 7060,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-24T07:40:00.000Z",
      "duration_seconds": 11,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7060.mp4"
    },
    {
      "event_id": 7063,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-23T18:30:00.000Z",
      "duration_seconds": 10,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7063.mp4"
    },
    {
      "event_id": 7068,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-23T11:00:00.000Z",
      "duration_seconds": 9,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7068.mp4"
    },
    {
      "event_id": 7071,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-23T07:30:00.000Z",
      "duration_seconds": 12,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7071.mp4"
    },
    {
      "event_id": 7074,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-22T18:40:00.000Z",
      "duration_seconds": 11,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7074.mp4"
    },
    {
      "event_id": 7079,
      "doorbot_id": 987003,
      "device_id": "cam_driveway",
      "kind": "motion",
      "created_at": "2025-04-22T12:15:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/cam_driveway/7079.mp4"
    }
  ]
}
```


---


## 40. GET /clients_api/doorbots/987001/recordings?date_from=2025-04-25T00:00:00.000Z&date_to=2025-04-26T23:59:59.000Z (Recordings - Date Range)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987001/recordings?date_from=2025-04-25T00:00:00.000Z&date_to=2025-04-26T23:59:59.000Z"
```


**Status:** 200


```json
{
  "type": "recordings",
  "count": 13,
  "results": [
    {
      "event_id": 7027,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-26T18:40:00.000Z",
      "duration_seconds": 6,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7027.mp4"
    },
    {
      "event_id": 7028,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-26T18:38:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7028.mp4"
    },
    {
      "event_id": 7032,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-26T15:40:00.000Z",
      "duration_seconds": 10,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7032.mp4"
    },
    {
      "event_id": 7033,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "person_detected",
      "created_at": "2025-04-26T13:10:00.000Z",
      "duration_seconds": 14,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7033.mp4"
    },
    {
      "event_id": 7035,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-26T10:55:00.000Z",
      "duration_seconds": 11,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7035.mp4"
    },
    {
      "event_id": 7036,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-26T07:40:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7036.mp4"
    },
    {
      "event_id": 7039,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-25T18:55:00.000Z",
      "duration_seconds": 7,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7039.mp4"
    },
    {
      "event_id": 7041,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-25T17:15:00.000Z",
      "duration_seconds": 9,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7041.mp4"
    },
    {
      "event_id": 7043,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-25T15:50:00.000Z",
      "duration_seconds": 6,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7043.mp4"
    },
    {
      "event_id": 7044,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "ding",
      "created_at": "2025-04-25T15:48:00.000Z",
      "duration_seconds": 3,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7044.mp4"
    },
    {
      "event_id": 7046,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "package_detected",
      "created_at": "2025-04-25T11:10:00.000Z",
      "duration_seconds": 13,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7046.mp4"
    },
    {
      "event_id": 7047,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-25T11:05:00.000Z",
      "duration_seconds": 5,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7047.mp4"
    },
    {
      "event_id": 7049,
      "doorbot_id": 987001,
      "device_id": "doorbell_front",
      "kind": "motion",
      "created_at": "2025-04-25T07:22:00.000Z",
      "duration_seconds": 8,
      "recording_url": "https://ring-recordings.s3.amazonaws.com/loc_martinez_001/doorbell_front/7049.mp4"
    }
  ]
}
```


---


## 41. GET /clients_api/locations/loc_martinez_001/users (List Shared Users)


```
curl -s -X GET "http://localhost:8010/clients_api/locations/loc_martinez_001/users"
```


**Status:** 200


```json
{
  "type": "shared_users",
  "count": 3,
  "results": [
    {
      "user_id": 100001,
      "first_name": "Carlos",
      "last_name": "Martinez",
      "email": "carlos.martinez@email.com",
      "role": "owner",
      "device_access": "all",
      "shared_at": "2022-06-15T10:00:00.000Z"
    },
    {
      "user_id": 100002,
      "first_name": "Maria",
      "last_name": "Martinez",
      "email": "maria.martinez@email.com",
      "role": "owner",
      "device_access": "all",
      "shared_at": "2022-06-15T10:05:00.000Z"
    },
    {
      "user_id": 100003,
      "first_name": "Tom",
      "last_name": "Henderson",
      "email": "tom.henderson@email.com",
      "role": "guest",
      "device_access": "987001",
      "shared_at": "2023-08-12T09:30:00.000Z"
    }
  ]
}
```


---


## 42. GET /clients_api/locations/loc_martinez_001/users/100001 (Get User - Carlos (owner))


```
curl -s -X GET "http://localhost:8010/clients_api/locations/loc_martinez_001/users/100001"
```


**Status:** 200


```json
{
  "type": "shared_user",
  "shared_user": {
    "user_id": 100001,
    "first_name": "Carlos",
    "last_name": "Martinez",
    "email": "carlos.martinez@email.com",
    "role": "owner",
    "device_access": "all",
    "shared_at": "2022-06-15T10:00:00.000Z"
  }
}
```


---


## 43. GET /clients_api/locations/loc_martinez_001/users/100003 (Get User - Tom (guest))


```
curl -s -X GET "http://localhost:8010/clients_api/locations/loc_martinez_001/users/100003"
```


**Status:** 200


```json
{
  "type": "shared_user",
  "shared_user": {
    "user_id": 100003,
    "first_name": "Tom",
    "last_name": "Henderson",
    "email": "tom.henderson@email.com",
    "role": "guest",
    "device_access": "987001",
    "shared_at": "2023-08-12T09:30:00.000Z"
  }
}
```


---


## 44. GET /clients_api/locations/loc_martinez_001/users/999999 (Get User - Not Found (404))


```
curl -s -X GET "http://localhost:8010/clients_api/locations/loc_martinez_001/users/999999"
```


**Status:** 404


```json
{
  "error": "User 999999 not found"
}
```


---


## 45. GET /clients_api/chimes/987006/settings (Get Chime Settings)


```
curl -s -X GET "http://localhost:8010/clients_api/chimes/987006/settings"
```


**Status:** 200


```json
{
  "type": "chime_settings",
  "settings": {
    "volume": 7,
    "ding_audio_id": "ring_default",
    "ding_audio_user_id": null,
    "motion_audio_id": null,
    "motion_audio_user_id": null,
    "linked_doorbots": [
      987001
    ]
  }
}
```


---


## 46. GET /clients_api/chimes/987001/settings (Get Chime Settings - Not a Chime (404))


```
curl -s -X GET "http://localhost:8010/clients_api/chimes/987001/settings"
```


**Status:** 404


```json
{
  "error": "Device 987001 is not a chime"
}
```


---


## 47. PUT /clients_api/chimes/987006/link (Link Chime to Doorbell)


```
curl -s -X PUT "http://localhost:8010/clients_api/chimes/987006/link" -H 'Content-Type: application/json' -d '{"doorbell_id": 987001}'
```


**Status:** 200


```json
{
  "type": "chime_settings",
  "settings": {
    "volume": 7,
    "ding_audio_id": "ring_default",
    "ding_audio_user_id": null,
    "motion_audio_id": null,
    "motion_audio_user_id": null,
    "linked_doorbots": [
      987001
    ]
  }
}
```


---


## 48. PUT /clients_api/chimes/987006/unlink (Unlink Chime from Doorbell)


```
curl -s -X PUT "http://localhost:8010/clients_api/chimes/987006/unlink" -H 'Content-Type: application/json' -d '{"doorbell_id": 987001}'
```


**Status:** 200


```json
{
  "type": "chime_settings",
  "settings": {
    "volume": 7,
    "ding_audio_id": "ring_default",
    "ding_audio_user_id": null,
    "motion_audio_id": null,
    "motion_audio_user_id": null,
    "linked_doorbots": []
  }
}
```


---


## 49. GET /clients_api/doorbots/987001/motion_zones (Motion Zones - Doorbell)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987001/motion_zones"
```


**Status:** 200


```json
{
  "type": "motion_zones",
  "count": 3,
  "results": [
    {
      "device_id": 987001,
      "zone_id": "zone_001",
      "zone_name": "Porch",
      "sensitivity": 7,
      "enabled": true,
      "coordinates": "0.1,0.2,0.9,0.8"
    },
    {
      "device_id": 987001,
      "zone_id": "zone_002",
      "zone_name": "Sidewalk",
      "sensitivity": 5,
      "enabled": true,
      "coordinates": "0.0,0.6,1.0,1.0"
    },
    {
      "device_id": 987001,
      "zone_id": "zone_003",
      "zone_name": "Front Yard",
      "sensitivity": 6,
      "enabled": true,
      "coordinates": "0.0,0.3,1.0,0.7"
    }
  ]
}
```


---


## 50. GET /clients_api/doorbots/987003/motion_zones (Motion Zones - Driveway)


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/987003/motion_zones"
```


**Status:** 200


```json
{
  "type": "motion_zones",
  "count": 3,
  "results": [
    {
      "device_id": 987003,
      "zone_id": "zone_007",
      "zone_name": "Driveway",
      "sensitivity": 8,
      "enabled": true,
      "coordinates": "0.1,0.1,0.9,0.9"
    },
    {
      "device_id": 987003,
      "zone_id": "zone_008",
      "zone_name": "Street",
      "sensitivity": 3,
      "enabled": false,
      "coordinates": "0.0,0.7,1.0,1.0"
    },
    {
      "device_id": 987003,
      "zone_id": "zone_009",
      "zone_name": "Garage Door",
      "sensitivity": 7,
      "enabled": true,
      "coordinates": "0.3,0.0,0.7,0.4"
    }
  ]
}
```


---


## 51. GET /clients_api/doorbots/999999/motion_zones (Motion Zones - Not Found (404))


```
curl -s -X GET "http://localhost:8010/clients_api/doorbots/999999/motion_zones"
```


**Status:** 404


```json
{
  "error": "Device 999999 not found"
}
```


---


## 52. GET /clients_api/notifications (List Notification Prefs)


```
curl -s -X GET "http://localhost:8010/clients_api/notifications"
```


**Status:** 200


```json
{
  "type": "notification_prefs",
  "count": 6,
  "results": [
    {
      "device_id": 987001,
      "motion_alerts": true,
      "ding_alerts": true,
      "person_alerts": true,
      "package_alerts": true
    },
    {
      "device_id": 987002,
      "motion_alerts": true,
      "ding_alerts": null,
      "person_alerts": true,
      "package_alerts": null
    },
    {
      "device_id": 987003,
      "motion_alerts": true,
      "ding_alerts": null,
      "person_alerts": true,
      "package_alerts": null
    },
    {
      "device_id": 987004,
      "motion_alerts": false,
      "ding_alerts": null,
      "person_alerts": false,
      "package_alerts": null
    },
    {
      "device_id": 987005,
      "motion_alerts": true,
      "ding_alerts": null,
      "person_alerts": true,
      "package_alerts": null
    },
    {
      "device_id": 987006,
      "motion_alerts": true,
      "ding_alerts": true,
      "person_alerts": null,
      "package_alerts": null
    }
  ]
}
```


---


## 53. GET /clients_api/notifications/987001 (Notification Pref - Doorbell)


```
curl -s -X GET "http://localhost:8010/clients_api/notifications/987001"
```


**Status:** 200


```json
{
  "type": "notification_pref",
  "notification_pref": {
    "device_id": 987001,
    "motion_alerts": true,
    "ding_alerts": true,
    "person_alerts": true,
    "package_alerts": true
  }
}
```


---


## 54. GET /clients_api/notifications/987004 (Notification Pref - Living Room (alerts off))


```
curl -s -X GET "http://localhost:8010/clients_api/notifications/987004"
```


**Status:** 200


```json
{
  "type": "notification_pref",
  "notification_pref": {
    "device_id": 987004,
    "motion_alerts": false,
    "ding_alerts": null,
    "person_alerts": false,
    "package_alerts": null
  }
}
```


---


## 55. GET /clients_api/notifications/999999 (Notification Pref - Not Found (404))


```
curl -s -X GET "http://localhost:8010/clients_api/notifications/999999"
```


**Status:** 404


```json
{
  "error": "Notification preferences for device 999999 not found"
}
```


---


## 56. PUT /clients_api/notifications/987002 (Update Notification - Motion Off)


```
curl -s -X PUT "http://localhost:8010/clients_api/notifications/987002" -H 'Content-Type: application/json' -d '{"motion_alerts": false}'
```


**Status:** 200


```json
{
  "type": "notification_pref",
  "notification_pref": {
    "device_id": 987002,
    "motion_alerts": false,
    "ding_alerts": null,
    "person_alerts": true,
    "package_alerts": null
  }
}
```


---


## 57. PUT /clients_api/notifications/987004 (Update Notification - Motion On)


```
curl -s -X PUT "http://localhost:8010/clients_api/notifications/987004" -H 'Content-Type: application/json' -d '{"motion_alerts": true}'
```


**Status:** 200


```json
{
  "type": "notification_pref",
  "notification_pref": {
    "device_id": 987004,
    "motion_alerts": true,
    "ding_alerts": null,
    "person_alerts": false,
    "package_alerts": null
  }
}
```


---


## 58. POST /clients_api/doorbots/987003/siren_on (Activate Siren - Driveway)


```
curl -s -X POST "http://localhost:8010/clients_api/doorbots/987003/siren_on" -H 'Content-Type: application/json' -d '{"duration_seconds": 15}'
```


**Status:** 200


```json
{
  "type": "siren",
  "device_id": 987003,
  "siren_status": {
    "seconds_remaining": 15
  }
}
```


---


## 59. POST /clients_api/doorbots/987003/siren_off (Deactivate Siren - Driveway)


```
curl -s -X POST "http://localhost:8010/clients_api/doorbots/987003/siren_off"
```


**Status:** 200


```json
{
  "type": "siren",
  "device_id": 987003,
  "siren_status": {
    "seconds_remaining": 0
  }
}
```


---


## 60. POST /clients_api/doorbots/987002/siren_on (Siren - No Siren Device (404))


```
curl -s -X POST "http://localhost:8010/clients_api/doorbots/987002/siren_on" -H 'Content-Type: application/json' -d '{"duration_seconds": 30}'
```


**Status:** 404


```json
{
  "error": "Device 987002 does not have a siren"
}
```


---


## 61. PUT /clients_api/doorbots/987003/floodlight_light_on (Floodlight On)


```
curl -s -X PUT "http://localhost:8010/clients_api/doorbots/987003/floodlight_light_on" -H 'Content-Type: application/json' -d '{"on": true}'
```


**Status:** 200


```json
{
  "type": "floodlight",
  "device_id": 987003,
  "floodlight_status": {
    "on": true
  }
}
```


---


## 62. PUT /clients_api/doorbots/987003/floodlight_light_on (Floodlight Off)


```
curl -s -X PUT "http://localhost:8010/clients_api/doorbots/987003/floodlight_light_on" -H 'Content-Type: application/json' -d '{"on": false}'
```


**Status:** 200


```json
{
  "type": "floodlight",
  "device_id": 987003,
  "floodlight_status": {
    "on": false
  }
}
```


---


## 63. PUT /clients_api/doorbots/987002/floodlight_light_on (Floodlight - No Floodlight (404))


```
curl -s -X PUT "http://localhost:8010/clients_api/doorbots/987002/floodlight_light_on" -H 'Content-Type: application/json' -d '{"on": true}'
```


**Status:** 404


```json
{
  "error": "Device 987002 does not have a floodlight"
}
```


---


## Summary

Total endpoints tested: 63
