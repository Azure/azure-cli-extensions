# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from azext_confcom.lib.images import get_image_layers, get_image_config
from azext_confcom.lib.platform import ACI_MOUNTS


def containers_from_image(image: str, platform: str) -> str:

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
