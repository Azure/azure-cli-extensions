# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


def healthbot_update(client,
                     resource_group_name,
                     bot_name,
                     tags=None,
                     sku=None):
    parameters = {}
    parameters['tags'] = tags
    if sku is not None:
        parameters['sku'] = {'name': sku}
    return client.update(resource_group_name=resource_group_name,
                         bot_name=bot_name,
                         parameters=parameters)
