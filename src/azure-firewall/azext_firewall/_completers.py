# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.decorators import Completer

from ._client_factory import network_client_factory


def get_af_subresource_completion_list(prop):

    # pylint: disable=inconsistent-return-statements
    @Completer
    def completer(cmd, prefix, namespace, **kwargs):  # pylint: disable=unused-argument
        client = network_client_factory(cmd.cli_ctx)
        try:
            firewall_name = namespace.firewall_name
        except AttributeError:
            firewall_name = namespace.resource_name
        if namespace.resource_group_name and firewall_name:
            af = client.azure_firewalls.get(namespace.resource_group_name, firewall_name)
            return [r.name for r in getattr(af, prop)]
    return completer
