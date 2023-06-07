# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from azext_containerapp_preview._client_factory import ex_handler_factory


def transform_containerapp_output(app):
    props = ['name', 'location', 'resourceGroup', 'provisioningState']
    result = {k: app[k] for k in app if k in props}

    try:
        result['fqdn'] = app['properties']['configuration']['ingress']['fqdn']
    except:
        result['fqdn'] = None

    return result


def load_command_table(self, _):

    with self.command_group('containerapp', is_preview=True) as g:
        g.custom_command('create', 'create_containerapp', supports_no_wait=True, exception_handler=ex_handler_factory(), table_transformer=transform_containerapp_output)
