#!/usr/bin/env python3
"""End-to-end test runner for every kensei2 mock API environment.

For each environment that has both a `service.toml` and a `server.py`, this
script:
  1. boots the FastAPI server (via uvicorn) on its configured port,
  2. waits for the health endpoint,
  3. fires every request defined in that env's Postman collection
     (`*_postman_collection.json`), substituting the base-URL variable to point
     at the locally-running server,
  4. records the HTTP status + response body,
  5. shuts the server down.

It then writes two artifacts (next to this script by default):
  - `api_test_report.md`      human-readable pass/fail document
  - `api_test_responses.json` full machine-readable responses

Result classes per endpoint:
  PASS  -> 2xx/3xx response
  WARN  -> 4xx (client error: an intentional error-path test, or an
           unresolved/runtime variable such as a created-resource id)
  FAIL  -> 5xx, connection error, or the server failed to start
  SKIP  -> request references an unresolved {{variable}} so it was not sent

Usage:
  python3 test_all_apis.py                      # test every environment
  python3 test_all_apis.py --only stripe-api,github-api
  python3 test_all_apis.py --skip kubernetes-api
  python3 test_all_apis.py --dry-run            # plan only: parse collections,
                                                # no servers booted, no requests
  python3 test_all_apis.py --install-deps       # pip install fastapi/uvicorn
                                                # into the current interpreter
                                                # if they are missing, then run

Requires: fastapi + uvicorn installed in the interpreter that runs this script
(the server side). The client side uses only the standard library.
"""

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENV_ROOT = Path(__file__).resolve().parent           # .../kensei2/environment
SKIP_DIRS = {"skills", "__pycache__"}
HEALTH_TIMEOUT_S = 25
REQUEST_TIMEOUT_S = 15
MD_BODY_TRUNC = 600         # chars of response shown inline in markdown
JSON_BODY_TRUNC = 20000     # chars of response stored in the JSON dump
VAR_RE = re.compile(r"\{\{\s*([^}]+?)\s*\}\}")


# ---------------------------------------------------------------------------
# Discovery + parsing
# ---------------------------------------------------------------------------

def parse_service_toml(path):
    """Minimal service.toml reader (tomllib isn't on Python < 3.11)."""
    name = port = health = None
    in_service = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("[") and line.endswith("]"):
            in_service = (line == "[service]")
            continue
        if not in_service or "=" not in line or line.startswith("#"):
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key == "name":
            name = val
        elif key == "port":
            try:
                port = int(val)
            except ValueError:
                pass
        elif key == "healthcheck_path":
            health = val
    return name, port, (health or "/health")


def discover_envs():
    """Return [{name, dir, port, health, collection}] for runnable envs."""
    envs = []
    for entry in sorted(ENV_ROOT.iterdir()):
        if not entry.is_dir() or entry.name in SKIP_DIRS:
            continue
        toml = entry / "service.toml"
        server = entry / "server.py"
        if not toml.is_file() or not server.is_file():
            continue  # skip dirs without a runnable server
        name, port, health = parse_service_toml(toml)
        collections = sorted(entry.glob("*postman_collection.json"))
        envs.append({
            "name": name or entry.name,
            "dir": entry,
            "port": port,
            "health": health,
            "collection": collections[0] if collections else None,
        })
    return envs


def _iter_items(items):
    """Yield leaf request items, recursing through Postman folders."""
    for it in items or []:
        if "item" in it:
            yield from _iter_items(it["item"])
        elif "request" in it:
            yield it


def load_endpoints(collection_path, port):
    """Parse a Postman collection into a list of resolvable requests.

    Returns (endpoints, skipped) where each endpoint is a dict with name,
    method, url, headers, body, and `skipped` requests carry the unresolved
    variable name.
    """
    data = json.loads(collection_path.read_text(encoding="utf-8"))

    # Build the variable map; force every localhost/base-url style var to the
    # port the server actually binds to, so collection/port drift can't matter.
    variables = {}
    for v in data.get("variable", []) or []:
        variables[v.get("key")] = v.get("value", "")
    local_base = "http://127.0.0.1:%d" % port
    for k, val in list(variables.items()):
        if isinstance(val, str) and "localhost" in val.lower():
            variables[k] = local_base
    # Common base-url variable names, in case the collection didn't declare one.
    variables.setdefault("baseUrl", local_base)
    variables.setdefault("base_url", local_base)

    def substitute(text):
        if text is None:
            return None, None
        def repl(m):
            key = m.group(1)
            return str(variables.get(key, m.group(0)))
        out = VAR_RE.sub(repl, text)
        leftover = VAR_RE.search(out)
        return out, (leftover.group(1) if leftover else None)

    endpoints, skipped = [], []
    for it in _iter_items(data.get("item", [])):
        req = it["request"]
        method = (req.get("method") or "GET").upper()
        url_raw = req.get("url")
        if isinstance(url_raw, dict):
            url_raw = url_raw.get("raw", "")
        headers = {h.get("key"): h.get("value")
                   for h in (req.get("header") or []) if h.get("key")}
        body = None
        b = req.get("body")
        if isinstance(b, dict) and b.get("mode") == "raw":
            body = b.get("raw")

        url, url_missing = substitute(url_raw)
        body_out, body_missing = substitute(body)
        missing = url_missing or body_missing
        record = {
            "name": it.get("name", ""),
            "method": method,
            "url": url,
            "path": _path_only(url),
            "headers": headers,
            "body": body_out,
        }
        if missing:
            record["missing_var"] = missing
            skipped.append(record)
        else:
            endpoints.append(record)
    return endpoints, skipped


