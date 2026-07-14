# environment — MOCK-API FLEET

101 self-contained FastAPI mock services (`<name>-api/`) + a shared admin/drift/audit
plane. Each runs in its own container; agents reach them via injected `*_API_URL` env vars.

## PER-API LAYOUT (`<name>-api/`)
```
server.py        # FastAPI app: mirrors a real API subset; installs tracker + admin plane
<name>_data.py   # in-memory data layer (the `_store`); CSV/JSON seed files alongside
service.toml     # [service] name/port/env_var_name/healthcheck_path + [k8s] limits
Dockerfile  requirements.txt  *.csv/*.json  *_postman_collection.json
```
`server.py` boilerplate (keep this shape):
```python
import <name>_data
try:
    from tracking_middleware import install_tracker
    from admin_plane import install_admin_plane
except ModuleNotFoundError:           # standalone run: no-op fallbacks
    ...
app = FastAPI(...); install_tracker(app); install_admin_plane(app, store=<name>_data._store)
@app.get("/health") ...
```

## SHARED PLANE (repo-root of environment/)
| File | Role |
|------|------|
| `tracking_middleware.py` | captures all req/resp → `GET /audit/requests`, `/audit/summary` (skips `/audit`,`/admin`) |
| `admin_plane.py` | `/admin/*` out-of-band mutation surface; **off unless `MOCK_ADMIN_ENABLED=1`** + IP allowlist |
| `_mutable_store.py` | mutable store backing drift |
| `test_all_apis.py` | cross-fleet smoke harness |
| `skills/` | 101 `<api>-connector/` skill dirs + media skills (audio/pdf/video) injected into tasks |

## CONVENTIONS
- Each service owns a **unique port** + `env_var_name` (e.g. github-api → 8019 / `GITHUB_API_URL`)
  declared in `service.toml`. Don't collide ports across services.
- Port 8069 is intentionally unassigned — historical artifact from an API renumbering. Do not reuse.
- Data lives in `<name>_data.py` module-global `_store`; servers are thin route wrappers.
- Drift = admin plane mutates `_store` mid-run so responses diverge from persona MEMORY.md;
  drift events are hidden from the agent's `/audit` view by design.

## ANTI-PATTERNS
- Don't enable `/admin/*` in normal runs — default-absent keeps behavior byte-identical to
  plain mocks; only DriftDirector (host) flips `MOCK_ADMIN_ENABLED=1`.
- Don't let `/admin/*` or `/audit/*` show up in agent-visible audit logs (skip-lists already set).
- `skills/` comments still say "Kensei2" — that's vendored heritage, not a new dependency.
  Same for "Kensei3" references; don't "fix" them.

## STORE INVARIANTS (`_mutable_store.py`)
- `:235` — sibling `.csv` overlay ALWAYS wins over baked `.json` for the same key.
- `:891` — file blobs read from `<api_dir>/file_blobs/<basename>`; these MUST NEVER touch the
  agent's `/root/workspace/` — read-only bind mount only.
- The per-task `:ro` file mounts under `/opt/mocks/<api>/` (set up by
  `src/utils/mock_stack.py::start_mock_stack(overlays=...)`) are the runtime view this directory
  serves. The host-side equivalent — `environment/<api>/` baseline merged with
  `input/<task>/mock_data/<api>/` overlays — is snapshotted into
  `output/<backend>/<task>/data/environment/<api>/` by `src/utils/env_overlay_snapshot.py` so
  bundles + downstream tooling can inspect EXACTLY what each mock served. If you change baseline
  layout or filename conventions here, audit `env_overlay_snapshot.py` and the bundler in lockstep.

## IMAGE BUILD
- Mock image is `kensei3-mocks:v1`; content-hash labeled over `environment/*`.
- After editing any `<name>_data.py` or shared-plane file: `KENSEI_MOCK_REBUILD=1 <cmd>`.
- All per-API Dockerfiles are `python:3.12-slim` SHA-pinned, use hash-verified
  `pip install --require-hashes -r requirements-locked.txt`, run as non-root `app` user.

## DOCKERFILE PINNING POLICY
- Each `<name>-api/requirements-locked.txt` is hash-pinned. NEVER regenerate without re-running
  `pip-compile --generate-hashes` and committing both `.in` and `.txt` together.
