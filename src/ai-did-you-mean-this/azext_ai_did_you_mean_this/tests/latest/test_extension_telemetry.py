# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
import unittest.mock as mock
from contextlib import contextmanager

import azure.cli.core.telemetry as telemetry

from azext_ai_did_you_mean_this._telemetry import FaultType, TelemetryProperty
from azext_ai_did_you_mean_this.tests.latest.aladdin_scenario_test_base import \
    patch_ids
from azext_ai_did_you_mean_this.tests.latest.extension_telemetry_test_base import \
    ExtensionTelemetryTest
from azext_ai_did_you_mean_this.tests.latest.mock.extension_telemetry_session import \
    ExtensionTelemetryMockSession


class TestExtensionTelemetry(ExtensionTelemetryTest):
    def setUp(self):
        super().setUp()

        for patch in [patch_ids]:
            patch(self)

        self.mock_command = 'vm create'
        self.unexpected_error_exception_msg = 'foo'

    def test_telemetry_is_disabled_if_consent_is_not_given(self):
        with ExtensionTelemetryMockSession(enable_telemetry=False):
            self.assertCorrelationIdIsNone()
            self.assertSubscriptionIdIsNone()

            self.set_telemetry_property(TelemetryProperty.Command, self.mock_command, validate=True)

    def test_telemetry_properties_are_set_if_consent_is_given(self):
        with ExtensionTelemetryMockSession(enable_telemetry=True):
            self.assertCorrelationIdEquals(self.mock_uuid)
            self.assertSubscriptionIdEquals(self.mock_uuid)

            self.set_telemetry_property(TelemetryProperty.Command, self.mock_command, validate=True)

    def test_can_set_multiple_properties_with_and_without_consent(self):
        properties = {
            TelemetryProperty.Command: self.mock_command,
            TelemetryProperty.CoreVersion: self.mock_version
        }

        with ExtensionTelemetryMockSession(enable_telemetry=True):
            self.set_telemetry_properties(properties, validate=True)

        with ExtensionTelemetryMockSession(enable_telemetry=False):
            self.set_telemetry_properties(properties, validate=True)

    def test_exception_is_caught_by_extension_telemetry_session(self):
        msg = self.unexpected_error_exception_msg

        with self.assertRaises(self.unexpected_error_cls):
            with ExtensionTelemetryMockSession() as session:
                raise self.unexpected_error_cls(msg)

        self.assertTelemetryFaultEventIsSet(
            session.fault,
            FaultType.UnexpectedError,
            self.unexpected_error_summary,
            self.unexpected_error_cls,
            msg
        )

        self.assertTelemetryExtensionEventIsSet(session.extension_event)

    def test_no_telemetry_is_logged_without_user_consent(self):
        with ExtensionTelemetryMockSession(enable_telemetry=False) as session:
            pass

        self.assertIsNone(session.fault)
        self.assertIsNone(session.extension_event)
        self.assertDictEqual(self.telemetry_properties, dict())
