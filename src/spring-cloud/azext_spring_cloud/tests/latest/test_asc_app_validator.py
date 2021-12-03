# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
import copy
from argparse import Namespace
from azure.cli.core.azclierror import InvalidArgumentValueError
from msrestazure.azure_exceptions import CloudError
from ..._app_validator import (fulfill_deployment_param)

try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock

from azure.cli.core.mock import DummyCli
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand


def _get_test_cmd():
    cli_ctx = DummyCli()
    cli_ctx.data['subscription_id'] = '00000000-0000-0000-0000-000000000000'
    loader = AzCommandsLoader(cli_ctx, resource_type='Microsoft.AppPlatform')
    cmd = AzCliCommand(loader, 'test', None)
    cmd.command_kwargs = {'resource_type': 'Microsoft.AppPlatform'}
    cmd.cli_ctx = cli_ctx
    return cmd


def _get_deployment(resource_group, service, app, deployment, active):
    resource = mock.MagicMock()
    resource.id = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}/apps/{}/deployments/{}'.format(resource_group, service, app, deployment)
    resource.properties = mock.MagicMock()
    resource.properties.active = active
    return resource


class TestFulfillDeploymentParameter(unittest.TestCase):
    @mock.patch('azext_spring_cloud._app_validator.cf_spring_cloud', autospec=True)
    def test_deployment_provide(self, client_factory_mock):
        client = mock.MagicMock()
        client.deployments.get.return_value = _get_deployment('rg1', 'asc1', 'app1', 'green1', False)
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment='green1')
        fulfill_deployment_param(_get_test_cmd(), ns)
        self.assertEqual('/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1/providers/Microsoft.AppPlatform/Spring/asc1/apps/app1/deployments/green1',
                          ns.deployment.id)
        self.assertFalse(ns.deployment.properties.active)


    @mock.patch('azext_spring_cloud._app_validator.cf_spring_cloud', autospec=True)
    def test_deployment_provide_but_not_found(self, client_factory_mock):
        client = mock.MagicMock()
        resp = mock.MagicMock()
        resp.status_code = 404
        resp.text = '{"Message": "Not Found"}'
        client.deployments.get.side_effect = CloudError(resp, error='deployment not found.')
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment='green1')
        with self.assertRaises(InvalidArgumentValueError) as context:
            fulfill_deployment_param(_get_test_cmd(), ns)
        self.assertEqual('Deployment green1 not found under app app1', str(context.exception))
    
    @mock.patch('azext_spring_cloud._app_validator.cf_spring_cloud', autospec=True)
    def test_deployment_with_active_deployment(self, client_factory_mock):
        client = mock.MagicMock()
        client.deployments.list.return_value = [
            _get_deployment('rg1', 'asc1', 'app1', 'green1', False),
            _get_deployment('rg1', 'asc1', 'app1', 'default', True),
        ]
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment=None)
        fulfill_deployment_param(_get_test_cmd(), ns)
        self.assertEqual('/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1/providers/Microsoft.AppPlatform/Spring/asc1/apps/app1/deployments/default',
                          ns.deployment.id)
        self.assertTrue(ns.deployment.properties.active)

    @mock.patch('azext_spring_cloud._app_validator.cf_spring_cloud', autospec=True)
    def test_deployment_without_active_deployment(self, client_factory_mock):
        client = mock.MagicMock()
        client.deployments.list.return_value = [
            _get_deployment('rg1', 'asc1', 'app1', 'green1', False)
        ]
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            fulfill_deployment_param(_get_test_cmd(), ns)
        self.assertEqual('No production deployment found, use --deployment to specify deployment or create deployment with: az spring-cloud app deployment create', str(context.exception))

    @mock.patch('azext_spring_cloud._app_validator.cf_spring_cloud', autospec=True)
    def test_deployment_without_deployment(self, client_factory_mock):
        client = mock.MagicMock()
        client.deployments.list.return_value = []
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            fulfill_deployment_param(_get_test_cmd(), ns)
        self.assertEqual('No production deployment found, use --deployment to specify deployment or create deployment with: az spring-cloud app deployment create', str(context.exception))