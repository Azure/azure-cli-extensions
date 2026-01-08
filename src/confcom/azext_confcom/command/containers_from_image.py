# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from azext_confcom.lib.containers import from_image as lib_containers_from_image


def containers_from_image(image: str, platform: str) -> None:
    print(json.dumps(lib_containers_from_image(image, platform)))
