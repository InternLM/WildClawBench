#!/usr/bin/env python3
"""Backfill richer references/ + scripts/ for the "thin" mock-API connectors.

CONTEXT
-------
environment/skills/<name>-api-connector/ ships one of two shapes:
  * RICH  (10 dirs): hand-authored references/<name>-api-guide.md + scripts/fetch_*.py
          (quickbooks, etsy, ring, ...). These are upstream/curated — NEVER touched.
  * THIN  (91 dirs): SKILL.md only. SKILL.md carries a parseable endpoint table
          (| Method | Path |) plus the env-var name in its frontmatter/body.

This standalone tool reads each THIN connector's SKILL.md endpoint table and the
sibling environment/<name>-api/service.toml, then emits, to match the rich shape:
  references/<name>-api-guide.md   curl example per endpoint, grouped by resource
  scripts/fetch_<name>_data.py     stdlib-only argparse CLI, one flag per endpoint
                                   (GET + POST + DELETE, per the run config)

It is ISOLATED: no pipeline import, no Docker, no network, no LLM. Idempotent by
default (skips a connector that already has references/), so re-runs are safe.

WHY GENERATED (not hand-written): the 91 thin connectors are themselves
auto-generated mock stubs; their SKILL.md endpoint table is the single source of
truth, so a deterministic generator stays in lockstep with the mock surface.

DATA SOURCES PER CONNECTOR
  SKILL.md  ->  title (# heading), env-var ($<ENV>), endpoint rows (method, path)
  ../<name>-api/service.toml  ->  env_var_name, port (for the localhost fallback)

SELECTION
  Default: every *-api-connector that LACKS references/ (the 91 thin ones).
  --only NAME[,NAME...]  restrict to specific connectors (by api name, e.g. gmail).
  --force                regenerate even if references/ already exists (still skips
                         the curated RICH set unless --include-rich is also given).

BUNDLE ENRICH MODE (--bundle-root)
  A bundle produced by repackage_to_bundle.py copies data/environment/skills/
  verbatim from a run-output SNAPSHOT frozen at run time, so tasks run before this
  generator existed carry THIN connector dirs (SKILL.md only) even though the live
  environment/skills tree is now rich. With --bundle-root, this tool switches to an
  in-place enrich pass: it copies references/ + scripts/ from the live
  environment/skills/<name>-api-connector into every connector dir ALREADY present
  in the bundle (never adding a new API, never touching media skills). Use the live
  tree as the source — run the default generate mode first so it is rich.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# Curated, hand-authored connectors — never overwrite unless --include-rich.
RICH_CONNECTORS = {
    "amazon-seller", "etsy", "google-classroom", "instagram", "linear",
    "myfitnesspal", "pinterest", "quickbooks", "ring", "youtube",
}

# --bundle-root enrich mode: the two doc subdirs copied from live -> bundle, and the
# patterns excluded so no build cruft leaks into a published bundle.
ENRICH_SUBDIRS = ("references", "scripts")
COPY_IGNORE = shutil.ignore_patterns("__pycache__", ".DS_Store", "*.pyc")
CONNECTOR_SUFFIX = "-api-connector"

# Endpoint table row: | GET | `/path/{id}` |  (backticks optional, spacing loose).
_ROW_RE = re.compile(r"^\|\s*([A-Z]+)\s*\|\s*`?([^`|]+?)`?\s*\|\s*$")
# Frontmatter / body env-var token like `GMAIL_API_URL`.
_ENV_RE = re.compile(r"`([A-Z][A-Z0-9_]*_API_URL)`")
# A path placeholder: {message_id}, {id}, ...
_PARAM_RE = re.compile(r"\{([^}]+)\}")


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def parse_service_toml(svc_path: Path) -> dict[str, str]:
    """Minimal [service] reader (stdlib-only; avoids tomllib for py<3.11 parity)."""
    out: dict[str, str] = {}
    for line in _read(svc_path).splitlines():
        line = line.strip()
        m = re.match(r'^(\w+)\s*=\s*"?([^"]*)"?\s*$', line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def parse_skill(skill_md: Path) -> dict:
    """Extract title, env var, and (method, path) endpoint rows from a SKILL.md."""
    text = _read(skill_md)
    title = ""
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    env_m = _ENV_RE.search(text)
    env_var = env_m.group(1) if env_m else ""
    endpoints: list[tuple[str, str]] = []
    for line in text.splitlines():
        m = _ROW_RE.match(line)
        if not m:
            continue
        method, path = m.group(1).strip(), m.group(2).strip()
        # Skip the header/separator rows ("Method"/"---") that also match loosely.
        if method.lower() == "method" or set(path) <= {"-", " "}:
            continue
        if not path.startswith("/"):
            continue
        endpoints.append((method, path))
    return {"title": title, "env_var": env_var, "endpoints": endpoints}


def _resource_of(path: str) -> str:
    """First non-versioned, non-param path segment — used to group endpoints."""
    for seg in path.strip("/").split("/"):
        if not seg:
            continue
        if _PARAM_RE.search(seg):
            continue
        # Skip pure version segments like v1, v3, gmail (api-prefix) is kept though.
        if re.fullmatch(r"v\d+", seg):
            continue
        return seg
    return "root"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _flag_for(method: str, path: str, seen: set[str]) -> str:
    """Stable, unique CLI flag name derived from method+path."""
    params = _PARAM_RE.findall(path)
    segs = [s for s in path.strip("/").split("/") if s and not _PARAM_RE.search(s)
            and not re.fullmatch(r"v\d+", s)]
    base = _slug("_".join(segs)) or "root"
    verb = {"GET": "get", "POST": "post", "DELETE": "delete"}.get(method, method.lower())
    name = f"{verb}_{base}"
    if params:
        name += "_" + "_".join(_slug(p) for p in params)
    candidate = name
    n = 2
    while candidate in seen:
        candidate = f"{name}_{n}"
        n += 1
    seen.add(candidate)
    return candidate


def build_reference(info: dict, env_var: str) -> str:
    title = info["title"] or "Mock API"
    lines = [f"# {title} Guide", ""]
    lines.append(
        f"Worked `curl` examples for every endpoint. **All requests target the base "
        f"URL in `${env_var}`.** Auth headers are mocked (any token is accepted) and "
        f"responses are deterministic fixtures."
    )
    lines += ["", "## Base URL", "",
              "| Variable | Purpose |", "|----------|---------|",
              f"| `{env_var}` | Base URL for all requests |", ""]

    # Group endpoints by resource for readable sections.
    groups: dict[str, list[tuple[str, str]]] = {}
    for method, path in info["endpoints"]:
        groups.setdefault(_resource_of(path), []).append((method, path))

    for resource in sorted(groups):
        lines.append(f"## {resource.replace('-', ' ').title()}")
        lines.append("")
        lines.append("```bash")
        for method, path in groups[resource]:
            example_path = _PARAM_RE.sub(lambda m: f"<{m.group(1)}>", path)
            if method == "GET":
                lines.append(f'curl -s "${env_var}{example_path}"')
            elif method == "DELETE":
                lines.append(f'curl -s -X DELETE "${env_var}{example_path}"')
            else:  # POST / PUT / PATCH
                lines.append(
                    f'curl -s -X {method} "${env_var}{example_path}" '
                    f"-H 'Content-Type: application/json' -d '{{}}'"
                )
        lines.append("```")
        lines.append("")

    lines.append(
        f"The audit log of every call is available at `${env_var}/audit/requests` "
        f"(used for grading)."
    )
    lines.append("")
    return "\n".join(lines)


def build_script(info: dict, api_name: str, env_var: str, port: str) -> str:
    fallback = f"http://localhost:{port}" if port else "http://localhost:8000"
    seen: set[str] = set()
    arg_lines: list[str] = []
    dispatch: list[str] = []

    for method, path in info["endpoints"]:
        params = _PARAM_RE.findall(path)
        flag = _flag_for(method, path, seen)
        dest = flag  # argparse turns dashes into underscores; we already use _.
        help_txt = f"{method} {path}"
        if method == "GET" and not params:
            arg_lines.append(
                f'    p.add_argument("--{flag.replace("_", "-")}", action="store_true", '
                f'help="{help_txt}")'
            )
            dispatch.append(
                f"    if args.{dest}:\n"
                f'        return show(api_get(base, "{path}"))'
            )
        elif method == "GET":
            metavar = "/".join(pp.upper() for pp in params)
            arg_lines.append(
                f'    p.add_argument("--{flag.replace("_", "-")}", metavar="{metavar}", '
                f'nargs={len(params)}, help="{help_txt}")'
            )
            dispatch.append(
                f"    if args.{dest}:\n"
                f"        return show(api_get(base, _fill({path!r}, args.{dest})))"
            )
        else:  # POST / DELETE / PUT / PATCH
            if params:
                metavar = "/".join(pp.upper() for pp in params)
                arg_lines.append(
                    f'    p.add_argument("--{flag.replace("_", "-")}", metavar="{metavar}", '
                    f'nargs={len(params)}, help="{help_txt}")'
                )
                guard = f"args.{dest}"
                fill = f"_fill({path!r}, args.{dest})"
            else:
                arg_lines.append(
                    f'    p.add_argument("--{flag.replace("_", "-")}", action="store_true", '
                    f'help="{help_txt}")'
                )
                guard = f"args.{dest}"
                fill = f"{path!r}"
            if method == "DELETE":
                dispatch.append(
                    f"    if {guard}:\n"
                    f"        return show(api_delete(base, {fill}))"
                )
            else:
                dispatch.append(
                    f"    if {guard}:\n"
                    f"        return show(api_send(base, {fill}, {method!r}, _body(args)))"
                )

    args_block = "\n".join(arg_lines)
    dispatch_block = "\n".join(dispatch)

    return f'''#!/usr/bin/env python3
"""CLI helper for the {info["title"] or api_name} mock API.

