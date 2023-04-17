# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def load_arguments(self, _):
    from azure.cli.core.commands.validators import get_default_location_from_resource_group

    with self.argument_context('acr query') as c:
        c.argument('registry_name', options_list=['--name', '-n'], help='The name of the container registry that the query is run against.')
        c.argument('repository', options_list=['--repository'], help='The repository that the query is run against. If no repository is provided, the query is run at the registry level.')
        c.argument('kql_query', options_list=['--kql-query', '-q'], help='The KQL query to execute.')
        c.argument('skip_token', options_list=['--skip-token'], help='Skip token to get the next page of the query if applicable.')
        c.argument('username', options_list=['--username'], help='Registry username')
        c.argument('password', options_list=['--password'], help='Registry password')
