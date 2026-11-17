# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from ._show import Show as _PrivateLinkResourceShow


class PrivateLinkResourceShow(_PrivateLinkResourceShow):
    AZ_HELP = {
        **_PrivateLinkResourceShow.AZ_HELP,
        'examples': [{
            'name': 'Get a HorizonDB private link resource',
            'text': 'az horizondb cluster private-link-resource show --resource-group example-resource-group '
                    '--cluster-name example-cluster --resource-name example-resource',
        }],
    }
