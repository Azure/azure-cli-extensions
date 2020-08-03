# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import unittest.mock as mock
from contextlib import contextmanager

import azure.cli.core.telemetry as telemetry

from azext_ai_did_you_mean_this._const import (
    EXTENSION_NAME,
    UNEXPECTED_ERROR_STR
)
from azext_ai_did_you_mean_this.telemetry import (
    FaultType,
    TelemetryProperty,
    _extension_telemetry_manager,
    get_correlation_id,
    get_property,
    get_subscription_id,
    set_properties,
    set_property)
from azext_ai_did_you_mean_this.tests.latest.aladdin_scenario_test_base import patch_ids
from azext_ai_did_you_mean_this.tests.latest.data.telemetry_property import CoreTelemetryProperty
from azext_ai_did_you_mean_this.tests.latest.mock.const import (
    MOCK_INVALID_CORE_CLI_VERSION,
    MOCK_UUID,
    TELEMETRY_EXTENSION_EVENT_NAME,
    TELEMETRY_FAULT_EVENT_NAME,
    TELEMETRY_IS_ENABLED_PATCH_TARGET
)
from azext_ai_did_you_mean_this.tests.latest.mock.extension_telemetry_session import (
    ExtensionTelemetryMockSession,
    UnknownException
)


@contextmanager
def patch_is_telemetry_enabled(value: bool):
    with mock.patch(TELEMETRY_IS_ENABLED_PATCH_TARGET, lambda: value):
        yield None


class TestExtensionTelemetry(unittest.TestCase):
    def setUp(self):
        super().setUp()

        for patch in [patch_ids]:
            patch(self)

        self.test_command = 'vm create'
        self.test_version = MOCK_INVALID_CORE_CLI_VERSION
        self.default_exception_msg = 'foo'

    def test_telemetry_is_disabled_if_consent_is_not_given(self):
        with patch_is_telemetry_enabled(False):
            self.assertIsNone(get_correlation_id())
            self.assertIsNone(get_correlation_id())
            self.assertIsNone(set_property(TelemetryProperty.Command, self.test_command))
            self.assertIsNone(get_property(TelemetryProperty.Command))
            # verify that data is not set internally when we do not have the consent to do so
            self.assertNotIn(TelemetryProperty.Command, _extension_telemetry_manager.properties)

    def test_telemetry_properties_are_set_if_consent_is_given(self):
        with patch_is_telemetry_enabled(True):
            self.assertEqual(get_correlation_id(), MOCK_UUID)
            self.assertEqual(get_subscription_id(), MOCK_UUID)

            set_property(TelemetryProperty.Command, self.test_command)
            self.assertEqual(get_property(TelemetryProperty.Command), self.test_command)

            self.assertIn(TelemetryProperty.Command, _extension_telemetry_manager.properties)

    def test_can_set_multiple_properties_with_and_without_consent(self):
        props = {
            TelemetryProperty.Command: self.test_command,
            TelemetryProperty.CoreVersion: self.test_version
        }

        with patch_is_telemetry_enabled(True):
            set_properties(props)
            for prop, value in props.items():
                self.assertEqual(get_property(prop), value)

        with patch_is_telemetry_enabled(False):
            set_properties(props)
            for prop in props:
                self.assertIsNone(get_property(prop))

    def test_exception_is_caught_by_extension_telemetry_session(self):
        with self.assertRaises(UnknownException):
            with ExtensionTelemetryMockSession() as session:
                raise UnknownException(self.default_exception_msg)

        expected_fault_type = FaultType.UnexpectedError

        # test that the fault information was set correctly
        self.assertIsNotNone(session.fault)
        self.assertEqual(session.fault.name, TELEMETRY_FAULT_EVENT_NAME)
        self.assertEqual(session.fault.fault_type, expected_fault_type)
        self.assertEqual(session.fault.summary, UNEXPECTED_ERROR_STR)
        self.assertIsInstance(session.fault.exception, UnknownException)

        # test that the exception was added to CLI telemetry
        self.assertIsNotNone(session.fault.details)
        details = session.fault.details
        self.assertEqual(details.fault_type, expected_fault_type)
        self.assertEqual(details.description, UNEXPECTED_ERROR_STR)
        self.assertEqual(details.correlation_id, MOCK_UUID)
        self.assertEqual(details.message, self.default_exception_msg)

        # test that an extension event is added to CLI telemetry
        self.assertIsNotNone(session.extension_event)
        self.assertEqual(session.extension_event.name, TELEMETRY_EXTENSION_EVENT_NAME)
        self.assertEqual(session.extension_event.extension_name, EXTENSION_NAME)
        self.assertDictEqual(
            session.extension_event.properties,
            {
                CoreTelemetryProperty.EXTENSION_NAME: EXTENSION_NAME,
                CoreTelemetryProperty.CORRELATION_ID: MOCK_UUID
            }
        )

    def test_no_telemetry_is_logged_without_user_consent(self):
        with ExtensionTelemetryMockSession(enable_telemetry=False) as session:
            pass

        self.assertIsNone(session.fault)
        self.assertIsNone(session.extension_event)
        self.assertDictEqual(_extension_telemetry_manager.properties, dict())
