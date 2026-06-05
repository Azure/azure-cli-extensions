# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Extract container definitions from Radius templates for policy generation.

Supports two Radius container resource types:
  - Applications.Core/containers   (singular ``container`` property)
  - Radius.Compute/containers      (``containers`` dict of named containers)

Each Radius template field is mapped to its corresponding policy container
field by a dedicated ``_map_*`` function.  The overall flow is:

  1. ``from_image`` produces the **image-base** container definition
     (id, name, layers, platform mounts, command, env_rules, working_dir,
     signals).
  2. The ``_map_*`` helpers read Radius template fields and return the
     **template overrides** expressed as policy fields.
  3. ``merge_containers`` combines the two: list fields (env_rules, mounts,
     exec_processes, signals) are concatenated; scalar fields are replaced
     by the template value when present.

The ``_map_*`` functions operate on a canonical container dict with inline
``volumes`` and ``{kind, command, ...}``-style probes.  For
``Radius.Compute`` resources, ``_normalize_compute_container`` converts
each container to that canonical form first.

Template field                          Policy field      Mapper
--------------------------------------  ----------------  --------------------------
container.image                         id, name, layers  from_image
container.command / container.args      command           _map_command
container.workingDir                    working_dir       _map_working_dir
container.env                           env_rules         _map_env_rules
resource.connections                    env_rules         _map_connection_env_rules
container.volumes                       mounts            _map_volume_mounts
container.livenessProbe                 exec_processes    _map_exec_processes
container.readinessProbe                exec_processes    _map_exec_processes
runtimes.kubernetes.pod.containers      (sidecars — Applications.Core only)
"""

import json
import os
import tempfile
import re

from azext_confcom import config
from azext_confcom.lib.containers import from_image, merge_containers
from azext_confcom.lib.templates import parse_deployment_template


_PLATFORM_ENV_RULES = {
    "aci": (
        config.OPENGCS_ENV_RULES
        + config.FABRIC_ENV_RULES
        + config.MANAGED_IDENTITY_ENV_RULES
        + config.ENABLE_RESTART_ENV_RULE
    ),
    "vn2": (
        config.OPENGCS_ENV_RULES
        + config.FABRIC_ENV_RULES
        + config.MANAGED_IDENTITY_ENV_RULES
        + config.ENABLE_RESTART_ENV_RULE
        + config.VIRTUAL_NODE_ENV_RULES
    ),
}


def _platform_env_rules(platform: str) -> list[dict]:
    return [
        {
            "pattern": rule.get("pattern") or f"{rule.get('name')}={rule.get('value')}",
            "strategy": rule.get("strategy", "string"),
            "required": rule.get("required", False),
        }
        for rule in _PLATFORM_ENV_RULES.get(platform, [])
    ]


# ---------------------------------------------------------------------------
# Template field → Policy field mappers
# ---------------------------------------------------------------------------

def _map_command(container: dict, image_command: list) -> list | None:
    """Template: container.command, container.args  →  Policy: command

    Radius uses 'command' for the entrypoint and 'args' for arguments.
    - If command is specified, it replaces the image entrypoint entirely,
      with args appended.
    - If only args is specified, they are appended to the image entrypoint.
    - If neither is specified, returns None (image default is kept).
    """
    template_command = container.get("command")
    template_args = container.get("args")

    if template_command is not None:
        return list(template_command) + list(template_args or [])
    if template_args is not None:
        return list(image_command) + list(template_args)
    return None


def _map_working_dir(container: dict) -> str | None:
    """Template: container.workingDir  →  Policy: working_dir"""
    return container.get("workingDir") or None


def _map_env_rules(container: dict) -> list[dict]:
    """Template: container.env  →  Policy: env_rules[]

    - Plain values produce a string-match rule: NAME=value
    - Secret references (valueFrom) produce a regex rule: NAME=.+

    Handles both Radius dict format (main containers) and Kubernetes list
    format (sidecar containers from runtimes.kubernetes.pod.containers).
    """
    env = container.get("env")
    if not env:
        return []

    # Kubernetes list format: [{name: "X", value: "Y"}, ...]
    if isinstance(env, list):
        env = {item["name"]: {k: v for k, v in item.items() if k != "name"} for item in env}

    rules = []
    for env_name, env_spec in env.items():
        if "value" in env_spec:
            rules.append({
                "pattern": f'{env_name}={env_spec["value"]}',
                "strategy": "string",
                "required": False,
            })
        elif "valueFrom" in env_spec:
            rules.append({
                "pattern": f"{env_name}=.+",
                "strategy": "re2",
                "required": False,
            })
    return rules


def _map_connection_env_rules(resource: dict) -> list[dict]:
    """Template: resource.connections  →  Policy: env_rules[]

    Radius injects CONNECTION_<NAME>_* environment variables for each
    connection defined on the resource, unless the connection sets
    disableDefaultEnvVars to true.

    Additionally, the Radius ACI deployment template has special-case
    handling for a connection literally named ``secrets``: if its target
    resource exposes a ``userAssignedIdentityClientId`` in computedValues,
    the container group is injected with ``AZURE_CLIENT_ID`` and
    ``AZURE_KEYVAULT_URI`` env vars. Emit matching policy rules so that
    these are allowed when present.
    """
    rules = []
    for name, conn in resource.get("connections", {}).items():
        if conn.get("disableDefaultEnvVars"):
            continue
        rules.append({
            "pattern": f"CONNECTION_{name.upper()}_.+=.*",
            "strategy": "re2",
            "required": True,
        })
        if name == "secrets":
            for var in ("AZURE_CLIENT_ID", "AZURE_KEYVAULT_URI"):
                rules.append({
                    "pattern": f"{var}=.*",
                    "strategy": "re2",
                    "required": False,
                })
    return rules


def _map_volume_mounts(container: dict) -> list[dict]:
    """Template: container.volumes  →  Policy: mounts[]

    Operates on the Applications.Core volume shape (Radius.Compute volumes
    are converted first by ``_normalize_compute_container``):
      volumes[name].mountPath   → mount.destination
      volumes[name].kind        → mount.source  (atlas path picked by kind)
      volumes[name].permission  → mount.options  (read-only for persistent unless 'write')
      volumes[name].rbac        → (legacy alias for permission)

    Ephemeral volumes (kind=='ephemeral') are writable by default and use
    the emptydir source.  Persistent volumes default to read-only per the
    Radius spec; a writable persistent volume uses the azureFileVolume
    source, while a read-only one allows either azureFileVolume or
    secretsVolume since secret mounts from Radius.Compute normalize to a
    read-only persistent volume.
    """
    mounts = []
    # this takes the normalized volumes object added to the container object by
    # _normalize_compute_container
    for _volume_name, mount_info in container.get("volumes", {}).items():
        options = ["rbind", "rshared"]

        kind = mount_info.get("kind")
        # The API reference uses "permission"; the human-readable docs use "rbac".
        access = mount_info.get("permission") or mount_info.get("rbac")

        # TODO: these constants are defined in src/confcom/azext_confcom/data/internal_config.json
        if kind == "ephemeral":
            read_only = access == "read"
            source = "sandbox:///tmp/atlas/emptydir/.+"
        else:
            read_only = access != "write"
            if read_only:
                source = "sandbox:///tmp/atlas/(azureFileVolume|secretsVolume)/.+"
            else:
                source = "sandbox:///tmp/atlas/azureFileVolume/.+"

        options.append("ro" if read_only else "rw")

        mounts.append({
            "destination": mount_info.get("mountPath"),
            "options": options,
            "source": source,
            "type": "bind",
        })
    return mounts


def _map_exec_processes(container: dict) -> list[dict]:
    """Template: container.livenessProbe, container.readinessProbe  →  Policy: exec_processes[]

    Only exec-kind probes are mapped; HTTP/TCP probes are ignored.
    """
    processes = []
    for probe_key in ("livenessProbe", "readinessProbe"):
        probe = container.get(probe_key, {})
        if probe.get("kind") == "exec" and probe.get("command"):
            command = probe["command"]
            if isinstance(command, str):
                command = [command]
            processes.append({"command": command, "signals": []})
    return processes


# ---------------------------------------------------------------------------
# Radius.Compute schema normalization
# ---------------------------------------------------------------------------

# Both resource types represent container workloads; the schema differs.
_CONTAINER_RESOURCE_TYPES = {
    "Applications.Core/containers",
    "Radius.Compute/containers",
}


def _normalize_compute_probe(probe: dict) -> dict | None:
    """Convert a Radius.Compute probe to canonical {kind, command, ...} format."""
    if not probe:
        return None
    if "exec" in probe:
        return {"kind": "exec", "command": probe["exec"].get("command")}
    if "httpGet" in probe:
        hg = probe["httpGet"]
        return {"kind": "httpGet", "containerPort": hg.get("port"), "path": hg.get("path")}
    if "tcpSocket" in probe:
        return {"kind": "tcp", "containerPort": probe["tcpSocket"].get("port")}
    return None


def _normalize_compute_container(container: dict, resource_volumes: dict) -> dict:
    """Normalize a Radius.Compute/containers entry to canonical internal format.

    Converts the Radius.Compute representation to the Applications.Core
    representation so that the ``_map_*`` helpers can be applied uniformly.

    Volumes:
      - emptyDir          → kind: 'ephemeral'
      - persistentVolume  → kind: 'persistent' (read/write from accessMode)
      - secretName        → kind: 'persistent', permission: 'read'
        (Applications.Core has no dedicated secret kind; secret mounts
        always become read-only persistent volumes.  ``_map_volume_mounts``
        emits a source pattern accepting both azureFileVolume and
        secretsVolume for that case.)
    Probes:
      - {exec,httpGet,tcpSocket: ...} → {kind: ..., command/path/port: ...}
    All other fields (image, command, args, env, workingDir) pass through.
    """
    normalized = dict(container)

    # --- volumeMounts + resource-level volumes → inline Applications.Core volumes ---
    volume_mounts = container.get("volumeMounts", [])
    if volume_mounts and resource_volumes:
        inline_volumes = {}
        for vm in volume_mounts:
            vol_name = vm["volumeName"]
            vol_def = resource_volumes.get(vol_name, {})
            mount_path = vm["mountPath"]

            if "emptyDir" in vol_def:
                inline_volumes[vol_name] = {
                    "kind": "ephemeral",
                    "mountPath": mount_path,
                    "managedStore": vol_def["emptyDir"].get("medium", "disk"),
                }
            elif "persistentVolume" in vol_def:
                pv = vol_def["persistentVolume"]
                access = pv.get("accessMode", "ReadWriteOnce")
                inline_volumes[vol_name] = {
                    "kind": "persistent",
                    "mountPath": mount_path,
                    "source": pv.get("resourceId", ""),
                    "permission": "read" if access == "ReadOnlyMany" else "write",
                }
            elif "secretName" in vol_def:
                inline_volumes[vol_name] = {
                    "kind": "persistent",
                    "mountPath": mount_path,
                    "source": vol_def["secretName"],
                    "permission": "read",
                }
        normalized["volumes"] = inline_volumes

    # --- probes: structured → canonical {kind, ...} ---
    for probe_key in ("livenessProbe", "readinessProbe"):
        probe = container.get(probe_key)
        if probe:
            canonical = _normalize_compute_probe(probe)
            if canonical:
                normalized[probe_key] = canonical

    return normalized


# ---------------------------------------------------------------------------
# Per-resource-type container collectors
# ---------------------------------------------------------------------------

def _collect_applications_core_containers(resource: dict) -> list[dict]:
    """Extract containers from an Applications.Core/containers resource.

    The main container lives at ``properties.container`` (singular).
    Sidecar containers come from ``runtimes.kubernetes.pod.containers``.
    """
    props = resource.get("properties", {})
    results = []

    main_container = props.get("container", {})
    if main_container.get("image"):
        results.append({"container": main_container, "resource": props})

    runtimes = props.get("runtimes", {})
    pod_spec = runtimes.get("kubernetes", {}).get("pod", {})
    for sidecar in pod_spec.get("containers", []):
        if sidecar.get("image"):
            results.append({"container": sidecar, "resource": props})

    return results


def _collect_radius_compute_containers(resource: dict) -> list[dict]:
    """Extract containers from a Radius.Compute/containers resource.

    All containers live in ``properties.containers`` (dict of named
    containers).  Volumes are defined at ``properties.volumes`` and
    referenced via ``volumeMounts`` inside each container.  Each container
    is normalized to the canonical internal format before being returned.
    """
    props = resource.get("properties", {})
    resource_volumes = props.get("volumes", {})
    results = []

    for _name, raw_container in props.get("containers", {}).items():
        if raw_container.get("image"):
            container = _normalize_compute_container(raw_container, resource_volumes)
            results.append({"container": container, "resource": props})

    return results


# ---------------------------------------------------------------------------
# Container extraction
# ---------------------------------------------------------------------------

def _extract_container_def(container: dict, resource: dict, aci_or_vn2: str = "aci") -> dict:
    """
    Build a policy container definition from a Radius container spec.

    The base definition comes from the Docker image (via ``from_image``).
    Template-level overrides are computed by the ``_map_*`` helpers above,
    then merged on top of the image defaults via ``merge_containers``.
    """
    image = container.get("image")
    if not image:
        raise ValueError("Container must have an image")

    image_def = from_image(image, aci_or_vn2=aci_or_vn2)

    template_def = {}

    command = _map_command(container, image_def.get("command", []))
    if command is not None:
        template_def["command"] = command

    # ACI does not support overriding working directory, so any workingDir
    # defined in the recipe are ignored and the container starts with the
    # image's default working directory.  Therefore, our policygen should ignore
    # it as well.
    if aci_or_vn2 != "aci":
        working_dir = _map_working_dir(container)
        if working_dir is not None:
            template_def["working_dir"] = working_dir

    env_rules = (
        _platform_env_rules(aci_or_vn2)
        + _map_env_rules(container)
        + _map_connection_env_rules(resource)
    )
    if env_rules:
        template_def["env_rules"] = env_rules

    mounts = _map_volume_mounts(container)
    if mounts:
        template_def["mounts"] = mounts

    exec_processes = _map_exec_processes(container)
    if exec_processes:
        template_def["exec_processes"] = exec_processes

    return merge_containers(image_def, template_def)


def containers_from_radius(
    az_cli_command,
    template: str,
    parameters: list,
    container_index: int,
    platform: str = "aci",
) -> str:
    """
    Extract container definitions from a Radius bicep template.

    Args:
        az_cli_command: Azure CLI command context
        template: Path to the Radius bicep template
        parameters: List of parameter files/values
        container_index: Index of container to extract (0 = main container,
                        higher indices may refer to sidecars)
        platform: Target platform (aci, vn2)

    Returns:
        JSON string containing the container definition for policy generation.
    """

    # Remove radius extension lines to avoid bicep compilation errors.
    # Uses line-level regex so that 'extension radiusResources' etc. are
    # removed cleanly without leaving stray text.
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_template_path = os.path.join(temp_dir, "template.bicep")
        with open(template, 'r') as f:
            content = re.sub(r'^extension\s+\S+.*$', '', f.read(), flags=re.MULTILINE)
        with open(temp_template_path, 'w') as out:
            out.write(content)

        # Handle parameters file if it's a path
        if len(parameters) > 0 and isinstance(parameters[0][0], str) and os.path.isfile(parameters[0][0]):
            parameters_path = parameters[0][0]
            with open(parameters_path, 'r') as params_file:
                params_content = params_file.read()

            # Replace any references to the original template file with the temporary one
            params_content = re.sub(
                r"using\s+'.*\.bicep'",
                f"using '{os.path.basename(temp_template_path)}'",
                params_content
            )

            temp_params_path = os.path.join(temp_dir, "params.bicepparam")
            with open(temp_params_path, 'w') as out:
                out.write(params_content)
            parameters = [[temp_params_path]]

        parsed_template = parse_deployment_template(
            az_cli_command,
            temp_template_path,
            parameters,
        )

    # Find all container resources (both resource type schemas)
    container_resources = [
        r for r in parsed_template.get("resources", [])
        if r.get("type") in _CONTAINER_RESOURCE_TYPES
    ]

    # Each resource type has its own extraction function that returns a flat
    # list of (container_dict, resource_props) pairs.
    _RESOURCE_COLLECTORS = {
        "Applications.Core/containers": _collect_applications_core_containers,
        "Radius.Compute/containers": _collect_radius_compute_containers,
    }

    all_containers = []
    for resource in container_resources:
        collector = _RESOURCE_COLLECTORS.get(resource.get("type", ""))
        if collector:
            all_containers.extend(collector(resource))

    if container_index >= len(all_containers):
        raise IndexError(
            f"Container index {container_index} out of range. "
            f"Template has {len(all_containers)} container(s)."
        )

    target = all_containers[container_index]
    container_def = _extract_container_def(
        target["container"],
        target["resource"],
        platform,
    )

    return json.dumps(container_def)
