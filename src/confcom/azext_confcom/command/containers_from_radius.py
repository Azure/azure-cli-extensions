# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import tempfile

from azext_confcom.lib.images import get_image_config, get_image_layers
from azext_confcom.lib.deployments import parse_deployment_template
from azext_confcom.lib.platform import ACI_MOUNTS
import re


def containers_from_radius(
    az_cli_command,
    template: str,
    parameters: list,
    container_index: int,
    platform: str,
) -> None:

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

        template = parse_deployment_template(
            az_cli_command,
            temp_template_file.name,
            parameters,
        )

    supported_resources = [r for r in template.get("resources", []) if r.get("type") in {
        "Applications.Core/containers",
    }]

    resource = supported_resources[container_index].get("properties", {})
    container = resource.get("container", {})
    image = container.get("image")

    mounts = {
        "aci": ACI_MOUNTS,
    }.get(platform, None)

    mounts += [
        {
            "destination": mount_info["mountPath"],
            "options": ["rbind", "rshared", "ro"],
            "source": mount_info["source"],
            "type": "bind"
        }
        for mount_info in container.get("volumes", {}).values()
    ]

    image_config = get_image_config(image)

    env_rules = image_config.pop("env_rules", [])
    env_rules += [
        {
            "pattern": f'{k}={v["value"]}',
            "strategy": "string",
            "required": False,
        }
        for k, v in container.get("env", {}).items()
    ]
    env_rules += [
        {
            "name": f"CONNECTIONS_{k.upper()}_.+",
            "value": ".+",
            "strategy": "re2",
            "required": True,
        }
        for k in resource.get("connections", {}).keys()
    ]

    return json.dumps({
        "id": image,
        "name": image,
        "layers": get_image_layers(image),
        **({"mounts": mounts} if mounts else {}),
        "env_rules": env_rules,
        **image_config,
    })
