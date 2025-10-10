# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azext_arcdata.kubernetes_sdk.models.dict_utils import SerializationUtils
from azext_arcdata.kubernetes_sdk.models.volume_claim import VolumeClaim


class StorageSpec(SerializationUtils):
    """
    Namespaces the properties of the storage spec for a custom resource. What volumes it should have, what type,
    and what size they are.

    CustomResource.spec.storage.<type_of_storage>
    """

    def __init__(self):
        self.volumes = []

    @property
    def volumes(self) -> list:
        return self._volumes

    @volumes.setter
    def volumes(self, v: list):
        self._volumes = v

    def _to_dict(self):
        """
        @override
        """
        volumes = []
        for v in getattr(self, "volumes", []):
            volumes.append(v._to_dict())

        return {"volumes": volumes}

    def _hydrate(self, d: dict):
        """
        @override
        """
        if "volumes" in d and d["volumes"] is not None:
            for v in d["volumes"]:
                curr = VolumeClaim()
                curr._hydrate(v)
                self.volumes.append(curr)
