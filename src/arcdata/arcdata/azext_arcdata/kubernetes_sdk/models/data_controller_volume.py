# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azext_arcdata.kubernetes_sdk.models.volume_claim import VolumeClaim


class DataControllerVolume(VolumeClaim):
    """
    A representation of a k8s VolumeClaim
    """

    def __init__(self, accessMode: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.accessMode = accessMode

    @property
    def accessMode(self) -> str:
        return self._accessMode

    @accessMode.setter
    def accessMode(self, am: str):
        self._accessMode = am

    def _to_dict(self):
        """
        @override
        """
        base = super()._to_dict()
        base["accessMode"] = getattr(self, "accessMode", None)
        return base

    def _hydrate(self, d: dict):
        """
        @override
        """
        super()._hydrate(d)

        if "accessMode" in d:
            self.accessMode = d["accessMode"]
