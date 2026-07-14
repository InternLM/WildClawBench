"""Data access module for the Kubernetes API mock service."""

import csv
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_str, strict_bool, strict_int)

_store = get_store("kubernetes-api")
_API = "kubernetes-api"


def _store_patch(_table, _row_or_pk, _updates):
    """Persist field updates to a stored row (was: in-place mutation of a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.patch(_pk, _updates)


def _store_delete(_table, _row_or_pk):
    """Persist a row deletion (was: pop/remove on a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.delete(_pk)

_store.register("namespaces", primary_key="name",
                initial_loader=lambda: _coerce_namespaces(_load("namespaces.json", "namespaces")))
_store.register("nodes", primary_key="name",
                initial_loader=lambda: _coerce_nodes(_load("nodes.json", "nodes")))
_store.register("pods", primary_key="name",
                initial_loader=lambda: _coerce_pods(_load("pods.json", "pods")))
_store.register("deployments", primary_key="_pk",
                initial_loader=lambda: _coerce_deployments(_load("deployments.json", "deployments")))
_store.register("services", primary_key="_pk",
                initial_loader=lambda: _coerce_services(_load("services.json", "services")))


def _namespaces_rows():
    return _store.table("namespaces").rows()


def _nodes_rows():
    return _store.table("nodes").rows()


def _pods_rows():
    return _store.table("pods").rows()


def _deployments_rows():
    return _store.table("deployments").rows()


def _services_rows():
    return _store.table("services").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _labels(raw):
    out = {}
    for pair in (raw or "").split(";"):
        pair = pair.strip()
        if not pair or "=" not in pair:
            continue
        k, v = pair.split("=", 1)
        out[k] = v
    return out


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_namespaces(rows):
    return [{**_strip_ctx(r), "labels": _labels(r["labels"])} for r in rows]


def _coerce_nodes(rows):
    return [{**_strip_ctx(r)} for r in rows]


def _coerce_pods(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "restart_count": strict_int(r, "restart_count"),
            "ready": strict_bool(r, "ready"),
            "node": opt_str(r, "node", default="") or None,
            "pod_ip": opt_str(r, "pod_ip", default="") or None,
        })
    return out


def _coerce_deployments(rows):
    out = []
    for r in rows:
        clean = _strip_ctx(r)
        out.append({
            **clean,
            "_pk": f"{clean['namespace']}/{clean['name']}",
            "replicas": strict_int(r, "replicas"),
            "available_replicas": strict_int(r, "available_replicas"),
            "ready_replicas": strict_int(r, "ready_replicas"),
            "updated_replicas": strict_int(r, "updated_replicas"),
        })
    return out


def _coerce_services(rows):
    out = []
    for r in rows:
        clean = _strip_ctx(r)
        out.append({
            **clean,
            "_pk": f"{clean['namespace']}/{clean['name']}",
            "port": strict_int(r, "port"),
            "target_port": strict_int(r, "target_port"),
            "external_ip": opt_str(r, "external_ip", default="") or None,
        })
    return out












# ---------------------------------------------------------------------------
# Serializers (k8s-style object metadata)
# ---------------------------------------------------------------------------

def _ns_obj(ns):
    return {
        "kind": "Namespace",
        "apiVersion": "v1",
        "metadata": {
            "name": ns["name"],
            "labels": ns["labels"],
            "creationTimestamp": ns["created_time"],
        },
        "status": {"phase": ns["status"]},
    }


def _pod_obj(p):
    return {
        "kind": "Pod",
        "apiVersion": "v1",
        "metadata": {
            "name": p["name"],
            "namespace": p["namespace"],
            "creationTimestamp": p["created_time"],
        },
        "spec": {
            "nodeName": p["node"],
            "containers": [{"name": p["container_name"], "image": p["image"]}],
        },
        "status": {
            "phase": p["phase"],
            "podIP": p["pod_ip"],
            "containerStatuses": [{
                "name": p["container_name"],
                "ready": p["ready"],
                "restartCount": p["restart_count"],
                "state": p["status"],
            }],
        },
    }


def _deployment_obj(d):
    return {
        "kind": "Deployment",
        "apiVersion": "apps/v1",
        "metadata": {
            "name": d["name"],
            "namespace": d["namespace"],
            "creationTimestamp": d["created_time"],
        },
        "spec": {
            "replicas": d["replicas"],
            "strategy": {"type": d["strategy"]},
            "template": {
                "spec": {"containers": [{"name": d["name"], "image": d["image"]}]},
            },
        },
        "status": {
            "replicas": d["replicas"],
            "availableReplicas": d["available_replicas"],
            "readyReplicas": d["ready_replicas"],
            "updatedReplicas": d["updated_replicas"],
        },
    }


