# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest.mock as mock

import azure.cli.core.telemetry as telemetry

from azext_ai_did_you_mean_this.tests.latest._fault import Fault
from azext_ai_did_you_mean_this.telemetry import ExtensionTelemterySession

SET_EXCEPTION_PATCH = 'azure.cli.core.telemetry.set_exception'
ADD_EXTENSION_EVENT_PATCH = 'azure.cli.core.telemetry.add_extension_event'
TELEMETRY_ENABLED_PATCH = 'azext_ai_did_you_mean_this.telemetry.IS_TELEMETRY_ENABLED'


class UnknownException(Exception):
    pass


class ExtensionTelemetryEvent():
    EXTENSION_NAME_PROPERTY = 'Context.Default.AzureCLI.ExtensionName'

    def __init__(self, event: dict):
        super().__init__()
        self._name = event.get('name', None)
        self._properties = event.get('properties', {})
        self._extension_name = self._properties.get(self.EXTENSION_NAME_PROPERTY, None)

    @property
    def name(self):
        return self._name

    @property
    def properties(self):
        return self._properties

    @property
    def extension_name(self):
        return self._extension_name


class ExtensionTelemetryMockSession():
    def __init__(self, enable_telemetry: bool = True):
        super().__init__()
        self._enable_telemetry = enable_telemetry
        self._fault = None
        self._extension_event = None
        self._session = ExtensionTelemterySession()
        self.patches = [
            mock.patch(TELEMETRY_ENABLED_PATCH, self._enable_telemetry)
        ]
        self._add_telemetry_patches()

    def _add_telemetry_patches(self):
        _set_exception_func_orig = telemetry.set_exception
        _add_extension_event_func_orig = telemetry.add_extension_event

        def _set_exception_hook(exception: Exception, fault_type: str, *args, summary: str = None, **kwargs):
            result = _set_exception_func_orig(exception, fault_type, *args, summary, **kwargs)
            fault_name, details = telemetry._session.exceptions[-1]  # pylint: disable=protected-access
            self._fault = Fault(fault_name, details, exception, fault_type, summary)
            return result

        def _add_extension_event_hook(extension_name: str, properties: dict):
            instrumentation_key = telemetry.DEFAULT_INSTRUMENTATION_KEY
            result = _add_extension_event_func_orig(extension_name, properties)
            event = telemetry._session.events[instrumentation_key][-1]  # pylint: disable=protected-access
            self._extension_event = ExtensionTelemetryEvent(event)
            return result

        self.patches.append(mock.patch(SET_EXCEPTION_PATCH, wraps=_set_exception_hook))
        self.patches.append(mock.patch(ADD_EXTENSION_EVENT_PATCH, wraps=_add_extension_event_hook))

    def __enter__(self):
        for patch in self.patches:
            patch.__enter__()

        self._session.__enter__()

        return self

    def __exit__(self, *args):
        self._session.__exit__(*args)

        for patch in self.patches:
            patch.__exit__(*args)

    @property
    def fault(self) -> Fault:
        return self._fault

    @property
    def extension_event(self):
        return self._extension_event
