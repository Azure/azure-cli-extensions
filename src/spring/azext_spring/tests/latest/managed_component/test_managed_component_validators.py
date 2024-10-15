# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import unittest

from argparse import Namespace
from azure.cli.core import AzCommandsLoader
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.mock import DummyCli
from azure.cli.core.commands import AzCliCommand

from ..common.test_utils import get_test_cmd
from ....managed_components.managed_component import get_component
from ....managed_components.validators_managed_component import (validate_component_logs,
                                                                 validate_component_list,
                                                                 validate_instance_list)
from ...._clierror import NotSupportedPricingTierError

try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock


valid_component_names = [
    "application-configuration-service",
    "APPLICATION-configuration-service",
    "APPlication-configuration-service",
    "Application-configuration-serVIcE",
    "application-CONFIGuratioN-service",
    "flux-source-controller",
    "FLUX-source-controller",
    "flux-sOurce-controller",
    "flux-source-controllEr",
    "flux-source-controlleR",
    "spring-cloud-gateway",
    "SPrINg-cloud-gateway",
    "spring-cloud-gaTeway",
    "spring-cloud-Gateway",
    "spring-cloud-GATEWAY",
    "spring-cloud-gateway-operator",
    "spring-cloud-gateway-operatoR",
    "spring-cloud-gatewaY-operator",
    "spring-CLOUD-gateway-operator",
    "sprinG-cloud-gateway-operator"
]


invalid_component_names = [
    "app-configuration-service",
    "",
    "None",
    "flux"
]


