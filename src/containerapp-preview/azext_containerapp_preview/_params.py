# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType

from ._utils import (_get_or_add_extension, _get_azext_module, GA_CONTAINERAPP_EXTENSION_NAME)


def load_arguments(self, _):
    if not _get_or_add_extension(self, GA_CONTAINERAPP_EXTENSION_NAME):
        return
    azext_params = _get_azext_module(
        GA_CONTAINERAPP_EXTENSION_NAME, "azext_containerapp._params")
    azext_params.load_arguments(self, _)

    from azure.cli.core.commands.parameters import tags_type
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    name_type = CLIArgumentType(options_list=['--name', '-n'])

    with self.argument_context('containerapp') as c:
        c.argument('tags', tags_type)
        c.argument('location', validator=get_default_location_from_resource_group)
        c.argument('name', name_type, options_list=['--name', '-n'])

    with self.argument_context('containerapp create') as c:
        c.argument('custom_location', nargs='*', options_list=['--traffic-weight'],
                   help="A list of revision weight(s) for the container app. Space-separated values in 'revision_name=weight' format. For latest revision, use 'latest=weight'")
