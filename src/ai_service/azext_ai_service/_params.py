# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

# from knack.arguments import CLIArgumentType


def load_arguments(self, _):

    # from azure.cli.core.commands.validators import get_default_location_from_resource_group

    # ai_service_name_type = CLIArgumentType(options_list='--ai-service-name-name', help='Name of the Ai_service.', id_part='name')

    with self.argument_context('ai_service') as c:
        c.argument('api_version')
        c.argument('model_format')
        c.argument('model_name')
        c.argument('model_version')

# End-of-file (EOF)