class TestValidateComponentList(unittest.TestCase):
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_tier(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = False

        with self.assertRaises(NotSupportedPricingTierError):
            validate_component_list(get_test_cmd(), Namespace(resource_group="group", service="service"))

        is_enterprise_tier_mock.return_value = True
        validate_component_list(get_test_cmd(), Namespace(resource_group="group", service="service"))


class TestValidateComponentInstanceList(unittest.TestCase):
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_component_name(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        for c in valid_component_names:
            ns = Namespace(resource_group="group", service="service", component=c)
            validate_instance_list(get_test_cmd(), ns)
            component_obj = get_component(ns.component)
            self.assertIsNotNone(component_obj)

        for c in invalid_component_names:
            with self.assertRaises(InvalidArgumentValueError) as context:
                ns = Namespace(resource_group="group", service="service", component=c)
                validate_instance_list(get_test_cmd(), ns)

            self.assertTrue("is not supported" in str(context.exception))
            self.assertTrue("Supported components are:" in str(context.exception))

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_tier(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        ns = Namespace(resource_group="group", service="service", component="application-configuration-service")
        validate_instance_list(get_test_cmd(), ns)

        is_enterprise_tier_mock.return_value = False
        with self.assertRaises(NotSupportedPricingTierError):
            validate_instance_list(get_test_cmd(), ns)


class TestValidateComponentLogs(unittest.TestCase):
    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_mutual_exclusive_param(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        ns = Namespace(
            resource_group="group",
            service="service",
            all_instances=True,
            instance="fake-instance-name"
        )

        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_component_logs(get_test_cmd(), ns)

        self.assertEquals("--all-instances cannot be set together with --instance/-i.", str(context.exception))

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_required_param_missing(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        ns = Namespace(
            resource_group="group",
            service="service",
            all_instances=False,
            name=None,
            instance=None,
        )

        with self.assertRaises(InvalidArgumentValueError) as context:
            validate_component_logs(get_test_cmd(), ns)

        self.assertEquals("When --name/-n is not set, --instance/-i is required.", str(context.exception))

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_only_instance_name(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        ns = Namespace(
            resource_group="group",
            service="service",
            all_instances=False,
            name=None,
            instance="fake-instance-name",
            lines=50,
            limit=2048,
            since=None,
            max_log_requests=5
        )

        with self.assertLogs('cli.azext_spring.managed_components.validators_managed_component', 'WARNING') as cm:
            validate_component_logs(get_test_cmd(), ns)
        self.assertEquals(cm.output, ['WARNING:cli.azext_spring.managed_components.validators_managed_component:--instance/-i is specified without --name/-n, will try best effort get logs by instance.'])

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_valid_component_name(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        for n in valid_component_names:
            ns = Namespace(
                resource_group="group",
                service="service",
                all_instances=False,
                name=n,
                instance="fake-instance-name",
                lines=50,
                limit=2048,
                since=None,
                max_log_requests=5
            )
            validate_component_logs(get_test_cmd(), ns)

            component_obj = get_component(ns.name)
            self.assertIsNotNone(component_obj)

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_invalid_component_name(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_valid_log_lines(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        valid_log_lines = [1, 2, 5, 10, 99, 100, 200, 10000]

        for n in valid_component_names:
            for lines in valid_log_lines:
                ns = Namespace(
                    resource_group="group",
                    service="service",
                    all_instances=False,
                    name=n,
                    instance="fake-instance-name",
                    lines=lines,
                    limit=2048,
                    since=None,
                    max_log_requests=5
                )
                validate_component_logs(get_test_cmd(), ns)
                self.assertEquals(lines, ns.lines)

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_log_lines_too_small(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        for n in valid_component_names:
            ns = Namespace(
                resource_group="group",
                service="service",
                all_instances=False,
                name=n,
                instance="fake-instance-name",
                lines=-1,
                limit=2048,
                since=None
            )
            with self.assertRaises(InvalidArgumentValueError) as context:
                validate_component_logs(get_test_cmd(), ns)
            self.assertEquals('--lines must be in the range [1,10000]', str(context.exception))

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_log_lines_too_big(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        for n in valid_component_names:
            ns = Namespace(
                resource_group="group",
                service="service",
                all_instances=False,
                name=n,
                instance="fake-instance-name",
                lines=10001,
                limit=2048,
                since=None,
                max_log_requests=5
            )
            with self.assertLogs('cli.azext_spring.log_stream.log_stream_validators', 'ERROR') as cm:
                validate_component_logs(get_test_cmd(), ns)
            expect_error_msgs = ['ERROR:cli.azext_spring.log_stream.log_stream_validators:'
                                 '--lines can not be more than 10000, using 10000 instead']
            self.assertEquals(expect_error_msgs, cm.output)
            self.assertEquals(10000, ns.lines)

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_valid_log_since(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        valid_log_since = ['1h',
                           '1m', '2m', '5m', '10m', '11m', '20m', '30m', '40m', '50m', '59m', '60m',
                           '1s', '2s', '5s', '9s', '10s', '20s', '29s', '30s', '60s', '100s', '500s', '3000s', '3600s',
                           '1', '2', '5', '10', '20', '29', '30', '3000', '3600']

        for n in valid_component_names:
            for since in valid_log_since:
                ns = Namespace(
                    resource_group="group",
                    service="service",
                    all_instances=False,
                    name=n,
                    instance="fake-instance-name",
                    lines=10001,
                    limit=2048,
                    since=since,
                    max_log_requests=5
                )
                validate_component_logs(get_test_cmd(), ns)
                last = since[-1:]
                since_in_seconds = int(since[:-1]) if last in ("hms") else int(since)
                if last == 'h':
                    since_in_seconds = since_in_seconds * 3600
                elif last == 'm':
                    since_in_seconds = since_in_seconds * 60
                self.assertEquals(since_in_seconds, ns.since)

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_invalid_log_since(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        invalid_log_since = ['asdf1h', '1masdf', 'asdfe2m', 'asd5m', '1efef0m', '11mm']

        for n in valid_component_names:
            for since in invalid_log_since:
                ns = Namespace(
                    resource_group="group",
                    service="service",
                    all_instances=False,
                    name=n,
                    instance="fake-instance-name",
                    lines=10001,
                    limit=2048,
                    since=since
                )
                with self.assertRaises(InvalidArgumentValueError) as context:
                    validate_component_logs(get_test_cmd(), ns)
                self.assertEquals("--since contains invalid characters", str(context.exception))

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_log_since_too_big(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        invalid_log_since = ['2h', '61m', '3601s', '9000s', '9000']

        for n in valid_component_names:
            for since in invalid_log_since:
                ns = Namespace(
                    resource_group="group",
                    service="service",
                    all_instances=False,
                    name=n,
                    instance="fake-instance-name",
                    lines=10000,
                    limit=2048,
                    since=since
                )
                with self.assertRaises(InvalidArgumentValueError) as context:
                    validate_component_logs(get_test_cmd(), ns)
                self.assertEquals("--since can not be more than 1h", str(context.exception))

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_valid_log_limit(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        valid_log_limit = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]

        for n in valid_component_names:
            for limit in valid_log_limit:
                ns = Namespace(
                    resource_group="group",
                    service="service",
                    all_instances=False,
                    name=n,
                    instance="fake-instance-name",
                    lines=10000,
                    limit=limit,
                    since='1h',
                    max_log_requests=5
                )
                validate_component_logs(get_test_cmd(), ns)
                self.assertEquals(limit * 1024, ns.limit)

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_negative_log_limit(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        invalid_log_limit = [-1, -2, -3, -4, -10, -100, -1000]

        for n in valid_component_names:
            for limit in invalid_log_limit:
                ns = Namespace(
                    resource_group="group",
                    service="service",
                    all_instances=False,
                    name=n,
                    instance="fake-instance-name",
                    lines=10000,
                    limit=limit,
                    since='1h'
                )
                with self.assertRaises(InvalidArgumentValueError) as context:
                    validate_component_logs(get_test_cmd(), ns)
                self.assertEquals('--limit must be in the range [1,2048]', str(context.exception))

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_log_limit_too_big(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        invalid_log_limit = [2049, 2050, 3000, 3001, 10000, 20000, 100000]

        for n in valid_component_names:
            for limit in invalid_log_limit:
                ns = Namespace(
                    resource_group="group",
                    service="service",
                    all_instances=False,
                    name=n,
                    instance="fake-instance-name",
                    lines=10000,
                    limit=limit,
                    since='1h',
                    max_log_requests=5,
                )
                with self.assertLogs('cli.azext_spring.log_stream.log_stream_validators', 'ERROR') as cm:
                    validate_component_logs(get_test_cmd(), ns)
                error_msgs = ['ERROR:cli.azext_spring.log_stream.log_stream_validators:'
                              '--limit can not be more than 2048, using 2048 instead']
                self.assertEquals(error_msgs, cm.output)
                self.assertEquals(2048 * 1024, ns.limit)

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_tier(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = True

        ns = Namespace(
            resource_group="group",
            service="service",
            all_instances=False,
            name="application-configuration-service",
            instance="fake-instance-name",
            lines=10000,
            limit=2048,
            since='1h',
            max_log_requests=5
        )

        validate_component_logs(get_test_cmd(), ns)

    @mock.patch('azext_spring.managed_components.validators_managed_component.is_enterprise_tier', autospec=True)
    def test_invalid_tier(self, is_enterprise_tier_mock):
        is_enterprise_tier_mock.return_value = False

        ns = Namespace(
            resource_group="group",
            service="service",
            all_instances=False,
            name="application-configuration-service",
            instance="fake-instance-name",
            lines=10000,
            limit=2048,
            since='1h',
            max_log_requests=5,
        )

        with self.assertRaises(NotSupportedPricingTierError) as context:
            validate_component_logs(get_test_cmd(), ns)
        self.assertEquals("Only enterprise tier service instance is supported in this command.", str(context.exception))
