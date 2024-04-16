# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import re
import unittest
import os
from azure.cli.core.azclierror import ResourceNotFoundError
from knack.util import CLIError
from msrestazure.tools import resource_id
from ...vendored_sdks.appplatform.v2024_05_01_preview import models
from ..._utils import _get_sku_name
from ...app import (app_create, app_update, app_deploy, deployment_create)
from ...custom import (app_set_deployment, app_unset_deployment,
                       deployment_enable_remote_debugging,
                       deployment_disable_remote_debugging,
                       deployment_get_remote_debugging,
                       domain_update, domain_unbind)

try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock

from .common.test_utils import get_test_cmd
from azure.cli.core.mock import DummyCli
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand

from knack.log import get_logger

logger = get_logger(__name__)
TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


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


class TestSetActiveDeploy(BasicTest):
    def test_blue_green_enterprise(self):
        client = self._get_basic_mock_client(sku='Enterprise')
        app_set_deployment(get_test_cmd(), client, 'rg', 'asc', 'app', 'default')
        call_args = client.apps.begin_set_active_deployments.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(4, len(call_args[0][0]))
        request = call_args[0][0][3]
        self.assertEqual('default', request.active_deployment_names[0])

    def test_unset_active_enterprise(self):
        client = self._get_basic_mock_client(sku='Enterprise')
        app_unset_deployment(get_test_cmd(), client, 'rg', 'asc', 'app')
        call_args = client.apps.begin_set_active_deployments.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(4, len(call_args[0][0]))
        request = call_args[0][0][3]
        self.assertEqual(0, len(request.active_deployment_names))

    def test_blue_green_standard(self):
        client = self._get_basic_mock_client(sku='Standard')
        app_set_deployment(get_test_cmd(), client, 'rg', 'asc', 'app', 'default')
        call_args = client.apps.begin_set_active_deployments.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(4, len(call_args[0][0]))
        active_deployment_collection = call_args[0][0][3]
        self.assertEqual('default', active_deployment_collection.active_deployment_names[0])

    def test_unset_active_standard(self):
        client = self._get_basic_mock_client(sku='Standard')
        app_unset_deployment(get_test_cmd(), client, 'rg', 'asc', 'app')
        call_args = client.apps.begin_set_active_deployments.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(4, len(call_args[0][0]))
        active_deployment_collection = call_args[0][0][3]
        self.assertEqual(0, len(active_deployment_collection.active_deployment_names))


