# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import unittest
from argparse import Namespace
from azure.cli.core import AzCommandsLoader
from azure.cli.core.commands import AzCliCommand
from azure.cli.core.mock import DummyCli
from azure.cli.core.util import CLIError
from .common.test_utils import get_test_cmd
from ..._validators import (validate_tracing_parameters_asc_create, validate_tracing_parameters_asc_update,
                            validate_java_agent_parameters, validate_app_insights_parameters)


class TestAppInsightsValidators(unittest.TestCase):
    def test_validate_tracing_parameters_asc_create_param_conflict_1(self):
        ns = Namespace(app_insights="fake-app-insights-name",
                       app_insights_key=None,
                       sampling_rate=None,
                       disable_app_insights=True)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
                        "can not be set with '--disable-app-insights'." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_2(self):
        ns = Namespace(app_insights=None,
                       app_insights_key="0000-0000-0000-0000",
                       sampling_rate=None,
                       disable_app_insights=True)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
                        "can not be set with '--disable-app-insights'." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_3(self):
        ns = Namespace(app_insights=None,
                       app_insights_key=None,
                       sampling_rate=50,
                       disable_app_insights=True)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
                        "can not be set with '--disable-app-insights'." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_4(self):
        ns = Namespace(app_insights="fake-app-insights-name",
                       app_insights_key=None,
                       sampling_rate=50,
                       disable_app_insights=True)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
                        "can not be set with '--disable-app-insights'." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_5(self):
        ns = Namespace(app_insights="fake-app-insights-name",
                       app_insights_key="0000-000-0000-0000",
                       sampling_rate=None,
                       disable_app_insights=None)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(ns)
        self.assertTrue("Conflict detected: '--app-insights' and '--app-insights-key' "
                        "can not be set at the same time." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_6(self):
        ns = Namespace(app_insights="fake-app-insights-name",
                       app_insights_key="0000-000-0000-0000",
                       sampling_rate=None,
                       disable_app_insights=False)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(ns)
        self.assertTrue("Conflict detected: '--app-insights' and '--app-insights-key' "
                        "can not be set at the same time." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_7(self):
        ns = Namespace(app_insights="",
                       app_insights_key=None,
                       sampling_rate=None,
                       disable_app_insights=None)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(ns)
        self.assertTrue("Invalid value: '--app-insights' can not be empty." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_8(self):
        ns = Namespace(app_insights=None,
                       app_insights_key=None,
                       sampling_rate=-1,
                       disable_app_insights=None)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(ns)
        self.assertTrue("Invalid value: Sampling Rate must be in the range [0,100]." in str(context.exception))

    def test_validate_tracing_parameters_asc_create_param_conflict_9(self):
        ns = Namespace(app_insights=None,
                       app_insights_key=None,
                       sampling_rate=101,
                       disable_app_insights=None)
        with self.assertRaises(CLIError) as context:
            validate_tracing_parameters_asc_create(ns)
        self.assertTrue("Invalid value: Sampling Rate must be in the range [0,100]." in str(context.exception))

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
            validate_app_insights_parameters(get_test_cmd(), ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
                        "can not be set with '--disable'." in str(context.exception))

    def test_validate_app_insights_parameters_2(self):
        ns = Namespace(app_insights=None,
                       app_insights_key=None,
                       sampling_rate=50,
                       disable=True)
        with self.assertRaises(CLIError) as context:
            validate_app_insights_parameters(get_test_cmd(), ns)
        self.assertTrue("Conflict detected: '--app-insights' or '--app-insights-key' or '--sampling-rate' "
                        "can not be set with '--disable'." in str(context.exception))

    def test_validate_app_insights_parameters_3(self):
        ns = Namespace(app_insights=None,
                       app_insights_key=None,
                       sampling_rate=None,
                       disable=False)
        with self.assertRaises(CLIError) as context:
            validate_app_insights_parameters(get_test_cmd(), ns)
        self.assertTrue("Invalid value: nothing is updated for application insights." in str(context.exception))
