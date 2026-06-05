# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Unit tests for the _map_* and _normalize_* helper functions in
containers_from_radius.

Each function maps one Radius template field to its corresponding policy field.
Tests are grouped by helper function.
"""

from azext_confcom.command.containers_from_radius import (
    _map_command,
    _map_working_dir,
    _map_env_rules,
    _map_connection_env_rules,
    _map_volume_mounts,
    _map_exec_processes,
    _normalize_compute_container,
    _normalize_compute_probe,
)


# ---------------------------------------------------------------------------
# _map_command
# ---------------------------------------------------------------------------

def test_command_no_overrides_returns_none():
    assert _map_command({}, ["/bin/sh"]) is None


def test_command_replaces_image_entrypoint():
    result = _map_command({"command": ["/app/run"]}, ["/bin/sh"])
    assert result == ["/app/run"]


def test_command_with_args():
    result = _map_command({"command": ["/app/run"], "args": ["--verbose"]}, ["/bin/sh"])
    assert result == ["/app/run", "--verbose"]


def test_command_args_only_appends_to_image():
    result = _map_command({"args": ["--debug"]}, ["/bin/sh", "-c"])
    assert result == ["/bin/sh", "-c", "--debug"]


def test_command_args_only_with_empty_image_command():
    result = _map_command({"args": ["start"]}, [])
    assert result == ["start"]


def test_command_empty_is_not_none():
    """An explicit empty command list is a valid override."""
    result = _map_command({"command": []}, ["/bin/sh"])
    assert result == []


# ---------------------------------------------------------------------------
# _map_working_dir
# ---------------------------------------------------------------------------

def test_working_dir_absent():
    assert _map_working_dir({}) is None


def test_working_dir_returns_value():
    assert _map_working_dir({"workingDir": "/app"}) == "/app"


def test_working_dir_empty_string():
    assert _map_working_dir({"workingDir": ""}) is None


# ---------------------------------------------------------------------------
# _map_env_rules
# ---------------------------------------------------------------------------

def test_env_rules_empty():
    assert _map_env_rules({}) == []


def test_env_rules_plain_value():
    result = _map_env_rules({"env": {"MY_VAR": {"value": "hello"}}})
    assert result == [{"pattern": "MY_VAR=hello", "strategy": "string", "required": False}]


def test_env_rules_value_from_secret():
    result = _map_env_rules({"env": {"SECRET": {"valueFrom": {"secretRef": {}}}}})
    assert result == [{"pattern": "SECRET=.+", "strategy": "re2", "required": False}]


def test_env_rules_mixed_values():
    result = _map_env_rules({"env": {
        "A": {"value": "1"},
        "B": {"valueFrom": {"secretRef": {}}},
    }})
    assert len(result) == 2
    patterns = {r["pattern"] for r in result}
    assert "A=1" in patterns
    assert "B=.+" in patterns


def test_env_rules_kubernetes_list_format():
    """Sidecar containers use Kubernetes [{name, value}] format."""
    result = _map_env_rules({"env": [
        {"name": "FOO", "value": "bar"},
        {"name": "BAZ", "value": "qux"},
    ]})
    assert len(result) == 2
    patterns = {r["pattern"] for r in result}
    assert "FOO=bar" in patterns
    assert "BAZ=qux" in patterns


def test_env_rules_kubernetes_list_with_value_from():
    result = _map_env_rules({"env": [
        {"name": "SECRET", "valueFrom": {"secretKeyRef": {"name": "s", "key": "k"}}},
    ]})
    assert result == [{"pattern": "SECRET=.+", "strategy": "re2", "required": False}]


# ---------------------------------------------------------------------------
# _map_connection_env_rules
# ---------------------------------------------------------------------------

def test_connection_env_no_connections():
    assert _map_connection_env_rules({}) == []


def test_connection_env_single():
    result = _map_connection_env_rules({"connections": {"db": {"source": "x"}}})
    assert result == [{
        "pattern": "CONNECTION_DB_.+=.*", "strategy": "re2", "required": True,
    }]


def test_connection_env_multiple():
    result = _map_connection_env_rules({"connections": {
        "redis": {"source": "a"},
        "sql": {"source": "b"},
    }})
    names = {r["pattern"].split("_")[1] for r in result}
    assert names == {"REDIS", "SQL"}


def test_connection_env_disable_default_env_vars():
    """Connections with disableDefaultEnvVars should be skipped."""
    result = _map_connection_env_rules({"connections": {
        "db": {"source": "a"},
        "metrics": {"source": "b", "disableDefaultEnvVars": True},
    }})
    assert len(result) == 1
    assert "DB" in result[0]["pattern"]


def test_connection_env_all_disabled():
    result = _map_connection_env_rules({"connections": {
        "a": {"source": "x", "disableDefaultEnvVars": True},
    }})
    assert result == []


# ---------------------------------------------------------------------------
# _map_volume_mounts
# ---------------------------------------------------------------------------

def test_volumes_none():
    assert _map_volume_mounts({}) == []


def test_volumes_ephemeral_is_writable():
    """Ephemeral volumes should be writable by default."""
    result = _map_volume_mounts({"volumes": {
        "tmp": {"kind": "ephemeral", "mountPath": "/tmp", "managedStore": "memory"},
    }})
    assert len(result) == 1
    assert "ro" not in result[0]["options"]
    assert result[0]["destination"] == "/tmp"
    assert result[0]["source"] == "sandbox:///tmp/atlas/emptydir/.+"


def test_volumes_persistent_default_readonly():
    """Persistent volumes default to read-only per the Radius spec.

    A read-only persistent volume's source pattern accepts either
    azureFileVolume or secretsVolume because secret mounts from the
    Radius.Compute schema normalize to a read-only persistent volume.
    """
    result = _map_volume_mounts({"volumes": {
        "data": {"kind": "persistent", "mountPath": "/data", "source": "vol.id"},
    }})
    assert "ro" in result[0]["options"]
    assert result[0]["source"] == "sandbox:///tmp/atlas/(azureFileVolume|secretsVolume)/.+"


def test_volumes_persistent_permission_write():
    """API reference uses 'permission' field."""
    result = _map_volume_mounts({"volumes": {
        "data": {"kind": "persistent", "mountPath": "/data", "source": "v", "permission": "write"},
    }})
    assert "ro" not in result[0]["options"]
    assert result[0]["source"] == "sandbox:///tmp/atlas/azureFileVolume/.+"


def test_volumes_persistent_rbac_write():
    """Human-readable docs use 'rbac' field."""
    result = _map_volume_mounts({"volumes": {
        "data": {"kind": "persistent", "mountPath": "/data", "source": "v", "rbac": "write"},
    }})
    assert "ro" not in result[0]["options"]
    assert result[0]["source"] == "sandbox:///tmp/atlas/azureFileVolume/.+"


def test_volumes_persistent_permission_read():
    result = _map_volume_mounts({"volumes": {
        "cfg": {"kind": "persistent", "mountPath": "/cfg", "source": "v", "permission": "read"},
    }})
    assert "ro" in result[0]["options"]
    assert result[0]["source"] == "sandbox:///tmp/atlas/(azureFileVolume|secretsVolume)/.+"


def test_volumes_ephemeral_explicit_read():
    """Ephemeral volume can be explicitly set to read-only."""
    result = _map_volume_mounts({"volumes": {
        "ro_tmp": {"kind": "ephemeral", "mountPath": "/ro", "managedStore": "disk", "permission": "read"},
    }})
    assert "ro" in result[0]["options"]
    assert result[0]["source"] == "sandbox:///tmp/atlas/emptydir/.+"


def test_volumes_multiple():
    result = _map_volume_mounts({"volumes": {
        "a": {"kind": "ephemeral", "mountPath": "/a", "managedStore": "memory"},
        "b": {"kind": "persistent", "mountPath": "/b", "source": "vol"},
    }})
    assert len(result) == 2


# ---------------------------------------------------------------------------
# _map_exec_processes
# ---------------------------------------------------------------------------

def test_exec_no_probes():
    assert _map_exec_processes({}) == []


def test_exec_liveness_probe():
    result = _map_exec_processes({"livenessProbe": {"kind": "exec", "command": "ls"}})
    assert result == [{"command": ["ls"], "signals": []}]


def test_exec_readiness_probe():
    result = _map_exec_processes({"readinessProbe": {"kind": "exec", "command": ["cat", "/tmp/ready"]}})
    assert result == [{"command": ["cat", "/tmp/ready"], "signals": []}]


def test_exec_both_probes():
    result = _map_exec_processes({
        "livenessProbe": {"kind": "exec", "command": "live"},
        "readinessProbe": {"kind": "exec", "command": "ready"},
    })
    assert len(result) == 2


def test_exec_httpget_probe_ignored():
    """Only exec probes generate exec_processes."""
    result = _map_exec_processes({
        "livenessProbe": {"kind": "httpGet", "containerPort": 8080, "path": "/health"},
    })
    assert result == []


def test_exec_tcp_probe_ignored():
    result = _map_exec_processes({
        "readinessProbe": {"kind": "tcp", "containerPort": 3000},
    })
    assert result == []


def test_exec_probe_without_command_ignored():
    result = _map_exec_processes({"livenessProbe": {"kind": "exec"}})
    assert result == []


# ---------------------------------------------------------------------------
# _normalize_compute_probe
# ---------------------------------------------------------------------------

def test_normalize_probe_exec():
    result = _normalize_compute_probe({"exec": {"command": ["cat", "/tmp/healthy"]}})
    assert result == {"kind": "exec", "command": ["cat", "/tmp/healthy"]}


def test_normalize_probe_httpget():
    result = _normalize_compute_probe({"httpGet": {"path": "/health", "port": 8080}})
    assert result == {"kind": "httpGet", "containerPort": 8080, "path": "/health"}


def test_normalize_probe_tcp():
    result = _normalize_compute_probe({"tcpSocket": {"port": 3000}})
    assert result == {"kind": "tcp", "containerPort": 3000}


def test_normalize_probe_empty():
    assert _normalize_compute_probe({}) is None
    assert _normalize_compute_probe(None) is None


# ---------------------------------------------------------------------------
# _normalize_compute_container
# ---------------------------------------------------------------------------

def test_normalize_compute_passthrough_fields():
    """Fields shared between schemas pass through unchanged."""
    container = {
        "image": "nginx:latest",
        "command": ["/bin/sh"],
        "args": ["-c", "echo hi"],
        "workingDir": "/app",
        "env": {"FOO": {"value": "bar"}},
    }
    result = _normalize_compute_container(container, {})
    assert result["image"] == "nginx:latest"
    assert result["command"] == ["/bin/sh"]
    assert result["args"] == ["-c", "echo hi"]
    assert result["workingDir"] == "/app"
    assert result["env"] == {"FOO": {"value": "bar"}}


def test_normalize_compute_emptydir_volume():
    """emptyDir volumes normalize to Applications.Core ephemeral."""
    container = {
        "image": "nginx",
        "volumeMounts": [{"volumeName": "tmp", "mountPath": "/tmp/data"}],
    }
    resource_volumes = {"tmp": {"emptyDir": {"medium": "memory"}}}
    result = _normalize_compute_container(container, resource_volumes)

    assert "volumes" in result
    assert result["volumes"]["tmp"] == {
        "kind": "ephemeral",
        "mountPath": "/tmp/data",
        "managedStore": "memory",
    }


def test_normalize_compute_emptydir_default_medium():
    """emptyDir without medium defaults to 'disk'."""
    container = {
        "image": "nginx",
        "volumeMounts": [{"volumeName": "scratch", "mountPath": "/scratch"}],
    }
    resource_volumes = {"scratch": {"emptyDir": {}}}
    result = _normalize_compute_container(container, resource_volumes)
    assert result["volumes"]["scratch"]["managedStore"] == "disk"


def test_normalize_compute_persistent_volume():
    """persistentVolume normalizes to Applications.Core persistent."""
    container = {
        "image": "nginx",
        "volumeMounts": [{"volumeName": "data", "mountPath": "/data"}],
    }
    resource_volumes = {"data": {"persistentVolume": {"resourceId": "vol.id"}}}
    result = _normalize_compute_container(container, resource_volumes)

    assert result["volumes"]["data"] == {
        "kind": "persistent",
        "mountPath": "/data",
        "source": "vol.id",
        "permission": "write",  # ReadWriteOnce default → write
    }


def test_normalize_compute_persistent_readonly():
    """ReadOnlyMany access mode maps to permission 'read'."""
    container = {
        "image": "nginx",
        "volumeMounts": [{"volumeName": "cfg", "mountPath": "/cfg"}],
    }
    resource_volumes = {"cfg": {"persistentVolume": {
        "resourceId": "vol.id",
        "accessMode": "ReadOnlyMany",
    }}}
    result = _normalize_compute_container(container, resource_volumes)
    assert result["volumes"]["cfg"]["permission"] == "read"


def test_normalize_compute_secret_volume():
    """secretName volumes normalize to a read-only persistent volume."""
    container = {
        "image": "nginx",
        "volumeMounts": [{"volumeName": "certs", "mountPath": "/etc/certs"}],
    }
    resource_volumes = {"certs": {"secretName": "my-tls-secret"}}
    result = _normalize_compute_container(container, resource_volumes)

    assert result["volumes"]["certs"] == {
        "kind": "persistent",
        "mountPath": "/etc/certs",
        "source": "my-tls-secret",
        "permission": "read",
    }


def test_normalize_compute_probes():
    """Structured probes convert to canonical {kind, ...} format."""
    container = {
        "image": "nginx",
        "livenessProbe": {"exec": {"command": ["cat", "/tmp/healthy"]}},
        "readinessProbe": {"httpGet": {"path": "/ready", "port": 8080}},
    }
    result = _normalize_compute_container(container, {})

    assert result["livenessProbe"] == {"kind": "exec", "command": ["cat", "/tmp/healthy"]}
    assert result["readinessProbe"] == {"kind": "httpGet", "containerPort": 8080, "path": "/ready"}


def test_normalize_compute_no_volumes_or_probes():
    """Minimal container with no volumes or probes passes through cleanly."""
    container = {"image": "nginx", "ports": {"web": {"containerPort": 80}}}
    result = _normalize_compute_container(container, {})
    assert result["image"] == "nginx"
    assert "volumes" not in result