class TestAppDeploy_Patch(BasicTest):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.patch_deployment_resource = None

    def _get_basic_mock_client(self, sku='Standard'):
        client = super()._get_basic_mock_client(sku=sku)
        client.apps.get_resource_upload_url.return_value = self._get_upload_info()
        client.deployments.get.return_value = self._get_deployment()
        return client

    def _get_upload_info(self):
        resp = mock.MagicMock()
        resp.relative_path = 'my-relative-path'
        resp.upload_url = 'https://mystorage.file.core.windows.net/root/my-relative-path?sv=2018-03-28&sr=f&sig=my-fake-pass&se=2021-12-28T06%3A43%3A17Z&sp=w'
        return resp

    def _execute(self, *args, **kwargs):
        client = kwargs.pop('client', None) or self._get_basic_mock_client()
        app_deploy(get_test_cmd(), client, *args, **kwargs)

        call_args = client.deployments.begin_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(5, len(call_args[0][0]))
        self.assertEqual(args[0:3] + ('default',), call_args[0][0][0:4])
        self.patch_deployment_resource = call_args[0][0][4]

    @mock.patch('azext_spring._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), artifact_path='my-path')
        resource = self.patch_deployment_resource
        self.assertEqual('Jar', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('Java_11', resource.properties.source.runtime_version)
        # self.assertIsNone(resource.sku)

    @mock.patch('azext_spring._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy_with_runtime_version(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), artifact_path='my-path',
                      runtime_version='Java_8')
        resource = self.patch_deployment_resource
        self.assertEqual('Jar', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('Java_8', resource.properties.source.runtime_version)

    @mock.patch('azext_spring._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy_war(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), artifact_path='my-path/test.war',
                      runtime_version='Java_8', server_version='Tomcat_10')
        resource = self.patch_deployment_resource
        self.assertEqual('War', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('Java_8', resource.properties.source.runtime_version)
        self.assertEqual('Tomcat_10', resource.properties.source.server_version)

    @mock.patch('azext_spring._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy_net(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), artifact_path='my-path',
                      runtime_version='NetCore_31', main_entry='test')
        resource = self.patch_deployment_resource
        self.assertEqual('NetCoreZip', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('NetCore_31', resource.properties.source.runtime_version)
        self.assertEqual('test', resource.properties.source.net_core_main_entry_path)

    @mock.patch('azext_spring._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy_net_with_jvm_options(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        deployment = self._get_deployment()
        deployment.properties.source.jvm_options = 'test-options'
        self._execute('rg', 'asc', 'app', deployment=deployment, artifact_path='my-path', runtime_version='NetCore_31',
                      main_entry='test')
        resource = self.patch_deployment_resource
        self.assertEqual('NetCoreZip', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('NetCore_31', resource.properties.source.runtime_version)
        self.assertEqual('test', resource.properties.source.net_core_main_entry_path)

    @mock.patch('azext_spring._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_continous_deploy_net(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        deployment = self._get_deployment()
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

    @mock.patch('azext_spring._deployment_uploadable_factory.FolderUpload.upload_and_build')
    def test_app_deploy_source(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), source_path='my-path')
        resource = self.patch_deployment_resource
        self.assertEqual('Source', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('Java_11', resource.properties.source.runtime_version)

    @mock.patch('azext_spring._deployment_uploadable_factory.FolderUpload.upload_and_build')
    def test_app_continous_deploy_source(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        deployment = self._get_deployment()
        deployment.properties.source.type = 'Container'
        deployment.properties.source.relative_path = 'my-path'
        deployment.properties.source.version = '123'
        deployment.properties.source.artifact_selector = 'test'
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), source_path='my-path')
        resource = self.patch_deployment_resource
        self.assertEqual('Source', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('Java_11', resource.properties.source.runtime_version)


class TestAppDeploy_Enterprise_Patch(BasicTest):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.patch_deployment_resource = None
        self.put_build_resource = None
        self.result_id = None

    def _get_basic_mock_client(self, sku='Standard'):
        client = super()._get_basic_mock_client(sku=sku)
        client.build_service.get_resource_upload_url.return_value = self._get_upload_info()
        client.build_service.create_or_update_build.return_value = self._get_build_resource()
        client.build_service.get_build_result.side_effect = [self._get_result_resource()]
        client.build_service.get_build_result_log.side_effect = ResourceNotFoundError('Log not found')
        client.deployments.get.return_value = self._get_deployment()
        return client

    def _get_result_resource(self, status='Succeeded'):
        resp = mock.MagicMock()
        resp.properties.provisioning_state = status
        return resp

    def _get_build_resource(self):
        self.result_id = resource_id(
            subscription='00000000-0000-0000-0000-000000000000',
            resource_group='rg',
            name='asc',
            namespace='Microsoft.AppPlatform',
            type='Spring',
            child_type_1='buildService',
            child_name_1='default',
            child_type_2='builds',
            child_name_2='builder',
            child_type_3='results',
            child_name_3='my-result',
        )
        resp = mock.MagicMock()
        resp.properties.triggered_build_result.id = self.result_id
        return resp

    def _get_upload_info(self):
        resp = mock.MagicMock()
        resp.relative_path = 'my-relative-path'
        resp.upload_url = 'https://mystorage.file.core.windows.net/root/my-relative-path?sv=2018-03-28&sr=f&sig=my-fake-pass&se=2021-12-28T06%3A43%3A17Z&sp=w'
        return resp

    def verify_build_args(self, client, *args):
        build_args = client.build_service.create_or_update_build.call_args_list

        if build_args and build_args[0]:
            self.assertEqual(1, len(build_args))
            self.assertEqual(5, len(build_args[0][0]))
            self.assertEqual(args[0:2] + ('default',) + (args[2] + '-default',), build_args[0][0][0:4])
            self.put_build_resource = build_args[0][0][4]

    def _execute(self, *args, **kwargs):
        client = kwargs.pop('client', None) or self._get_basic_mock_client()
        app_deploy(get_test_cmd(), client, *args, **kwargs)

        self.verify_build_args(client, *args)

        call_args = client.deployments.begin_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(5, len(call_args[0][0]))
        self.assertEqual(args[0:3] + ('default',), call_args[0][0][0:4])
        self.patch_deployment_resource = call_args[0][0][4]

    def _get_deployment(self):
        deployment = super()._get_deployment()
        deployment.properties.source.type = 'BuildResult'
        deployment.properties.source.build_result_id = 'my-id'
        deployment.properties.source.relative_path = None
        deployment.properties.source.runtime_version = None
        deployment.properties.source.version = '123'
        deployment.properties.source.jvm_options = None
        deployment.sku.tier = 'Enterprise'
        deployment.sku.name = 'E0'
        deployment.properties.deployment_settings.addon_configs = None
        return deployment

    @mock.patch('azext_spring._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy_enterprise(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        deployment = self._get_deployment()
        self._execute('rg', 'asc', 'app', deployment=deployment, artifact_path='my-path',
                      config_file_patterns='my-pattern')
        resource = self.patch_deployment_resource
        self.assertEqual('BuildResult', resource.properties.source.type)
        self.assertEqual(self.result_id, resource.properties.source.build_result_id)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual({'applicationConfigurationService': {'configFilePatterns': 'my-pattern'}},
                         resource.properties.deployment_settings.addon_configs)

    @mock.patch('azext_spring._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy_build_enterprise(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        deployment = self._get_deployment()
        self._execute('rg', 'asc', 'app', deployment=deployment, artifact_path='my-path',
                      build_env={'BP_JVM_VERSION': '8.*'}, build_cpu='2', build_memory='4Gi')
        resource = self.put_build_resource
        self.assertEqual({"BP_JVM_VERSION": "8.*"}, resource.properties.env)
        self.assertEqual('2', resource.properties.resource_requests.cpu)
        self.assertEqual('4Gi', resource.properties.resource_requests.memory)

    @mock.patch('azext_spring._deployment_uploadable_factory.FolderUpload.upload_and_build')
    def test_app_deploy_folder_enterprise(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        deployment = self._get_deployment()
        self._execute('rg', 'asc', 'app', deployment=deployment, source_path='my-path')
        resource = self.patch_deployment_resource
        self.assertEqual('BuildResult', resource.properties.source.type)
        self.assertEqual(self.result_id, resource.properties.source.build_result_id)
        self.assertIsNone(resource.properties.source.version)

    @mock.patch('azext_spring._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy_waiting_enterprise(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        client = self._get_basic_mock_client()
        client.build_service.get_build_result.side_effect = [
            self._get_result_resource(status='Queueing'),
            self._get_result_resource(status='Building'),
            self._get_result_resource(status='Succeeded')
        ]
        deployment = self._get_deployment()
        self._execute('rg', 'asc', 'app', deployment=deployment, artifact_path='my-path')
        resource = self.patch_deployment_resource
        self.assertEqual('BuildResult', resource.properties.source.type)
        self.assertEqual(self.result_id, resource.properties.source.build_result_id)
        self.assertIsNone(resource.properties.source.version)

    @mock.patch('azext_spring._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy_failed_enterprise(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        client = self._get_basic_mock_client()
        client.build_service.get_build_result.side_effect = [
            self._get_result_resource(status='Queueing'),
            self._get_result_resource(status='Building'),
            self._get_result_resource(status='Failed')
        ]
        deployment = self._get_deployment()
        with self.assertRaisesRegexp(CLIError, 'Failed to build container image'):
            self._execute('rg', 'asc', 'app', deployment=deployment, artifact_path='my-path', client=client)


class TestAppDeploy_Put(BasicTest):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.put_deployment_resource = None

    def _get_basic_mock_client(self, sku='Standard'):
        client = super()._get_basic_mock_client(sku=sku)
        client.apps.get_resource_upload_url.return_value = self._get_upload_info()
        client.deployments.get.return_value = self._get_deployment()
        return client

    def _get_upload_info(self):
        resp = mock.MagicMock()
        resp.relative_path = 'my-relative-path'
        resp.upload_url = 'https://mystorage.file.core.windows.net/root/my-relative-path?sv=2018-03-28&sr=f&sig=my-fake-pass&se=2021-12-28T06%3A43%3A17Z&sp=w'
        return resp

    def _execute(self, *args, **kwargs):
        client = kwargs.pop('client', None) or self._get_basic_mock_client()
        app_deploy(get_test_cmd(), client, *args, **kwargs)

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

    @mock.patch('azext_spring._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy_war_from_container(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        deployment = self._get_deployment()
        deployment.properties.source.type = 'Container'
        deployment.properties.source.custom_container = mock.MagicMock()
        deployment.properties.source.relative_path = None
        deployment.properties.source.runtime_version = None
        deployment.properties.source.version = '123'
        self._execute('rg', 'asc', 'app', deployment=deployment, artifact_path='my-path/test.war',
                      server_version='Tomcat_9')
        resource = self.put_deployment_resource
        self.assertEqual('War', resource.properties.source.type)
        self.assertEqual('my-relative-path', resource.properties.source.relative_path)
        self.assertIsNone(resource.properties.source.version)
        self.assertEqual('Java_11', resource.properties.source.runtime_version)
        self.assertEqual('Tomcat_9', resource.properties.source.server_version)
        self.assertEqual('2', resource.properties.deployment_settings.resource_requests.cpu)
        self.assertEqual('2Gi', resource.properties.deployment_settings.resource_requests.memory)
        self.assertEqual(2, resource.sku.capacity)

    @mock.patch('azext_spring._deployment_uploadable_factory.FileUpload.upload_and_build')
    def test_app_deploy_jar_from_container(self, file_mock):
        file_mock.return_value = mock.MagicMock()
        deployment = self._get_deployment()
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
        self.assertEqual('Java_11', resource.properties.source.runtime_version)
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
        app_update(get_test_cmd(), client, *args, **kwargs)

        call_args = client.deployments.begin_update.call_args_list
        if len(call_args):
            self.assertEqual(1, len(call_args))
            self.assertEqual(5, len(call_args[0][0]))
            self.assertEqual(args[0:3] + ('default',), call_args[0][0][0:4])
            self.patch_deployment_resource = call_args[0][0][4]
        else:
            self.patch_deployment_resource = None

        call_args = client.apps.begin_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(4, len(call_args[0][0]))
        self.assertEqual(args[0:3], call_args[0][0][0:3])
        self.patch_app_resource = call_args[0][0][3]

    def test_app_update_without_deployment(self):
        self._execute('rg', 'asc', 'app', assign_endpoint=True)

        self.assertIsNone(self.patch_deployment_resource)
        resource = self.patch_app_resource
        self.assertEqual(True, resource.properties.public)

    def test_invalid_app_update_deployment_settings_without_deployment(self):
        with self.assertRaisesRegexp(CLIError, '--jvm-options cannot be set when there is no active deployment.'):
            self._execute('rg', 'asc', 'app', jvm_options='test-option')

    def test_app_update_jvm_options(self):
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), jvm_options='test-option')
        resource = self.patch_deployment_resource
        self.assertEqual('Jar', resource.properties.source.type)
        self.assertEqual('my-path', resource.properties.source.relative_path)
        self.assertEqual('123', resource.properties.source.version)
        self.assertEqual('Java_11', resource.properties.source.runtime_version)
        self.assertEqual('test-option', resource.properties.source.jvm_options)

    def test_app_set_termination_grace_period_seconds(self):
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), termination_grace_period_seconds=88)
        resource = self.patch_deployment_resource
        self.assertEqual(88, resource.properties.deployment_settings.termination_grace_period_seconds)

    def test_app_disable_probes(self):
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), enable_liveness_probe=False,
                      enable_readiness_probe=False, enable_startup_probe=False)
        resource = self.patch_deployment_resource
        self.assertEqual(True, resource.properties.deployment_settings.liveness_probe.disable_probe)
        self.assertEqual(True, resource.properties.deployment_settings.readiness_probe.disable_probe)
        self.assertEqual(True, resource.properties.deployment_settings.startup_probe.disable_probe)

    def test_app_enable_probe(self):
        py_path = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(py_path, 'files/probe.json').replace("\\", "/")
        self._execute('rg', 'asc', 'app', deployment=self._get_deployment(), enable_liveness_probe=True,
                      liveness_probe_config=file_path)
        resource = self.patch_deployment_resource
        self.assertEqual(False, resource.properties.deployment_settings.liveness_probe.disable_probe)
        self.assertEqual(30, resource.properties.deployment_settings.liveness_probe.initial_delay_seconds)
        self.assertEqual(1, resource.properties.deployment_settings.liveness_probe.success_threshold)
        self.assertEqual(1, resource.properties.deployment_settings.liveness_probe.timeout_seconds)
        self.assertEqual(10, resource.properties.deployment_settings.liveness_probe.period_seconds)
        self.assertEqual(30, resource.properties.deployment_settings.liveness_probe.failure_threshold)

    def test_app_update_net_core_main_entry(self):
        deployment = self._get_deployment()
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
        deployment = self._get_deployment()
        self._execute('rg', 'asc', 'app', deployment=deployment, env={'key': 'value'})
        resource = self.patch_deployment_resource
        self.assertIsNone(resource.properties.source)
        self.assertEqual({'key': 'value'}, resource.properties.deployment_settings.environment_variables)

    def test_app_update_in_enterprise(self):
        client = self._get_basic_mock_client(sku='Enterprise')
        deployment = self._get_deployment(sku='Enterprise')
        deployment.properties.deployment_settings.addon_configs = {
            'applicationConfigurationService': {'configFilePatterns': 'my-pattern'}}
        self._execute('rg', 'asc', 'app', deployment=deployment, client=client, config_file_patterns='updated-pattern')
        resource = self.patch_deployment_resource
        self.assertEqual({'applicationConfigurationService': {'configFilePatterns': 'updated-pattern'}},
                         resource.properties.deployment_settings.addon_configs)

    def test_app_update_clear_jvm_option_in_enterprise(self):
        client = self._get_basic_mock_client(sku='Enterprise')
        deployment = self._get_deployment(sku='Enterprise')
        deployment.properties.deployment_settings.environment_variables = {"JAVA_OPTS": "test_options", "foo": "bar"}
        self._execute('rg', 'asc', 'app', deployment=deployment, client=client, jvm_options='')
        resource = self.patch_deployment_resource
        self.assertEqual({"foo": "bar"}, resource.properties.deployment_settings.environment_variables)

    def test_app_update_in_enterprise_with_new_set_env(self):
        client = self._get_basic_mock_client(sku='Enterprise')
        deployment = self._get_deployment(sku='Enterprise')
        deployment.properties.deployment_settings.environment_variables = {"JAVA_OPTS": "test_options", "foo": "bar"}
        self._execute('rg', 'asc', 'app', deployment=deployment, client=client, env={'key': 'value'})
        resource = self.patch_deployment_resource
        self.assertEqual({'key': 'value'}, resource.properties.deployment_settings.environment_variables)

    def test_app_update_env_and_jvm_in_enterprise(self):
        client = self._get_basic_mock_client(sku='Enterprise')
        deployment = self._get_deployment(sku='Enterprise')
        deployment.properties.deployment_settings.environment_variables = {"JAVA_OPTS": "test_options", "foo": "bar"}
        self._execute('rg', 'asc', 'app', deployment=deployment, client=client, jvm_options='another-option',
                      env={'key': 'value'})
        resource = self.patch_deployment_resource
        self.assertEqual({'JAVA_OPTS': 'another-option', 'key': 'value'},
                         resource.properties.deployment_settings.environment_variables)

    def test_app_update_custom_container_deployment(self):
        deployment = self._get_deployment()
        deployment.properties.source.type = 'Container'
        deployment.properties.source.custom_container.container_image = 'my-image'
        self._execute('rg', 'asc', 'app', deployment=deployment, env={'key': 'value'})
        resource = self.patch_deployment_resource
        self.assertIsNone(resource.properties.source)
        self.assertEqual({'key': 'value'}, resource.properties.deployment_settings.environment_variables)

    def test_app_update_custom_container_deployment_with_invalid_source(self):
        deployment = self._get_deployment()
        deployment.properties.source.type = 'Container'
        deployment.properties.source.custom_container.container_image = 'my-image'
        self._execute('rg', 'asc', 'app', deployment=deployment, env={'key': 'value'}, runtime_version='Java_11')
        resource = self.patch_deployment_resource
        self.assertIsNone(resource.properties.source)
        self.assertEqual({'key': 'value'}, resource.properties.deployment_settings.environment_variables)

    def test_steeltoe_app_cannot_set_jvm_options(self):
        deployment = self._get_deployment()
        deployment.properties.source.type = 'NetCoreZip'
        deployment.properties.source.runtime_version = 'NetCore_31'
        deployment.properties.source.net_core_main_entry_path = 'main-entry'
        with self.assertRaisesRegexp(CLIError, '--jvm-options cannot be set when --runtime-version is NetCore_31.'):
            self._execute('rg', 'asc', 'app', jvm_options='test-option', deployment=deployment)

    def test_vnet_public_endpoint(self):
        deployment = self._get_deployment()

        self._execute('rg', 'asc', 'app', assign_public_endpoint=True, deployment=deployment)
        resource = self.patch_app_resource
        self.assertTrue(resource.properties.vnet_addons.public_endpoint)

        self._execute('rg', 'asc', 'app', deployment=deployment)
        resource = self.patch_app_resource
        self.assertIsNone(resource.properties.vnet_addons)

        self._execute('rg', 'asc', 'app', assign_public_endpoint=False, deployment=deployment)
        resource = self.patch_app_resource
        self.assertFalse(resource.properties.vnet_addons.public_endpoint)

    def test_client_auth(self):
        deployment = self._get_deployment()
        self._execute('rg', 'asc', 'app', client_auth_certs=['my-cert-id'], deployment=deployment)
        resource = self.patch_app_resource
        self.assertEqual(['my-cert-id'], resource.properties.ingress_settings.client_auth.certificates)

    def test_app_i2a_tls(self):
        deployment = self._get_deployment()

        self._execute('rg', 'asc', 'app', enable_ingress_to_app_tls=True, deployment=deployment)
        resource = self.patch_app_resource
        self.assertTrue(resource.properties.enable_end_to_end_tls)

        self._execute('rg', 'asc', 'app', deployment=deployment)
        resource = self.patch_app_resource
        self.assertIsNone(resource.properties.enable_end_to_end_tls)

        self._execute('rg', 'asc', 'app', enable_ingress_to_app_tls=False, deployment=deployment)
        resource = self.patch_app_resource
        self.assertFalse(resource.properties.enable_end_to_end_tls)

    def test_update_workload_profile(self):
        self._execute('rg', 'asc', 'app', workload_profile='w2')
        resource = self.patch_app_resource
        self.assertEqual('w2', resource.properties.workload_profile_name)


class TestAppCreate(BasicTest):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)
        self.put_app_resource = None
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
        app_create(get_test_cmd(), client, *args, **kwargs)
        call_args = client.apps.begin_create_or_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(4, len(call_args[0][0]))
        self.assertEqual(args[0:3], call_args[0][0][0:3])
        self.put_app_resource = call_args[0][0][3]

        call_args = client.deployments.begin_create_or_update.call_args_list
        self.assertEqual(1, len(call_args))
        self.assertEqual(5, len(call_args[0][0]))
        self.put_deployment_resource = call_args[0][0][4]
        self.put_deployment_resource.name = call_args[0][0][3]

    def test_app_create_happy_path(self):
        self._execute('rg', 'asc', 'app', cpu='1', memory='1Gi', instance_count=1)
        resource = self.put_deployment_resource
        self.assertEqual('Jar', resource.properties.source.type)
        self.assertEqual('Java_11', resource.properties.source.runtime_version)
        self.assertEqual('<default>', resource.properties.source.relative_path)

    def test_app_create_with_netcore(self):
        self._execute('rg', 'asc', 'app', cpu='1', memory='1Gi', instance_count=1, runtime_version='NetCore_31')
        resource = self.put_deployment_resource
        self.assertEqual('NetCoreZip', resource.properties.source.type)
        self.assertEqual('NetCore_31', resource.properties.source.runtime_version)
        self.assertEqual('<default>', resource.properties.source.relative_path)

    def test_app_create_in_enterprise(self):
        client = self._get_basic_mock_client(sku='Enterprise')
        self._execute('rg', 'asc', 'app', cpu='500m', memory='2Gi', instance_count=1, client=client)
        resource = self.put_deployment_resource
        self.assertEqual('BuildResult', resource.properties.source.type)
        self.assertEqual('<default>', resource.properties.source.build_result_id)
        self.assertEqual('500m', resource.properties.deployment_settings.resource_requests.cpu)
        self.assertEqual('2Gi', resource.properties.deployment_settings.resource_requests.memory)

    def test_app_with_large_instance_count_enterprise(self):
        client = self._get_basic_mock_client(sku='Enterprise')
        with self.assertRaisesRegexp(CLIError, f'Invalid --instance-count, should be in range {re.escape("[")}1, 1000{re.escape("]")}'):
            self._execute('rg', 'asc', 'app', cpu='500m', memory='2Gi', instance_count=1001, client=client)

    def test_app_with_large_instance_count(self):
        with self.assertRaisesRegexp(CLIError, f'Invalid --instance-count, should be in range {re.escape("[")}1, 500{re.escape("]")}'):
            self._execute('rg', 'asc', 'app', cpu='500m', memory='2Gi', instance_count=501)

    def test_app_with_large_instance_count_basic(self):
        client = self._get_basic_mock_client(sku='Basic')
        with self.assertRaisesRegexp(CLIError, f'Invalid --instance-count, should be in range {re.escape("[")}1, 25{re.escape("]")}'):
            self._execute('rg', 'asc', 'app', cpu='500m', memory='2Gi', instance_count=26, client=client)

    def test_app_with_persistent_storage_enterprise(self):
        client = self._get_basic_mock_client(sku='Enterprise')
        with self.assertRaisesRegexp(CLIError,
                                     'Enterprise tier Spring instance does not support --enable-persistent-storage'):
            self._execute('rg', 'asc', 'app', cpu='500m', memory='2Gi', instance_count=1,
                          enable_persistent_storage=True, client=client)

    def test_app_binding_tanzu_components_enterprise(self):
        client = self._get_basic_mock_client(sku='Enterprise')
        default_service_registry_id = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.AppPlatform/Spring/asa/serviceRegistries/default'
        default_application_configuration_service_id = '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg/providers/Microsoft.AppPlatform/Spring/asa/configurationServices/default'
        self._execute('rg', 'asc', 'app', cpu='500m', memory='2Gi', instance_count=1,
                      bind_service_registry=default_service_registry_id,
                      bind_application_configuration_service=default_application_configuration_service_id,
                      client=client)
        addon_configs = self.put_app_resource.properties.addon_configs
        self.assertEqual(default_service_registry_id, addon_configs['serviceRegistry']['resourceId'])
        self.assertEqual(default_application_configuration_service_id,
                         addon_configs['applicationConfigurationService']['resourceId'])

    def test_app_with_persistent_storage(self):
        self._execute('rg', 'asc', 'app', cpu='500m', memory='2Gi', instance_count=1, enable_persistent_storage=True)
        resource = self.put_app_resource
        self.assertEqual(50, resource.properties.persistent_disk.size_in_gb)

    def test_app_with_persistent_storage_basic(self):
        client = self._get_basic_mock_client(sku='Basic')
        self._execute('rg', 'asc', 'app', cpu='500m', memory='2Gi', instance_count=1, enable_persistent_storage=True,
                      client=client)
        resource = self.put_app_resource
        self.assertEqual(1, resource.properties.persistent_disk.size_in_gb)

    def test_app_with_assign_public_endpoint(self):
        self._execute('rg', 'asc', 'app', cpu='500m', memory='2Gi', instance_count=1, assign_public_endpoint=True)
        resource = self.put_app_resource
        self.assertEqual(True, resource.properties.vnet_addons.public_endpoint)

    def test_app_with_ingress_settings(self):
        self._execute('rg', 'asc', 'app', instance_count=1, ingress_read_timeout=600, ingress_send_timeout=1200,
                      session_affinity='Cookie',
                      session_max_age=1000, backend_protocol='Default')
        resource = self.put_app_resource
        self.assertEqual(600, resource.properties.ingress_settings.read_timeout_in_seconds)
        self.assertEqual(1200, resource.properties.ingress_settings.send_timeout_in_seconds)
        self.assertEqual("Cookie", resource.properties.ingress_settings.session_affinity)
        self.assertEqual(1000, resource.properties.ingress_settings.session_cookie_max_age)
        self.assertEqual('Default', resource.properties.ingress_settings.backend_protocol)

    def test_app_with_client_auth(self):
        self._execute('rg', 'asc', 'app', instance_count=1, client_auth_certs=[])
        resource = self.put_app_resource
        self.assertIsNotNone(resource.properties.ingress_settings.client_auth.certificates)
        self.assertEqual(0, len(resource.properties.ingress_settings.client_auth.certificates))
        self._execute('rg', 'asc', 'app', instance_count=1, client_auth_certs=['cert1', 'cert2'])
        resource = self.put_app_resource
        self.assertIsNotNone(resource.properties.ingress_settings.client_auth.certificates)
        self.assertEqual(2, len(resource.properties.ingress_settings.client_auth.certificates))
        self._execute('rg', 'asc', 'app', instance_count=1)
        resource = self.put_app_resource
        self.assertIsNone(resource.properties.ingress_settings)

    def test_app_create_with_deployment_name(self):
        self._execute('rg', 'asc', 'app', cpu='1', memory='1Gi', instance_count=1, deployment_name='hello')
        resource = self.put_deployment_resource
        self.assertEqual('hello', resource.name)

    def test_create_vnet_public_endpoint(self):
        self._execute('rg', 'asc', 'app', assign_public_endpoint=True, cpu='1', memory='1Gi', instance_count=1)
        resource = self.put_app_resource
        self.assertTrue(resource.properties.vnet_addons.public_endpoint)

        self._execute('rg', 'asc', 'app', cpu='1', memory='1Gi', instance_count=1)
        resource = self.put_app_resource
        self.assertIsNone(resource.properties.vnet_addons)

        self._execute('rg', 'asc', 'app', assign_public_endpoint=False, cpu='1', memory='1Gi', instance_count=1)
        resource = self.put_app_resource
        self.assertFalse(resource.properties.vnet_addons.public_endpoint)

    def test_create_with_workload_profile(self):
        self._execute('rg', 'asc', 'app', cpu='1', memory='1Gi', instance_count=1, workload_profile='w1')
        resource = self.put_app_resource
        self.assertEqual('w1', resource.properties.workload_profile_name)


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
        deployment_create(get_test_cmd(), client, *args, **kwargs)

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
        self._execute('rg', 'asc', 'app', 'green', cpu='3', memory=None, instance_count=5, runtime_version='NetCore_31',
                      client=client)
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

    def test_create_deployment_with_ACS_Pattern_in_enterprise(self):
        deployment = self._get_deployment(sku='Enterprise')
        client = self._get_basic_mock_client('Enterprise', deployment)
        deployment.properties.deployment_settings.addon_configs = {
            'applicationConfigurationService': {'configFilePatterns': 'my-pattern'}}
        self._execute('rg', 'asc', 'app', 'green', client=client)
        resource = self.put_deployment_resource
        self.assertEqual({'applicationConfigurationService': {'configFilePatterns': 'my-pattern'}},
                         resource.properties.deployment_settings.addon_configs)


class RemoteDebugTest(BasicTest):
    def __init__(self, methodName: str = ...):
        super().__init__(methodName=methodName)

    def test_enable(self):
        client = self._get_basic_mock_client()
        deployment = self._get_deployment()
        deployment.name = 'my-deployment'
        deployment_enable_remote_debugging(
            get_test_cmd(),
            client,
            'rg', 'asc', 'app', 123, deployment)
        args = client.deployments.begin_enable_remote_debugging.call_args_list
        self.assertEqual(1, len(args))
        self.assertEqual(5, len(args[0][0]))
        self.assertEqual(('rg', 'asc', 'app', 'my-deployment'), args[0][0][0:4])
        resource = args[0][0][4]
        self.assertEqual(123, resource.port)

        client = self._get_basic_mock_client()
        deployment = self._get_deployment()
        deployment.name = 'my-deployment'
        deployment_enable_remote_debugging(
            get_test_cmd(),
            client,
            'rg', 'asc', 'app', deployment=deployment)
        args = client.deployments.begin_enable_remote_debugging.call_args_list
        resource = args[0][0][4]
        self.assertIsNone(resource.port)

    def test_disable(self):
        client = self._get_basic_mock_client()
        deployment = self._get_deployment()
        deployment.name = 'my-deployment'
        deployment_disable_remote_debugging(
            get_test_cmd(),
            client,
            'rg', 'asc', 'app', deployment)
        args = client.deployments.begin_disable_remote_debugging.call_args_list
        self.assertEqual(1, len(args))
        self.assertEqual(('rg', 'asc', 'app', 'my-deployment'), args[0][0])

    def test_get(self):
        client = self._get_basic_mock_client()
        deployment = self._get_deployment()
        deployment.name = 'my-deployment'
        deployment_get_remote_debugging(
            get_test_cmd(),
            client,
            'rg', 'asc', 'app', deployment)
        args = client.deployments.get_remote_debugging_config.call_args_list
        self.assertEqual(1, len(args))
        self.assertEqual(('rg', 'asc', 'app', 'my-deployment'), args[0][0])


class CustomDomainTests(BasicTest):

    def test_create_domain(self):
        client = self._get_basic_mock_client()
        domain_update(get_test_cmd(), client,
                      'rg', 'asc', 'app', 'my-domain')
        args = client.custom_domains.begin_create_or_update.call_args_list
        self.assertEqual(1, len(args))
        self.assertEqual(5, len(args[0][0]))
        self.assertEqual(('rg', 'asc', 'app', 'my-domain'), args[0][0][0:4])
        resource = args[0][0][4]
        self.assertIsNone(resource.properties.thumbprint)
        self.assertIsNone(resource.properties.cert_name)
        app_args = client.apps.begin_update.call_args_list
        self.assertEqual(0, len(app_args))

    def test_bind_cert(self):
        def _get_cert(*_, **__):
            resp = models.CertificateResource(
                properties=models.CertificateProperties()
            )
            resp.properties.thumbprint = 'my-thumbprint'
            return resp

        client = self._get_basic_mock_client()
        client.certificates.get = _get_cert
        domain_update(get_test_cmd(), client,
                      'rg', 'asc', 'app', 'my-domain', 'my-cert')
        args = client.custom_domains.begin_create_or_update.call_args_list
        self.assertEqual(1, len(args))
        self.assertEqual(5, len(args[0][0]))
        self.assertEqual(('rg', 'asc', 'app', 'my-domain'), args[0][0][0:4])
        resource = args[0][0][4]
        self.assertEqual('my-thumbprint', resource.properties.thumbprint)
        self.assertEqual('my-cert', resource.properties.cert_name)
        app_args = client.apps.begin_update.call_args_list
        self.assertEqual(0, len(app_args))

    def test_create_domain_with_ingress(self):
        client = self._get_basic_mock_client()
        domain_update(get_test_cmd(), client,
                      'rg', 'asc', 'app', 'my-domain', enable_ingress_to_app_tls=True)
        args = client.custom_domains.begin_create_or_update.call_args_list
        self.assertEqual(1, len(args))
        self.assertEqual(5, len(args[0][0]))
        self.assertEqual(('rg', 'asc', 'app', 'my-domain'), args[0][0][0:4])
        resource = args[0][0][4]
        self.assertIsNone(resource.properties.thumbprint)
        self.assertIsNone(resource.properties.cert_name)
        app_args = client.apps.begin_update.call_args_list
        self.assertEqual(1, len(app_args))
