"""Data access module for the Kubernetes API mock service."""

import csv
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
    return [{**r, "labels": _labels(r["labels"])} for r in rows]


def _coerce_nodes(rows):
    return [{**r} for r in rows]


def _coerce_pods(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "restart_count": int(r["restart_count"]),
            "ready": _to_bool(r["ready"]),
            "node": r["node"] or None,
            "pod_ip": r["pod_ip"] or None,
        })
    return out


def _coerce_deployments(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "replicas": int(r["replicas"]),
            "available_replicas": int(r["available_replicas"]),
            "ready_replicas": int(r["ready_replicas"]),
            "updated_replicas": int(r["updated_replicas"]),
        })
    return out


def _coerce_services(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "port": int(r["port"]),
            "target_port": int(r["target_port"]),
            "external_ip": r["external_ip"] or None,
        })
    return out


_namespaces = _coerce_namespaces(_load("namespaces.csv"))
_nodes = _coerce_nodes(_load("nodes.csv"))
_pods = _coerce_pods(_load("pods.csv"))
_deployments = _coerce_deployments(_load("deployments.csv"))
_services = _coerce_services(_load("services.csv"))

_namespaces_store = deepcopy(_namespaces)
_nodes_store = deepcopy(_nodes)
_pods_store = deepcopy(_pods)
_deployments_store = deepcopy(_deployments)
_services_store = deepcopy(_services)


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
    return any(n["name"] == ns for n in _namespaces_store)


# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------

def list_namespaces():
    return _list_envelope("NamespaceList", [_ns_obj(n) for n in _namespaces_store])


# ---------------------------------------------------------------------------
# Pods
# ---------------------------------------------------------------------------

def list_pods(namespace):
    if not _ns_exists(namespace):
        return {"error": f"namespace {namespace} not found"}
    pods = [_pod_obj(p) for p in _pods_store if p["namespace"] == namespace]
    return _list_envelope("PodList", pods)


def get_pod(namespace, name):
    for p in _pods_store:
        if p["namespace"] == namespace and p["name"] == name:
            return _pod_obj(p)
    return {"error": f"pod {name} not found in namespace {namespace}"}


def delete_pod(namespace, name):
    for i, p in enumerate(_pods_store):
        if p["namespace"] == namespace and p["name"] == name:
            obj = _pod_obj(p)
            _pods_store.pop(i)
            obj["status"]["phase"] = "Terminating"
            return obj
    return {"error": f"pod {name} not found in namespace {namespace}"}


# ---------------------------------------------------------------------------
# Deployments
# ---------------------------------------------------------------------------

def list_deployments(namespace):
    if not _ns_exists(namespace):
        return {"error": f"namespace {namespace} not found"}
    deps = [_deployment_obj(d) for d in _deployments_store if d["namespace"] == namespace]
    return _list_envelope("DeploymentList", deps)


def get_deployment(namespace, name):
    for d in _deployments_store:
        if d["namespace"] == namespace and d["name"] == name:
            return _deployment_obj(d)
    return {"error": f"deployment {name} not found in namespace {namespace}"}


def scale_deployment(namespace, name, replicas):
    for i, d in enumerate(_deployments_store):
        if d["namespace"] == namespace and d["name"] == name:
            replicas = max(0, int(replicas))
            _deployments_store[i]["replicas"] = replicas
            # Mock: available/ready converge to requested replica count.
            _deployments_store[i]["available_replicas"] = replicas
            _deployments_store[i]["ready_replicas"] = replicas
            _deployments_store[i]["updated_replicas"] = replicas
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
    svcs = [_service_obj(s) for s in _services_store if s["namespace"] == namespace]
    return _list_envelope("ServiceList", svcs)


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def list_nodes():
    return _list_envelope("NodeList", [_node_obj(n) for n in _nodes_store])