def _service_obj(s):
    return {
        "kind": "Service",
        "apiVersion": "v1",
        "metadata": {
            "name": s["name"],
            "namespace": s["namespace"],
            "creationTimestamp": s["created_time"],
        },
        "spec": {
            "type": s["type"],
            "clusterIP": s["cluster_ip"],
            "selector": _labels(s["selector"]),
            "ports": [{"port": s["port"], "targetPort": s["target_port"],
                       "protocol": s["protocol"]}],
        },
        "status": {
            "loadBalancer": (
                {"ingress": [{"ip": s["external_ip"]}]} if s["external_ip"] else {}
            ),
        },
    }


def _node_obj(n):
    return {
        "kind": "Node",
        "apiVersion": "v1",
        "metadata": {
            "name": n["name"],
            "labels": {"node-role.kubernetes.io/" + n["role"]: ""},
            "creationTimestamp": n["created_time"],
        },
        "status": {
            "capacity": {"cpu": n["cpu_capacity"], "memory": n["memory_capacity"]},
            "nodeInfo": {
                "kubeletVersion": n["kubelet_version"],
                "osImage": n["os_image"],
            },
            "addresses": [{"type": "InternalIP", "address": n["internal_ip"]}],
            "conditions": [{"type": "Ready",
                            "status": "True" if n["status"] == "Ready" else "False"}],
        },
    }


def _list_envelope(kind, items):
    return {"kind": kind, "apiVersion": "v1", "items": items}


def _ns_exists(ns):
    return any(n["name"] == ns for n in _namespaces_rows())


# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------

def list_namespaces():
    return _list_envelope("NamespaceList", [_ns_obj(n) for n in _namespaces_rows()])


# ---------------------------------------------------------------------------
# Pods
# ---------------------------------------------------------------------------

def list_pods(namespace):
    if not _ns_exists(namespace):
        return {"error": f"namespace {namespace} not found"}
    pods = [_pod_obj(p) for p in _pods_rows() if p["namespace"] == namespace]
    return _list_envelope("PodList", pods)


def get_pod(namespace, name):
    for p in _pods_rows():
        if p["namespace"] == namespace and p["name"] == name:
            return _pod_obj(p)
    return {"error": f"pod {name} not found in namespace {namespace}"}


def delete_pod(namespace, name):
    for p in _pods_rows():
        if p["namespace"] == namespace and p["name"] == name:
            obj = _pod_obj(p)
            _store_delete("pods", p)
            obj["status"]["phase"] = "Terminating"
            return obj
    return {"error": f"pod {name} not found in namespace {namespace}"}


# ---------------------------------------------------------------------------
# Deployments
# ---------------------------------------------------------------------------

def list_deployments(namespace):
    if not _ns_exists(namespace):
        return {"error": f"namespace {namespace} not found"}
    deps = [_deployment_obj(d) for d in _deployments_rows() if d["namespace"] == namespace]
    return _list_envelope("DeploymentList", deps)


def get_deployment(namespace, name):
    for d in _deployments_rows():
        if d["namespace"] == namespace and d["name"] == name:
            return _deployment_obj(d)
    return {"error": f"deployment {name} not found in namespace {namespace}"}


def scale_deployment(namespace, name, replicas):
    for d in _deployments_rows():
        if d["namespace"] == namespace and d["name"] == name:
            replicas = max(0, int(replicas))
            # Mock: available/ready converge to requested replica count.
            _changes = {
                "replicas": replicas,
                "available_replicas": replicas,
                "ready_replicas": replicas,
                "updated_replicas": replicas,
            }
            d.update(_changes)
            _store_patch("deployments", d, _changes)
            return {
                "kind": "Scale",
                "apiVersion": "autoscaling/v1",
                "metadata": {"name": name, "namespace": namespace},
                "spec": {"replicas": replicas},
                "status": {"replicas": replicas},
            }
    return {"error": f"deployment {name} not found in namespace {namespace}"}


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

def list_services(namespace):
    if not _ns_exists(namespace):
        return {"error": f"namespace {namespace} not found"}
    svcs = [_service_obj(s) for s in _services_rows() if s["namespace"] == namespace]
    return _list_envelope("ServiceList", svcs)


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def list_nodes():
    return _list_envelope("NodeList", [_node_obj(n) for n in _nodes_rows()])

_store.eager_load()
