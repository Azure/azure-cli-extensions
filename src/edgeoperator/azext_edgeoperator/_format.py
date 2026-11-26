# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict


def transform_log_collection_list(result):
    rows = []
    for item in result:
        properties = item.get("properties") or {}
        rows.append(OrderedDict([
            ("Name", item.get("name")),
            ("ProvisioningState", properties.get("provisioningState")),
            ("State", properties.get("state")),
            ("JobType", properties.get("jobType")),
            ("StartTime", properties.get("startTime")),
            ("EndTime", properties.get("endTime")),
        ]))
    return rows
