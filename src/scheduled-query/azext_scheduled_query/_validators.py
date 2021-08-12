# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def validate_tag(string):
    result = {}
    if string:
        comps = string.split('=', 1)
        result = {comps[0]: comps[1]} if len(comps) > 1 else {string: ''}
    return result


def validate_custom_properties(ns):
    if isinstance(ns.custom_properties, list):
        custom_properties_dict = {}
        for item in ns.custom_properties:
            custom_properties_dict.update(validate_tag(item))
        ns.custom_properties = custom_properties_dict