def _path_only(url):
    if not url:
        return ""
    return re.sub(r"^https?://[^/]+", "", url)


# ---------------------------------------------------------------------------
# HTTP + server lifecycle
# ---------------------------------------------------------------------------

# Structural characters to preserve when percent-encoding a URL. Everything
# else outside the unreserved set (notably spaces) gets encoded, mirroring what
# a browser/Postman does before sending a human-readable URL.
_PATH_SAFE = "/%:@-._~!$&'()*+,;="
_QUERY_SAFE = "=&|,/:@+*'\"().;?%$!-._~"


def encode_url(url):
    """Percent-encode an otherwise human-readable URL so urllib will send it.

    Existing %XX escapes are preserved (because '%' is in the safe sets), so
    pre-encoded URLs (e.g. jql=...%3D...) are not double-encoded.
    """
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parts.path, safe=_PATH_SAFE)
    query = urllib.parse.quote(parts.query, safe=_QUERY_SAFE)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


def http_request(method, url, headers, body, timeout=REQUEST_TIMEOUT_S):
    url = encode_url(url)
    data = body.encode("utf-8") if body else None
    hdrs = dict(headers or {})
    if data and not any(k.lower() == "content-type" for k in hdrs):
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            payload = e.read().decode("utf-8", "replace")
        except Exception:
            payload = ""
        return e.code, payload
    except Exception as e:  # connection refused, timeout, etc.
        return None, "<request error: %s>" % e


def wait_for_health(port, health_path, proc, timeout=HEALTH_TIMEOUT_S):
    url = "http://127.0.0.1:%d%s" % (port, health_path)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            return False  # server process died
        status, _ = http_request("GET", url, {}, None, timeout=2)
        if status and 200 <= status < 300:
            return True
        time.sleep(0.4)
    return False


def start_server(env):
    log_path = env["dir"] / ".test_server.log"
    log = open(log_path, "w", encoding="utf-8")
    sub_env = os.environ.copy()
    sub_env["PYTHONPATH"] = str(ENV_ROOT) + os.pathsep + sub_env.get("PYTHONPATH", "")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app",
         "--host", "127.0.0.1", "--port", str(env["port"]),
         "--app-dir", str(env["dir"]), "--log-level", "warning"],
        stdout=log, stderr=subprocess.STDOUT, env=sub_env,
    )
    return proc, log, log_path


def stop_server(proc, log):
    try:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    finally:
        try:
            log.close()
        except Exception:
            pass


def classify(status):
    if status is None:
        return "FAIL"
    if 200 <= status < 400:
        return "PASS"
    if 400 <= status < 500:
        return "WARN"
    return "FAIL"


# ---------------------------------------------------------------------------
# Per-environment run
# ---------------------------------------------------------------------------

def run_env(env):
    result = {
        "name": env["name"], "port": env["port"], "dir": str(env["dir"]),
        "server": "not-started", "server_log": "",
        "endpoints": [], "counts": {"PASS": 0, "WARN": 0, "FAIL": 0, "SKIP": 0},
    }
    if not env["collection"]:
        result["server"] = "no-collection"
        return result

    endpoints, skipped = load_endpoints(env["collection"], env["port"])
    for sk in skipped:
        result["endpoints"].append({
            "name": sk["name"], "method": sk["method"], "path": sk["path"],
            "status": None, "result": "SKIP",
            "note": "unresolved variable {{%s}}" % sk.get("missing_var"),
            "response": "",
        })
        result["counts"]["SKIP"] += 1

    proc, log, log_path = start_server(env)
    healthy = wait_for_health(env["port"], env["health"], proc)
    if not healthy:
        stop_server(proc, log)
        tail = ""
        try:
            tail = log_path.read_text(encoding="utf-8")[-1500:]
        except Exception:
            pass
        result["server"] = "failed-to-start"
        result["server_log"] = tail
        # Mark every (would-be) endpoint as FAIL so the failure is visible.
        for ep in endpoints:
            result["endpoints"].append({
                "name": ep["name"], "method": ep["method"], "path": ep["path"],
                "status": None, "result": "FAIL",
                "note": "server did not become healthy", "response": "",
            })
            result["counts"]["FAIL"] += 1
        _cleanup_log(log_path)
        return result

    result["server"] = "started"
    try:
        for ep in endpoints:
            status, body = http_request(ep["method"], ep["url"], ep["headers"], ep["body"])
            res = classify(status)
            result["counts"][res] += 1
            result["endpoints"].append({
                "name": ep["name"], "method": ep["method"], "path": ep["path"],
                "status": status, "result": res, "note": "",
                "response": body[:JSON_BODY_TRUNC] if body else "",
            })
    finally:
        stop_server(proc, log)
        _cleanup_log(log_path)
    return result


