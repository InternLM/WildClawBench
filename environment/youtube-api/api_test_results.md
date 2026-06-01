# YouTube Data API v3 (Mock) - API Test Results

**Total endpoints tested:** 49
**Date:** 2025-05-07

## 1. GET /health (Health check)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/health"
```

```json
{
  "status": "ok"
}
```

## 2. GET /youtube/v3/channels (GET Channel by ID)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/channels?id=UC_EquineHealthChannel&part=snippet,contentDetails,statistics,brandingSettings"
```

```json
{
  "kind": "youtube#channelListResponse",
  "pageInfo": {
    "totalResults": 1,
    "resultsPerPage": 1
  },
  "items": [
    {
      "id": "UC_EquineHealthChannel",
      "snippet": {
        "title": "Equine Wellness Academy",
        "description": "Learn programming, master new tools, and level up your developer career. New tutorials every Tuesday, Thursday & Saturday!\n\nTopics: Python, JavaScript, React, System Design, Career Advice, Code Reviews, and more.\n\nBusiness inquiries: techcraftacademy@gmail.com",
        "customUrl": "@techcraftacademy",
        "publishedAt": "2022-01-10T15:30:00Z",
        "thumbnails": {
          "default": {
            "url": "https://yt3.ggpht.com/ytc/techcraft_default.jpg",
            "width": 88,
            "height": 88
          },
          "medium": {
            "url": "https://yt3.ggpht.com/ytc/techcraft_medium.jpg",
            "width": 240,
            "height": 240
          },
          "high": {
            "url": "https://yt3.ggpht.com/ytc/techcraft_high.jpg",
            "width": 800,
            "height": 800
          }
        },
        "country": "US"
      },
      "statistics": {
        "viewCount": "22145830",
        "subscriberCount": "145000",
        "hiddenSubscriberCount": false,
        "videoCount": "380"
      },
      "contentDetails": {
        "relatedPlaylists": {
          "likes": "LL_TechCraftAcademy",
          "uploads": "UU_TechCraftAcademy"
        }
      },
      "brandingSettings": {
        "channel": {
          "title": "Equine Wellness Academy",
          "description": "Learn programming, master new tools, and level up your developer career.",
          "keywords": "programming tutorials coding python javascript react career advice developer",
          "unsubscribedTrailer": "vid_001",
          "country": "US"
        },
        "image": {
          "bannerExternalUrl": "https://yt3.googleusercontent.com/techcraft_banner.jpg"
        }
      }
    }
  ]
}
```

## 3. GET /youtube/v3/channels (GET Channel - 404)

**Status:** 404

```bash
curl -X GET "http://localhost:8008/youtube/v3/channels?id=INVALID_CHANNEL_99"
```

```json
{
  "error": "Channel INVALID_CHANNEL_99 not found"
}
```

