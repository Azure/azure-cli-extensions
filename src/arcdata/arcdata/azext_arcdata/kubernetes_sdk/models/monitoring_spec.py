# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azext_arcdata.kubernetes_sdk.models.dict_utils import SerializationUtils


class MonitoringSpec(SerializationUtils):
    """
    Monitoring spec for Data Controller custom resource
    """

    def __init__(
        self,
        enableOpenTelemetry: bool = None,
    ):
        if enableOpenTelemetry is not None:
            self.enableOpenTelemetry = enableOpenTelemetry

    @property
    def enableOpenTelemetry(self) -> bool:
        return self._enableOpenTelemetry

    @enableOpenTelemetry.setter
    def enableOpenTelemetry(self, enable: bool):
        self._enableOpenTelemetry = enable

    def _to_dict(self) -> dict:
        return {
            "enableOpenTelemetry": getattr(self, "enableOpenTelemetry", None),
        }

    def _hydrate(self, d: dict):
        if "enableOpenTelemetry" in d:
            self.enableOpenTelemetry = d["enableOpenTelemetry"]
