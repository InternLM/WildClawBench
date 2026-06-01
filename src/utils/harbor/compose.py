"""Harbor docker-compose.yaml generator.

Walks `<env_dir>/<svc>/service.toml` and emits a compose file with a `main`
service (sleep infinity, depends_on each svc service_healthy) plus one entry
per mock service (build context, expose, healthcheck via python3 urllib).

Port of `_generate_harbor_docker_compose` from kensei2.py (line 3035).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List, Mapping, Optional

try:
    import tomllib  # py3.11+
except ImportError:  # pragma: no cover
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:  # pragma: no cover
        tomllib = None  # type: ignore


def _parse_service_toml_fallback(path: Path) -> dict:
    """Minimal TOML parser when tomllib unavailable."""
    data = {
        "name": path.parent.name,
        "port": 8000,
        "env_var_name": "",
        "healthcheck_path": "/health",
        "k8s_image": "",
        "cpu_request": "25m",
        "memory_request": "128Mi",
        "memory_limit": "256Mi",
    }
    if not path.exists():
        return data
    section: Optional[str] = None
    try:
        text = path.read_text()
    except Exception:
        return data
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if section == "service":
            if k == "name":
                data["name"] = v
            elif k == "port":
                try:
                    data["port"] = int(v)
                except ValueError:
                    pass
            elif k == "env_var_name":
                data["env_var_name"] = v
            elif k == "healthcheck_path":
                data["healthcheck_path"] = v
        elif section == "k8s":
            if k == "image":
                data["k8s_image"] = v
            elif k == "cpu_request":
                data["cpu_request"] = v
            elif k == "memory_request":
                data["memory_request"] = v
            elif k == "memory_limit":
                data["memory_limit"] = v
    return data


def _parse_service_toml(path: Path) -> dict:
    if tomllib is None:
        return _parse_service_toml_fallback(path)
    try:
        with open(path, "rb") as f:
            doc = tomllib.load(f)
    except Exception:
        return _parse_service_toml_fallback(path)
    svc = doc.get("service", {}) if isinstance(doc, dict) else {}
    k8s = doc.get("k8s", {}) if isinstance(doc, dict) else {}
    return {
        "name": svc.get("name", path.parent.name),
        "port": int(svc.get("port", 8000) or 8000),
        "env_var_name": svc.get("env_var_name", ""),
        "healthcheck_path": svc.get("healthcheck_path", "/health"),
        "k8s_image": k8s.get("image", ""),
        "cpu_request": k8s.get("cpu_request", "25m"),
        "memory_request": k8s.get("memory_request", "128Mi"),
        "memory_limit": k8s.get("memory_limit", "256Mi"),
    }


def discover_services(env_dir: Path) -> List[dict]:
    """List service metadata for every `<env_dir>/<svc>/service.toml`."""
    services: List[dict] = []
    if not env_dir.is_dir():
        return services
    for entry in sorted(env_dir.iterdir()):
        if not entry.is_dir():
            continue
        toml_path = entry / "service.toml"
        if not toml_path.exists():
            continue
        services.append(_parse_service_toml(toml_path))
    return services


def _healthcheck_cmd(port: int, path: str) -> str:
    return (
        "python3 -c \"import urllib.request,sys; "
        f"sys.exit(0 if urllib.request.urlopen('http://localhost:{port}{path}',timeout=3)"
        ".status<400 else 1)\""
    )


def generate_harbor_compose(env_dir: Path,
                            services: Optional[Iterable[Mapping]] = None) -> str:
    """Render the Harbor `data/environment/docker-compose.yaml`.

    The `main` service waits for every mock service to become healthy.
    """
    if services is None:
        services = discover_services(env_dir)
    svc_list = list(services)

    lines: List[str] = ["services:"]

    lines.append("  main:")
    lines.append("    build:")
    lines.append("      context: .")
    lines.append("    image: harbor-main:local")
    lines.append("    command: [\"sleep\", \"infinity\"]")
    if svc_list:
        lines.append("    depends_on:")
        for svc in svc_list:
            lines.append(f"      {svc['name']}:")
            lines.append("        condition: service_healthy")

    for svc in svc_list:
        name = svc["name"]
        port = int(svc["port"])
        hc_path = svc.get("healthcheck_path") or "/health"
        mem_limit = svc.get("memory_limit") or ""
        lines.append(f"  {name}:")
        lines.append("    build:")
        lines.append(f"      context: ./{name}")
        lines.append(f"    image: harbor-{name}:local")
        lines.append("    expose:")
        lines.append(f"      - \"{port}\"")
        lines.append("    healthcheck:")
        # Block-list form: keeps the cmd's embedded `"` out of YAML flow-sequence quoting.
        lines.append("      test:")
        lines.append("        - CMD")
        lines.append("        - sh")
        lines.append("        - -c")
        lines.append(f"        - {_healthcheck_cmd(port, hc_path)}")
        lines.append("      interval: 5s")
        lines.append("      timeout: 5s")
        lines.append("      retries: 12")
        if mem_limit:
            lines.append("    deploy:")
            lines.append("      resources:")
            lines.append("        limits:")
            lines.append(f"          memory: {mem_limit}")

    return "\n".join(lines) + "\n"