def _cleanup_log(log_path):
    try:
        log_path.unlink()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _fmt_response_md(text):
    if not text:
        return "_(empty)_"
    snippet = text[:MD_BODY_TRUNC]
    # Pretty-print JSON when possible for readability.
    try:
        snippet = json.dumps(json.loads(text), indent=2)[:MD_BODY_TRUNC]
    except Exception:
        pass
    suffix = "\n... (truncated)" if len(text) > MD_BODY_TRUNC else ""
    return "```\n%s%s\n```" % (snippet, suffix)


def write_markdown(results, path, started_at):
    totals = {"PASS": 0, "WARN": 0, "FAIL": 0, "SKIP": 0}
    n_endpoints = 0
    for r in results:
        for k in totals:
            totals[k] += r["counts"][k]
        n_endpoints += sum(r["counts"].values())

    lines = []
    lines.append("# kensei2 Mock API Test Report")
    lines.append("")
    lines.append("- Generated: %s" % started_at)
    lines.append("- Python: %s" % sys.version.split()[0])
    lines.append("- Environments tested: %d" % len(results))
    lines.append("- Endpoints exercised: %d" % n_endpoints)
    lines.append("- Totals: PASS %d | WARN(4xx) %d | FAIL %d | SKIP %d"
                 % (totals["PASS"], totals["WARN"], totals["FAIL"], totals["SKIP"]))
    lines.append("")
    lines.append("Result legend: PASS = 2xx/3xx, WARN = 4xx (error-path or "
                 "runtime-dependent id), FAIL = 5xx / connection error / server "
                 "down, SKIP = unresolved `{{variable}}` (not sent).")
    lines.append("")

    # Summary table
    lines.append("## Summary by environment")
    lines.append("")
    lines.append("| Environment | Port | Server | Endpoints | PASS | WARN | FAIL | SKIP |")
    lines.append("|-------------|------|--------|-----------|------|------|------|------|")
    for r in sorted(results, key=lambda x: x["name"]):
        total = sum(r["counts"].values())
        lines.append("| %s | %s | %s | %d | %d | %d | %d | %d |" % (
            r["name"], r["port"], r["server"], total,
            r["counts"]["PASS"], r["counts"]["WARN"],
            r["counts"]["FAIL"], r["counts"]["SKIP"]))
    lines.append("")

    # Envs with problems, called out up top
    problem = [r for r in results if r["counts"]["FAIL"] or r["server"] != "started"]
    if problem:
        lines.append("## Environments needing attention")
        lines.append("")
        for r in sorted(problem, key=lambda x: x["name"]):
            lines.append("- **%s** (port %s): server=%s, FAIL=%d"
                         % (r["name"], r["port"], r["server"], r["counts"]["FAIL"]))
            if r["server_log"]:
                lines.append("  <details><summary>server log tail</summary>\n\n```\n%s\n```\n</details>"
                             % r["server_log"][-1200:])
        lines.append("")

    # Detailed per-env sections
    lines.append("## Details")
    lines.append("")
    for r in sorted(results, key=lambda x: x["name"]):
        lines.append("### %s (port %s) — server: %s" % (r["name"], r["port"], r["server"]))
        lines.append("")
        if not r["endpoints"]:
            lines.append("_No endpoints found in collection._")
            lines.append("")
            continue
        lines.append("| Result | Method | Path | Status | Endpoint |")
        lines.append("|--------|--------|------|--------|----------|")
        for ep in r["endpoints"]:
            st = ep["status"] if ep["status"] is not None else "-"
            note = (" — %s" % ep["note"]) if ep.get("note") else ""
            lines.append("| %s | %s | %s | %s | %s%s |" % (
                ep["result"], ep["method"], ep["path"], st, ep["name"], note))
        lines.append("")
        # Responses
        lines.append("<details><summary>responses</summary>")
        lines.append("")
        for ep in r["endpoints"]:
            if ep["result"] == "SKIP":
                continue
            lines.append("**%s %s** — `%s` (status %s)"
                         % (ep["method"], ep["name"], ep["path"],
                            ep["status"] if ep["status"] is not None else "-"))
            lines.append("")
            lines.append(_fmt_response_md(ep["response"]))
            lines.append("")
        lines.append("</details>")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(results, path, started_at):
    payload = {
        "generated": started_at,
        "python": sys.version.split()[0],
        "environments": results,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def ensure_deps(install):
    have = importlib.util.find_spec("uvicorn") and importlib.util.find_spec("fastapi")
    if have:
        return True
    if not install:
        print("ERROR: fastapi + uvicorn are required to boot the mock servers "
              "but are not installed in this interpreter (%s)." % sys.executable)
        print("Fix it with either:")
        print("  python3 test_all_apis.py --install-deps")
        print("  or: pip install fastapi==0.115.5 uvicorn==0.32.1")
        return False
    print("Installing fastapi + uvicorn into %s ..." % sys.executable)
    rc = subprocess.call([sys.executable, "-m", "pip", "install",
                          "fastapi==0.115.5", "uvicorn==0.32.1"])
    if rc != 0:
        print("ERROR: dependency install failed (pip exit %d)." % rc)
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description="Test every kensei2 mock API environment.")
    ap.add_argument("--only", help="comma-separated env names to test (default: all)")
    ap.add_argument("--skip", help="comma-separated env names to exclude")
    ap.add_argument("--dry-run", action="store_true",
                    help="parse collections and print a plan; do not boot servers")
    ap.add_argument("--install-deps", action="store_true",
                    help="pip install fastapi/uvicorn if missing, then run")
    ap.add_argument("--report", default=str(ENV_ROOT / "api_test_report.md"),
                    help="output markdown report path")
    ap.add_argument("--responses", default=str(ENV_ROOT / "api_test_responses.json"),
                    help="output JSON responses path")
    args = ap.parse_args()

    envs = discover_envs()
    if args.only:
        wanted = {s.strip() for s in args.only.split(",") if s.strip()}
        envs = [e for e in envs if e["name"] in wanted]
    if args.skip:
        unwanted = {s.strip() for s in args.skip.split(",") if s.strip()}
        envs = [e for e in envs if e["name"] not in unwanted]

    if not envs:
        print("No runnable environments matched.")
        return 1

    print("Discovered %d environment(s) with a server + service.toml." % len(envs))

    if args.dry_run:
        print("\n--dry-run: parsing collections (no servers booted)\n")
        grand_ep = grand_skip = 0
        for e in sorted(envs, key=lambda x: x["name"]):
            if not e["collection"]:
                print("  %-22s port %-5s  NO COLLECTION" % (e["name"], e["port"]))
                continue
            eps, sk = load_endpoints(e["collection"], e["port"])
            grand_ep += len(eps)
            grand_skip += len(sk)
            extra = ("  (skip %d unresolved-var)" % len(sk)) if sk else ""
            print("  %-22s port %-5s  %2d requests%s" % (e["name"], e["port"], len(eps), extra))
        print("\nPlan: %d requests would be sent across %d envs; %d skipped "
              "(unresolved vars)." % (grand_ep, len(envs), grand_skip))
        return 0

    if not ensure_deps(args.install_deps):
        return 2

    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    results = []
    for i, e in enumerate(sorted(envs, key=lambda x: x["name"]), 1):
        print("[%2d/%2d] %-22s port %s ..." % (i, len(envs), e["name"], e["port"]),
              end=" ", flush=True)
        r = run_env(e)
        results.append(r)
        c = r["counts"]
        print("server=%s  PASS %d / WARN %d / FAIL %d / SKIP %d"
              % (r["server"], c["PASS"], c["WARN"], c["FAIL"], c["SKIP"]))

    report_path = Path(args.report)
    responses_path = Path(args.responses)
    write_markdown(results, report_path, started_at)
    write_json(results, responses_path, started_at)

    totals = {"PASS": 0, "WARN": 0, "FAIL": 0, "SKIP": 0}
    for r in results:
        for k in totals:
            totals[k] += r["counts"][k]
    print("\n=== Totals: PASS %d | WARN %d | FAIL %d | SKIP %d ===" % (
        totals["PASS"], totals["WARN"], totals["FAIL"], totals["SKIP"]))
    print("Markdown report : %s" % report_path)
    print("JSON responses  : %s" % responses_path)
    return 1 if totals["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
