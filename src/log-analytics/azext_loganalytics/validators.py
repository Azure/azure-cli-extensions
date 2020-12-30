# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json


def validate_analytics_query(namespace):
    try:
        namespace.analytics_query = json.loads(namespace.analytics_query)
    except json.decoder.JSONDecodeError:
        pass
