# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from argparse import Namespace
from azure.cli.core.azclierror import InvalidArgumentValueError
from msrestazure.azure_exceptions import CloudError
from azure.core.exceptions import ResourceNotFoundError
from .common.test_utils import get_test_cmd
from ..._app_validator import (fulfill_deployment_param, active_deployment_exist,
                               validate_cpu, validate_memory, validate_deloyment_create_path, validate_deloy_path)

try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock

from azure.cli.core.mock import DummyCli
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand


def _get_deployment(resource_group, service, app, deployment, active):
    resource = mock.MagicMock()
    resource.id = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/{}/providers/Microsoft.AppPlatform/Spring/{}/apps/{}/deployments/{}'.format(
        resource_group, service, app, deployment)
    resource.properties = mock.MagicMock()
    resource.properties.active = active
    return resource


class TestCpuAndMemoryValidator(unittest.TestCase):
    def test_none_input(self):
        ns = Namespace(cpu=None, memory=None)
        validate_memory(ns)
        validate_cpu(ns)
        self.assertIsNone(ns.cpu)
        self.assertIsNone(ns.memory)

    def test_int_input(self):
        ns = Namespace(cpu='1', memory='1')
        validate_memory(ns)
        validate_cpu(ns)
        self.assertEqual('1', ns.cpu)
        self.assertEqual('1Gi', ns.memory)

    def test_str_input(self):
        ns = Namespace(cpu='1', memory='1Gi')
        validate_memory(ns)
        validate_cpu(ns)
        self.assertEqual('1', ns.cpu)
        self.assertEqual('1Gi', ns.memory)

    def test_invalid_memory(self):
        ns = Namespace(memory='invalid')
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_memory(ns)
        self.assertEqual('Memory quantity should be integer followed by unit (Mi/Gi)', str(context.exception))

    def test_invalid_cpu(self):
        ns = Namespace(cpu='invalid')
        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_cpu(ns)
        self.assertEqual('CPU quantity should be millis (250m, 500m, 750m, 1250m) or integer (1, 2, ...)',
                         str(context.exception))


class TestDeployPath(unittest.TestCase):
    @mock.patch('azext_spring._app_validator.cf_spring', autospec=True)
    def test_no_deploy_path_provided_when_create(self, client_factory_mock):
        ns = Namespace(source_path=None, artifact_path=None, container_image=None, resource_group='rg', service='test')
        client = mock.MagicMock()
        client.buildservices.get.return_value = []
        client_factory_mock.return_value = client
        validate_deloyment_create_path(get_test_cmd(), ns)

    def test_no_deploy_path_when_deploy(self):
        ns = Namespace(source_path=None, artifact_path=None, container_image=None)
        with self.assertRaises(InvalidArgumentValueError):
            validate_deloy_path(get_test_cmd(), ns)

    def test_more_than_one_path(self):
        ns = Namespace(source_path='test', artifact_path='test', container_image=None)
        with self.assertRaises(InvalidArgumentValueError):
            validate_deloy_path(get_test_cmd(), ns)
        with self.assertRaises(InvalidArgumentValueError):
            validate_deloyment_create_path(get_test_cmd(), ns)

    def test_more_than_one_path_1(self):
        ns = Namespace(source_path='test', artifact_path='test', container_image='test')
        with self.assertRaises(InvalidArgumentValueError):
            validate_deloy_path(get_test_cmd(), ns)
        with self.assertRaises(InvalidArgumentValueError):
            validate_deloyment_create_path(get_test_cmd(), ns)

    def test_more_than_one_path_2(self):
        ns = Namespace(source_path='test', artifact_path=None, container_image='test')
        with self.assertRaises(InvalidArgumentValueError):
            validate_deloy_path(get_test_cmd(), ns)
        with self.assertRaises(InvalidArgumentValueError):
            validate_deloyment_create_path(get_test_cmd(), ns)


