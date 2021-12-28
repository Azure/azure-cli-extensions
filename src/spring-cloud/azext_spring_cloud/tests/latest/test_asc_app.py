# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from os import name
import unittest
from unittest.mock import MagicMock
from azure.cli.core.azclierror import InvalidArgumentValueError, ResourceNotFoundError
from knack.util import CLIError
from msrestazure.azure_exceptions import CloudError
from ...vendored_sdks.appplatform.v2022_01_01_preview import models
from ..._utils import _get_sku_name
from ...app import (app_create, app_update, app_deploy, deployment_create)
try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock

from azure.cli.core.mock import DummyCli
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand

from knack.log import get_logger
from azure.cli.core.azclierror import InvalidArgumentValueError

logger = get_logger(__name__)

def _get_test_cmd():
    cli_ctx = DummyCli()
    cli_ctx.data['subscription_id'] = '00000000-0000-0000-0000-000000000000'
    loader = AzCommandsLoader(cli_ctx, resource_type='Microsoft.AppPlatform')
    cmd = AzCliCommand(loader, 'test', None)
    cmd.command_kwargs = {'resource_type': 'Microsoft.AppPlatform'}
    cmd.cli_ctx = cli_ctx
    return cmd


class BasicTest(unittest.TestCase):
    def _get_basic_mock_client(self, sku='Standard'):
        client = mock.MagicMock()
        client.services.get.return_value = models.ServiceResource(
            sku=models.Sku(
                tier=sku,
                name=_get_sku_name(sku)
            )
        )
        return client

    def _get_deployment(self, sku='Standard'):
        deployment = mock.MagicMock()
        deployment.name = 'default'
        deployment.properties.source.type = 'Jar'
        deployment.properties.source.relative_path = 'my-path'
        deployment.properties.source.runtime_version = 'Java_11'
        deployment.properties.source.version = '123'
        deployment.properties.source.jvm_options = None

        deployment.properties.deployment_settings.environment_variables = {'foo': 'bar'}
        deployment.properties.deployment_settings.resource_requests.cpu = '2'
        deployment.properties.deployment_settings.resource_requests.memory = '2Gi'
        deployment.sku.capacity = 2
        deployment.sku.tier = sku
        deployment.sku.name = _get_sku_name(sku)
        return deployment


