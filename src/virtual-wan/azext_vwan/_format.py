# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict


def transform_effective_route_table(result):
    transformed = []
    for item in result.get('value', []):
        transformed.append(OrderedDict([
            ('Address Prefix', ' '.join(item['addressPrefixes'] or [])),
            ('Next Hop Type', item['nextHopType']),
            ('Next Hop', ' '.join(item['nextHops'] or [])),
            ('Route Origin', item['routeOrigin'])
        ]))
    return transformed
