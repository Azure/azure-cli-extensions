# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import subprocess
from ._resource_config import RESOURCE


class AddonFactory:

    Factory = {
        RESOURCE.Postgres: [
            {
                'create': 'az postgres server create -g {rg} -n {name} -l {loc} -u {user} -p {password}',
                'delete': 'az postgres server delete -g {rg} -n {name}'
            },
            {
                'create': 'az postgres db create -g {rg} -s {server} -n {name}',
                'delete': 'az postgres db delete -g {rg} -s {server} -n {name}'
            }
        ],
        RESOURCE.KeyVault: [
            {
                'create': 'az postgres keyvault create -g {rg} -n {name} -l {loc}',
                'delete': 'az postgres keyvault delete -g {rg} -n {name}'
            }
        ]
    }

    def __init__(self, resource_group, resource_type):
        self._resource_group = resource_group
        self._resource_type = resource_type