## 4. GET /youtube/v3/videos (GET Videos by channel (limit 5))

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/videos?channelId=UC_EquineHealthChannel&part=snippet,contentDetails,statistics,status&maxResults=5"
```

```json
{
  "kind": "youtube#videoListResponse",
  "pageInfo": {
    "totalResults": 30,
    "resultsPerPage": 5
  },
  "items": [
    {
      "id": "vid_001",
      "snippet": {
        "publishedAt": "2025-03-15T14:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "5 Projects That Got Me Hired as a Developer",
        "description": "Building a portfolio is the #1 way to stand out. Here are 5 real projects that helped me land my first dev job.\\n\\n0:00 Intro\\n2:15 Project 1: Full-Stack Todo App\\n8:30 Project 2: Real-time Chat\\n15:00 Project 3: E-commerce Store\\n22:45 Project 4: CLI Tool\\n28:00 Project 5: Open Source Contribution\\n33:15 Tips for Your Portfolio\\n36:00 Outro",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_001/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/vid_001/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/vid_001/hqdefault.jpg",
            "width": 480,
            "height": 360
          },
          "maxres": {
            "url": "https://i.ytimg.com/vi/vid_001/maxresdefault.jpg",
            "width": 1280,
            "height": 720
          }
        },
        "channelTitle": "Equine Wellness Academy",
        "tags": [
          "portfolio",
          "developer job",
          "coding projects",
          "get hired",
          "junior developer",
          "projects",
          "resume"
        ],
        "categoryId": "27",
        "liveBroadcastContent": "none",
        "defaultLanguage": "en",
        "defaultAudioLanguage": "en"
      },
      "contentDetails": {
        "duration": "PT37M42S",
        "dimension": "2d",
        "definition": "hd",
        "caption": "true",
        "licensedContent": true,
        "projection": "rectangular"
      },
      "statistics": {
        "v
... (truncated)
```

## 5. GET /youtube/v3/videos (GET Video by ID - vid_001)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/videos?id=vid_001&part=snippet,contentDetails,statistics,status"
```

```json
{
  "kind": "youtube#videoListResponse",
  "pageInfo": {
    "totalResults": 1,
    "resultsPerPage": 25
  },
  "items": [
    {
      "id": "vid_001",
      "snippet": {
        "publishedAt": "2025-03-15T14:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "5 Projects That Got Me Hired as a Developer",
        "description": "Building a portfolio is the #1 way to stand out. Here are 5 real projects that helped me land my first dev job.\\n\\n0:00 Intro\\n2:15 Project 1: Full-Stack Todo App\\n8:30 Project 2: Real-time Chat\\n15:00 Project 3: E-commerce Store\\n22:45 Project 4: CLI Tool\\n28:00 Project 5: Open Source Contribution\\n33:15 Tips for Your Portfolio\\n36:00 Outro",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_001/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/vid_001/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/vid_001/hqdefault.jpg",
            "width": 480,
            "height": 360
          },
          "maxres": {
            "url": "https://i.ytimg.com/vi/vid_001/maxresdefault.jpg",
            "width": 1280,
            "height": 720
          }
        },
        "channelTitle": "Equine Wellness Academy",
        "tags": [
          "portfolio",
          "developer job",
          "coding projects",
          "get hired",
          "junior developer",
          "projects",
          "resume"
        ],
        "categoryId": "27",
        "liveBroadcastContent": "none",
        "defaultLanguage": "en",
        "defaultAudioLanguage": "en"
      },
      "contentDetails": {
        "duration": "PT37M42S",
        "dimension": "2d",
        "definition": "hd",
        "caption": "true",
        "licensedContent": true,
        "projection": "rectangular"
      },
      "statistics": {
        "v
... (truncated)
```

## 6. GET /youtube/v3/videos (GET Video - not found)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/videos?id=INVALID_ID_99999&part=snippet"
```

```json
{
  "kind": "youtube#videoListResponse",
  "pageInfo": {
    "totalResults": 0,
    "resultsPerPage": 25
  },
  "items": []
}
```

## 7. GET /youtube/v3/videos (GET Multiple videos by ID)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/videos?id=vid_001,vid_002,vid_003&part=snippet,statistics"
```

```json
{
  "kind": "youtube#videoListResponse",
  "pageInfo": {
    "totalResults": 3,
    "resultsPerPage": 25
  },
  "items": [
    {
      "id": "vid_001",
      "snippet": {
        "publishedAt": "2025-03-15T14:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "5 Projects That Got Me Hired as a Developer",
        "description": "Building a portfolio is the #1 way to stand out. Here are 5 real projects that helped me land my first dev job.\\n\\n0:00 Intro\\n2:15 Project 1: Full-Stack Todo App\\n8:30 Project 2: Real-time Chat\\n15:00 Project 3: E-commerce Store\\n22:45 Project 4: CLI Tool\\n28:00 Project 5: Open Source Contribution\\n33:15 Tips for Your Portfolio\\n36:00 Outro",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_001/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/vid_001/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/vid_001/hqdefault.jpg",
            "width": 480,
            "height": 360
          },
          "maxres": {
            "url": "https://i.ytimg.com/vi/vid_001/maxresdefault.jpg",
            "width": 1280,
            "height": 720
          }
        },
        "channelTitle": "Equine Wellness Academy",
        "tags": [
          "portfolio",
          "developer job",
          "coding projects",
          "get hired",
          "junior developer",
          "projects",
          "resume"
        ],
        "categoryId": "27",
        "liveBroadcastContent": "none",
        "defaultLanguage": "en",
        "defaultAudioLanguage": "en"
      },
      "contentDetails": {
        "duration": "PT37M42S",
        "dimension": "2d",
        "definition": "hd",
        "caption": "true",
        "licensedContent": true,
        "projection": "rectangular"
      },
      "statistics": {
        "v
... (truncated)
```

## 8. PUT /youtube/v3/videos (PUT Update video)

**Status:** 200

```bash
curl -X PUT "http://localhost:8008/youtube/v3/videos?part=snippet,status" -H 'Content-Type: application/json' -d '{"id": "vid_005", "snippet": {"title": "8 VS Code Extensions Senior Devs Use Daily", "tags": ["vs code", "productivity", "2025"]}}'
```

```json
{
  "kind": "youtube#video",
  "items": [
    {
      "id": "vid_005",
      "snippet": {
        "publishedAt": "2025-03-06T14:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "8 VS Code Extensions Senior Devs Use Daily",
        "description": "After 8 years of coding, these are the only VS Code extensions I actually use daily.\\n\\n0:00 Intro\\n0:45 Extension 1: GitLens\\n3:15 Extension 2: Error Lens\\n5:30 Extension 3: GitHub Copilot\\n8:00 Extension 4: REST Client\\n10:15 Extension 5: Docker\\n12:00 Extension 6: Prettier\\n13:30 Extension 7: Thunder Client\\n15:00 Bonus Tips",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_005/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/vid_005/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/vid_005/hqdefault.jpg",
            "width": 480,
            "height": 360
          },
          "maxres": {
            "url": "https://i.ytimg.com/vi/vid_005/maxresdefault.jpg",
            "width": 1280,
            "height": 720
          }
        },
        "channelTitle": "Equine Wellness Academy",
        "tags": [
          "vs code",
          "productivity",
          "2025"
        ],
        "categoryId": "28",
        "liveBroadcastContent": "none",
        "defaultLanguage": "en",
        "defaultAudioLanguage": "en"
      },
      "contentDetails": {
        "duration": "PT16M22S",
        "dimension": "2d",
        "definition": "hd",
        "caption": "true",
        "licensedContent": true,
        "projection": "rectangular"
      },
      "statistics": {
        "viewCount": "95432",
        "likeCount": "5678",
        "dislikeCount": "45",
        "commentCount": "876"
      },
      "status": {
        "uploadStatus": "processed",
        "privacyStatus": "publi
... (truncated)
```

## 9. PUT /youtube/v3/videos (PUT Update video - 404)

**Status:** 404

```bash
curl -X PUT "http://localhost:8008/youtube/v3/videos?part=snippet" -H 'Content-Type: application/json' -d '{"id": "INVALID_ID_99999", "snippet": {"title": "Test"}}'
```

```json
{
  "error": "Video INVALID_ID_99999 not found"
}
```

## 10. DELETE /youtube/v3/videos (DELETE Video)

**Status:** 204

```bash
curl -X DELETE "http://localhost:8008/youtube/v3/videos?id=vid_030"
```

_(No content - 204)_

## 11. DELETE /youtube/v3/videos (DELETE Video - 404)

**Status:** 404

```bash
curl -X DELETE "http://localhost:8008/youtube/v3/videos?id=INVALID_ID_99999"
```

```json
{
  "error": "Video INVALID_ID_99999 not found"
}
```

## 12. GET /youtube/v3/playlists (GET Playlists by channel)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/playlists?channelId=UC_EquineHealthChannel&part=snippet,contentDetails,status&maxResults=10"
```

```json
{
  "kind": "youtube#playlistListResponse",
  "pageInfo": {
    "totalResults": 10,
    "resultsPerPage": 10
  },
  "items": [
    {
      "id": "PL_001",
      "snippet": {
        "publishedAt": "2022-03-15T10:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Python for Beginners",
        "description": "Complete Python course from zero to confident programmer. Follow along in order!",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/playlist_PL_001/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/playlist_PL_001/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/playlist_PL_001/hqdefault.jpg",
            "width": 480,
            "height": 360
          }
        },
        "channelTitle": "Equine Wellness Academy"
      },
      "status": {
        "privacyStatus": "public"
      },
      "contentDetails": {
        "itemCount": 12
      }
    },
    {
      "id": "PL_002",
      "snippet": {
        "publishedAt": "2023-01-10T10:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Web Dev 2025",
        "description": "Frontend and backend web development tutorials for the modern stack.",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/playlist_PL_002/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/playlist_PL_002/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/playlist_PL_002/hqdefault.jpg",
            "width": 480,
            "height": 360
          }
        },
        "channelTitle": "Equine Wellness Academy"
      },
      "status": {
        "privacyStatus": "public"
     
... (truncated)
```

## 13. GET /youtube/v3/playlists (GET Playlist by ID)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/playlists?id=PL_001&part=snippet,contentDetails,status"
```

```json
{
  "kind": "youtube#playlistListResponse",
  "pageInfo": {
    "totalResults": 1,
    "resultsPerPage": 25
  },
  "items": [
    {
      "id": "PL_001",
      "snippet": {
        "publishedAt": "2022-03-15T10:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Python for Beginners",
        "description": "Complete Python course from zero to confident programmer. Follow along in order!",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/playlist_PL_001/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/playlist_PL_001/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/playlist_PL_001/hqdefault.jpg",
            "width": 480,
            "height": 360
          }
        },
        "channelTitle": "Equine Wellness Academy"
      },
      "status": {
        "privacyStatus": "public"
      },
      "contentDetails": {
        "itemCount": 12
      }
    }
  ]
}
```

## 14. GET /youtube/v3/playlists (GET Playlist - not found)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/playlists?id=INVALID_PL_99999&part=snippet"
```

```json
{
  "kind": "youtube#playlistListResponse",
  "pageInfo": {
    "totalResults": 0,
    "resultsPerPage": 25
  },
  "items": []
}
```

## 15. POST /youtube/v3/playlists (POST Create playlist)

**Status:** 201

```bash
curl -X POST "http://localhost:8008/youtube/v3/playlists?part=snippet,status" -H 'Content-Type: application/json' -d '{"snippet": {"title": "AI & Machine Learning", "description": "AI tutorials"}, "status": {"privacyStatus": "public"}}'
```

```json
{
  "kind": "youtube#playlist",
  "items": [
    {
      "id": "PL_011",
      "snippet": {
        "publishedAt": "2026-05-06T18:43:43Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "AI & Machine Learning",
        "description": "AI tutorials",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/playlist_PL_011/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/playlist_PL_011/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/playlist_PL_011/hqdefault.jpg",
            "width": 480,
            "height": 360
          }
        },
        "channelTitle": "Equine Wellness Academy"
      },
      "status": {
        "privacyStatus": "public"
      },
      "contentDetails": {
        "itemCount": 0
      }
    }
  ]
}
```

## 16. PUT /youtube/v3/playlists (PUT Update playlist)

**Status:** 200

```bash
curl -X PUT "http://localhost:8008/youtube/v3/playlists?part=snippet" -H 'Content-Type: application/json' -d '{"id": "PL_005", "snippet": {"title": "Tool Reviews 2025"}}'
```

```json
{
  "kind": "youtube#playlist",
  "items": [
    {
      "id": "PL_005",
      "snippet": {
        "publishedAt": "2022-09-12T10:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Tool Reviews 2025",
        "description": "Honest reviews of developer tools IDEs and frameworks.",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/playlist_PL_005/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/playlist_PL_005/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/playlist_PL_005/hqdefault.jpg",
            "width": 480,
            "height": 360
          }
        },
        "channelTitle": "Equine Wellness Academy"
      },
      "status": {
        "privacyStatus": "public"
      },
      "contentDetails": {
        "itemCount": 10
      }
    }
  ]
}
```

## 17. PUT /youtube/v3/playlists (PUT Update playlist - 404)

**Status:** 404

```bash
curl -X PUT "http://localhost:8008/youtube/v3/playlists?part=snippet" -H 'Content-Type: application/json' -d '{"id": "INVALID_PL_99999", "snippet": {"title": "Test"}}'
```

```json
{
  "error": "Playlist INVALID_PL_99999 not found"
}
```

## 18. DELETE /youtube/v3/playlists (DELETE Playlist)

**Status:** 204

```bash
curl -X DELETE "http://localhost:8008/youtube/v3/playlists?id=PL_010"
```

_(No content - 204)_

## 19. DELETE /youtube/v3/playlists (DELETE Playlist - 404)

**Status:** 404

```bash
curl -X DELETE "http://localhost:8008/youtube/v3/playlists?id=INVALID_PL_99999"
```

```json
{
  "error": "Playlist INVALID_PL_99999 not found"
}
```

## 20. GET /youtube/v3/playlistItems (GET Playlist items)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/playlistItems?playlistId=PL_001&part=snippet,contentDetails&maxResults=10"
```

