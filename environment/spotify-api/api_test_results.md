# Spotify Mock API — Test Results

Base URL: `http://localhost:8039` (docker-compose: `http://spotify-api:8039`)

## Endpoints

| Method | Path                                  | Status   |
|--------|---------------------------------------|----------|
| GET    | /health                               | 200      |
| GET    | /v1/me                                | 200      |
| GET    | /v1/me/playlists                      | 200      |
| GET    | /v1/playlists/{playlist_id}           | 200/404  |
| GET    | /v1/playlists/{playlist_id}/tracks    | 200/404  |
| POST   | /v1/users/{user_id}/playlists         | 201      |
| POST   | /v1/playlists/{playlist_id}/tracks    | 201/404  |
| GET    | /v1/search                            | 200      |
| GET    | /v1/me/player                         | 200      |
| PUT    | /v1/me/player/play                    | 200      |

## Seed data

- User: `user-leo` (Leo Vasquez, premium)
- Artists: 4 | Albums: 4 | Tracks: 10
- Playlists: 4 (owned by user-leo) with 11 playlist-track links

## Notes

- IDs use Spotify-style 22-char base62 identifiers; newly created playlists get fresh ones.
- Mutations (new playlists, added tracks, playback state) are held in process
  memory and reset on container restart.
- `GET /v1/search` accepts `q` and a comma-separated `type` (track/album/artist).
- `PUT /v1/me/player/play` accepts `uris` or a playlist `context_uri` and sets the
  current item + `is_playing` true.
