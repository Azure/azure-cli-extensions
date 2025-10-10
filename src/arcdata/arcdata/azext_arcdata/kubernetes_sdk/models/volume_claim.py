# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azext_arcdata.kubernetes_sdk.models.dict_utils import SerializationUtils
from azext_arcdata.kubernetes_sdk.models.kube_quantity import KubeQuantity
from typing import Union


class VolumeClaim(SerializationUtils):
    """
    A representation of a k8s VolumeClaim
    """

    def __init__(
        self,
        className: str = None,
        size: Union[str, KubeQuantity] = None,
        labels: dict = None,
        annotations: dict = None,
    ):
        self.className = className
        self.size = size
        self.labels = labels
        self.annotations = annotations

    @property
    def className(self) -> str:
        return self._className

    @className.setter
    def className(self, n: str):
        self._className = n

    @property
    def size(self) -> KubeQuantity:
        return self._size

    @size.setter
    def size(self, s: Union[str, KubeQuantity]):
        if s is None:
            self._size = None
        else:
            self._size = KubeQuantity(s)

    @property
    def labels(self) -> dict:
        return self._labels

    @labels.setter
    def labels(self, l: dict):
        self._labels = l

    @property
    def annotations(self) -> dict:
        return self._annotations

    @annotations.setter
    def annotations(self, a: dict):
        self._annotations = a

    def _to_dict(self):
        """
        @override
        """
        return {
            "size": self.size.quantity if self.size else None,
            "className": self.className,
            "labels": self.labels,
            "annotations": self.annotations,
        }

    def _hydrate(self, d: dict):
        """
        @override
        """
        if "className" in d:
            self.className = d["className"]

        if "size" in d:
            self.size = d["size"]

        if "labels" in d:
            self.labels = d["labels"]

        if "annotations" in d:
            self.annotations = d["annotations"]
