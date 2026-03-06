# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Extract container definitions from Radius templates for policy generation.

Supports the Applications.Core/containers resource type as defined in:
https://docs.radapp.io/reference/resource-schema/core-schema/container-schema/

Coverage:
- properties.container.image (required)
- properties.container.env (environment variables)
- properties.container.command (entrypoint override)
- properties.container.args (arguments override)
- properties.container.workingDir (working directory override)
- properties.container.volumes (volume mounts)
- properties.container.livenessProbe (exec probes become exec_processes)
- properties.container.readinessProbe (exec probes become exec_processes)
- properties.connections (generates CONNECTIONS_* env rules)
- properties.runtimes.kubernetes.pod.containers (sidecar containers)
"""

import json
import os
import tempfile
import re
from dataclasses import asdict

from azext_confcom.lib.images import get_image_config, get_image_layers
from azext_confcom.lib.deployments import parse_deployment_template
from azext_confcom.lib.platform import ACI_MOUNTS


def _extract_container_def(container: dict, resource: dict, platform: str) -> dict:
    """
    Extract a single container definition from Radius container properties.

    Args:
        container: The container spec (properties.container or sidecar)
        resource: The full resource properties (for connections)
        platform: Target platform (aci, vn2, etc.)

    Returns:
        Container definition dict suitable for policy generation.
    """
    image = container.get("image")
    if not image:
        raise ValueError("Container must have an image")

    # Get base config from image
    image_config = get_image_config(image)

    # Template overrides for command/args/workingDir
    # Radius uses 'command' for entrypoint and 'args' for arguments
    template_command = container.get("command")
    template_args = container.get("args")
    template_working_dir = container.get("workingDir")

    # Build the final command: template overrides image defaults
    if template_command is not None:
        # If template specifies command, use it (with args if provided)
        final_command = list(template_command)
        if template_args:
            final_command.extend(template_args)
        image_config["command"] = final_command
    elif template_args is not None:
        # If only args specified, append to image entrypoint
        existing_command = image_config.get("command", [])
        image_config["command"] = list(existing_command) + list(template_args)

    # Working directory override
    if template_working_dir:
        image_config["working_dir"] = template_working_dir

    # Platform mounts + volume mounts
    # Convert ContainerMount dataclass objects to dicts for JSON serialization
    platform_mounts = {
        "aci": ACI_MOUNTS,
    }.get(platform, []) or []
    mounts = [asdict(m) if hasattr(m, '__dataclass_fields__') else m for m in platform_mounts]

    for volume_name, mount_info in container.get("volumes", {}).items():
        mount_def = {
            "destination": mount_info.get("mountPath"),
            "options": ["rbind", "rshared"],
            "type": "bind",
        }
        # Persistent volumes may have a source; ephemeral ones use managedStore
        if mount_info.get("source"):
            mount_def["source"] = mount_info.get("source")
        else:
            # Ephemeral volume - use a synthetic source based on name
            mount_def["source"] = f"ephemeral://{volume_name}"

        # rbac: 'read' or 'write' affects mount options
        if mount_info.get("rbac") != "write":
            mount_def["options"].append("ro")

        mounts.append(mount_def)

    # Environment rules: image defaults + template env + connections
    env_rules = image_config.pop("env_rules", [])

    # Add template-defined environment variables
    for env_name, env_spec in container.get("env", {}).items():
        if "value" in env_spec:
            env_rules.append({
                "pattern": f'{env_name}={env_spec["value"]}',
                "strategy": "string",
                "required": False,
            })
        elif "valueFrom" in env_spec:
            # Secret references - use regex pattern since value is dynamic
            env_rules.append({
                "pattern": f'{env_name}=.+',
                "strategy": "re2",
                "required": False,
            })

    # Connection-injected environment variables
    # Radius injects CONNECTIONS_<NAME>_* variables for each connection
    for conn_name in resource.get("connections", {}).keys():
        env_rules.append({
            "pattern": f"CONNECTIONS_{conn_name.upper()}_.+=.+",
            "strategy": "re2",
            "required": True,
        })

    # Exec processes from probes
    exec_processes = []

    for probe_type in ["livenessProbe", "readinessProbe"]:
        probe = container.get(probe_type, {})
        if probe.get("kind") == "exec" and probe.get("command"):
            # exec probes run a command inside the container
            command = probe.get("command")
            if isinstance(command, str):
                command = [command]
            exec_processes.append({
                "command": command,
                "signals": [],
            })

    # Build the container definition
    container_def = {
        "id": image,
        "name": image,
        "layers": get_image_layers(image),
        "env_rules": env_rules,
        **image_config,
    }

    if mounts:
        container_def["mounts"] = mounts

    if exec_processes:
        container_def["exec_processes"] = exec_processes

    return container_def


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