```json
{
  "kind": "youtube#playlistItemListResponse",
  "pageInfo": {
    "totalResults": 2,
    "resultsPerPage": 10
  },
  "items": [
    {
      "id": "PLI_001",
      "snippet": {
        "publishedAt": "2025-02-27T14:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Python for Beginners - Complete Course 2025",
        "playlistId": "PL_001",
        "position": 0,
        "resourceId": {
          "kind": "youtube#video",
          "videoId": "vid_002"
        },
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_002/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/vid_002/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/vid_002/hqdefault.jpg",
            "width": 480,
            "height": 360
          }
        },
        "channelTitle": "Equine Wellness Academy"
      },
      "contentDetails": {
        "videoId": "vid_002",
        "videoPublishedAt": "2025-02-27T14:00:00Z"
      }
    },
    {
      "id": "PLI_002",
      "snippet": {
        "publishedAt": "2025-02-27T14:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Building a REST API with FastAPI - Full Tutorial",
        "playlistId": "PL_001",
        "position": 1,
        "resourceId": {
          "kind": "youtube#video",
          "videoId": "vid_009"
        },
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_009/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/vid_009/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/vid_009/hqdefault.jpg",
            "width": 480,
            "height": 360
          }
... (truncated)
```

## 21. POST /youtube/v3/playlistItems (POST Insert playlist item)

