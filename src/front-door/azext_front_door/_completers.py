# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.decorators import Completer

from ._client_factory import cf_frontdoor


def get_fd_subresource_completion_list(prop):

    # pylint: disable=inconsistent-return-statements
    @Completer
    def completer(cmd, prefix, namespace, **kwargs):  # pylint: disable=unused-argument
        client = cf_frontdoor(cmd.cli_ctx, None)
        try:
            frontdoor_name = namespace.frontdoor_name
        except AttributeError:
            frontdoor_name = namespace.resource_name
        if namespace.resource_group_name and frontdoor_name:
            frontdoor = client.get(namespace.resource_group_name, frontdoor_name)
            return [r.name for r in getattr(frontdoor, prop)]
    return completer
