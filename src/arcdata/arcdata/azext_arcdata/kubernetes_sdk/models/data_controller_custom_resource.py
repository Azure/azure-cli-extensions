# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azext_arcdata.kubernetes_sdk.models.custom_resource import CustomResource
from azext_arcdata.kubernetes_sdk.models.custom_resource_update import Update
from azext_arcdata.kubernetes_sdk.models.dict_utils import SerializationUtils
from azext_arcdata.kubernetes_sdk.models.data_controller_volume import (
    DataControllerVolume,
)
from azext_arcdata.kubernetes_sdk.models.resource_sizing_spec import (
    ResourceSizingSpec,
)
from azext_arcdata.kubernetes_sdk.models.security_spec import SecuritySpec
from azext_arcdata.kubernetes_sdk.models.endpoint_spec import EndpointSpec
from azext_arcdata.kubernetes_sdk.models.monitoring_spec import MonitoringSpec
from azext_arcdata.core.util import name_meets_dns_requirements
from azext_arcdata.core.class_utils import enforcetype
from azext_arcdata.core.labels import parse_labels

from azext_arcdata.core.constants import (
    DNS_NAME_REQUIREMENTS,
    CONNECTION_MODE,
    DISPLAY_NAME,
    LOCATION,
    RESOURCE_GROUP,
    SUBSCRIPTION,
)


