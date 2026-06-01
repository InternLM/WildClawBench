from __future__ import annotations

from collections import Counter

from ._helpers import discover_api_dirs, read_service_toml


def test_ports_are_unique():
    by_port: dict[int, list[str]] = {}
    for api_dir in discover_api_dirs():
        cfg = read_service_toml(api_dir)
        port = int(cfg["port"])
        by_port.setdefault(port, []).append(cfg["name"])
    collisions = {p: names for p, names in by_port.items() if len(names) > 1}
    assert not collisions, f"Port collisions: {collisions}"


def test_names_are_unique():
    names = [read_service_toml(d)["name"] for d in discover_api_dirs()]
    counts = Counter(names)
    dupes = {n: c for n, c in counts.items() if c > 1}
    assert not dupes, f"Duplicate service names: {dupes}"


def test_env_var_names_are_unique():
    by_env: dict[str, list[str]] = {}
    for api_dir in discover_api_dirs():
        cfg = read_service_toml(api_dir)
        ev = cfg.get("env_var_name")
        if not ev:
            continue
        by_env.setdefault(str(ev), []).append(cfg["name"])
    collisions = {k: v for k, v in by_env.items() if len(v) > 1}
    assert not collisions, f"env_var_name collisions: {collisions}"


def test_directory_name_matches_service_name():
    mismatches: list[tuple[str, str]] = []
    for api_dir in discover_api_dirs():
        cfg = read_service_toml(api_dir)
        if cfg["name"] != api_dir.name:
            mismatches.append((api_dir.name, str(cfg["name"])))
    assert not mismatches, f"Dir/name mismatches: {mismatches}"