**Status:** 201

```bash
curl -X POST "http://localhost:8008/youtube/v3/playlistItems?part=snippet" -H 'Content-Type: application/json' -d '{"snippet": {"playlistId": "PL_001", "resourceId": {"kind": "youtube#video", "videoId": "vid_020"}, "position": 2}}'
```

```json
{
  "kind": "youtube#playlistItem",
  "items": [
    {
      "id": "PLI_026",
      "snippet": {
        "publishedAt": "2026-05-06T18:43:43Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Build a CLI Tool with Go - Beginner Friendly",
        "playlistId": "PL_001",
        "position": 2,
        "resourceId": {
          "kind": "youtube#video",
          "videoId": "vid_020"
        },
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_020/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/vid_020/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/vid_020/hqdefault.jpg",
            "width": 480,
            "height": 360
          }
        },
        "channelTitle": "Equine Wellness Academy"
      },
      "contentDetails": {
        "videoId": "vid_020",
        "videoPublishedAt": "2025-02-06T14:00:00Z"
      }
    }
  ]
}
```

## 22. POST /youtube/v3/playlistItems (POST Insert playlist item - invalid playlist)

**Status:** 400

```bash
curl -X POST "http://localhost:8008/youtube/v3/playlistItems?part=snippet" -H 'Content-Type: application/json' -d '{"snippet": {"playlistId": "INVALID_PL", "resourceId": {"kind": "youtube#video", "videoId": "vid_001"}}}'
```

```json
{
  "error": "Playlist INVALID_PL not found"
}
```

## 23. PUT /youtube/v3/playlistItems (PUT Update playlist item position)

**Status:** 200

```bash
curl -X PUT "http://localhost:8008/youtube/v3/playlistItems?part=snippet" -H 'Content-Type: application/json' -d '{"id": "PLI_003", "snippet": {"position": 5}}'
```

```json
{
  "kind": "youtube#playlistItem",
  "items": [
    {
      "id": "PLI_003",
      "snippet": {
        "publishedAt": "2025-03-11T14:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "React vs Vue in 2025 - Which Should You Learn?",
        "playlistId": "PL_002",
        "position": 5,
        "resourceId": {
          "kind": "youtube#video",
          "videoId": "vid_003"
        },
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_003/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/vid_003/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/vid_003/hqdefault.jpg",
            "width": 480,
            "height": 360
          }
        },
        "channelTitle": "Equine Wellness Academy"
      },
      "contentDetails": {
        "videoId": "vid_003",
        "videoPublishedAt": "2025-03-11T14:00:00Z"
      }
    }
  ]
}
```

## 24. DELETE /youtube/v3/playlistItems (DELETE Playlist item)

**Status:** 204

```bash
curl -X DELETE "http://localhost:8008/youtube/v3/playlistItems?id=PLI_025"
```

_(No content - 204)_

## 25. DELETE /youtube/v3/playlistItems (DELETE Playlist item - 404)

**Status:** 404

```bash
curl -X DELETE "http://localhost:8008/youtube/v3/playlistItems?id=INVALID_PLI_99999"
```

```json
{
  "error": "Playlist item INVALID_PLI_99999 not found"
}
```

