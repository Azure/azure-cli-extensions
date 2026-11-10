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


def transform_billing_snapshot_list(result):
    rows = []
    for item in result:
        properties = item.get("properties") or {}
        billing = properties.get("billingConfiguration") or {}
        current = billing.get("current") or {}
        rows.append(OrderedDict([
            ("Name", item.get("name")),
            ("BillingStatus", billing.get("billingStatus")),
            ("Cores", current.get("cores")),
            ("PricingModel", current.get("pricingModel")),
            ("StartDate", current.get("startDate")),
            ("EndDate", current.get("endDate")),
        ]))
    return rows
