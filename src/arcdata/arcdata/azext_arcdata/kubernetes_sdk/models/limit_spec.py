# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from typing import Union
from azext_arcdata.kubernetes_sdk.models.dict_utils import SerializationUtils
from azext_arcdata.kubernetes_sdk.models.kube_quantity import KubeQuantity


class Limits(SerializationUtils):
    """
    Limits spec
    """

    def __init__(self):
        self._memory = None
        self._cpu = None

    @property
    def memory(self) -> KubeQuantity:
        return self._memory

    @memory.setter
    def memory(self, m: Union[str, KubeQuantity]):
        if type(m) is str and m == "":
            self._memory = None
            return

        val = KubeQuantity(m)
        self._memory = val

    @property
    def cpu(self) -> KubeQuantity:
        return self._cpu

    @cpu.setter
    def cpu(self, c: Union[str, KubeQuantity]):
        if type(c) is str and c == "":
            self._cpu = None
            return

        val = KubeQuantity(c)
        self._cpu = val

    def _to_dict(self):
        """
        @override
        """
        mem = getattr(self, "memory", None)
        cores = getattr(self, "cpu", None)
        return {
            "memory": mem.quantity if mem is not None else mem,
            "cpu": cores.quantity if cores is not None else cores,
        }

    def _hydrate(self, d: dict):
        """
        @override
        """
        if "memory" in d:
            self.memory = d["memory"]

        if "cpu" in d:
            self.cpu = d["cpu"]
