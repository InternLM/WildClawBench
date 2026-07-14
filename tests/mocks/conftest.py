from __future__ import annotations

from pathlib import Path

import pytest

from ._helpers import (
    ENV_DIR,
    discover_api_dirs,
    harvest_ids,
    list_routes,
    load_app,
    read_service_toml,
)

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

API_DIRS = discover_api_dirs()


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "api_dir" in item.fixturenames:
            api_dir = item.callspec.params.get("api_dir") if hasattr(item, "callspec") else None
            if isinstance(api_dir, Path):
                item.add_marker(pytest.mark.xdist_group(api_dir.name))


@pytest.fixture(scope="session", params=API_DIRS, ids=[p.name for p in API_DIRS])
def api_dir(request) -> Path:
    return request.param


@pytest.fixture(scope="session")
def service_cfg(api_dir: Path) -> dict:
    return read_service_toml(api_dir)


@pytest.fixture(scope="session")
def app(api_dir: Path):
    return load_app(api_dir)


@pytest.fixture(scope="session")
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def routes(app) -> list[tuple[str, str]]:
    return list_routes(app)


@pytest.fixture(scope="session")
def id_pool(api_dir: Path) -> dict[str, list[str]]:
    return harvest_ids(api_dir)


@pytest.fixture(scope="session")
def env_dir() -> Path:
    return ENV_DIR
