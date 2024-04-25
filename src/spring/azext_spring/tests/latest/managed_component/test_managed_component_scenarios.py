# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest

from azure.cli.testsdk import (ScenarioTest, record_only, live_only)
from azure.cli.testsdk.base import ExecutionResult
from requests import Response
from ....managed_components.managed_component import get_component
from ...._utils import BearerAuth


try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock


class TestingWriter:
    def __init__(self, buffer):
        self.buffer = buffer

    def write(self, data, end='', file=None):
        self.buffer.append(data)


class ManagedComponentTest(ScenarioTest):
    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_component_list(self, is_enterprise_tier_mock, cf_spring_mock):
        self.kwargs.update({
            'serviceName': 'asae-name',
            'rg': 'resource-group',
        })

        cf_spring_mock.return_value = mock.MagicMock()

        is_enterprise_tier_mock.return_value = True
        result: ExecutionResult = self.cmd('spring component list -s {serviceName} -g {rg}')
        self.assertTrue(isinstance(result.get_output_in_json(), list))
        component_list: list = result.get_output_in_json()

        for e in component_list:
            self.assertTrue(isinstance(e, dict))
            e: dict = e
            self.assertTrue("name" in e)
            component_obj = get_component(e["name"])
            self.assertIsNotNone(component_obj)

    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_acs_component_instance_list(self, is_enterprise_tier_mock, cf_spring_mock):
        self.kwargs.update({
            'serviceName': 'asae-name',
            'rg': 'resource-group',
            'component': 'application-configuration-service'
        })

        is_enterprise_tier_mock.return_value = True

        client = mock.MagicMock()
        client.configuration_services.get.return_value = self._get_mocked_acs_gen2()
        cf_spring_mock.return_value = client

        # ACS (Gen1 or Gen2) is enabled in service instance.
        result: ExecutionResult = self.cmd('spring component instance list -s {serviceName} -g {rg} -c {component}')
        output = result.get_output_in_json()
        self.assertTrue(type(output), list)
        self.assertEqual(2, len(output))
        for e in output:
            self.assertTrue(isinstance(e, dict))
            self.assertTrue("name" in e)
            instance: str = e["name"]
            self.assertTrue(instance.startswith("application-configuration-service"))

    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_flux_component_instance_list(self, is_enterprise_tier_mock, client_factory_mock):
        self.kwargs.update({
            'serviceName': 'asae-name',
            'rg': 'resource-group',
            'component': 'flux-source-controller',
        })

        is_enterprise_tier_mock.return_value = True

        client = mock.MagicMock()
        client.configuration_services.get.return_value = self._get_mocked_acs_gen2()
        client_factory_mock.return_value = client

        # flux is a subcomponent of ACS Gen2, make sure it's enabled in service instance.
        result: ExecutionResult = self.cmd('spring component instance list -s {serviceName} -g {rg} -c {component}')
        output = result.get_output_in_json()
        self.assertTrue(type(output), list)
        self.assertEqual(1, len(output))
        for e in output:
            self.assertTrue(isinstance(e, dict))
            self.assertTrue("name" in e)
            instance: str = e["name"]
            self.assertTrue(instance.startswith("fluxcd-source-controller"))

    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_scg_component_instance_list(self, is_enterprise_tier_mock, client_factory_mock):
        self.kwargs.update({
            'serviceName': 'asae-name',
            'rg': 'resource-group',
            'component': 'spring-cloud-gateway',
        })

        is_enterprise_tier_mock.return_value = True

        client = mock.MagicMock()
        client.gateways.get.return_value = self._get_mocked_scg()
        client_factory_mock.return_value = client

        # scg is a subcomponent of Spring Cloud Gateway, need to enable it first.
        result: ExecutionResult = self.cmd('spring component instance list -s {serviceName} -g {rg} -c {component}')
        output = result.get_output_in_json()
        self.assertTrue(type(output), list)
        self.assertEqual(3, len(output))
        for e in output:
            self.assertTrue(isinstance(e, dict))
            self.assertTrue("name" in e)
            instance: str = e["name"]
            self.assertTrue(instance.startswith("asc-scg-default"))

    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_scg_operator_component_instance_list(self, is_enterprise_tier_mock, client_factory_mock):
        self.kwargs.update({
            'serviceName': 'asae-name',
            'rg': 'resource-group',
            'component': 'spring-cloud-gateway-operator'
        })

        is_enterprise_tier_mock.return_value = True

        client = mock.MagicMock()
        client.gateways.get.return_value = self._get_mocked_scg()
        client_factory_mock.return_value = client

        # scg operator is a subcomponent of Spring Cloud Gateway, need to enable it first.
        result: ExecutionResult = self.cmd('spring component instance list -s {serviceName} -g {rg} -c {component}')
        output = result.get_output_in_json()
        self.assertTrue(type(output), list)
        self.assertEqual(2, len(output))
        for e in output:
            self.assertTrue(isinstance(e, dict))
            self.assertTrue("name" in e)
            instance: str = e["name"]
            self.assertTrue(instance.startswith("scg-operator"))

    @mock.patch('azext_spring.log_stream.log_stream_operations.iter_lines', autospec=True)
    @mock.patch('azext_spring.log_stream.log_stream_operations.requests', autospec=True)
    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_hostname', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_bearer_auth', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_default_writer', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_prefix_writer', autospec=True)
    def test_acs_log_stream(self, _get_prefix_writer_mock, _get_default_writer_mock, _get_bearer_auth_mock,
                            _get_hostname_mock, is_enterprise_tier_mock, client_factory_mock, requests_mock,
                            iter_lines_mock):
        command_std_out = []
        _get_default_writer_mock.return_value = TestingWriter(command_std_out)
        _get_prefix_writer_mock.return_value = TestingWriter(command_std_out)

        _get_bearer_auth_mock.return_value = BearerAuth("fake-bearer-token")
        asae_name = "asae-name"
        _get_hostname_mock.return_value = "{}.asc-test.net".format(asae_name)

        is_enterprise_tier_mock.return_value = True

        client = mock.MagicMock()
        client.configuration_services.get.return_value = self._get_mocked_acs_gen2()
        client_factory_mock.return_value = client

        response = Response()
        response.status_code = 200
        requests_mock.get.return_value = response

        lines = []
        for i in range(50):
            line = "Log line No.{}\n".format(i)
            line = line.encode('utf-8')
            lines.append(line)
        iter_lines_mock.return_value = lines

        self.kwargs.update({
            'serviceName': asae_name,
            'rg': 'resource-group',
            'component': 'application-configuration-service'
        })

        self.cmd('spring component logs -s {serviceName} -g {rg} -n {component} --all-instances --lines 50')
        self.assertEqual(len(command_std_out), 100)

    @mock.patch('azext_spring.log_stream.log_stream_operations.iter_lines', autospec=True)
    @mock.patch('azext_spring.log_stream.log_stream_operations.requests', autospec=True)
    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_hostname', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_bearer_auth', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_default_writer', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_prefix_writer', autospec=True)
    def test_flux_log_stream(self, _get_prefix_writer_mock, _get_default_writer_mock, _get_bearer_auth_mock,
                             _get_hostname_mock, is_enterprise_tier_mock, client_factory_mock, requests_mock,
                             iter_lines_mock):
        command_std_out = []
        _get_default_writer_mock.return_value = TestingWriter(command_std_out)
        _get_prefix_writer_mock.return_value = TestingWriter(command_std_out)

        _get_bearer_auth_mock.return_value = BearerAuth("fake-bearer-token")
        asae_name = "asae-name"
        _get_hostname_mock.return_value = "{}.asc-test.net".format(asae_name)

        is_enterprise_tier_mock.return_value = True

        client = mock.MagicMock()
        client.configuration_services.get.return_value = self._get_mocked_acs_gen2()
        client_factory_mock.return_value = client

        response = Response()
        response.status_code = 200
        requests_mock.get.return_value = response

        lines = []
        for i in range(50):
            line = "Log line No.{}\n".format(i)
            line = line.encode('utf-8')
            lines.append(line)
        iter_lines_mock.return_value = lines

        self.kwargs.update({
            'serviceName': asae_name,
            'rg': 'resource-group',
            'component': 'flux-source-controller'
        })

        self.cmd('spring component logs -s {serviceName} -g {rg} -n {component} --all-instances --lines 50')
        self.assertEqual(len(command_std_out), 50)

    @mock.patch('azext_spring.log_stream.log_stream_operations.iter_lines', autospec=True)
    @mock.patch('azext_spring.log_stream.log_stream_operations.requests', autospec=True)
    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_hostname', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_bearer_auth', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_default_writer', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_prefix_writer', autospec=True)
    def test_scg_log_stream(self, _get_prefix_writer_mock, _get_default_writer_mock, _get_bearer_auth_mock,
                            _get_hostname_mock, is_enterprise_tier_mock, client_factory_mock, requests_mock,
                            iter_lines_mock):
        command_std_out = []
        _get_default_writer_mock.return_value = TestingWriter(command_std_out)
        _get_prefix_writer_mock.return_value = TestingWriter(command_std_out)

        _get_bearer_auth_mock.return_value = BearerAuth("fake-bearer-token")
        asae_name = "asae-name"
        _get_hostname_mock.return_value = "{}.asc-test.net".format(asae_name)

        is_enterprise_tier_mock.return_value = True

        client = mock.MagicMock()
        client.gateways.get.return_value = self._get_mocked_scg()
        client_factory_mock.return_value = client

        response = Response()
        response.status_code = 200
        requests_mock.get.return_value = response

        lines = []
        for i in range(50):
            line = "Log line No.{}\n".format(i)
            line = line.encode('utf-8')
            lines.append(line)
        iter_lines_mock.return_value = lines

        self.kwargs.update({
            'serviceName': asae_name,
            'rg': 'resource-group',
            'component': 'spring-cloud-gateway'
        })

        self.cmd('spring component logs -s {serviceName} -g {rg} -n {component} --all-instances --lines 50')
        self.assertEqual(len(command_std_out), 150)

    @mock.patch('azext_spring.log_stream.log_stream_operations.iter_lines', autospec=True)
    @mock.patch('azext_spring.log_stream.log_stream_operations.requests', autospec=True)
    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_hostname', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_bearer_auth', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_default_writer', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_prefix_writer', autospec=True)
    def test_scg_operator_log_stream(self, _get_prefix_writer_mock, _get_default_writer_mock, _get_bearer_auth_mock,
                                     _get_hostname_mock, is_enterprise_tier_mock, client_factory_mock, requests_mock,
                                     iter_lines_mock):
        command_std_out = []
        _get_default_writer_mock.return_value = TestingWriter(command_std_out)
        _get_prefix_writer_mock.return_value = TestingWriter(command_std_out)

        _get_bearer_auth_mock.return_value = BearerAuth("fake-bearer-token")
        asae_name = "asae-name"
        _get_hostname_mock.return_value = "{}.asc-test.net".format(asae_name)

        is_enterprise_tier_mock.return_value = True

        client = mock.MagicMock()
        client.gateways.get.return_value = self._get_mocked_scg()
        client_factory_mock.return_value = client

        response = Response()
        response.status_code = 200
        requests_mock.get.return_value = response

        lines = []
        for i in range(50):
            line = "Log line No.{}\n".format(i)
            line = line.encode('utf-8')
            lines.append(line)
        iter_lines_mock.return_value = lines

        self.kwargs.update({
            'serviceName': asae_name,
            'rg': 'resource-group',
            'component': 'spring-cloud-gateway-operator'
        })

        self.cmd('spring component logs -s {serviceName} -g {rg} -n {component} --all-instances --lines 50')
        self.assertEqual(len(command_std_out), 100)

    @mock.patch('azext_spring.log_stream.log_stream_operations.iter_lines', autospec=True)
    @mock.patch('azext_spring.log_stream.log_stream_operations.requests', autospec=True)
    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_hostname', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_bearer_auth', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_default_writer', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_prefix_writer', autospec=True)
    def test_log_stream_without_instance_info_1(self, _get_prefix_writer_mock, _get_default_writer_mock,
                                                _get_bearer_auth_mock, _get_hostname_mock, is_enterprise_tier_mock,
                                                client_factory_mock, requests_mock, iter_lines_mock):
        command_std_out = []
        _get_default_writer_mock.return_value = TestingWriter(command_std_out)
        _get_prefix_writer_mock.return_value = TestingWriter(command_std_out)

        _get_bearer_auth_mock.return_value = BearerAuth("fake-bearer-token")
        asae_name = "asae-name"
        _get_hostname_mock.return_value = "{}.asc-test.net".format(asae_name)

        is_enterprise_tier_mock.return_value = True

        client = mock.MagicMock()
        client.gateways.get.return_value = self._get_mocked_scg()
        client_factory_mock.return_value = client

        response = Response()
        response.status_code = 200
        requests_mock.get.return_value = response

        lines = []
        for i in range(50):
            line = "Log line No.{}\n".format(i)
            line = line.encode('utf-8')
            lines.append(line)
        iter_lines_mock.return_value = lines

        self.kwargs.update({
            'serviceName': asae_name,
            'rg': 'resource-group',
            'component': 'spring-cloud-gateway-operator'
        })

        self.cmd('spring component logs -s {serviceName} -g {rg} -n {component} --lines 50')
        self.assertEqual(len(command_std_out), 0)

    @mock.patch('azext_spring.log_stream.log_stream_operations.iter_lines', autospec=True)
    @mock.patch('azext_spring.log_stream.log_stream_operations.requests', autospec=True)
    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_hostname', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_bearer_auth', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_default_writer', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_prefix_writer', autospec=True)
    def test_log_stream_without_instance_info_1(self, _get_prefix_writer_mock, _get_default_writer_mock,
                                                _get_bearer_auth_mock, _get_hostname_mock, is_enterprise_tier_mock,
                                                client_factory_mock, requests_mock, iter_lines_mock):
        command_std_out = []
        _get_default_writer_mock.return_value = TestingWriter(command_std_out)
        _get_prefix_writer_mock.return_value = TestingWriter(command_std_out)

        _get_bearer_auth_mock.return_value = BearerAuth("fake-bearer-token")
        asae_name = "asae-name"
        _get_hostname_mock.return_value = "{}.asc-test.net".format(asae_name)

        is_enterprise_tier_mock.return_value = True

        client = mock.MagicMock()
        client.gateways.get.return_value = self._get_mocked_single_instance_scg()
        client_factory_mock.return_value = client

        response = Response()
        response.status_code = 200
        requests_mock.get.return_value = response

        lines = []
        for i in range(50):
            line = "Log line No.{}\n".format(i)
            line = line.encode('utf-8')
            lines.append(line)
        iter_lines_mock.return_value = lines

        self.kwargs.update({
            'serviceName': asae_name,
            'rg': 'resource-group',
            'component': 'spring-cloud-gateway-operator'
        })

        self.cmd('spring component logs -s {serviceName} -g {rg} -n {component} --lines 50')
        self.assertEqual(len(command_std_out), 50)

    @mock.patch('azext_spring.commands.cf_spring', autospec=True)
    @mock.patch('azext_spring.log_stream.log_stream_operations.iter_lines', autospec=True)
    @mock.patch('azext_spring.log_stream.log_stream_operations.requests', autospec=True)
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_hostname', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations.get_bearer_auth', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_default_writer', autospec=True)
    @mock.patch('azext_spring.managed_components.managed_component_operations._get_prefix_writer', autospec=True)
    def test_log_stream_only_by_instance_name(self, _get_prefix_writer_mock, _get_default_writer_mock,
                                              _get_bearer_auth_mock, _get_hostname_mock, is_enterprise_tier_mock,
                                              requests_mock, iter_lines_mock, cf_spring_mock):
        instance_names = [
            "application-configuration-service-6fb669cfc5-z6tq9",
            "fluxcd-source-controller-675dbdd58b-8sk75",
            "asc-scg-default-0",
            "scg-operator-6d8895c44b-wcngh"
        ]

        for i in instance_names:

            command_std_out = []
            _get_default_writer_mock.return_value = TestingWriter(command_std_out)
            _get_prefix_writer_mock.return_value = TestingWriter(command_std_out)

            _get_bearer_auth_mock.return_value = BearerAuth("fake-bearer-token")
            asae_name = "asae-name"
            _get_hostname_mock.return_value = "{}.asc-test.net".format(asae_name)

            is_enterprise_tier_mock.return_value = True

            cf_spring_mock.return_value = mock.MagicMock()

            response = Response()
            response.status_code = 200
            requests_mock.get.return_value = response

            lines = []
            for i in range(50):
                line = "Log line No.{}\n".format(i)
                line = line.encode('utf-8')
                lines.append(line)
            iter_lines_mock.return_value = lines

            self.kwargs.update({
                'serviceName': asae_name,
                'rg': 'resource-group',
                'instance': i
            })

            self.cmd('spring component logs -s {serviceName} -g {rg} -i {instance} --lines 50')
            self.assertEqual(len(command_std_out), 50)

    def _get_mocked_acs_gen2(self):
        resource = mock.MagicMock()
        instance_1 = mock.MagicMock()
        instance_2 = mock.MagicMock()
        instance_3 = mock.MagicMock()
        resource.properties = mock.MagicMock()
        resource.properties.instances = [instance_1, instance_2, instance_3]
        instance_1.name = "application-configuration-service-11111111-1111"
        instance_2.name = "application-configuration-service-11111111-2222"
        instance_3.name = "fluxcd-source-controller-11111111-3333"
        return resource

    def _get_mocked_scg(self):
        resource = mock.MagicMock()
        resource.properties = mock.MagicMock()
        instance_1 = mock.MagicMock()
        instance_2 = mock.MagicMock()
        instance_3 = mock.MagicMock()
        resource.properties.instances = [instance_1, instance_2, instance_3]
        instance_1.name = "asc-scg-default-0"
        instance_2.name = "asc-scg-default-1"
        instance_3.name = "asc-scg-default-2"
        resource.properties.operator_properties = mock.MagicMock()
        operator_1 = mock.MagicMock()
        operator_2 = mock.MagicMock()
        resource.properties.operator_properties.instances = [operator_1, operator_2]
        operator_1.name = "scg-operator-74947fdcb-8hj85"
        operator_2.name = "scg-operator-74947fdcb-askdj"
        return resource

    def _get_mocked_single_instance_scg(self):
        resource = mock.MagicMock()
        resource.properties = mock.MagicMock()
        instance_1 = mock.MagicMock()
        resource.properties.instances = [instance_1]
        instance_1.name = "asc-scg-default-0"
        resource.properties.operator_properties = mock.MagicMock()
        operator_1 = mock.MagicMock()
        resource.properties.operator_properties.instances = [operator_1]
        operator_1.name = "scg-operator-74947fdcb-8hj85"
        return resource
