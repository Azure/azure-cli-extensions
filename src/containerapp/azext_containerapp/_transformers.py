# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def transform_usages_output(result):
    table_result = []
    for item in result["value"]:
        value = {
            "Name": item["name"]["value"],
            "Usage": item["usage"],
            "Limit": item["limit"]
        }
        table_result.append(value)

    return table_result
