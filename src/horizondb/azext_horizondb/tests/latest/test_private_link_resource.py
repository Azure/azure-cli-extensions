# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from argparse import ArgumentParser
from unittest import TestCase
from unittest.mock import patch

from azure.cli.core import get_default_cli
from azure.cli.core.aaz import AAZCommand
from azext_horizondb import HorizonDBCommandsLoader
from azext_horizondb.aaz.latest.horizondb.cluster.private_link_resource.custom import PrivateLinkResourceShow


class PrivateLinkResourceTests(TestCase):

    def setUp(self):
        http_client = patch(
            'azure.cli.core.aaz._command_ctx.AAZCommandCtx.get_http_client',
            side_effect=AssertionError('Unit tests must not use Azure credentials or HTTP clients.')
        )
        http_client.start()
        self.addCleanup(http_client.stop)
        self.loader = HorizonDBCommandsLoader(cli_ctx=get_default_cli())
        self.command = self.loader.load_command_table(
            ['horizondb', 'cluster', 'private-link-resource', 'show']
        )['horizondb cluster private-link-resource show']
        self.command.load_arguments()

    def test_loader_registers_custom_show_with_resource_name_option(self):
        self.assertIsInstance(self.command, PrivateLinkResourceShow)
        self.assertEqual(
            self.command.arguments['group_name'].type.settings['options_list'],
            ['-n', '--name', '--resource-name'],
        )

    def test_resource_name_and_existing_aliases_select_request_resource(self):
        settings = self.command.arguments['group_name'].type.settings
        parser = ArgumentParser()
        parser.add_argument(*settings['options_list'], dest='group_name', action=settings['action'], required=True)
        for option in ['--resource-name', '--name', '-n']:
            with self.subTest(option=option):
                args = vars(parser.parse_args([option, 'test-resource']))
                args.update(
                    subscription='00000000-0000-0000-0000-000000000001',
                    resource_group='test-rg',
                    cluster_name='test-cluster',
                )
                AAZCommand._handler(self.command, args)  # pylint: disable=protected-access
                with patch.object(self.command.ctx, 'get_http_client'):
                    operation = self.command.PrivateLinkResourcesGet(ctx=self.command.ctx)
                self.assertEqual(operation.url_parameters, {
                    'subscriptionId': args['subscription'],
                    'resourceGroupName': 'test-rg',
                    'clusterName': 'test-cluster',
                    'groupName': 'test-resource',
                })
