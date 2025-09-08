# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import datetime
import logging
import os
import platform

from applicationinsights import TelemetryClient
from azure.cli.core.telemetry import (_get_azure_subscription_id,
                                      _get_hash_mac_address, _get_user_agent)

DEFAULT_INSTRUMENTATION_KEY = "c301e561-daea-42d9-b9d1-65fca4166704"
APPLICATIONINSIGHTS_INSTRUMENTATION_KEY_ENV = "APPLICATIONINSIGHTS_INSTRUMENTATION_KEY"


class CLITelemetryClient:
    def __init__(self):
        instrumentation_key = self._get_application_insights_instrumentation_key()
        self._telemetry_client = TelemetryClient(
            instrumentation_key=instrumentation_key
        )
        self.start_time = datetime.datetime.utcnow()
        self.end_time = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = datetime.datetime.utcnow()
        self.track_agent_started()
        self.flush()

    def track(self, event_name, properties=None):
        if properties is None:
            properties = {}
        properties.update(self._generate_payload())
        self._telemetry_client.track_trace(event_name, properties, logging.INFO)

    def track_agent_started(self):
        timestamp_properties = {
            "time.start": str(self.start_time),
            "time.end": str(self.end_time),
        }
        self.track("AgentCLIStartup", properties=timestamp_properties)

    def flush(self):
        self._telemetry_client.flush()

    def _generate_payload(self):
        extension_name = "aks-agent"
        try:
            from azure.cli.core.extension import get_extension

            ext_name = "aks-agent"
            ext = get_extension(ext_name)
            extension_name = f"aks-agent@{ext.version}"
        except:  # pylint: disable=W0702
            pass

        return {
            "device.id": _get_hash_mac_address(),
            "service.name": "aks agent",
            "userAzureSubscriptionId": _get_azure_subscription_id(),
            "OS.Type": platform.system().lower(),  # eg. darwin, windows
            "OS.Version": platform.version().lower(),  # eg. 10.0.14942
            "OS.Platform": platform.platform().lower(),  # eg. windows-10-10.0.19041-sp0
            "userAgent": _get_user_agent(),
            "extensionname": extension_name,  # extension and version
        }

    def _get_application_insights_instrumentation_key(self) -> str:
        return os.getenv(
            APPLICATIONINSIGHTS_INSTRUMENTATION_KEY_ENV, DEFAULT_INSTRUMENTATION_KEY
        )
