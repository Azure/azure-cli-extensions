# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.acr._validators import validate_registry_name


def load_arguments(self, _):

    with self.argument_context('acr query') as c:
        c.argument('registry_name', options_list=['--name', '-n'], validator=validate_registry_name, help='The name of the container registry that the query is run against.')
        c.argument('repository', help='The repository that the query is run against. If no repository is provided, the query is run at the registry level.')
        c.argument('kql_query', options_list=['--kql-query', '-q'], help='The KQL query to execute.')
        c.argument('skip_token', help='Skip token to get the next page of the query if applicable.')
        c.argument('username', help='Registry username')
        c.argument('password', help='Registry password')