class TestActiveDeploymentExist(unittest.TestCase):
    @mock.patch('azext_spring._app_validator.cf_spring', autospec=True)
    def test_deployment_found(self, client_factory_mock):
        client = mock.MagicMock()
        client.deployments.list.return_value = [
            _get_deployment('rg1', 'asc1', 'app1', 'green1', False),
            _get_deployment('rg1', 'asc1', 'app1', 'default', True),
        ]
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment=None)
        active_deployment_exist(get_test_cmd(), ns)

    @mock.patch('azext_spring._app_validator.cf_spring', autospec=True)
    def test_deployment_without_active_exist(self, client_factory_mock):
        client = mock.MagicMock()
        client.deployments.list.return_value = [
            _get_deployment('rg1', 'asc1', 'app1', 'green1', False)
        ]
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            active_deployment_exist(get_test_cmd(), ns)
        self.assertEqual(
            'This app has no production deployment, use \"az spring app deployment create\" to create a deployment and \"az spring app set-deployment\" to set production deployment.',
            str(context.exception))

    @mock.patch('azext_spring._app_validator.cf_spring', autospec=True)
    def test_no_deployments(self, client_factory_mock):
        client = mock.MagicMock()
        client.deployments.list.return_value = []
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            active_deployment_exist(get_test_cmd(), ns)
        self.assertEqual(
            'This app has no production deployment, use \"az spring app deployment create\" to create a deployment and \"az spring app set-deployment\" to set production deployment.',
            str(context.exception))

    @mock.patch('azext_spring._app_validator.cf_spring', autospec=True)
    def test_app_not_found(self, client_factory_mock):
        client = mock.MagicMock()
        resp = mock.MagicMock()
        resp.status_code = 404
        resp.text = '{"Message": "Not Found"}'
        client.deployments.list.side_effect = ResourceNotFoundError(resp, error='App not found.')
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            active_deployment_exist(get_test_cmd(), ns)
        self.assertEqual('App app1 not found', str(context.exception))


class TestFulfillDeploymentParameter(unittest.TestCase):
    @mock.patch('azext_spring._app_validator.cf_spring', autospec=True)
    def test_deployment_provide(self, client_factory_mock):
        client = mock.MagicMock()
        client.deployments.get.return_value = _get_deployment('rg1', 'asc1', 'app1', 'green1', False)
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment='green1')
        fulfill_deployment_param(get_test_cmd(), ns)
        self.assertEqual(
            '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1/providers/Microsoft.AppPlatform/Spring/asc1/apps/app1/deployments/green1',
            ns.deployment.id)
        self.assertFalse(ns.deployment.properties.active)

    @mock.patch('azext_spring._app_validator.cf_spring', autospec=True)
    def test_deployment_provide_but_not_found(self, client_factory_mock):
        client = mock.MagicMock()
        resp = mock.MagicMock()
        resp.status_code = 404
        resp.text = '{"Message": "Not Found"}'
        client.deployments.get.side_effect = CloudError(resp, error='deployment not found.')
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment='green1')
        with self.assertRaises(InvalidArgumentValueError) as context:
            fulfill_deployment_param(get_test_cmd(), ns)
        self.assertEqual('Deployment green1 not found under app app1', str(context.exception))

    @mock.patch('azext_spring._app_validator.cf_spring', autospec=True)
    def test_deployment_with_active_deployment(self, client_factory_mock):
        client = mock.MagicMock()
        client.deployments.list.return_value = [
            _get_deployment('rg1', 'asc1', 'app1', 'green1', False),
            _get_deployment('rg1', 'asc1', 'app1', 'default', True),
        ]
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment=None)
        fulfill_deployment_param(get_test_cmd(), ns)
        self.assertEqual(
            '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1/providers/Microsoft.AppPlatform/Spring/asc1/apps/app1/deployments/default',
            ns.deployment.id)
        self.assertTrue(ns.deployment.properties.active)

    @mock.patch('azext_spring._app_validator.cf_spring', autospec=True)
    def test_deployment_with_active_deployment_for_app_parameter(self, client_factory_mock):
        client = mock.MagicMock()
        client.deployments.list.return_value = [
            _get_deployment('rg1', 'asc1', 'app1', 'green1', False),
            _get_deployment('rg1', 'asc1', 'app1', 'default', True),
        ]
        client_factory_mock.return_value = client

        ns = Namespace(app='app1', service='asc1', resource_group='rg1', deployment=None)
        fulfill_deployment_param(get_test_cmd(), ns)
        self.assertEqual(
            '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg1/providers/Microsoft.AppPlatform/Spring/asc1/apps/app1/deployments/default',
            ns.deployment.id)
        self.assertTrue(ns.deployment.properties.active)

    @mock.patch('azext_spring._app_validator.cf_spring', autospec=True)
    def test_deployment_without_active_deployment(self, client_factory_mock):
        client = mock.MagicMock()
        client.deployments.list.return_value = [
            _get_deployment('rg1', 'asc1', 'app1', 'green1', False)
        ]
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            fulfill_deployment_param(get_test_cmd(), ns)
        self.assertEqual(
            'No production deployment found, use --deployment to specify deployment or create deployment with: az spring app deployment create',
            str(context.exception))

    @mock.patch('azext_spring._app_validator.cf_spring', autospec=True)
    def test_deployment_without_deployment(self, client_factory_mock):
        client = mock.MagicMock()
        client.deployments.list.return_value = []
        client_factory_mock.return_value = client

        ns = Namespace(name='app1', service='asc1', resource_group='rg1', deployment=None)
        with self.assertRaises(InvalidArgumentValueError) as context:
            fulfill_deployment_param(get_test_cmd(), ns)
        self.assertEqual(
            'No production deployment found, use --deployment to specify deployment or create deployment with: az spring app deployment create',
            str(context.exception))
