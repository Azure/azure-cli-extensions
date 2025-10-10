# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from datetime import datetime

from azext_arcdata.kubernetes_sdk.models import (
    CustomResource,
    KubeQuantity,
    SerializationUtils,
    StorageSpec,
    VolumeClaim,
)


class SqlmiRestoreTaskCustomResource(CustomResource):
    """
    Internal Sqlmi Custom Resource object to be used for deployments.
    """

    def __init__(
        self,
        spec: "SqlmiRestoreTaskCustomResource.Spec" = None,
        metadata: "SqlmiRestoreTaskCustomResource.Metadata" = None,
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
            self._source = self.Source()
            self._restorePoint = None
            self._destination = self.Destination()
            self._dryRun = None

        class Source(SerializationUtils):
            def __init__(
                self,
                name: str = None,
                database: str = None,
            ):
                self.name = name
                self.database = database

            @property
            def name(self) -> str:
                return self._name

            @name.setter
            def name(self, name: str):
                self._name = name

            @property
            def database(self) -> str:
                return self._database

            @database.setter
            def database(self, db: str):
                self._database = db

            def _hydrate(self, d: dict):
                if "name" in d:
                    self.name = d["name"]
                if "database" in d:
                    self.database = d["database"]

            def _to_dict(self) -> dict:
                return {
                    "name": self.name,
                    "database": self.database,
                }

        class Destination(SerializationUtils):
            def __init__(
                self,
                name: str = None,
                database: str = None,
            ):
                self.name = name
                self.database = database

            @property
            def name(self) -> str:
                return self._name

            @name.setter
            def name(self, name: str):
                self._name = name

            @property
            def database(self) -> str:
                return self._database

            @database.setter
            def database(self, db: str):
                self._database = db

            def _hydrate(self, d: dict):
                if "name" in d:
                    self.name = d["name"]
                if "database" in d:
                    self.database = d["database"]

            def _to_dict(self) -> dict:
                return {
                    "name": self.name,
                    "database": self.database,
                }

        @property
        def source(self) -> Source:
            return self._source

        @source.setter
        def source(self, s: Source):
            self._source = s

        @property
        def destination(self) -> Destination:
            return self._destination

        @destination.setter
        def destination(self, d: Destination):
            self._destination = d

        @property
        def restorePoint(self) -> datetime:
            return self._restorePoint

        @restorePoint.setter
        def restorePoint(self, rt: datetime):
            self._restorePoint = rt

        @property
        def dryRun(self):
            return self._dryRun

        @dryRun.setter
        def dryRun(self, d):
            self._dryRun = d

        def _hydrate(self, d: dict):
            super()._hydrate(d)
            if "source" in d:
                self.source._hydrate(d["source"])
            if "destination" in d:
                self.destination._hydrate(d["destination"])
            if "restorePoint" in d:
                self.restorePoint = d["restorePoint"]
            if "dryRun" in d:
                self.dryRun = d["dryRun"]

        def _to_dict(self):
            base = super()._to_dict()
            base["source"] = self.source._to_dict()
            base["destination"] = self.destination._to_dict()
            base["restorePoint"] = self.restorePoint
            base["dryRun"] = self.dryRun
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
