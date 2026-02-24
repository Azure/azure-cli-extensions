# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from dataclasses import asdict
from azext_confcom.lib.images import get_image_layers, get_image_config
from azext_confcom.lib.platform import ACI_MOUNTS, VN2_MOUNTS


def merge_containers(*args) -> dict:

    merged_container = args[0].copy()

    for incoming_container in args[1:]:

        for key, value in incoming_container.items():

            if key in {
                "env_rules",
                "exec_processes",
                "mounts",
                "signals",
            }:
                existing = merged_container.get(key) or []
                merged_container[key] = list(existing) + list(value or [])
            else:
                merged_container[key] = value

    return merged_container


def from_image(image: str, platform: str) -> dict:

    mounts = {
        "aci": [asdict(mount) for mount in ACI_MOUNTS],
        "vn2": VN2_MOUNTS,
    }.get(platform, None)

    return {
        "id": image,
        "name": image,
        "layers": get_image_layers(image),
        **({"mounts": mounts} if mounts else {}),
        **get_image_config(image),
    }