## 26. GET /youtube/v3/commentThreads (GET Comment threads for video)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/commentThreads?videoId=vid_001&part=snippet,replies&maxResults=10"
```

```json
{
  "kind": "youtube#commentThreadListResponse",
  "pageInfo": {
    "totalResults": 4,
    "resultsPerPage": 10
  },
  "items": [
    {
      "kind": "youtube#commentThread",
      "id": "cmt_041",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "videoId": "vid_001",
        "topLevelComment": {
          "kind": "youtube#comment",
          "id": "cmt_041",
          "snippet": {
            "authorDisplayName": "GratefulDev",
            "authorChannelId": {
              "value": "UC_user034"
            },
            "textDisplay": "Update: I followed your advice and built all 5 projects. Got 3 interviews in my first week of applying! This channel is gold.",
            "textOriginal": "Update: I followed your advice and built all 5 projects. Got 3 interviews in my first week of applying! This channel is gold.",
            "likeCount": 38,
            "publishedAt": "2025-04-01T10:00:00Z",
            "updatedAt": "2025-04-01T10:00:00Z",
            "videoId": "vid_001",
            "parentId": null
          }
        },
        "canReply": true,
        "totalReplyCount": 0,
        "isPublic": true
      }
    },
    {
      "kind": "youtube#commentThread",
      "id": "cmt_004",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "videoId": "vid_001",
        "topLevelComment": {
          "kind": "youtube#comment",
          "id": "cmt_004",
          "snippet": {
            "authorDisplayName": "FullStackFrank",
            "authorChannelId": {
              "value": "UC_user003"
            },
            "textDisplay": "Been watching for 2 years and this is your best video yet. The advice about open source contributions is SO underrated.",
            "textOriginal": "Been watching for 2 years and this is your best video yet. The advice about open source contributions is SO underrated.",
            "likeCount": 8,
            "publishedAt": "2025-03-17T14:20:00Z",
            "updatedAt": "2025-03-17T14:20:0
... (truncated)
```

## 27. GET /youtube/v3/commentThreads (GET Comment threads - held for review)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/commentThreads?videoId=vid_019&part=snippet,replies&moderationStatus=heldForReview"
```

```json
{
  "kind": "youtube#commentThreadListResponse",
  "pageInfo": {
    "totalResults": 1,
    "resultsPerPage": 20
  },
  "items": [
    {
      "kind": "youtube#commentThread",
      "id": "cmt_028",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "videoId": "vid_019",
        "topLevelComment": {
          "kind": "youtube#comment",
          "id": "cmt_028",
          "snippet": {
            "authorDisplayName": "ControversialTake",
            "authorChannelId": {
              "value": "UC_user023"
            },
            "textDisplay": "This feels like humble bragging about your salary tbh...",
            "textOriginal": "This feels like humble bragging about your salary tbh...",
            "likeCount": 2,
            "publishedAt": "2025-02-11T22:00:00Z",
            "updatedAt": "2025-02-11T22:00:00Z",
            "videoId": "vid_019",
            "parentId": null
          }
        },
        "canReply": true,
        "totalReplyCount": 0,
        "isPublic": true
      }
    }
  ]
}
```

## 28. POST /youtube/v3/commentThreads (POST Create comment thread)

**Status:** 201

```bash
curl -X POST "http://localhost:8008/youtube/v3/commentThreads?part=snippet" -H 'Content-Type: application/json' -d '{"snippet": {"videoId": "vid_001", "topLevelComment": {"snippet": {"textOriginal": "Great video!"}}}}'
```

```json
{
  "kind": "youtube#commentThread",
  "items": [
    {
      "kind": "youtube#commentThread",
      "id": "cmt_051",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "videoId": "vid_001",
        "topLevelComment": {
          "kind": "youtube#comment",
          "id": "cmt_051",
          "snippet": {
            "authorDisplayName": "Equine Wellness Academy",
            "authorChannelId": {
              "value": "UC_EquineHealthChannel"
            },
            "textDisplay": "Great video!",
            "textOriginal": "Great video!",
            "likeCount": 0,
            "publishedAt": "2026-05-06T18:43:43Z",
            "updatedAt": "2026-05-06T18:43:43Z",
            "videoId": "vid_001",
            "parentId": null
          }
        },
        "canReply": true,
        "totalReplyCount": 0,
        "isPublic": true
      }
    }
  ]
}
```

## 29. GET /youtube/v3/comments (GET Replies to comment)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/comments?parentId=cmt_002&part=snippet"
```

```json
{
  "kind": "youtube#commentListResponse",
  "pageInfo": {
    "totalResults": 1,
    "resultsPerPage": 20
  },
  "items": [
    {
      "kind": "youtube#comment",
      "id": "cmt_003",
      "snippet": {
        "authorDisplayName": "Equine Wellness Academy",
        "authorChannelId": {
          "value": "UC_EquineHealthChannel"
        },
        "textDisplay": "Great question! I used Socket.io because it handles reconnection and fallbacks automatically. For a portfolio piece, Socket.io is perfect \u2014 it shows you understand real-time concepts without reinventing the wheel.",
        "textOriginal": "Great question! I used Socket.io because it handles reconnection and fallbacks automatically. For a portfolio piece, Socket.io is perfect \u2014 it shows you understand real-time concepts without reinventing the wheel.",
        "likeCount": 32,
        "publishedAt": "2025-03-16T12:00:00Z",
        "updatedAt": "2025-03-16T12:00:00Z",
        "videoId": "vid_001",
        "parentId": "cmt_002"
      }
    }
  ]
}
```

## 30. POST /youtube/v3/comments (POST Reply to comment)

**Status:** 201

```bash
curl -X POST "http://localhost:8008/youtube/v3/comments?part=snippet" -H 'Content-Type: application/json' -d '{"snippet": {"parentId": "cmt_005", "textOriginal": "Thanks! I used Next.js."}}'
```

```json
{
  "kind": "youtube#comment",
  "items": [
    {
      "kind": "youtube#comment",
      "id": "cmt_052",
      "snippet": {
        "authorDisplayName": "Equine Wellness Academy",
        "authorChannelId": {
          "value": "UC_EquineHealthChannel"
        },
        "textDisplay": "Thanks! I used Next.js.",
        "textOriginal": "Thanks! I used Next.js.",
        "likeCount": 0,
        "publishedAt": "2026-05-06T18:43:43Z",
        "updatedAt": "2026-05-06T18:43:43Z",
        "videoId": "vid_004",
        "parentId": "cmt_005"
      }
    }
  ]
}
```

## 31. POST /youtube/v3/comments (POST Reply - invalid parent)

**Status:** 400

```bash
curl -X POST "http://localhost:8008/youtube/v3/comments?part=snippet" -H 'Content-Type: application/json' -d '{"snippet": {"parentId": "INVALID_CMT_99999", "textOriginal": "Fail"}}'
```

```json
{
  "error": "Parent comment INVALID_CMT_99999 not found"
}
```

## 32. PUT /youtube/v3/comments (PUT Update comment)

**Status:** 200

```bash
curl -X PUT "http://localhost:8008/youtube/v3/comments?part=snippet" -H 'Content-Type: application/json' -d '{"id": "cmt_003", "snippet": {"textOriginal": "Updated reply."}}'
```

```json
{
  "kind": "youtube#comment",
  "items": [
    {
      "kind": "youtube#comment",
      "id": "cmt_003",
      "snippet": {
        "authorDisplayName": "Equine Wellness Academy",
        "authorChannelId": {
          "value": "UC_EquineHealthChannel"
        },
        "textDisplay": "Updated reply.",
        "textOriginal": "Updated reply.",
        "likeCount": 32,
        "publishedAt": "2025-03-16T12:00:00Z",
        "updatedAt": "2026-05-06T18:43:43Z",
        "videoId": "vid_001",
        "parentId": "cmt_002"
      }
    }
  ]
}
```

## 33. PUT /youtube/v3/comments (PUT Update comment - 404)

**Status:** 404

```bash
curl -X PUT "http://localhost:8008/youtube/v3/comments?part=snippet" -H 'Content-Type: application/json' -d '{"id": "INVALID_CMT_99999", "snippet": {"textOriginal": "Fail"}}'
```

```json
{
  "error": "Comment INVALID_CMT_99999 not found"
}
```

## 34. DELETE /youtube/v3/comments (DELETE Comment (spam))

**Status:** 204

```bash
curl -X DELETE "http://localhost:8008/youtube/v3/comments?id=cmt_026"
```

_(No content - 204)_

## 35. DELETE /youtube/v3/comments (DELETE Comment - 404)

**Status:** 404

```bash
curl -X DELETE "http://localhost:8008/youtube/v3/comments?id=INVALID_CMT_99999"
```

```json
{
  "error": "Comment INVALID_CMT_99999 not found"
}
```

## 36. POST /youtube/v3/comments/setModerationStatus (POST Set moderation status)

**Status:** 204

```bash
curl -X POST "http://localhost:8008/youtube/v3/comments/setModerationStatus?id=cmt_028&moderationStatus=published"
```

_(No content - 204)_

## 37. POST /youtube/v3/comments/setModerationStatus (POST Set moderation - not found)

**Status:** 404

```bash
curl -X POST "http://localhost:8008/youtube/v3/comments/setModerationStatus?id=INVALID_CMT_99999&moderationStatus=rejected"
```

```json
{
  "error": "No matching comments found"
}
```

## 38. GET /youtube/v3/search (Search - python)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/search?q=python&channelId=UC_EquineHealthChannel&part=snippet&maxResults=10"
```

```json
{
  "kind": "youtube#searchListResponse",
  "pageInfo": {
    "totalResults": 2,
    "resultsPerPage": 10
  },
  "items": [
    {
      "kind": "youtube#searchResult",
      "id": {
        "kind": "youtube#video",
        "videoId": "vid_002"
      },
      "snippet": {
        "publishedAt": "2025-03-13T14:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Python for Beginners - Complete Course 2025",
        "description": "Everything you need to start coding in Python from scratch. No experience required!\\n\\n0:00 Intro & Setup\\n3:20 Variables & Data Types\\n12:45 Control Flow\\n22:00 Functions\\n35:15 Lists & Dictionaries\\",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_002/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/vid_002/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/vid_002/hqdefault.jpg",
            "width": 480,
            "height": 360
          },
          "maxres": {
            "url": "https://i.ytimg.com/vi/vid_002/maxresdefault.jpg",
            "width": 1280,
            "height": 720
          }
        },
        "channelTitle": "Equine Wellness Academy",
        "liveBroadcastContent": "none"
      }
    },
    {
      "kind": "youtube#searchResult",
      "id": {
        "kind": "youtube#video",
        "videoId": "vid_009"
      },
      "snippet": {
        "publishedAt": "2025-02-27T14:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Building a REST API with FastAPI - Full Tutorial",
        "description": "Complete hands-on tutorial building a production-ready REST API with Python's FastAPI framework.\\n\\n0:00 Intro & Setup\\n4:00 Project Structure\\n8:30 First Endpoint\\n14:00 Pydantic Models\\n20:00 Databa",
        "thumbnails": {
          "default": {
 
... (truncated)
```

## 39. GET /youtube/v3/search (Search - career by viewCount)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/search?q=career&channelId=UC_EquineHealthChannel&part=snippet&order=viewCount&maxResults=5"
```

```json
{
  "kind": "youtube#searchListResponse",
  "pageInfo": {
    "totalResults": 5,
    "resultsPerPage": 5
  },
  "items": [
    {
      "kind": "youtube#searchResult",
      "id": {
        "kind": "youtube#video",
        "videoId": "vid_019"
      },
      "snippet": {
        "publishedAt": "2025-02-08T14:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Why I Left My $200K FAANG Job",
        "description": "After 3 years at a big tech company, I quit. Here's the real reason and what I'm doing instead.\\n\\n0:00 The Decision\\n4:00 What FAANG Was Like\\n10:00 The Breaking Point\\n16:00 Financial Preparation\\n2",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_019/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/vid_019/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/vid_019/hqdefault.jpg",
            "width": 480,
            "height": 360
          },
          "maxres": {
            "url": "https://i.ytimg.com/vi/vid_019/maxresdefault.jpg",
            "width": 1280,
            "height": 720
          }
        },
        "channelTitle": "Equine Wellness Academy",
        "liveBroadcastContent": "none"
      }
    },
    {
      "kind": "youtube#searchResult",
      "id": {
        "kind": "youtube#video",
        "videoId": "vid_008"
      },
      "snippet": {
        "publishedAt": "2025-03-01T14:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "How I'd Learn to Code in 2025 (If I Could Start Over)",
        "description": "If I could go back and restart my coding journey with what I know now, here's exactly what I'd do differently.\\n\\n0:00 My Original Path (Mistakes)\\n4:30 Step 1: Pick ONE Language\\n8:00 Step 2: Build P",
        "thumbnails": {
          "default": {
            "u
... (truncated)
```

## 40. GET /youtube/v3/search (Search - order by date)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/search?channelId=UC_EquineHealthChannel&part=snippet&order=date&maxResults=5"
```

```json
{
  "kind": "youtube#searchListResponse",
  "pageInfo": {
    "totalResults": 28,
    "resultsPerPage": 5
  },
  "items": [
    {
      "kind": "youtube#searchResult",
      "id": {
        "kind": "youtube#video",
        "videoId": "vid_001"
      },
      "snippet": {
        "publishedAt": "2025-03-15T14:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "5 Projects That Got Me Hired as a Developer",
        "description": "Building a portfolio is the #1 way to stand out. Here are 5 real projects that helped me land my first dev job.\\n\\n0:00 Intro\\n2:15 Project 1: Full-Stack Todo App\\n8:30 Project 2: Real-time Chat\\n15:0",
        "thumbnails": {
          "default": {
            "url": "https://i.ytimg.com/vi/vid_001/default.jpg",
            "width": 120,
            "height": 90
          },
          "medium": {
            "url": "https://i.ytimg.com/vi/vid_001/mqdefault.jpg",
            "width": 320,
            "height": 180
          },
          "high": {
            "url": "https://i.ytimg.com/vi/vid_001/hqdefault.jpg",
            "width": 480,
            "height": 360
          },
          "maxres": {
            "url": "https://i.ytimg.com/vi/vid_001/maxresdefault.jpg",
            "width": 1280,
            "height": 720
          }
        },
        "channelTitle": "Equine Wellness Academy",
        "liveBroadcastContent": "none"
      }
    },
    {
      "kind": "youtube#searchResult",
      "id": {
        "kind": "youtube#video",
        "videoId": "vid_002"
      },
      "snippet": {
        "publishedAt": "2025-03-13T14:00:00Z",
        "channelId": "UC_EquineHealthChannel",
        "title": "Python for Beginners - Complete Course 2025",
        "description": "Everything you need to start coding in Python from scratch. No experience required!\\n\\n0:00 Intro & Setup\\n3:20 Variables & Data Types\\n12:45 Control Flow\\n22:00 Functions\\n35:15 Lists & Dictionaries\\",
        "thumbnails": {
          "default": {
       
... (truncated)
```

## 41. GET /youtube/v3/search (Search - no results)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/search?q=xyznonexistent123&channelId=UC_EquineHealthChannel&part=snippet"
```

```json
{
  "kind": "youtube#searchListResponse",
  "pageInfo": {
    "totalResults": 0,
    "resultsPerPage": 25
  },
  "items": []
}
```

## 42. GET /youtube/v3/videoCategories (GET Video categories)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/videoCategories?regionCode=US&part=snippet"
```

```json
{
  "kind": "youtube#videoCategoryListResponse",
  "items": [
    {
      "kind": "youtube#videoCategory",
      "id": "1",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "title": "Film & Animation",
        "assignable": true
      }
    },
    {
      "kind": "youtube#videoCategory",
      "id": "2",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "title": "Autos & Vehicles",
        "assignable": true
      }
    },
    {
      "kind": "youtube#videoCategory",
      "id": "10",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "title": "Music",
        "assignable": true
      }
    },
    {
      "kind": "youtube#videoCategory",
      "id": "15",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "title": "Pets & Animals",
        "assignable": true
      }
    },
    {
      "kind": "youtube#videoCategory",
      "id": "17",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "title": "Sports",
        "assignable": true
      }
    },
    {
      "kind": "youtube#videoCategory",
      "id": "20",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "title": "Gaming",
        "assignable": true
      }
    },
    {
      "kind": "youtube#videoCategory",
      "id": "22",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "title": "People & Blogs",
        "assignable": true
      }
    },
    {
      "kind": "youtube#videoCategory",
      "id": "23",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "title": "Comedy",
        "assignable": true
      }
    },
    {
      "kind": "youtube#videoCategory",
      "id": "24",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "title": "Entertainment",
        "assignable": true
      }
    },
    {
      "kind": "youtube#videoCategory",
      "id": "25",
      "snippet": {
        "channelId": "UC_EquineHealthChannel",
        "title": 
... (truncated)
```

## 43. GET /youtube/v3/captions (GET Captions for vid_002)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/captions?videoId=vid_002&part=snippet"
```

```json
{
  "kind": "youtube#captionListResponse",
  "items": [
    {
      "kind": "youtube#caption",
      "id": "cap_002",
      "snippet": {
        "videoId": "vid_002",
        "lastUpdated": "2025-03-13T14:30:00Z",
        "trackKind": "ASR",
        "language": "en",
        "name": "English (auto-generated)",
        "isDraft": false
      }
    },
    {
      "kind": "youtube#caption",
      "id": "cap_003",
      "snippet": {
        "videoId": "vid_002",
        "lastUpdated": "2025-03-20T10:00:00Z",
        "trackKind": "standard",
        "language": "es",
        "name": "Spanish",
        "isDraft": false
      }
    }
  ]
}
```

## 44. GET /youtube/v3/captions (GET Captions - 404)

**Status:** 404

```bash
curl -X GET "http://localhost:8008/youtube/v3/captions?videoId=INVALID_VID_99&part=snippet"
```

```json
{
  "error": "Video INVALID_VID_99 not found"
}
```

## 45. GET /youtube/v3/channelSections (GET Channel sections)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/v3/channelSections?channelId=UC_EquineHealthChannel&part=snippet,contentDetails"
```

```json
{
  "kind": "youtube#channelSectionListResponse",
  "items": [
    {
      "kind": "youtube#channelSection",
      "id": "section_001",
      "snippet": {
        "type": "singlePlaylist",
        "channelId": "UC_EquineHealthChannel",
        "title": "Python for Beginners",
        "position": 0
      },
      "contentDetails": {
        "playlists": [
          "PL_001"
        ]
      }
    },
    {
      "kind": "youtube#channelSection",
      "id": "section_002",
      "snippet": {
        "type": "singlePlaylist",
        "channelId": "UC_EquineHealthChannel",
        "title": "Web Dev 2025",
        "position": 1
      },
      "contentDetails": {
        "playlists": [
          "PL_002"
        ]
      }
    },
    {
      "kind": "youtube#channelSection",
      "id": "section_003",
      "snippet": {
        "type": "singlePlaylist",
        "channelId": "UC_EquineHealthChannel",
        "title": "Career Advice",
        "position": 2
      },
      "contentDetails": {
        "playlists": [
          "PL_003"
        ]
      }
    },
    {
      "kind": "youtube#channelSection",
      "id": "section_004",
      "snippet": {
        "type": "popularUploads",
        "channelId": "UC_EquineHealthChannel",
        "title": "Popular Uploads",
        "position": 3
      },
      "contentDetails": {
        "playlists": []
      }
    },
    {
      "kind": "youtube#channelSection",
      "id": "section_005",
      "snippet": {
        "type": "singlePlaylist",
        "channelId": "UC_EquineHealthChannel",
        "title": "System Design",
        "position": 4
      },
      "contentDetails": {
        "playlists": [
          "PL_007"
        ]
      }
    },
    {
      "kind": "youtube#channelSection",
      "id": "section_006",
      "snippet": {
        "type": "singlePlaylist",
        "channelId": "UC_EquineHealthChannel",
        "title": "Shorts & Quick Tips",
        "position": 5
      },
      "contentDetails": {
        "playlists": [
          "PL_008"
        
... (truncated)
```

## 46. GET /youtube/v3/channelSections (GET Channel sections - 404)

**Status:** 404

```bash
curl -X GET "http://localhost:8008/youtube/v3/channelSections?channelId=INVALID_CHANNEL_99&part=snippet"
```

```json
{
  "error": "Channel INVALID_CHANNEL_99 not found"
}
```

## 47. GET /youtube/analytics/v2/reports (GET Channel analytics)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/analytics/v2/reports?ids=channel==UC_EquineHealthChannel&metrics=views,estimatedMinutesWatched,subscribersGained"
```

```json
{
  "kind": "youtubeAnalytics#resultTable",
  "channelId": "UC_EquineHealthChannel",
  "period": "last28Days",
  "metrics": {
    "period": "last28Days",
    "views": 487234,
    "estimatedMinutesWatched": 1245678,
    "averageViewDuration": 456,
    "subscribersGained": 3245,
    "subscribersLost": 187,
    "likes": 24567,
    "dislikes": 456,
    "comments": 3890,
    "shares": 8901
  }
}
```

## 48. GET /youtube/analytics/v2/reports (GET Video analytics)

**Status:** 200

```bash
curl -X GET "http://localhost:8008/youtube/analytics/v2/reports?ids=channel==UC_EquineHealthChannel&filters=video==vid_001&metrics=views"
```

```json
{
  "kind": "youtubeAnalytics#resultTable",
  "videoId": "vid_001",
  "metrics": {
    "videoId": "vid_001",
    "views": 142567,
    "estimatedMinutesWatched": 356890,
    "averageViewDuration": 1245,
    "likes": 8234,
    "dislikes": 45,
    "comments": 567,
    "shares": 2345,
    "averageViewPercentage": 55.2
  }
}
```

## 49. GET /youtube/analytics/v2/reports (GET Video analytics - 404)

**Status:** 404

```bash
curl -X GET "http://localhost:8008/youtube/analytics/v2/reports?ids=channel==UC_EquineHealthChannel&filters=video==INVALID_VID_99&metrics=views"
```

```json
{
  "error": "Analytics for video INVALID_VID_99 not found"
}
```

