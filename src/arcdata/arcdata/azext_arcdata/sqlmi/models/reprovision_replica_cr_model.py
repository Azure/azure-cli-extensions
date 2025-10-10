# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.kubernetes_sdk.models import (
    CustomResource,
    SerializationUtils,
)


class SqlmiReprovisionReplicaTaskCustomResource(CustomResource):
    """
    Internal Sqlmi Custom Resource object to be used for reprovision.
    """

    def __init__(
        self,
        spec: "SqlmiReprovisionReplicaTaskCustomResource.Spec" = None,
        metadata: "SqlmiReprovisionReplicaTaskCustomResource.Metadata" = None,
    ):
        """
        Initializes a CR object with the given json.
        """
        super().__init__()
        self.spec = spec if spec else self.Spec()
        self.metadata = metadata if metadata else self.Metadata()

    class Spec(CustomResource.Spec):
        """
        @override CustomResource.spec
        """

        def __init__(self):
            super().__init__()
            self._replicaName = None

        @property
        def replicaName(self):
            return self._replicaName

        @replicaName.setter
        def replicaName(self, replicaName):
            self._replicaName = replicaName

        def _hydrate(self, d: dict):
            super()._hydrate(d)
            if "replicaName" in d:
                self.replicaName = d["replicaName"]

        def _to_dict(self):
            base = super()._to_dict()
            base["replicaName"] = self.replicaName
            return base

    class Metadata(CustomResource.Metadata):
        """
        @override CustomResource.metadata
        """

        def __init__(self, name: str = None):
            super().__init__()

        @CustomResource.Metadata.name.setter
        def name(self, n: str):
            """
            @override CustomResource.metadata.name.setter
            """
            if not n:
                raise ValueError("Rest API name cannot be empty")

            self._name = n

        def _hydrate(self, d: dict):
            super()._hydrate(d)

        def _to_dict(self):
            return super()._to_dict()

    class Status(CustomResource.Status):
        """
        @override CustomResource.Status
        """

        def __init__(self):
            super().__init__()

        @property
        def state(self) -> str:
            return self._state

        @state.setter
        def state(self, rp: str):
            self._state = rp

        @property
        def results(self) -> str:
            return self._results

        @results.setter
        def results(self, se: str):
            self._results = se

        def _hydrate(self, d: dict):
            """
            @override
            """
            super()._hydrate(d)
            if "state" in d:
                self.state = d["state"]
            if "results" in d:
                self.results = d["results"]

        def _to_dict(self):
            """
            @override
            """
            base = super()._to_dict()
            base["state"] = getattr(self, "state", None)
            base["results"] = getattr(self, "results", None)
            return base

    def _hydrate(self, d: dict):
        """
        @override
        """
        super()._hydrate(d)

    def _to_dict(self):
        """
        @override
        """
        return super()._to_dict()

    def apply_args(self, **kwargs):
        super().apply_args(**kwargs)
