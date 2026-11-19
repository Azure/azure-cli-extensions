# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unittest import TestCase
from unittest.mock import patch

from azure.cli.core import get_default_cli
from azure.cli.core.aaz import AAZCommand
from azext_horizondb.aaz.latest.horizondb.parameter_group import Create, Show, Update


class ParameterGroupCreateTests(TestCase):

    def setUp(self):
        http_client = patch(
            'azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client',
            side_effect=AssertionError('Unit tests must not use Azure credentials or HTTP clients.')
        )
        http_client.start()
        self.addCleanup(http_client.stop)
        self.cli_ctx = get_default_cli()
        self.args = {
            'subscription': '00000000-0000-0000-0000-000000000001',
            'resource_group': 'test-rg',
            'parameter_group_name': 'test-parameters',
        }
        self.parameters = [{'name': 'work_mem', 'value': '8192'}]

    def test_create_serializes_parameters_and_version(self):
        command = Create(cli_ctx=self.cli_ctx)
        args = dict(self.args, location='japaneast', version='17',
                    description='Test parameters', parameters=self.parameters)
        AAZCommand._handler(command, args)  # pylint: disable=protected-access
        with patch.object(command.ctx, 'get_http_client'):
            operation = command.ParameterGroupsCreateOrReplace(ctx=command.ctx)

        self.assertEqual(operation.method, 'PUT')
        self.assertEqual(operation.url_parameters, {
            'subscriptionId': self.args['subscription'],
            'resourceGroupName': 'test-rg',
            'parameterGroupName': 'test-parameters',
        })
        self.assertEqual(operation.content, {
            'location': 'japaneast',
            'properties': {
                'postgreSqlVersion': '17',
                'description': 'Test parameters',
                'parameters': self.parameters,
            },
        })

    def test_update_sends_only_supplied_properties(self):
        for changes in [
                {'parameters': self.parameters},
                {'description': 'Updated description'},
                {'parameters': []}]:
            with self.subTest(changes=changes):
                command = Update(cli_ctx=self.cli_ctx)
                AAZCommand._handler(command, dict(self.args, **changes))  # pylint: disable=protected-access
                with patch.object(command.ctx, 'get_http_client'):
                    operation = command.ParameterGroupsUpdate(ctx=command.ctx)

                self.assertEqual(operation.method, 'PATCH')
                self.assertEqual(operation.content, {'properties': changes})

    def test_show_returns_parameter_group(self):
        command = Show(cli_ctx=self.cli_ctx)
        schema_builder = command.ParameterGroupsGet._build_schema_on_200  # pylint: disable=protected-access
        resource = {
            'name': 'test-parameters',
            'location': 'japaneast',
            'properties': {
                'postgreSqlVersion': '17',
                'parameters': self.parameters,
                'provisioningState': 'Succeeded',
            },
        }

        def get_parameter_group():
            command.ctx.set_var('instance', resource, schema_builder=schema_builder)

        with patch.object(command, 'ParameterGroupsGet') as get:
            get.return_value.side_effect = get_parameter_group
            result = command(command_args=self.args)

        get.return_value.assert_called_once_with()
        self.assertEqual(result, resource)