Generated read/write helper: one flag per endpoint. Base URL comes from
${env_var} (override with --url). POST/PUT/PATCH bodies are read from --data
(JSON string) or --data-file; DELETE/GET take only path params.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def _fill(path, values):
    """Substitute {{placeholders}} in path order with the provided positional values."""
    import re as _re
    it = iter(values or [])
    return _re.sub(r"\\{{[^}}]+\\}}", lambda _m: urllib.parse.quote(str(next(it, "")), safe=""), path)


def _request(base, path, method, body=None):
    url = base.rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {{"Content-Type": "application/json"}} if data is not None else {{}}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        raw = resp.read().decode()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def api_get(base, path):
    return _request(base, path, "GET")


def api_delete(base, path):
    return _request(base, path, "DELETE")


def api_send(base, path, method, body):
    return _request(base, path, method, body if body is not None else {{}})


def _body(args):
    if getattr(args, "data_file", None):
        with open(args.data_file, "r", encoding="utf-8") as fh:
            return json.load(fh)
    if getattr(args, "data", None):
        return json.loads(args.data)
    return {{}}


def show(data):
    print(json.dumps(data, indent=2, ensure_ascii=False) if not isinstance(data, str) else data)
    return 0


def main():
    p = argparse.ArgumentParser(description="Query the {info["title"] or api_name} mock API")
{args_block}
    p.add_argument("--data", metavar="JSON", help="Request body as a JSON string (POST/PUT/PATCH)")
    p.add_argument("--data-file", metavar="PATH", help="Request body from a JSON file (POST/PUT/PATCH)")
    p.add_argument("--url", default=os.environ.get("{env_var}", "{fallback}"),
                   help="API base URL (default: ${env_var} or {fallback})")
    args = p.parse_args()
    base = args.url.rstrip("/")

    try:
        return _dispatch(args, base)
    except urllib.error.HTTPError as e:
        print(f"HTTP {{e.code}}: {{e.read().decode()}}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"Connection error: {{e.reason}}", file=sys.stderr)
        return 1


def _dispatch(args, base):
{dispatch_block}
    print("No endpoint flag provided. Use -h to list available endpoints.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def process_connector(
    skill_dir: Path, env_root: Path, force: bool, verbose: bool
) -> str:
    api_name = skill_dir.name[: -len("-api-connector")]
    references = skill_dir / "references"
    scripts = skill_dir / "scripts"

    if references.exists() and not force:
        return "skip-exists"

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return "skip-no-skill"

    info = parse_skill(skill_md)
    if not info["endpoints"]:
        return "skip-no-endpoints"

    svc = parse_service_toml(env_root / f"{api_name}-api" / "service.toml")
    env_var = svc.get("env_var_name") or info["env_var"] or f"{api_name.upper().replace('-', '_')}_API_URL"
    port = svc.get("port", "")

    references.mkdir(parents=True, exist_ok=True)
    scripts.mkdir(parents=True, exist_ok=True)
    (references / f"{api_name}-api-guide.md").write_text(
        build_reference(info, env_var), encoding="utf-8"
    )
    script_path = scripts / f"fetch_{_slug(api_name)}_data.py"
    script_path.write_text(build_script(info, api_name, env_var, port), encoding="utf-8")
    script_path.chmod(0o755)

    if verbose:
        n = len(info["endpoints"])
        print(f"  + {skill_dir.name}: {n} endpoint(s) -> references/ + scripts/")
    return "written"


def find_bundle_skill_dirs(bundle_root: Path) -> list[Path]:
    return sorted(
        p for p in bundle_root.glob("**/data/environment/skills/*" + CONNECTOR_SUFFIX)
        if p.is_dir()
    )


def enrich_one(bundle_skill_dir: Path, skills_root: Path, force: bool,
               dry_run: bool, verbose: bool) -> str:
    """Copy live references/+scripts/ into one bundle connector dir.

    Returns: copied | skipped-no-live | skipped-empty | skipped-rich.
    The caller's count summary keys off these exact strings.
    """
    name = bundle_skill_dir.name
    live_dir = skills_root / name
    if not live_dir.is_dir():
        if verbose:
            print(f"    ! no live connector for {name}; skipping", file=sys.stderr)
        return "skipped-no-live"

    live_subdirs = [s for s in ENRICH_SUBDIRS if (live_dir / s).is_dir()]
    if not live_subdirs:
        return "skipped-empty"

    # Already rich and not forcing -> leave it (e.g. originally-rich quickbooks).
    if all((bundle_skill_dir / s).is_dir() for s in live_subdirs) and not force:
        return "skipped-rich"

    for sub in live_subdirs:
        dest = bundle_skill_dir / sub
        if dest.exists() and force and not dry_run:
            shutil.rmtree(dest)
        if not dry_run:
            shutil.copytree(live_dir / sub, dest, ignore=COPY_IGNORE, dirs_exist_ok=True)
        if verbose:
            print(f"    {'~ ' if dry_run else '+ '}{name}/{sub}")
    return "copied"


def enrich_bundle(bundle_root: Path, skills_root: Path, force: bool,
                  dry_run: bool, verbose: bool) -> int:
    skill_dirs = find_bundle_skill_dirs(bundle_root)
    print(f"bundle-root : {bundle_root}")
    print(f"skills-root : {skills_root}")
    print(f"found       : {len(skill_dirs)} connector skill dir(s) in bundle")
    if dry_run:
        print("(dry-run: no files written)")

    counts: dict[str, int] = {}
    for sd in skill_dirs:
        status = enrich_one(sd, skills_root, force, dry_run, verbose)
        counts[status] = counts.get(status, 0) + 1

    summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    print(f"done        : {summary or '(nothing matched)'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skills-root", default="environment/skills",
                    help="Dir holding <name>-api-connector/ (default: environment/skills)")
    ap.add_argument("--env-root", default="environment",
                    help="Dir holding <name>-api/service.toml (default: environment)")
    ap.add_argument("--only", default="",
                    help="Comma-separated api names to restrict to (e.g. gmail,outlook).")
    ap.add_argument("--force", action="store_true",
                    help="Regenerate even if references/ already exists.")
    ap.add_argument("--include-rich", action="store_true",
                    help="Also (re)generate the 10 curated connectors (NOT recommended).")
    ap.add_argument("--bundle-root", default="",
                    help="Enrich mode: copy live references/+scripts/ into an already-built "
                         "bundle's connector dirs (sourced from --skills-root) instead of "
                         "generating into the live tree.")
    ap.add_argument("--dry-run", action="store_true", help="List what would be written; write nothing.")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    skills_root = Path(args.skills_root).resolve()
    env_root = Path(args.env_root).resolve()
    if not skills_root.is_dir():
        print(f"error: --skills-root not a directory: {skills_root}", file=sys.stderr)
        return 2

    if args.bundle_root:
        bundle_root = Path(args.bundle_root).resolve()
        if not bundle_root.is_dir():
            print(f"error: --bundle-root not a directory: {bundle_root}", file=sys.stderr)
            return 2
        return enrich_bundle(bundle_root, skills_root, args.force, args.dry_run, args.verbose)

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    connectors = sorted(p for p in skills_root.iterdir()
                        if p.is_dir() and p.name.endswith("-api-connector"))

    counts = {"written": 0, "skip-exists": 0, "skip-rich": 0,
              "skip-no-skill": 0, "skip-no-endpoints": 0, "skip-filter": 0}
    for skill_dir in connectors:
        api_name = skill_dir.name[: -len("-api-connector")]
        if only and api_name not in only:
            counts["skip-filter"] += 1
            continue
        if api_name in RICH_CONNECTORS and not args.include_rich:
            counts["skip-rich"] += 1
            continue
        if args.dry_run:
            md = skill_dir / "SKILL.md"
            info = parse_skill(md) if md.exists() else {"endpoints": []}
            status = "would-write" if info["endpoints"] else "skip-no-endpoints"
            if args.verbose:
                print(f"  ? {skill_dir.name}: {len(info['endpoints'])} endpoint(s) -> {status}")
            key = "written" if status == "would-write" else status
            counts[key] = counts.get(key, 0) + 1
            continue
        status = process_connector(skill_dir, env_root, args.force, args.verbose)
        counts[status] = counts.get(status, 0) + 1

    print(f"skills-root : {skills_root}")
    print(f"connectors  : {len(connectors)} found")
    print(f"written     : {counts.get('written', 0)}")
    print(f"skipped     : rich={counts['skip-rich']} exists={counts['skip-exists']} "
          f"no-endpoints={counts['skip-no-endpoints']} filtered={counts['skip-filter']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
