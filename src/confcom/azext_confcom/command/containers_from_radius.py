# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Extract container definitions from Radius templates for policy generation.

Supports the Applications.Core/containers resource type as defined in:
https://docs.radapp.io/reference/resource-schema/core-schema/container-schema/

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
runtimes.kubernetes.pod.containers      (sidecars — processed like main containers)
"""

import json
import os
import tempfile
import re

from azext_confcom.lib.containers import from_image, merge_containers
from azext_confcom.lib.templates import parse_deployment_template


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

    Radius injects CONNECTIONS_<NAME>_* environment variables for each
    connection defined on the resource, unless the connection sets
    disableDefaultEnvVars to true.
    """
    return [
        {
            "pattern": f"CONNECTIONS_{name.upper()}_.+=.+",
            "strategy": "re2",
            "required": True,
        }
        for name, conn in resource.get("connections", {}).items()
        if not conn.get("disableDefaultEnvVars")
    ]


def _map_volume_mounts(container: dict) -> list[dict]:
    """Template: container.volumes  →  Policy: mounts[]

    Each Radius volume maps to a bind mount:
      volumes[name].mountPath   → mount.destination
      volumes[name].source      → mount.source  (persistent) or ephemeral://<name>
      volumes[name].permission  → mount.options  (read-only for persistent unless 'write')
      volumes[name].rbac        → (legacy alias for permission)

    Ephemeral volumes (kind=='ephemeral') are writable by default.
    Persistent volumes default to read-only per the Radius spec.
    """
    mounts = []
    for volume_name, mount_info in container.get("volumes", {}).items():
        options = ["rbind", "rshared"]

        is_ephemeral = mount_info.get("kind") == "ephemeral"
        # The API reference uses "permission"; the human-readable docs use "rbac".
        access = mount_info.get("permission") or mount_info.get("rbac")

        if is_ephemeral:
            read_only = access == "read"
        else:
            read_only = access != "write"

        if read_only:
            options.append("ro")

        mounts.append({
            "destination": mount_info.get("mountPath"),
            "options": options,
            "source": mount_info.get("source") or f"ephemeral://{volume_name}",
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
# Container extraction
# ---------------------------------------------------------------------------

def _extract_container_def(container: dict, resource: dict, platform: str) -> dict:
    """
    Build a policy container definition from a Radius container spec.

    The base definition comes from the Docker image (via ``from_image``).
    Template-level overrides are computed by the ``_map_*`` helpers above,
    then merged on top of the image defaults via ``merge_containers``.
    """
    image = container.get("image")
    if not image:
        raise ValueError("Container must have an image")

    image_def = from_image(image, platform)

    template_def = {}

    command = _map_command(container, image_def.get("command", []))
    if command is not None:
        template_def["command"] = command

    working_dir = _map_working_dir(container)
    if working_dir is not None:
        template_def["working_dir"] = working_dir

    env_rules = _map_env_rules(container) + _map_connection_env_rules(resource)
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
    platform: str,
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

    # Remove the radius extension inclusion to avoid parsing errors
    # For the purpose of extracting the container info we don't care about it
    with tempfile.NamedTemporaryFile('w+', delete=True, suffix=".bicep") as temp_template_file:
        with open(template, 'r') as f:
            temp_template_file.write(f.read().replace("extension radius", ""))
        temp_template_file.flush()

        # Handle parameters file if it's a path
        if len(parameters) > 0 and isinstance(parameters[0][0], str) and os.path.isfile(parameters[0][0]):
            parameters_path = parameters[0][0]
            with open(parameters_path, 'r') as params_file:
                params_content = params_file.read()

            # Replace any references to the original template file with the temporary one
            params_content = re.sub(
                r"using\s+'.*\.bicep'",
                f"using '{os.path.basename(temp_template_file.name)}'",
                params_content
            )

            with tempfile.NamedTemporaryFile('w+', delete=False, suffix=".bicepparam") as temp_params_file:
                temp_params_file.write(params_content)
                temp_params_file.flush()
                parameters = [[temp_params_file.name]]

        parsed_template = parse_deployment_template(
            az_cli_command,
            temp_template_file.name,
            parameters,
        )

    # Find all Applications.Core/containers resources
    container_resources = [
        r for r in parsed_template.get("resources", [])
        if r.get("type") == "Applications.Core/containers"
    ]

    # Build a flat list of all containers (main + sidecars)
    all_containers = []

    for resource in container_resources:
        props = resource.get("properties", {})
        main_container = props.get("container", {})

        if main_container.get("image"):
            all_containers.append({
                "container": main_container,
                "resource": props,
                "source": "main",
            })

        # Extract sidecar containers from runtimes.kubernetes.pod.containers
        runtimes = props.get("runtimes", {})
        k8s_runtime = runtimes.get("kubernetes", {})
        pod_spec = k8s_runtime.get("pod", {})
        sidecar_containers = pod_spec.get("containers", [])

        for sidecar in sidecar_containers:
            if sidecar.get("image"):
                all_containers.append({
                    "container": sidecar,
                    "resource": props,  # Sidecars share the resource context
                    "source": "sidecar",
                })

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
