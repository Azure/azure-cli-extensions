# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from azext_confcom.lib.containers import from_image as lib_containers_from_image


def containers_from_image(image: str, aci_or_vn2: str) -> None:
    print(json.dumps(lib_containers_from_image(image, aci_or_vn2)))
