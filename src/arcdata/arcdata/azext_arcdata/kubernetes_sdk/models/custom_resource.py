# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------------------------------------------------

from azext_arcdata.kubernetes_sdk.models.dict_utils import SerializationUtils
from azext_arcdata.kubernetes_sdk.models.docker_spec import DockerSpec
from azext_arcdata.kubernetes_sdk.models.service_spec import ServiceSpec
from azext_arcdata.kubernetes_sdk.models.storage_spec import StorageSpec
from azext_arcdata.kubernetes_sdk.models.volume_claim import VolumeClaim
from azext_arcdata.core.util import prune_dict, trim_dict_entries
from azext_arcdata.core.class_utils import (
    validatedclass,
    validator,
    enforcetype,
)
from typing import List, Union, TYPE_CHECKING, Type
from abc import abstractmethod
from knack.cli import CLIError

import json


# KubernetesClient is only needed for typehints, but causes a circular import.
# This is the python provided workaround
if TYPE_CHECKING:
    from azext_arcdata.kubernetes_sdk.client import KubernetesClient

TYPE_ERROR = "Type '{}' is incompatible with property '{}'"


@validatedclass
class CustomResource(SerializationUtils):
    """
    Internal Custom Resource object to be used for deployments.
    """

    def __init__(
        self,
        api_version: str = None,
        kind: str = None,
        spec: SerializationUtils = None,
        metadata: SerializationUtils = None,
        status: SerializationUtils = None,
    ):
        """
        Initializes a CR object with the given json.
        :param cr_object: The custom resource json.
        """
        self.apiVersion = api_version
        self.kind = kind
        self.spec = spec if spec else self.Spec()
        self.metadata = metadata if metadata else self.Metadata()
        self.status = status if status else self.Status()

    @property
    def apiVersion(self) -> str:
        """
        A kubernetes required field - Which version of the kubernetes API is being used to create this object
        @see https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/#required-fields
        """
        return self._apiVersion

    @apiVersion.setter
    def apiVersion(self, v: str):
        self._apiVersion = v

    @property
    def kind(self) -> str:
        """
        A kubernetes required field - What kind of object this is
        @see https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/#required-fields
        """
        return self._kind

    @kind.setter
    def kind(self, k: str):
        self._kind = k

    @property
    def group(self):
        """
        A computed property equal to the first part of the apiVersion
        """
        return self.apiVersion.split("/")[0] if self.apiVersion else None

    @property
    def version(self):
        """
        A computed property equal to the second part of the apiVersion
        """
        return self.apiVersion.split("/")[1] if self.apiVersion else None

    class Metadata(SerializationUtils):
        """
        A kubernetes required field that contains unique information about a k8s object including name, UID, namespace etc
        @see https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/#required-fields

        CustomResource.metadata
        """

        def __init__(self, *args, **kwargs):
            if "name" in kwargs:
                self.name = kwargs["name"]

            if "namespace" in kwargs:
                self.namespace = kwargs["namespace"]

            if "labels" in kwargs:
                self.labels = kwargs["labels"]

            if "annotations" in kwargs:
                self.annotations = kwargs["annotations"]

            self._ownerReferences = []

        @property
        def uid(self) -> str:
            """
            A unique identifier for a resource
            """
            return self._uid

        @uid.setter
        def uid(self, uid: str):
            self._uid = uid

        @property
        def name(self) -> str:
            """
            The name of the resource
            """
            return self._name

        @name.setter
        def name(self, n: str):
            self._name = n

        @property
        def namespace(self) -> str:
            """
            Which k8s namespace the resource resides in
            """
            return self._namespace

        @namespace.setter
        def namespace(self, ns: str):
            self._namespace = ns

        @property
        def labels(self) -> dict:
            """
            Labels of the resource.
            """
            return self._labels

        @labels.setter
        def labels(self, labels: dict):
            self._labels = labels

        @property
        def annotations(self) -> dict:
            """
            Annotations of the resource.
            """
            return self._annotations

        @annotations.setter
        def annotations(self, labels: dict):
            self._annotations = labels

        @property
        def resourceVersion(self) -> int:
            """
            What version of the resource this object was created from. Updates to a resource may be concurrent so Kubernetes
            wants to know what version of the resource you think you're updating when this is serialized and sent to the backend
            """
            return self._resourceVersion

        @resourceVersion.setter
        def resourceVersion(self, rv: Union[str, int]):
            try:
                self._resourceVersion = int(rv)
            except ValueError:
                raise ValueError(
                    "Valid resource versions are positive integers"
                )

        @property
        def generation(self) -> int:
            """
            Gets the generation of the custom resource that this spec defines.
            """
            return self._generation

        @generation.setter
        def generation(self, gen: int):
            self._generation = gen

        class OwnerReference(SerializationUtils):
            def __init__(
                self,
                apiVersion: str = None,
                kind: str = None,
                name: str = None,
                uid: str = None,
            ):
                self._apiVersion = apiVersion
                self._kind = kind
                self._name = name
                self._uid = uid

            @property
            def apiVersion(self) -> str:
                return self._apiVersion

            @apiVersion.setter
            def apiVersion(self, av: str):
                self._apiVersion = av

            @property
            def kind(self) -> str:
                return self._kind

            @kind.setter
            def kind(self, k: str):
                self._kind = k

            @property
            def name(self) -> str:
                return self._name

            @name.setter
            def name(self, n: str):
                self._name = n

            @property
            def uid(self) -> str:
                return self._uid

            @uid.setter
            def uid(self, u: str):
                self._uid = u

            def _to_dict(self):
                return {
                    "apiVersion": getattr(self, "apiVersion", None),
                    "kind": getattr(self, "kind", None),
                    "name": getattr(self, "name", None),
                    "uid": getattr(self, "uid", None),
                }

            def _hydrate(self, d: dict):
                if "apiVersion" in d:
                    self.apiVersion = d["apiVersion"]
                if "kind" in d:
                    self.kind = d["kind"]
                if "name" in d:
                    self.name = d["name"]
                if "uid" in d:
                    self.uid = d["uid"]

        @property
        def ownerReferences(self) -> list:
            return self._ownerReferences

        @ownerReferences.setter
        def ownerReferences(self, ownerR: list):
            self._ownerReferences = ownerR

        def _to_dict(self):
            """
            @override
            """
            v = getattr(self, "resourceVersion", None)
            v_str = str(v) if v else None

            v_ownerReferences = []
            for s in getattr(self, "ownerReferences", []):
                v_ownerReferences.append(s._to_dict())

            return {
                "name": getattr(self, "name", None),
                "namespace": getattr(self, "namespace", None),
                "resourceVersion": v_str,
                "generation": getattr(self, "generation", None),
                "uid": getattr(self, "uid", None),
                "labels": getattr(self, "labels", None),
                "annotations": getattr(self, "annotations", None),
                "ownerReferences": v_ownerReferences,
            }

        def _hydrate(self, d: dict):
            """
            @override
            """
            if "name" in d:
                self.name = d["name"]
            if "namespace" in d:
                self.namespace = d["namespace"]
            if "resourceVersion" in d:
                self.resourceVersion = d["resourceVersion"]
            if "uid" in d:
                self.uid = d["uid"]
            if "generation" in d:
                self.generation = d["generation"]
            if "labels" in d:
                self.labels = d["labels"]
            if "annotations" in d:
                self.annotations = d["annotations"]
            if "ownerReferences" in d and d["ownerReferences"] is not None:
                self._ownerReferences = []
                for s in d["ownerReferences"]:
                    curr = self.OwnerReference()
                    curr._hydrate(s)
                    self._ownerReferences.append(curr)

    @property
    def metadata(self) -> Metadata:
        return self._metadata

    @metadata.setter
    def metadata(self, m: Union[Metadata, tuple]):
        if type(m) is self.Metadata:
            self._metadata = m
        elif type(m) is tuple:
            self._metadata = self.Metadata(*m)
        else:
            raise TypeError(TYPE_ERROR.format(type(m), "metadata"))

    class SubStatus(SerializationUtils):
        """
        Contains sub status about the resource
        """

        def __init__(
            self,
            state: str = None,
            healthState: str = None,
            message: str = None,
        ):
            self.state = state
            self.healthState = healthState
            self.message = message

        @property
        def state(self) -> str:
            return self._state

        @state.setter
        def state(self, s: str):
            self._state = s

        @property
        def healthState(self) -> str:
            return self._healthState

        @healthState.setter
        def healthState(self, s: str):
            self._healthState = s

        @property
        def message(self) -> str:
            """
            Gets message for this sub status.
            """
            return self._message

        @message.setter
        def message(self, e: str):
            self._message = e

        def _to_dict(self):
            """
            @override
            """
            return {
                "state": self.state,
                "healthState": self.healthState,
                "message": self.message,
            }

        def _hydrate(self, d: dict):
            """
            @override
            """
            if "state" in d:
                self.state = d["state"]
            if "healthState" in d:
                self.healthState = d["healthState"]
            if "message" in d:
                self.message = d["message"]

    class RoleSubStatus(SubStatus):
        """
        Contains scaled set role sub status about the resource.
        """

        def __init__(
            self,
            state: str = None,
            healthState: str = None,
            message: str = None,
            readyReplicas: int = None,
            replicas: int = None,
        ):
            super().__init__(state, healthState, message)
            self.readyReplicas = readyReplicas
            self.replicas = replicas

        @property
        def readyReplicas(self) -> int:
            """
            Number of replicas which are ready.
            """
            return self._readyReplicas

        @readyReplicas.setter
        def readyReplicas(self, rr: int):
            self._readyReplicas = rr

        @property
        def replicas(self) -> int:
            """
            Number of replicas requested.
            """
            return self._replicas

        @replicas.setter
        def replicas(self, r: int):
            self._replicas = r

        def _hydrate(self, d: dict):
            """
            @override
            """
            super()._hydrate(d)
            if "readyReplicas" in d:
                self.readyReplicas = d["readyReplicas"]
            if "replicas" in d:
                self.replicas = d["replicas"]

        def _to_dict(self):
            """
            @override
            """
            base = super()._to_dict()
            base["readyReplicas"] = getattr(self, "readyReplicas", None)
            base["replicas"] = getattr(self, "replicas", None)

            return base

    class Status(SerializationUtils):
        """
        Contains status information about the resource i.e. what the current state of the resource is

        CustomResource.status
        """

        class EndpointsStatus(SerializationUtils):
            """
            Contains endpoints status
            """

            def __init__(
                self,
                log_search_dashboard: str = None,
                metrics_dashboard: str = None,
            ) -> None:
                self.log_search_dashboard = log_search_dashboard
                self.metrics_dashboard = metrics_dashboard

            @property
            def log_search_dashboard(self) -> str:
                """
                The Log Search Dashboard endpoint for this custom resource.
                """
                return self._log_search_dashboard

            @log_search_dashboard.setter
            def log_search_dashboard(self, e: str):
                self._log_search_dashboard = e

            @property
            def metrics_dashboard(self) -> str:
                """
                The Metrics Dashboard endpoint for this custom resource.
                """
                return self._metrics_dashboard

            @metrics_dashboard.setter
            def metrics_dashboard(self, e: str):
                self._metrics_dashboard = e

            def _to_dict(self):
                """
                @override
                """
                return {
                    "logSearchDashboard": self.log_search_dashboard,
                    "metricsDashboard": self.metrics_dashboard,
                }

            def _hydrate(self, d: dict):
                """
                @override
                """
                if "logSearchDashboard" in d:
                    self.log_search_dashboard = d["logSearchDashboard"]
                if "metricsDashboard" in d:
                    self.metrics_dashboard = d["metricsDashboard"]

        def __init__(
            self,
            state: str = None,
            external_endpoint: str = None,
            log_search_dashboard: str = None,
            metrics_dashboard: str = None,
            observed_generation: int = None,
            message: str = None,
        ):
            self.state = state
            self.primaryEndpoint = external_endpoint
            self.log_search_dashboard = log_search_dashboard
            self.metrics_dashboard = metrics_dashboard
            self.observed_generation = observed_generation
            self.message = message

        @property
        def state(self) -> str:
            return self._state

        @state.setter
        def state(self, s: str):
            self._state = s

        @property
        def primaryEndpoint(self) -> str:
            """
            What endpoint you can hit this resource at
            """
            return self._primaryEndpoint

        @primaryEndpoint.setter
        def primaryEndpoint(self, e: str):
            self._primaryEndpoint = e

        @property
        def log_search_dashboard(self) -> str:
            """
            The Log Search Dashboard endpoint for this custom resource.
            """
            return self._log_search_dashboard

        @log_search_dashboard.setter
        def log_search_dashboard(self, e: str):
            self._log_search_dashboard = e

        @property
        def metrics_dashboard(self) -> str:
            """
            The Metrics Dashboard endpoint for this custom resource.
            """
            return self._metrics_dashboard

        @metrics_dashboard.setter
        def metrics_dashboard(self, e: str):
            self._metrics_dashboard = e

        @property
        def endpoints(self) -> EndpointsStatus:
            """
            The endpoints for this custom resource.
            """
            return getattr(self, "_endpoints", None)

        @endpoints.setter
        def endpoints(self, ep: EndpointsStatus):
            self._endpoints = ep

        @property
        def observed_generation(self) -> str:
            """
            Gets the most recent custom resource generation observed by the controller
            """
            return self._observed_generation

        @observed_generation.setter
        def observed_generation(self, e: str):
            self._observed_generation = e

        @property
        def message(self) -> str:
            """
            Gets message for this custom resource used by validation.
            """
            return self._message

        @message.setter
        def message(self, e: str):
            self._message = e

        def _to_dict(self):
            """
            @override
            """
            return {
                "primaryEndpoint": self.primaryEndpoint,
                "logSearchDashboard": self.log_search_dashboard,
                "metricsDashboard": self.metrics_dashboard,
                "endpoints": self.endpoints,
                "state": self.state,
                "observedGeneration": self.observed_generation,
                "message": self.message,
            }

        def _hydrate(self, d: dict):
            """
            @override
            """
            if "state" in d:
                self.state = d["state"]
            if "primaryEndpoint" in d:
                self.primaryEndpoint = d["primaryEndpoint"]
            if "logSearchDashboard" in d:
                self.log_search_dashboard = d["logSearchDashboard"]
            if "metricsDashboard" in d:
                self.metrics_dashboard = d["metricsDashboard"]
            if "endpoints" in d:
                self.endpoints = self.EndpointsStatus()
                self.endpoints._hydrate(d["endpoints"])
            if "observedGeneration" in d:
                self.observed_generation = d["observedGeneration"]
            if "message" in d:
                self.message = d["message"]

    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, s: Union[Status, tuple]):
        if type(s) is self.Status:
            self._status = s
        elif type(s) is tuple:
            self._status = self.Status(*s)
        else:
            raise TypeError(TYPE_ERROR.format(type(s), "status"))

    class Spec(SerializationUtils):
        """
        A kubernetes required field that contains information about the desired state of this object
        @see https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/#required-fields

        CustomResource.spec
        """

        def __init__(
            self,
            storage: "Storage" = None,
            services: "Services" = None,
            docker: DockerSpec = None,
        ):
            self.storage = storage if storage else self.Storage()
            self.services = services if services else self.Services()
            self.docker = docker if docker else DockerSpec()

        class Services(SerializationUtils):
            """
            Services property to register services of this custom resource.

            CustomResource.spec.services
            """

            def __init__(
                self,
                primary: ServiceSpec = None,
                readable_secondaries: ServiceSpec = None,
            ):
                self.primary = primary if primary else ServiceSpec()
                self.readable_secondaries = (
                    readable_secondaries
                    if readable_secondaries
                    else ServiceSpec()
                )

            @property
            def primary(self) -> ServiceSpec:
                """
                The primary service specification.
                @see VolumeClaim
                """
                return self._primary

            @primary.setter
            @enforcetype(ServiceSpec)
            def primary(self, s: ServiceSpec):
                self._primary = s

            @property
            def readable_secondaries(self) -> ServiceSpec:
                """
                The secondary service specification.
                @see VolumeClaim
                """
                return self._readable_secondaries

            @readable_secondaries.setter
            @enforcetype(ServiceSpec)
            def readable_secondaries(self, s: ServiceSpec):
                self._readable_secondaries = s

            def _hydrate(self, d: dict):
                """
                @override
                """
                if "primary" in d:
                    self.primary._hydrate(d["primary"])
                if "readableSecondaries" in d:
                    self.readable_secondaries._hydrate(d["readableSecondaries"])

            def _to_dict(self):
                """
                @override
                """
                return {
                    "primary": self.primary._to_dict(),
                    "readableSecondaries": self.readable_secondaries._to_dict(),
                }

        @property
        def services(self) -> Services:
            """
            @see Services
            """
            return self._services

        @services.setter
        @enforcetype(Services)
        def services(self, s: Services):
            self._services = s

        class Storage(SerializationUtils):
            """
            All the storage specs for a custom resource.

            CustomResource.spec.storage
            """

            def __init__(
                self,
                data: StorageSpec = None,
                logs: StorageSpec = None,
                backups: StorageSpec = None,
            ):
                self.data = data if data else StorageSpec()
                self.logs = logs if logs else StorageSpec()
                self.backups = backups if backups else StorageSpec()
                self.volumeClaimMounts = []

            @property
            def data(self) -> StorageSpec:
                """
                The storage spec to hold application data
                @see StorageSpec
                """
                return self._data

            @data.setter
            def data(self, s: StorageSpec):
                self._data = s

            @property
            def logs(self) -> StorageSpec:
                """
                The storage spec to hold log data
                @see StorageSpec
                """
                return self._logs

            @logs.setter
            def logs(self, s: StorageSpec):
                self._logs = s

            @property
            def backups(self) -> StorageSpec:
                """
                The storage spec to hold backups
                @see StorageSpec
                """
                return self._backups

            @backups.setter
            def backups(self, s):
                self._backups = s

            @property
            def volumeClaimMounts(self) -> list:
                return self._volumeClaimMounts

            @volumeClaimMounts.setter
            def volumeClaimMounts(self, vcm: Union[list, str]):
                if type(vcm) is str:
                    self._volumeClaimMounts = self._parse_mount_string(vcm)
                elif type(vcm) is list:
                    self._volumeClaimMounts = vcm
                else:
                    raise ValueError(
                        "Type '{}' is incompatible with property volumeClaimMounts. Need 'str' or 'list'".format(
                            type(vcm)
                        )
                    )

            @staticmethod
            def _parse_mount_string(mount_str: str):
                def _map_mount(mount):
                    parts = mount.split(":")
                    if len(parts) < 2:
                        raise CLIError(
                            "Volume claim mount must be in the form of [pvc-name]:[volume-type]:[optional-metadata]"
                        )
                    return {
                        "volumeClaimName": parts[0].strip(),
                        "volumeType": parts[1].strip(),
                    }

                return [_map_mount(mount) for mount in mount_str.split(",")]

            def _hydrate(self, d: dict):
                """
                @override
                """
                if "data" in d:
                    self.data._hydrate(d["data"])
                if "logs" in d:
                    self.logs._hydrate(d["logs"])
                if "backups" in d:
                    self.backups._hydrate(d["backups"])
                if "volumeClaimMounts" in d:
                    self.volumeClaimMounts = d["volumeClaimMounts"]

            def _to_dict(self):
                """
                @override
                """
                return {
                    "data": self.data._to_dict(),
                    "logs": self.logs._to_dict(),
                    "backups": self.backups._to_dict(),
                    "volumeClaimMounts": self.volumeClaimMounts,
                }

            def apply_args(self, **kwargs):
                key = "storage_class_logs"
                if key in kwargs and kwargs[key] is not None:
                    if not self.logs.volumes:
                        self.logs.volumes.append(VolumeClaim())
                    CustomResource._set_if_provided(
                        self.logs.volumes[0], "className", kwargs, key
                    )

                key = "volume_size_logs"
                if key in kwargs and kwargs[key] is not None:
                    if not self.logs.volumes:
                        self.logs.volumes.append(VolumeClaim())
                    CustomResource._set_if_provided(
                        self.logs.volumes[0], "size", kwargs, key
                    )

                key = "storage_class_data"
                if key in kwargs and kwargs[key] is not None:
                    if not self.data.volumes:
                        self.data.volumes.append(VolumeClaim())
                    CustomResource._set_if_provided(
                        self.data.volumes[0], "className", kwargs, key
                    )

                key = "volume_size_data"
                if key in kwargs and kwargs[key] is not None:
                    if not self.data.volumes:
                        self.data.volumes.append(VolumeClaim())
                    CustomResource._set_if_provided(
                        self.data.volumes[0], "size", kwargs, key
                    )

                key = "storage_class_backups"
                if key in kwargs and kwargs[key] is not None:
                    if not self.backups.volumes:
                        self.backups.volumes.append(VolumeClaim())
                    CustomResource._set_if_provided(
                        self.backups.volumes[0], "className", kwargs, key
                    )

                key = "volume_size_backups"
                if key in kwargs and kwargs[key] is not None:
                    if not self.backups.volumes:
                        self.backups.volumes.append(VolumeClaim())
                    CustomResource._set_if_provided(
                        self.backups.volumes[0], "size", kwargs, key
                    )

        @property
        def storage(self) -> Storage:
            """
            @see Storage
            """
            return self._storage

        @storage.setter
        @enforcetype(Storage)
        def storage(self, s: Storage):
            self._storage = s

        @property
        def docker(self) -> DockerSpec:
            """
            @see DockerSpec
            """
            return self._docker

        @docker.setter
        def docker(self, d: DockerSpec):
            self._docker = d

        def _hydrate(self, d: dict):
            """
            @override
            """

            if "services" in d:
                self.services._hydrate(d["services"])

            if "storage" in d:
                self.storage._hydrate(d["storage"])

            if "docker" in d:
                self.docker._hydrate(d["docker"])

        def _to_dict(self):
            """
            @override
            """
            return {
                "services": self.services._to_dict(),
                "storage": self.storage._to_dict(),
                "docker": self.docker._to_dict(),
            }

    @property
    def spec(self) -> Spec:
        """
        @see Spec
        """
        return self._spec

    @spec.setter
    @enforcetype(Spec)
    def spec(self, s: Spec):
        self._spec = s

    def encode(self):
        """
        Serializes this object into a dictionary
        :return: Dictionary representation of this object
        """
        return prune_dict(self._to_dict())

    def encodes(self):
        """
        Serializes this objects into a JSON string
        :return: JSON string representing this object
        """
        return json.dumps(self.encode())

    @staticmethod
    def decode(cls: "Type[CustomResource]", data: dict):
        """
        Takes JSON representation of this object and decodes into an object instance
        :param cls: The class to decode data into
        :param data: A dictionary used to hydrate a cls instance
        :returns: An instance of 'cls' hydrated by 'data'
        """
        if not issubclass(cls, CustomResource) and cls is not CustomResource:
            raise TypeError(
                "'{}' is not a valid subclass of CustomResource".format(cls)
            )

        ret = cls()
        ret._hydrate(trim_dict_entries(data))
        return ret

    @staticmethod
    def decodes(cls: "CustomResource", data: str):
        """
        Takes a dictionary representation of this object and decodes into an object instance
        :param cls: The class to decode data into
        :param data: A JSON string used to hydrate a cls instance
        :return: An instance of 'cls' hydrated by 'data'
        """
        return CustomResource.decode(cls, json.loads(data))

    @validator
    def _validate_storage_classes(self, client: "KubernetesClient"):
        """
        Ensures that all storage classes in the storage spec actually exist
        """
        STORAGE_CLASS_ERROR = "Storage class '{}' does not exist"

        logs = getattr(self.spec.storage, "logs", None)
        if logs and logs.volumes:
            for v in logs.volumes:
                if v.className and not client.storage_class_exists(v.className):
                    raise ValueError(STORAGE_CLASS_ERROR.format(v.className))

        data = getattr(self.spec.storage, "data", None)
        if data and data.volumes:
            for v in data.volumes:
                if v.className and not client.storage_class_exists(v.className):
                    raise ValueError(STORAGE_CLASS_ERROR.format(v.className))

        backups = getattr(self.spec.storage, "backups", None)
        if backups and backups.volumes:
            for v in backups.volumes:
                if v.className and not client.storage_class_exists(v.className):
                    raise ValueError(STORAGE_CLASS_ERROR.format(v.className))

    @validator
    def _validate_volume_claim_mounts(self, client: "KubernetesClient"):
        """
        Verifies various properties about volume claim mounts in the storage spec. Raises CLIErrors if anything
        is amiss
        """
        # There can be at most one backup claim mount
        num_backups = sum(
            1
            for m in self.spec.storage.volumeClaimMounts
            if m["volumeType"] == "backup"
        )
        if num_backups > 1:
            raise CLIError(
                "Volume claim mount with backup volume type cannot be specified multiple times"
            )

        # If there is a backup claim mount then should be no conflicting backup storage listed
        if num_backups == 1:
            backups = getattr(self.spec.storage, "backups", None)
            if (
                backups
                and backups.volumes
                and backups.volumes[0].className is not None
            ):
                raise CLIError(
                    "--storage-class-backups cannot be used with --volume-claim-mounts "
                    "when a volume claim mount is configured for backup purpose"
                )

        # Check that all volume claims exist in this namespace
        for mount in self.spec.storage.volumeClaimMounts:
            if not client.persistent_volume_claim_exists(
                mount["volumeClaimName"], self.metadata.namespace
            ):
                raise CLIError(
                    "Persistent volume claim %s not found"
                    % (mount["volumeClaimName"])
                )

    def _hydrate(self, d: dict):
        """
        @override
        """
        if "apiVersion" in d:
            self.apiVersion = d["apiVersion"]

        if "kind" in d:
            self.kind = d["kind"]

        if "spec" in d:
            self.spec._hydrate(d["spec"])

        if "metadata" in d:
            self.metadata._hydrate(d["metadata"])

        if "status" in d:
            self.status._hydrate(d["status"])

    def _to_dict(self):
        """
        @override
        """
        return {
            "apiVersion": self.apiVersion,
            "kind": self.kind,
            "spec": self.spec._to_dict(),
            "metadata": self.metadata._to_dict(),
            "status": self.status._to_dict(),
        }

    @abstractmethod
    def apply_args(self, **kwargs):

        self.spec.storage.apply_args(**kwargs)

        self._set_if_provided(self.metadata, "name", kwargs, "name")
        self._set_if_provided(self.metadata, "namespace", kwargs, "namespace")
        self._set_if_provided(
            self.spec.services.primary, "port", kwargs, "port"
        )
        self._set_if_provided(
            self.spec.storage,
            "volumeClaimMounts",
            kwargs,
            "volume_claim_mounts",
        )

    @staticmethod
    def _set_if_provided(obj, key, args, args_key):
        if args_key in args and args[args_key] is not None:
            setattr(obj, key, args[args_key])

    @staticmethod
    def _get_if_provided(args, args_key):
        if args_key in args and args[args_key] is not None:
            return args[args_key]
