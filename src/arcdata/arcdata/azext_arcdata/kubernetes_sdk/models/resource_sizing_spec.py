# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azext_arcdata.kubernetes_sdk.models.dict_utils import SerializationUtils
from azext_arcdata.kubernetes_sdk.models.request_spec import Requests
from azext_arcdata.kubernetes_sdk.models.limit_spec import Limits


class ResourceSizingSpec(SerializationUtils):
    """
    Resource sizing spec
    """

    def __init__(self):
        self._requests = Requests()
        self._limits = Limits()

    @property
    def limits(self) -> Limits:
        return self._limits

    @limits.setter
    def limits(self, r: Limits):
        self._limits = r

    @property
    def requests(self) -> Requests:
        return self._requests

    @requests.setter
    def requests(self, r: Requests):
        self._requests = r

    def _to_dict(self):
        return {
            "limits": self.limits._to_dict(),
            "requests": self.requests._to_dict(),
        }

    def _hydrate(self, d: dict):
        if "limits" in d:
            self.limits._hydrate(d["limits"])
        if "requests" in d:
            self.requests._hydrate(d["requests"])
