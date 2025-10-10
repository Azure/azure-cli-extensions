# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------


from azext_arcdata.core.constants import DNS_NAME_REQUIREMENTS
from azext_arcdata.kubernetes_sdk.models.custom_resource import CustomResource
from azext_arcdata.core.util import name_meets_dns_requirements
from azext_arcdata.core.class_utils import validatedclass


@validatedclass
class ExportTaskCustomResource(CustomResource):
    """
    Internal Custom Resource object to be used for deployments.
    """

    def __init__(self):
        super().__init__()

    @CustomResource.Metadata.name.setter
    def name(self, n: str):
        """
        @override
        """
        export_task_name_max_length = 253
        export_task_namespace_max_length = 63

        if not n:
            raise ValueError("Export custom resource name cannot be empty")

        if len(n) > self.export_task_name_max_length:
            raise ValueError(
                "Export custom resource name '{}' exceeds "
                "{} character length limit".format(
                    n, self.export_task_name_max_length
                )
            )

        self._name = n

    @CustomResource.Metadata.namespace.setter
    def namespace(self, ns: str):
        """
        @override
        """
        if not ns:
            raise ValueError("Kubernetes namespace cannot be empty")

        if len(ns) > self.export_task_namespace_max_length:
            raise ValueError(
                "Kubernetes namespace '{}' exceeds {} "
                "character name length limit".format(
                    ns, self.export_task_namespace_max_length
                )
            )

        if not name_meets_dns_requirements(ns):
            raise ValueError(
                "Kubernetes namespace '{}' does not follow "
                "DNS requirements: {}".format(ns, DNS_NAME_REQUIREMENTS)
            )

        self._namespace = ns

    class Spec(CustomResource.Spec):
        """
        @override CustomResource.spec
        """

        def init(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    def apply_args(self, **kwargs):
        self._set_if_provided(self.metadata, "name", kwargs, "name")
        self._set_if_provided(self.metadata, "namespace", kwargs, "namespace")

    class Metadata(CustomResource.Metadata):
        """
        @override CustomResource.metadata
        """

        export_name_max_length = 252

        def __init__(self, name: str = None, *args, **kwargs):
            super().__init__(*args, **kwargs)

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
        def path(self) -> int:
            """ """
            return self._path

        @path.setter
        def readyReplicas(self, path: str):
            self._path = path

        def _hydrate(self, d: dict):
            """
            @override
            """
            super()._hydrate(d)
            if "path" in d:
                self.path = d["path"]

        def _to_dict(self):
            """
            @override
            """
            base = super()._to_dict()
            base["path"] = getattr(self, "path", None)
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
