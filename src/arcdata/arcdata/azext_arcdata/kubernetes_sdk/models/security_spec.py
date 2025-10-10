# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azext_arcdata.kubernetes_sdk.models.dict_utils import SerializationUtils


class SecuritySpec(SerializationUtils):
    """
    Security spec for a custom resource
    """

    def __init__(
        self,
        allowDumps: bool = None,
        allowNodeMetricsCollection: bool = None,
        allowPodMetricsCollection: bool = None,
    ):
        if allowDumps is not None:
            self.allowDumps = allowDumps

        if allowNodeMetricsCollection is not None:
            self.allowNodeMetricsCollection = allowNodeMetricsCollection

        if allowPodMetricsCollection is not None:
            self.allowPodMetricsCollection = allowPodMetricsCollection

    @property
    def allowDumps(self) -> bool:
        return self._allowDumps

    @allowDumps.setter
    def allowDumps(self, allow: bool):
        self._allowDumps = allow

    @property
    def allowNodeMetricsCollection(self) -> bool:
        return self._allowNodeMetricsCollection

    @allowNodeMetricsCollection.setter
    def allowNodeMetricsCollection(self, allow: bool):
        self._allowNodeMetricsCollection = allow

    @property
    def allowPodMetricsCollection(self) -> bool:
        return self._allowPodMetricsCollection

    @allowPodMetricsCollection.setter
    def allowPodMetricsCollection(self, allow: bool):
        self._allowPodMetricsCollection = allow

    @property
    def activeDirectory(self) -> any:
        return self._activeDirectory

    @activeDirectory.setter
    def activeDirectory(self, ad: any):
        self._activeDirectory = ad

    def _to_dict(self) -> dict:
        return {
            "allowDumps": getattr(self, "allowDumps", None),
            "allowPodMetricsCollection": getattr(
                self, "allowPodMetricsCollection", None
            ),
            "allowNodeMetricsCollection": getattr(
                self, "allowNodeMetricsCollection", None
            ),
            "activeDirectory": getattr(self, "activeDirectory", None),
        }

    def _hydrate(self, d: dict):
        if "allowDumps" in d:
            self.allowDumps = d["allowDumps"]

        if "allowPodMetricsCollection" in d:
            self.allowPodMetricsCollection = d["allowPodMetricsCollection"]

        if "allowNodeMetricsCollection" in d:
            self.allowNodeMetricsCollection = d["allowNodeMetricsCollection"]

        if "activeDirectory" in d:
            self.activeDirectory = d["activeDirectory"]
