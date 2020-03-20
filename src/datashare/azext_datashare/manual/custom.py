# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines

import json


def datashare_account_test(cmd, client,
                           resource_group_name=None,
                           skip_token=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name,
                                             skip_token=skip_token)
    return client.list_by_subscription(skip_token=skip_token)

def datashare_account_show2(cmd, client,
                           a2,
                           bc):
    print('i am called')