# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from argparse import Namespace
from azure.cli.core import AzCommandsLoader
from azure.cli.core.azclierror import MutuallyExclusiveArgumentError
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.mock import DummyCli
from azure.cli.core.util import CLIError
from ..._validators import (validate_tracing_parameters_asc_create, validate_tracing_parameters_asc_update,
                            validate_java_agent_parameters, validate_app_insights_parameters)
try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock


free_mock_client = mock.MagicMock()

def _get_test_cmd():
    cli_ctx = DummyCli()
    cli_ctx.data['subscription_id'] = '00000000-0000-0000-0000-000000000000'
    loader = AzCommandsLoader(cli_ctx, resource_type='Microsoft.AppPlatform')
    cmd = AzCliCommand(loader, 'test', None)
    cmd.command_kwargs = {'resource_type': 'Microsoft.AppPlatform'}
    cmd.cli_ctx = cli_ctx
    return cmd


class TestAppInsightsValidators(unittest.TestCase):
    def test_validate_tracing_parameters_asc_create_param_conflict_1(self):
        ns = Namespace(app_insights="fake-app-insights-name",
                       app_insights_key=None,
                       sampling_rate=None,
                       disable_app_insights=True,
                       enable_java_agent=None)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(_get_test_cmd(), ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
                        "can not be set with '--disable-app-insights'." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_2(self):
        ns = Namespace(app_insights=None,
                       app_insights_key="0000-0000-0000-0000",
                       sampling_rate=None,
                       disable_app_insights=True,
                       enable_java_agent=None)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(_get_test_cmd(), ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
                        "can not be set with '--disable-app-insights'." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_3(self):
        ns = Namespace(app_insights=None,
                       app_insights_key=None,
                       sampling_rate=50,
                       disable_app_insights=True,
                       enable_java_agent=None)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(_get_test_cmd(), ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
                        "can not be set with '--disable-app-insights'." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_4(self):
        ns = Namespace(app_insights="fake-app-insights-name",
                       app_insights_key=None,
                       sampling_rate=50,
                       disable_app_insights=True,
                       enable_java_agent=None)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(_get_test_cmd(), ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
                        "can not be set with '--disable-app-insights'." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_5(self):
        ns = Namespace(app_insights="fake-app-insights-name",
                       app_insights_key="0000-000-0000-0000",
                       sampling_rate=None,
                       disable_app_insights=None,
                       enable_java_agent=None)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(_get_test_cmd(), ns)
        self.assertTrue("Conflict detected: '--app-insights' and '--app-insights-key' "
                        "can not be set at the same time." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_6(self):
        ns = Namespace(app_insights="fake-app-insights-name",
                       app_insights_key="0000-000-0000-0000",
                       sampling_rate=None,
                       disable_app_insights=False,
                       enable_java_agent=None)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(_get_test_cmd(), ns)
        self.assertTrue("Conflict detected: '--app-insights' and '--app-insights-key' "
                        "can not be set at the same time." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_7(self):
        ns = Namespace(app_insights="",
                       app_insights_key=None,
                       sampling_rate=None,
                       disable_app_insights=None,
                       enable_java_agent=None)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(_get_test_cmd(), ns)
        self.assertTrue("Invalid value: '--app-insights' can not be empty." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_8(self):
        ns = Namespace(app_insights=None,
                       app_insights_key=None,
                       sampling_rate=-1,
                       disable_app_insights=None,
                       enable_java_agent=None)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(_get_test_cmd(), ns)
        self.assertTrue("Invalid value: Sampling Rate must be in the range [0,100]." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_9(self):
        ns = Namespace(app_insights=None,
                       app_insights_key=None,
                       sampling_rate=101,
                       disable_app_insights=None,
                       enable_java_agent=None)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(_get_test_cmd(), ns)
        self.assertTrue("Invalid value: Sampling Rate must be in the range [0,100]." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_10(self):
        ns = Namespace(app_insights=None,
                       app_insights_key=None,
                       sampling_rate=5,
                       disable_app_insights=None,
                       enable_java_agent=False)
        with self.assertRaises(MutuallyExclusiveArgumentError) as context:
            validate_tracing_parameters_asc_create(_get_test_cmd(), ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' can not be set with '--disable-app-insights'." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_11(self):
        ns = Namespace(app_insights=None,
                       app_insights_key="0000-0000-0000",
                       sampling_rate=None,
                       disable_app_insights=None,
                       enable_java_agent=False)
        with self.assertRaises(MutuallyExclusiveArgumentError) as context:
            validate_tracing_parameters_asc_create(_get_test_cmd(), ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' can not be set with '--disable-app-insights'." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_12(self):
        ns = Namespace(app_insights="fale-app-insights-name",
                       app_insights_key=None,
                       sampling_rate=None,
                       disable_app_insights=None,
                       enable_java_agent=False)
        with self.assertRaises(MutuallyExclusiveArgumentError) as context:
            validate_tracing_parameters_asc_create(_get_test_cmd(), ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' can not be set with '--disable-app-insights'." in str(context.exception))

    def test_validate_tracing_parameters_asc_update_param_conflict_1(self):
        ns = Namespace(app_insights="fake-app-insights-name",
                       app_insights_key=None,
                       disable_app_insights=True)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_update(ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' "
                        "can not be set with '--disable-app-insights'." in str(context.exception))

    def test_validate_tracing_parameters_asc_update_param_conflict_2(self):
        ns = Namespace(app_insights=None,
                       app_insights_key="0000-000-0000-0000",
                       disable_app_insights=True)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_update(ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' "
                        "can not be set with '--disable-app-insights'." in str(context.exception))

    def test_validate_tracing_parameters_asc_update_param_conflict_3(self):
        ns = Namespace(app_insights="fake-app-insights-name",
                       app_insights_key="0000-000-0000-0000",
                       disable_app_insights=False)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_update(ns)
        self.assertTrue("Conflict detected: '--app-insights' and '--app-insights-key' "
                        "can not be set at the same time." in str(context.exception))

    def test_validate_java_agent_parameters(self):
        ns = Namespace(enable_java_agent=True,
                       disable_app_insights=True)
        with self.assertRaises(CLIError) as context:
            validate_java_agent_parameters(ns)
        self.assertTrue("Conflict detected: '--enable-java-agent' and '--disable-app-insights' "
                        "can not be set at the same time." in str(context.exception))

    def test_validate_app_insights_parameters_1(self):
        ns = Namespace(app_insights="fake-app-insights-name",
                       app_insights_key=None,
                       sampling_rate=None,
                       disable=True)
        with self.assertRaises(CLIError) as context:
            validate_app_insights_parameters(ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
                        "can not be set with '--disable'." in str(context.exception))

    def test_validate_app_insights_parameters_2(self):
        ns = Namespace(app_insights=None,
                       app_insights_key=None,
                       sampling_rate=50,
                       disable=True)
        with self.assertRaises(CLIError) as context:
            validate_app_insights_parameters(ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
                        "can not be set with '--disable'." in str(context.exception))

    def test_validate_app_insights_parameters_3(self):
        ns = Namespace(app_insights=None,
                       app_insights_key=None,
                       sampling_rate=None,
                       disable=False)
        with self.assertRaises(CLIError) as context:
            validate_app_insights_parameters(ns)
        self.assertTrue("Invalid value: nothing is updated for application insights." in str(context.exception))


class TestAppInsightsValidatorsForServiceCreate(unittest.TestCase):
    def _get_application_insights_client(ctx, type):
        application_insights_get_resource = mock.MagicMock()
        application_insights_get_resource.connection_string = 'fake-get-connection-string'

        free_mock_client.components.get.return_value = application_insights_get_resource

        return free_mock_client

    @mock.patch('azext_spring_cloud._app_insights.get_mgmt_service_client', _get_application_insights_client)
    def test_get_connection_string_from_app_insights_name_or_resource_id(self):
        ns = Namespace(app_insights="test-application-insights",
                       app_insights_key=None,
                       sampling_rate=None,
                       disable_app_insights=None,
                       enable_java_agent=None,
                       resource_group='rg')
        validate_tracing_parameters_asc_create(_get_test_cmd(), ns)
        self.assertEqual('fake-get-connection-string', ns.app_insights_key)
        self.assertIsNone(ns.app_insights)
