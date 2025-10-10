# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.kubernetes_sdk.models.dict_utils import SerializationUtils
from azext_arcdata.core.constants import (
    MAX_PORT_NUBMER,
    MIN_PORT_NUMBER,
    PORT_REQUIREMENTS,
)


class EndpointSpec(SerializationUtils):
    """
    A copy of the backend Endpoint class as used in the DataControllerCustomResource spec
    """

    def __init__(
        self,
        name: str = None,
        serviceType: str = None,
        port: int = None,
        labels: dict = None,
        annotations: dict = None,
    ):
        # Since `None` throws an error for port number we're allowing only the constructor to initialize to None here.
        # This would be an error in deserialization/argument application steps
        if port:
            self.port = port
        else:
            self._port = None

        if name:
            self.name = name

        if serviceType:
            self._serviceType = serviceType

        if labels:
            self._labels = labels

        if annotations:
            self._annotations = annotations

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, n: str):
        self._name = n

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

    @property
    def dnsName(self) -> str:
        return self._dnsName

    @dnsName.setter
    def dnsName(self, n: str):
        self._dnsName = n

    @property
    def serviceType(self) -> str:
        return self._serviceType

    @serviceType.setter
    def serviceType(self, t: str):
        self._serviceType = t

    @property
    def port(self) -> str:
        return self._port

    @port.setter
    def port(self, p: str):
        try:
            val = int(p)
            if not MIN_PORT_NUMBER <= val <= MAX_PORT_NUBMER:
                raise ValueError(PORT_REQUIREMENTS)
        except ValueError:
            raise ValueError(PORT_REQUIREMENTS)
        except TypeError:
            raise ValueError(PORT_REQUIREMENTS)

        self._port = p

    def _to_dict(self):
        """
        @override
        """
        return {
            "port": getattr(self, "port", None),
            "serviceType": getattr(self, "serviceType", None),
            "name": getattr(self, "name", None),
            "dnsName": getattr(self, "dnsName", None),
            "labels": getattr(self, "labels", None),
            "annotations": getattr(self, "annotations", None),
        }

    def _hydrate(self, d: dict):
        """
        @override
        """
        if "port" in d:
            self.port = d["port"]

        if "serviceType" in d:
            self.serviceType = d["serviceType"]

        if "name" in d:
            self.name = d["name"]

        if "dnsName" in d:
            self.dnsName = d["dnsName"]

        if "labels" in d:
            self.labels = d["labels"]

        if "annotations" in d:
            self.annotations = d["annotations"]
