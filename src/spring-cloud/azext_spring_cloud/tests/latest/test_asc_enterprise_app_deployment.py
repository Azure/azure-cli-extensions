# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from ...vendored_sdks.appplatform.v2022_01_01_preview import models
from ...custom import (app_get)

try:
    import unittest.mock as mock
except ImportError:
    import mock

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


def _mock_client(subscription_id=None, **_):
    return mock.MagicMock()


def _mock_app(resource_group, service, name, properties=None):
    app = mock.MagicMock()
    app.id = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}/apps/{}'.format(resource_group, service, name)
    app.name = name
    app.location = 'eastus'
    app.properties = properties or mock.MagicMock()
    return app


def _mock_deployment(resource_group, service, app, name, properties=None, instance_count=None, active=True):
    deployment = mock.MagicMock()
    deployment.id = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}/apps/{}/deployments/{}'.format(resource_group, service, app, name)
    deployment.name = name
    deployment.properties = properties or models.DeploymentResourceProperties(
        source = models.BuildResultUserSourceInfo(build_result_id='<default>'),
        active = active,
        deployment_settings = models.DeploymentSettings(
            resource_requests=models.ResourceRequests(
                cpu='1',
                memory='1Gi'
            )
        )
    )
    deployment.sku = models.Sku(name='E0', tier='Enterprise', capacity=(instance_count or 1))
    return deployment


def _mock_app_get(client, resource_group, service, name, response=None):
    def _mock_get(resource_group, service, name):
        return response
    response = response or _mock_app(resource_group, service, name)
    client.apps.get = _mock_get
    return client


def _mock_deployment_list(client, resource_group, service, name, deployments=None):
    def _mock_list(resource_group, service, name):
        return deployments or []
    client.deployments.list = _mock_list
    return client


class TestAppCRUD(unittest.TestCase):
    def test_get_app_without_active_deployment(self):
        cmd = _get_test_cmd()
        client = _mock_client()
        _mock_app_get(client, 'rg', 'asc', 'app')
        _mock_deployment_list(client, 'rg', 'asc', 'app')
        result = app_get(cmd, client, 'rg', 'asc', 'app')
        self.assertTrue(result is not None)
        self.assertTrue(result.properties is not None)
        self.assertEqual('app', result.name)
        self.assertTrue(result.properties.active_deployment is None)

    def test_get_app_with_active_deployment(self):
        cmd = _get_test_cmd()
        client = _mock_client()
        _mock_app_get(client, 'rg', 'asc', 'app')
        _mock_deployment_list(client, 'rg', 'asc', 'app', [_mock_deployment('rg', 'asc', 'app', 'default')])
        result = app_get(cmd, client, 'rg', 'asc', 'app')
        self.assertTrue(result is not None)
        self.assertTrue(result.properties is not None)
        self.assertEqual('app', result.name)
        self.assertTrue(result.properties.active_deployment is not None)
        self.assertEqual('default', result.properties.active_deployment.name)