class DataControllerCustomResource(CustomResource):
    """
    Internal Custom Resource object to be used for deployments.
    """

    def __init__(self):
        super().__init__()

    class Metadata(CustomResource.Metadata):
        """
        @override CustomResource.Metadata
        """

        arc_dc_name_max_length = 253
        arc_dc_namespace_max_length = 63

        def init(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @CustomResource.Metadata.name.setter
        def name(self, n: str):
            """
            @override
            """
            if not n:
                raise ValueError("Arc data controller name cannot be empty")

            if len(n) > self.arc_dc_name_max_length:
                raise ValueError(
                    "Arc data controller name '{}' exceeds {} character "
                    "length limit".format(n, self.arc_dc_name_max_length)
                )

            if not name_meets_dns_requirements(n):
                raise ValueError(
                    "Arc data controller name '{}' does not follow DNS "
                    "requirements: {}".format(n, DNS_NAME_REQUIREMENTS)
                )

            self._name = n

        @CustomResource.Metadata.namespace.setter
        def namespace(self, ns: str):
            """
            @override
            """
            if not ns:
                raise ValueError("Kubernetes namespace cannot be empty")

            if len(ns) > self.arc_dc_namespace_max_length:
                raise ValueError(
                    "Kubernetes namespace '{}' exceeds {} character name "
                    "length limit".format(ns, self.arc_dc_namespace_max_length)
                )

            if not name_meets_dns_requirements(ns):
                raise ValueError(
                    "Kubernetes namespace '{}' does not follow DNS "
                    "requirements: {}".format(ns, DNS_NAME_REQUIREMENTS)
                )

            self._namespace = ns

    class Spec(CustomResource.Spec):
        """
        @override CustomResource.Spec
        """

        def __init__(self, infrastructure: str = None):
            super().__init__()
            self.controllerServices = []
            self.settings = {}
            self.security = SecuritySpec()
            self.monitoring = MonitoringSpec()
            self.credentials = self.Credentials()
            self.update = Update()
            self.infrastructure = infrastructure
            self.resources = self.DataControllerResourcesSpec()

        class Credentials(SerializationUtils):
            """
            Contains "secret"/connection information for this data controller
            to communicate with a variety of resources

            CustomResource.Spec.Credentials
            """

            def __init__(
                self,
                domainServiceAccount: str = None,
                serviceAccount: str = None,
                dockerRegistry: str = None,
                controllerAdmin: str = None,
            ):

                self.controllerAdmin = controllerAdmin
                self.domainServiceAccount = domainServiceAccount
                self.serviceAccount = serviceAccount
                self.dockerRegistry = dockerRegistry

            @property
            def domainServiceAccount(self) -> str:
                return self._domainServiceAccount

            @domainServiceAccount.setter
            def domainServiceAccount(self, dsa: str):
                self._domainServiceAccount = dsa

            @property
            def serviceAccount(self) -> str:
                return self._serviceAccount

            @serviceAccount.setter
            def serviceAccount(self, sa: str):
                self._serviceAccount = sa

            @property
            def dockerRegistry(self) -> str:
                return self._dockerRegistry

            @dockerRegistry.setter
            def dockerRegistry(self, dr: str):
                self._dockerRegistry = dr

            @property
            def controllerAdmin(self) -> str:
                return self._controllerAdmin

            @controllerAdmin.setter
            def controllerAdmin(self, ca: str):
                self._controllerAdmin = ca

            def _to_dict(self) -> dict:
                return {
                    "domainServiceAccount": getattr(
                        self, "domainServiceAccount", None
                    ),
                    "serviceAccount": getattr(self, "serviceAccount", None),
                    "dockerRegistry": getattr(self, "dockerRegistry", None),
                    "controllerAdmin": getattr(self, "controllerAdmin", None),
                }

            def _hydrate(self, d: dict):
                if "domainServiceAccount" in d:
                    self.domainServiceAccount = d["domainServiceAccount"]

                if "controllerAdmin" in d:
                    self.controllerAdmin = d["controllerAdmin"]

                if "dockerRegistry" in d:
                    self.dockerRegistry = d["dockerRegistry"]

                if "serviceAccount" in d:
                    self.serviceAccount = d["serviceAccount"]

        @property
        def credentials(self) -> Credentials:
            return self._credentials

        @credentials.setter
        @enforcetype(Credentials)
        def credentials(self, c: Credentials):
            self._credentials = c

        class DataControllerResourcesSpec(SerializationUtils):
            """
            Contains the resource sizing parameters for the data controller
            """

            def __init__(
                self,
                controller: ResourceSizingSpec = None,
                controllerDb: ResourceSizingSpec = None,
            ):
                self._controller = ResourceSizingSpec()
                self._controllerDb = ResourceSizingSpec()

            @property
            def controller(self) -> ResourceSizingSpec:
                return self._controller

            @controller.setter
            @enforcetype(ResourceSizingSpec)
            def controller(self, c: ResourceSizingSpec):
                self._controller = c

            @property
            def controllerDb(self) -> ResourceSizingSpec:
                return self._controllerDb

            @controllerDb.setter
            @enforcetype(ResourceSizingSpec)
            def controllerDb(self, c: ResourceSizingSpec):
                self._controllerDb = c

            def _to_dict(self) -> dict:
                base = {}
                base["controller"] = self.controller._to_dict()
                base["controllerDb"] = self.controllerDb._to_dict()
                return base

            def _hydrate(self, d: dict):
                if "controller" in d:
                    self.controller._hydrate(d["controller"])
                if "controllerDb" in d:
                    self.controllerDb._hydrate(d["controllerDb"])

        @property
        def resources(self) -> DataControllerResourcesSpec:
            return self._resources

        @resources.setter
        def resources(self, r: DataControllerResourcesSpec):
            self._resources = r

        class Storage(CustomResource.Spec.Storage):
            """
            @override CustomResource.Spec.Storage
            """

            def __init__(self):
                super().__init__(
                    DataControllerVolume(),
                    DataControllerVolume(),
                    DataControllerVolume(),
                )

            def apply_args(self, **kwargs):
                if (
                    "storage_class" in kwargs
                    and kwargs["storage_class"] is not None
                ):
                    self.data.className = kwargs["storage_class"]
                    self.logs.className = kwargs["storage_class"]

                if (
                    "storage_labels" in kwargs
                    and kwargs["storage_labels"] is not None
                ):
                    labels = parse_labels(kwargs["storage_labels"])
                    self.data.labels = labels
                    self.logs.labels = labels
                    self.backups.labels = labels

                if (
                    "storage_annotations" in kwargs
                    and kwargs["storage_annotations"] is not None
                ):
                    annotations = parse_labels(kwargs["storage_annotations"])
                    self.data.annotations = annotations
                    self.logs.annotations = annotations
                    self.backups.annotations = annotations

        @property
        def security(self) -> SecuritySpec:
            return self._security

        @security.setter
        @enforcetype(SecuritySpec)
        def security(self, s: SecuritySpec):
            self._security = s

        @property
        def monitoring(self) -> MonitoringSpec:
            return self._monitoring

        @monitoring.setter
        @enforcetype(MonitoringSpec)
        def monitoring(self, m: MonitoringSpec):
            self._monitoring = m

        @property
        def controllerServices(self) -> list:
            return self._controller_services

        @controllerServices.setter
        def controllerServices(self, s: list):
            self._controller_services = s

        @property
        def settings(self):
            return self._settings

        @settings.setter
        def settings(self, s):
            self._settings = s

        @property
        def infrastructure(self) -> str:
            return self._infrastructure

        @infrastructure.setter
        def infrastructure(self, i: str):
            self._infrastructure = i

        def _to_dict(self):
            """
            @override
            """
            base = super()._to_dict()
            controller_services = []
            for s in getattr(self, "controllerServices", []):
                controller_services.append(s._to_dict())

            base["credentials"] = self.credentials._to_dict()
            base["services"] = controller_services
            base["settings"] = getattr(self, "settings", None)
            base["security"] = self.security._to_dict()
            base["monitoring"] = self.monitoring._to_dict()
            base["update"] = self.update._to_dict()
            base["infrastructure"] = self.infrastructure
            base["resources"] = self.resources._to_dict()
            return base

        def _hydrate(self, d: dict):
            """
            @override
            """
            super()._hydrate(d)
            if "services" in d and d["services"] is not None:
                for s in d["services"]:
                    curr = EndpointSpec()
                    curr._hydrate(s)
                    self.controllerServices.append(curr)

            if "security" in d:
                self.security._hydrate(d["security"])

            if "monitoring" in d:
                self.monitoring._hydrate(d["monitoring"])

            if "settings" in d:
                self.settings = d["settings"]

            if "credentials" in d:
                self.credentials._hydrate(d["credentials"])

            if "infrastructure" in d:
                self.infrastructure = d["infrastructure"]

            if "update" in d:
                self.update._hydrate(d["update"])

            if "resources" in d:
                self.resources._hydrate(d["resources"])

    class Status(CustomResource.Status):
        """
        CustomResource.Status
        """

        @property
        def phase(self):
            return self._phase

        @phase.setter
        def phase(self, p):
            self._phase = p

    def _to_dict(self) -> dict:
        return super()._to_dict()

    def _hydrate(self, d: dict):
        super()._hydrate(d)

    def get_controller_service(self) -> EndpointSpec:
        for s in self.spec.controllerServices:
            try:
                if s.name == "controller":
                    return s
            except AttributeError:
                continue

        return None

    def apply_args(self, **kwargs):
        """
        @override
        """
        super().apply_args(**kwargs)

        # Construct azure settings based on args
        self.spec.settings["azure"] = {
            CONNECTION_MODE: kwargs["connectivity_mode"].lower(),
            LOCATION: kwargs["location"].lower(),
            RESOURCE_GROUP: kwargs["resource_group"],
            SUBSCRIPTION: kwargs["subscription"],
        }

        # set the display name
        if "name" in kwargs:
            if "controller" not in self.spec.settings:
                self.spec.settings["controller"] = {}
            self.spec.settings["controller"][DISPLAY_NAME] = kwargs["name"]

        self._set_if_provided(
            self.spec, "infrastructure", kwargs, "infrastructure"
        )

        if "labels" in kwargs and kwargs["labels"] is not None:
            labels = parse_labels(kwargs["labels"])
            setattr(self.metadata, "labels", labels)

        if "annotations" in kwargs and kwargs["annotations"] is not None:
            annotations = parse_labels(kwargs["annotations"])
            setattr(self.metadata, "annotations", annotations)

        if "service_labels" in kwargs and kwargs["service_labels"] is not None:
            labels = parse_labels(kwargs["service_labels"])

            for service in self.spec.controllerServices:
                setattr(service, "labels", labels)

        if (
            "service_annotations" in kwargs
            and kwargs["service_annotations"] is not None
        ):
            annotations = parse_labels(kwargs["service_annotations"])

            for service in self.spec.controllerServices:
                setattr(service, "annotations", annotations)
