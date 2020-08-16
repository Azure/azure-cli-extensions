# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from typing import Any, Dict

import azure.cli.core.telemetry as core_telemetry

import azext_ai_did_you_mean_this._telemetry as extension_telemetry
from azext_ai_did_you_mean_this._const import (
    EXTENSION_NAME,
    UNEXPECTED_ERROR_STR
)
from azext_ai_did_you_mean_this._telemetry import (
    FaultType,
    TelemetryProperty
)
from azext_ai_did_you_mean_this.tests.latest.data.telemetry_property import \
    CoreTelemetryProperty
from azext_ai_did_you_mean_this.tests.latest.mock.const import (
    MOCK_INVALID_CORE_CLI_VERSION,
    MOCK_UUID,
    TELEMETRY_EXTENSION_EVENT_NAME,
    TELEMETRY_FAULT_EVENT_NAME
)
from azext_ai_did_you_mean_this.tests.latest.mock.extension_telemetry_session import (
    ExtensionTelemetryEvent,
    Fault,
    UnexpectedError
)


class ExtensionTelemetryTest(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.mock_uuid = MOCK_UUID
        self.mock_version = MOCK_INVALID_CORE_CLI_VERSION

        self.unexpected_error_cls = UnexpectedError
        self.unexpected_error_summary = UNEXPECTED_ERROR_STR

        self.extension_name = EXTENSION_NAME
        self.extension_event_name = TELEMETRY_EXTENSION_EVENT_NAME
        self.fault_event_name = TELEMETRY_FAULT_EVENT_NAME

    @property
    def is_telemetry_enabled(self):
        return core_telemetry.is_telemetry_enabled()

    @property
    def telemetry_properties(self):
        # pylint: disable=protected-access
        return extension_telemetry._extension_telemetry_manager.properties

    def assertTelemetryPropertyIsSet(self, telemetry_property: TelemetryProperty):
        self.assertIn(telemetry_property, self.telemetry_properties)

    def assertTelemetryPropertyIsNotSet(self, telemetry_property: TelemetryProperty):
        self.assertNotIn(telemetry_property, self.telemetry_properties)
        self.assertIsNone(extension_telemetry.get_property(telemetry_property))

    def assertTelemetryPropertyValueEquals(self, telemetry_property: TelemetryProperty, value: str):
        self.assertTelemetryPropertyIsSet(telemetry_property)
        self.assertEqual(extension_telemetry.get_property(telemetry_property), value)

    def assertCorrelationIdEquals(self, value: str):
        self.assertEqual(extension_telemetry.get_correlation_id(), value)

    def assertCorrelationIdIsNone(self):
        self.assertIsNone(extension_telemetry.get_correlation_id())

    def assertSubscriptionIdEquals(self, value: str):
        self.assertEqual(extension_telemetry.get_subscription_id(), value)

    def assertSubscriptionIdIsNone(self):
        self.assertIsNone(extension_telemetry.get_subscription_id())

    def assertTelemetryPropertiesWereSet(self, telemetry_properties: Dict[TelemetryProperty, Any]):
        for telemetry_property, value in telemetry_properties.items():
            if self.is_telemetry_enabled:
                self.assertTelemetryPropertyValueEquals(telemetry_property, value)
            else:
                self.assertTelemetryPropertyIsNotSet(telemetry_property)

    def assertTelemetryPropertyWasSet(self, telemetry_property: TelemetryProperty, value: str):
        if self.is_telemetry_enabled:
            self.assertTelemetryPropertyValueEquals(telemetry_property, value)
        else:
            self.assertTelemetryPropertyIsNotSet(telemetry_property)

    def assertTelemetryFaultEventIsSet(self,
                                       fault: Fault,
                                       fault_type: FaultType,
                                       summary: str,
                                       exception_type: type,
                                       exception_msg: str):

        # test that the fault information is set accordingly
        self.assertIsNotNone(fault)
        self.assertEqual(fault.name, self.fault_event_name)
        self.assertEqual(fault.fault_type, fault_type)
        self.assertEqual(fault.summary, summary)
        self.assertIsInstance(fault.exception, exception_type)

        # test that a fault event is added to the underlying CLI telemetry session
        self.assertIsNotNone(fault.details)
        details = fault.details
        self.assertEqual(details.fault_type, fault_type)
        self.assertEqual(details.description, summary)
        self.assertEqual(details.correlation_id, self.mock_uuid)
        self.assertEqual(details.message, exception_msg)

    def assertCoreTelemetryPropertiesAreSet(self, event: ExtensionTelemetryEvent):
        self.assertDictEqual(
            event.properties,
            {
                CoreTelemetryProperty.EXTENSION_NAME: self.extension_name,
                CoreTelemetryProperty.CORRELATION_ID: self.mock_uuid
            }
        )

    def assertTelemetryExtensionEventIsSet(self, event: ExtensionTelemetryEvent):
        # test that an extension event is added to the underlying CLI telemetry session
        self.assertIsNotNone(event)
        self.assertEqual(event.name, self.extension_event_name)
        self.assertEqual(event.extension_name, self.extension_name)
        self.assertCoreTelemetryPropertiesAreSet(event)

    def set_telemetry_property(self, telemetry_property: TelemetryProperty, value: str, validate: bool = False):
        extension_telemetry.set_property(telemetry_property, value)
        if validate:
            self.assertTelemetryPropertyWasSet(telemetry_property, value)

    def set_telemetry_properties(self, telemetry_properties: Dict[TelemetryProperty, Any], validate: bool = False):
        extension_telemetry.set_properties(telemetry_properties)
        if validate:
            self.assertTelemetryPropertiesWereSet(telemetry_properties)