class TestAppDeploy_Patch(BasicTest):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.patch_deployment_resource = None

    def _get_basic_mock_client(self, sku='Standard'):
        client = super()._get_basic_mock_client(sku=sku)
        client.apps.get_resource_upload_url.return_value = self._get_upload_info()
        return client

    def _get_upload_info(self):
        resp = mock.MagicMock()
        resp.relative_path = 'my-relative-path'
        resp.upload_url = 'https://mystorage.file.core.windows.net/root/my-relative-path?sv=2018-03-28&sr=f&sig=my-fake-pass&se=2021-12-28T06%3A43%3A17Z&sp=w'
        return resp

    def _execute(self, *args, **kwargs):
        client = kwargs.pop('client', None) or self._get_basic_mock_client()
        app_deploy(_get_test_cmd(), client, *args, **kwargs)

        call_args = client.deployments.begin_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(5, len(call_args[0][0]))
        self.assertEqual(args[0:3] + ('default',), call_args[0][0][0:4])
        self.patch_deployment_resource = call_args[0][0][4]

    @mock.patch('azext_spring_cloud._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), artifact_path='my-path')
        resource = self.patch_deployment_resource
        self.assertEqual('Jar', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('Java_11', resource.properties.source.runtime_version)
        # self.assertIsNone(resource.sku)

    @mock.patch('azext_spring_cloud._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy_with_runtime_version(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), artifact_path='my-path', runtime_version='Java_8')
        resource = self.patch_deployment_resource
        self.assertEqual('Jar', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('Java_8', resource.properties.source.runtime_version)

    @mock.patch('azext_spring_cloud._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy_net(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), artifact_path='my-path', runtime_version='NetCore_31', main_entry='test')
        resource = self.patch_deployment_resource
        self.assertEqual('NetCoreZip', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('NetCore_31', resource.properties.source.runtime_version)
        self.assertEqual('test', resource.properties.source.net_core_main_entry_path)

    @mock.patch('azext_spring_cloud._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_continous_deploy_net(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        deployment=self._get_deployment()
        deployment.properties.source.type = 'NetCoreZip'
        deployment.properties.source.relative_path = 'my-path'
        deployment.properties.source.runtime_version = 'NetCore_31'
        deployment.properties.source.version = '123'
        deployment.properties.source.net_core_main_entry_path = 'test'
        self._execute('rg', 'asc', 'app', deployment=deployment, artifact_path='my-path', main_entry='new-test')
        resource = self.patch_deployment_resource
        self.assertEqual('NetCoreZip', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('NetCore_31', resource.properties.source.runtime_version)
        self.assertEqual('new-test', resource.properties.source.net_core_main_entry_path)

    @mock.patch('azext_spring_cloud._deployment_uploadable_factory.FolderUpload.upload_and_build')
    def test_app_deploy_source(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), source_path='my-path')
        resource = self.patch_deployment_resource
        self.assertEqual('Source', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertIsNone(resource.properties.source.runtime_version)

    @mock.patch('azext_spring_cloud._deployment_uploadable_factory.FolderUpload.upload_and_build')
    def test_app_continous_deploy_source(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        deployment=self._get_deployment()
        deployment.properties.source.type = 'Container'
        deployment.properties.source.relative_path = 'my-path'
        deployment.properties.source.version = '123'
        deployment.properties.source.artifact_selector = 'test'
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), source_path='my-path')
        resource = self.patch_deployment_resource
        self.assertEqual('Source', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertIsNone(resource.properties.source.runtime_version)

class TestAppDeploy_Put(BasicTest):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.put_deployment_resource = None

    def _get_basic_mock_client(self, sku='Standard'):
        client = super()._get_basic_mock_client(sku=sku)
        client.apps.get_resource_upload_url.return_value = self._get_upload_info()
        return client

    def _get_upload_info(self):
        resp = mock.MagicMock()
        resp.relative_path = 'my-relative-path'
        resp.upload_url = 'https://mystorage.file.core.windows.net/root/my-relative-path?sv=2018-03-28&sr=f&sig=my-fake-pass&se=2021-12-28T06%3A43%3A17Z&sp=w'
        return resp

    def _execute(self, *args, **kwargs):
        client = kwargs.pop('client', None) or self._get_basic_mock_client()
        app_deploy(_get_test_cmd(), client, *args, **kwargs)

        call_args = client.deployments.begin_create_or_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(5, len(call_args[0][0]))
        self.assertEqual(args[0:3] + ('default',), call_args[0][0][0:4])
        self.put_deployment_resource = call_args[0][0][4]

    def test_app_deploy_container_from_jar(self):
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), container_image='my-image')
        resource = self.put_deployment_resource
        self.assertEqual('Container', resource.properties.source.type)
        self.assertEqual('my-image', resource.properties.source.custom_container.container_image)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('2', resource.properties.deployment_settings.resource_requests.cpu)
        self.assertEqual('2Gi', resource.properties.deployment_settings.resource_requests.memory)
        self.assertEqual(2, resource.sku.capacity)

    @mock.patch('azext_spring_cloud._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy_jar_from_container(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        deployment=self._get_deployment()
        deployment.properties.source.type = 'Container'
        deployment.properties.source.custom_container = mock.MagicMock()
        deployment.properties.source.relative_path = None
        deployment.properties.source.runtime_version = None
        deployment.properties.source.version = '123'
        self._execute('rg', 'asc', 'app', deployment=deployment, artifact_path='my-path')
        resource = self.put_deployment_resource
        self.assertEqual('Jar', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('Java_8', resource.properties.source.runtime_version)
        self.assertEqual('2', resource.properties.deployment_settings.resource_requests.cpu)
        self.assertEqual('2Gi', resource.properties.deployment_settings.resource_requests.memory)
        self.assertEqual(2, resource.sku.capacity)


class TestAppUpdate(BasicTest):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.patch_app_resource = None
        self.patch_deployment_resource = None

    def _execute(self, *args, **kwargs):
        client = kwargs.pop('client', None) or self._get_basic_mock_client()
        app_update(_get_test_cmd(), client, *args, **kwargs)

        call_args = client.deployments.begin_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(5, len(call_args[0][0]))
        self.assertEqual(args[0:3] + ('default',), call_args[0][0][0:4])
        self.patch_deployment_resource = call_args[0][0][4]

        call_args = client.apps.begin_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(4, len(call_args[0][0]))
        self.assertEqual(args[0:3], call_args[0][0][0:3])
        self.patch_app_resource = call_args[0][0][3]

    def test_app_update_jvm_options(self):
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), jvm_options='test-option')
        resource = self.patch_deployment_resource
        self.assertEqual('Jar', resource.properties.source.type)
        self.assertEqual('my-path', resource.properties.source.relative_path)
        self.assertEqual('123', resource.properties.source.version)
        self.assertEqual('Java_11', resource.properties.source.runtime_version)
        self.assertEqual('test-option', resource.properties.source.jvm_options)

    def test_app_update_net_core_main_entry(self):
        deployment=self._get_deployment()
        deployment.properties.source.type = 'NetCoreZip'
        deployment.properties.source.runtime_version = 'NetCore_31'
        deployment.properties.source.net_core_main_entry_path = 'main-entry'
        self._execute('rg', 'asc', 'app', deployment=deployment, main_entry='test-entry')
        resource = self.patch_deployment_resource
        self.assertEqual('NetCoreZip', resource.properties.source.type)
        self.assertEqual('my-path', resource.properties.source.relative_path)
        self.assertEqual('123', resource.properties.source.version)
        self.assertEqual('NetCore_31', resource.properties.source.runtime_version)
        self.assertEqual('test-entry', resource.properties.source.net_core_main_entry_path)

    def test_app_update_settings_only(self):
        deployment=self._get_deployment()
        self._execute('rg', 'asc', 'app', deployment=deployment, env={'key':'value'})
        resource = self.patch_deployment_resource
        self.assertIsNone(resource.properties.source)
        self.assertEqual({'key':'value'}, resource.properties.deployment_settings.environment_variables)


class TestAppCreate(BasicTest):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.put_app_resource = None
        self.patch_app_resource = None
        self.put_deployment_resource = None

    def _get_basic_mock_client(self, sku='Standard'):
        client = super()._get_basic_mock_client(sku=sku)
        client.apps.get.side_effect = [
            ResourceNotFoundError('App not found'),
            mock.MagicMock()
        ]
        client.deployments.list.return_value = []
        return client

    def _execute(self, *args, **kwargs):
        client = kwargs.pop('client', None) or self._get_basic_mock_client()
        app_create(_get_test_cmd(), client, *args, **kwargs)
        call_args = client.apps.begin_create_or_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(4, len(call_args[0][0]))
        self.assertEqual(args[0:3], call_args[0][0][0:3])
        self.put_app_resource = call_args[0][0][3]

        call_args = client.deployments.begin_create_or_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(5, len(call_args[0][0]))
        self.assertEqual(args[0:3] + ('default',), call_args[0][0][0:4])
        self.put_deployment_resource = call_args[0][0][4]

        call_args = client.apps.begin_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(4, len(call_args[0][0]))
        self.assertEqual(args[0:3], call_args[0][0][0:3])
        self.patch_app_resource = call_args[0][0][3]

    def test_app_create_happy_path(self):
        self._execute('rg', 'asc', 'app', cpu='1', memory='1Gi', instance_count=1)
        resource = self.put_deployment_resource
        self.assertEqual('Jar', resource.properties.source.type)
        self.assertEqual('Java_8', resource.properties.source.runtime_version)
        self.assertEqual('<default>', resource.properties.source.relative_path)

    def test_app_create_with_netcore(self):
        self._execute('rg', 'asc', 'app', cpu='1', memory='1Gi', instance_count=1, runtime_version='NetCore_31')
        resource = self.put_deployment_resource
        self.assertEqual('NetCoreZip', resource.properties.source.type)
        self.assertEqual('NetCore_31', resource.properties.source.runtime_version)
        self.assertEqual('<default>', resource.properties.source.relative_path)

    def test_app_create_in_enterprise(self):
        client = self._get_basic_mock_client(sku='Enterprise')
        self._execute('rg', 'asc', 'app', cpu='1', memory='1Gi', instance_count=1, client=client)
        resource = self.put_deployment_resource
        self.assertEqual('BuildResult', resource.properties.source.type)
        self.assertEqual('<default>', resource.properties.source.build_result_id)


class TestDeploymentCreate(BasicTest):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.put_deployment_resource = None

    def _get_basic_mock_client(self, sku='Standard', *deployments):
        client = super()._get_basic_mock_client(sku=sku)
        client.deployments.list.return_value = deployments
        return client

    def _execute(self, *args, **kwargs):
        client = kwargs.pop('client', None) or self._get_basic_mock_client()
        deployment_create(_get_test_cmd(), client, *args, **kwargs)

        call_args = client.deployments.begin_create_or_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(5, len(call_args[0][0]))
        self.assertEqual(args[0:4], call_args[0][0][0:4])
        self.put_deployment_resource = call_args[0][0][4]

    def test_create_deployment_without_active(self):
        client = self._get_basic_mock_client()
        self._execute('rg', 'asc', 'app', 'green', cpu='2', memory='2Gi', instance_count=3, client=client)
        resource = self.put_deployment_resource
        self.assertEqual(3, resource.sku.capacity)
        self.assertEqual('2', resource.properties.deployment_settings.resource_requests.cpu)
        self.assertEqual('2Gi', resource.properties.deployment_settings.resource_requests.memory)

    def test_create_deployment_with_active(self):
        deployment = self._get_deployment()
        deployment.properties.active = True
        deployment.properties.source.jvm_options = 'test-options'
        client = self._get_basic_mock_client('Standard', deployment)
        self._execute('rg', 'asc', 'app', 'green', cpu=None, memory=None, instance_count=None, client=client)
        resource = self.put_deployment_resource
        self.assertEqual(2, resource.sku.capacity)
        self.assertEqual('2', resource.properties.deployment_settings.resource_requests.cpu)
        self.assertEqual('2Gi', resource.properties.deployment_settings.resource_requests.memory)
        self.assertEqual('test-options', resource.properties.source.jvm_options)
        self.assertEqual('Java_11', resource.properties.source.runtime_version)
        self.assertEqual('<default>', resource.properties.source.relative_path)
        self.assertEqual('Jar', resource.properties.source.type)
    
    def test_create_deployment_with_active_override(self):
        deployment = self._get_deployment()
        deployment.properties.active = True
        deployment.properties.source.jvm_options = 'test-options'
        client = self._get_basic_mock_client('Standard', deployment)
        self._execute('rg', 'asc', 'app', 'green', cpu='3', memory=None, instance_count=5, runtime_version='NetCore_31', client=client)
        resource = self.put_deployment_resource
        self.assertEqual(5, resource.sku.capacity)
        self.assertEqual('3', resource.properties.deployment_settings.resource_requests.cpu)
        self.assertEqual('2Gi', resource.properties.deployment_settings.resource_requests.memory)
        self.assertEqual('NetCoreZip', resource.properties.source.type)
        self.assertEqual('NetCore_31', resource.properties.source.runtime_version)
        self.assertEqual('<default>', resource.properties.source.relative_path)
    
    def test_create_deployment_with_active_is_source(self):
        deployment = self._get_deployment()
        deployment.properties.active = True
        deployment.properties.source.type = 'Source'
        client = self._get_basic_mock_client('Standard', deployment)
        self._execute('rg', 'asc', 'app', 'green', cpu='3', memory=None, instance_count=5, client=client)
        resource = self.put_deployment_resource
        self.assertEqual(5, resource.sku.capacity)
        self.assertEqual('3', resource.properties.deployment_settings.resource_requests.cpu)
        self.assertEqual('2Gi', resource.properties.deployment_settings.resource_requests.memory)
        self.assertIsNone(resource.properties.source.jvm_options)
        self.assertEqual('Jar', resource.properties.source.type)
        self.assertEqual('Java_11', resource.properties.source.runtime_version)
        self.assertEqual('<default>', resource.properties.source.relative_path)
    
    def test_create_deployment_with_active_is_container(self):
        deployment = self._get_deployment()
        deployment.properties.active = True
        deployment.properties.source.type = 'Container'
        client = self._get_basic_mock_client('Standard', deployment)
        self._execute('rg', 'asc', 'app', 'green', cpu='3', memory=None, instance_count=5, client=client)
        resource = self.put_deployment_resource
        self.assertEqual(5, resource.sku.capacity)
        self.assertEqual('3', resource.properties.deployment_settings.resource_requests.cpu)
        self.assertEqual('2Gi', resource.properties.deployment_settings.resource_requests.memory)
        self.assertIsNone(resource.properties.source.jvm_options)
        self.assertEqual('Jar', resource.properties.source.type)
        self.assertEqual('Java_11', resource.properties.source.runtime_version)
        self.assertEqual('<default>', resource.properties.source.relative_path)