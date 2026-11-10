# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Unambiguous finite JSON decoding and type-preserving snapshot comparison."""

import json
import math


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate")
        result[key] = value
    return result


def _finite(_value):
    raise ValueError("nonfinite")


def _float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("nonfinite")
    return number


def strict_json_loads(data):
    return json.loads(data, object_pairs_hook=_unique, parse_constant=_finite, parse_float=_float)


def json_equal(left, right):
    pending = [(left, right)]
    while pending:
        left, right = pending.pop()
        if left is right:
            continue
        if type(left) is not type(right):
            return False
        if isinstance(left, dict):
            if left.keys() != right.keys():
                return False
            pending.extend((left[key], right[key]) for key in left)
        elif isinstance(left, list):
            if len(left) != len(right):
                return False
            pending.extend(zip(left, right))
        elif left != right:
            return False
    return True
