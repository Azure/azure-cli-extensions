# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from pathlib import Path
import yaml

# from azext_confcom.lib.deployments import parse_deployment_template
from azext_confcom import config
from azext_confcom.lib.images import get_image_config, get_image_layers
from azext_confcom.lib.platform import VN2_MOUNTS
# from azext_confcom.lib.platform import ACI_MOUNTS


def find_vn2_containers(vn2_template):
    for key, value in vn2_template.items():
        if key == "containers":
            yield from value
        elif isinstance(value, dict):
            result = find_vn2_containers(value)
            if result is not None:
                yield from result
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    result = find_vn2_containers(item)
                    if result is not None:
                        yield from result


def containers_from_vn2(
    template: str,
    container_name: str
) -> None:

    with Path(template).open("r") as f:
        template_yaml = list(yaml.safe_load_all(f))

    # Find containers matching the specified name (and check there's exactly one)
    template_containers = []
    for doc in template_yaml:
        template_containers += [
            container
            for container in find_vn2_containers(doc)
            if container.get("name") == container_name
        ]
    assert len(template_containers) > 0, f"No containers with name {container_name} found."
    assert len(template_containers) <= 1, f"Multiple containers with name {container_name} found."

    template_container = template_containers[0]

    image = template_container.get("image")

    image_config = get_image_config(image)

    env_rules = image_config.pop("env_rules", [])
    for env_var in template_container.get("env", []):
        env_rules.append({
            "pattern": f"{env_var.get('name')}={env_var.get('value')}",
            "strategy": "string",
            "required": False,
        })


    env_rules += (
        config.OPENGCS_ENV_RULES
        + config.FABRIC_ENV_RULES
        + config.MANAGED_IDENTITY_ENV_RULES
        + config.ENABLE_RESTART_ENV_RULE
        + config.VIRTUAL_NODE_ENV_RULES
    )

    mounts = image_config.pop("mounts", [])
    mounts += [
        {
            "destination": m.get("mountPath"),
            "options": [
                "rbind",
                "rshared",
                "ro" if m.get("readOnly") else "rw"
            ],
            "source": "sandbox:///tmp/atlas/emptydir/.+",
            "type": "bind",
        }
        for m in template_container.get("volumeMounts", [])
    ]
    mounts += VN2_MOUNTS

    return json.dumps({
        "id": image,
        "name": template_container.get("name"),
        "layers": get_image_layers(image),
        "env_rules": env_rules,
        "mounts": mounts,
        "command": template_container.get("command", []) + template_container.get("args", []),
        **image_config,
    })
