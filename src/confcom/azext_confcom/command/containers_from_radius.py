# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import tempfile

from azext_confcom.lib.images import get_image_config, get_image_layers
from azext_confcom.lib.deployments import parse_deployment_template
from azext_confcom.lib.platform import ACI_MOUNTS


def containers_from_radius(
    az_cli_command,
    template: str,
    parameters: dict,
    container_index: int,
    platform: str,
) -> None:

    # Remove the radius extension inclusion to avoid parsing errors
    # For the purpose of extracting the container info we don't care about it
    with tempfile.NamedTemporaryFile('w+', delete=True, suffix=".bicep") as temp_template_file:
        with open(template, 'r') as f:
            temp_template_file.write(f.read().replace("extension radius", ""))
        temp_template_file.flush()

        template = parse_deployment_template(
            az_cli_command,
            temp_template_file.name,
            parameters,
        )

    supported_resources = [r for r in template.get("resources", []) if r.get("type") in {
        "Applications.Core/containers",
    }]

    container = supported_resources[container_index]
    image = container.get("properties", {}).get("container", {}).get("image")

    mounts = {
        "aci": ACI_MOUNTS,
    }.get(platform, None)

    return json.dumps({
        "id": image,
        "name": image,
        "layers": get_image_layers(image),
        **({"mounts": mounts} if mounts else {}),
        **get_image_config(image),
    })
