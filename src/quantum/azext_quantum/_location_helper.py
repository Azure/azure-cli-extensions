# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re

DEFAULT_WORKSPACE_LOCATION = 'westus'


# Currently, we're only checking that the provided location doesn't contain unsafe characters
# but there is no guarantee that the returned value exists as an Azure region.
# If an invalid region is specified, then the error will happen when the corresponding API
# endpoint isn't found.
def normalize_location(raw_location):
    if not raw_location:
        return DEFAULT_WORKSPACE_LOCATION
    location = re.sub("[^A-Za-z0-9]", "", raw_location).lower()
    if not location:
        return DEFAULT_WORKSPACE_LOCATION
    return location
