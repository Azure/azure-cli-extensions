# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json

from typing import Optional

from azext_confcom.lib.fragment_references import from_image as lib_fragment_references_from_image


def fragment_references_from_image(image: str, minimum_svn: Optional[str]) -> str:
    return print(json.dumps(list(lib_fragment_references_from_image(image, minimum_svn))))
