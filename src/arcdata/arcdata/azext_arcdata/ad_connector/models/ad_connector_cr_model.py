# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from datetime import datetime
from typing import List
from azext_arcdata.core.constants import DNS_NAME_REQUIREMENTS
from azext_arcdata.core.util import name_meets_dns_requirements
from azext_arcdata.kubernetes_sdk.models import (
    CustomResource,
    SerializationUtils,
)

from typing import TYPE_CHECKING

# KubernetesClient is only needed for typehints, but causes a circular import. This is the python provided workaround
if TYPE_CHECKING:
    from azext_arcdata.kubernetes_sdk.client import KubernetesClient


class DomainControllerSpec(SerializationUtils):
    def __init__(self, hostname: str = None):
        self._hostname = hostname

    @property
    def hostname(self) -> str:
        return self._hostname

    @hostname.setter
    def hostname(self, value: str):
        self._hostname = value

    def _hydrate(self, d: dict):
        if "hostname" in d:
            self.hostname = d["hostname"]

    def _to_dict(self) -> dict:
        return {"hostname": self.hostname}


class DomainControllers(SerializationUtils):
    def __init__(
        self,
        primary_domain_controller: DomainControllerSpec = DomainControllerSpec(),
        secondary_domain_controllers: List[DomainControllerSpec] = [],
    ):
        self._primary_domain_controller = primary_domain_controller
        self._secondary_domain_controllers = secondary_domain_controllers

    @property
    def primary_domain_controller(self) -> DomainControllerSpec:
        return self._primary_domain_controller

    @primary_domain_controller.setter
    def primary_domain_controller(self, value: str):
        self._primary_domain_controller = value

    @property
    def secondary_domain_controllers(self) -> DomainControllerSpec:
        return self._secondary_domain_controllers

    @secondary_domain_controllers.setter
    def secondary_domain_controllers(self, value: List[DomainControllerSpec]):
        self._secondary_domain_controllers = value

    def _hydrate(self, d: dict):
        if (
            "primaryDomainController" in d
            and d["primaryDomainController"] is not None
        ):
            self.primary_domain_controller._hydrate(
                d["primaryDomainController"]
            )

        if "secondaryDomainControllers" in d:
            for dc in d["secondaryDomainControllers"]:
                domain_controller = DomainControllerSpec()
                domain_controller._hydrate(dc)
                self.secondary_domain_controllers.append(domain_controller)

    def _to_dict(self) -> dict:
        values = {
            "primaryDomainController": self.primary_domain_controller._to_dict()
        }

        if self.secondary_domain_controllers:
            values["secondaryDomainControllers"] = [
                dc._to_dict() for dc in self.secondary_domain_controllers
            ]

        return values


class ActiveDirectoryConnectorCustomResource(CustomResource):
    """
    Internal AD Connector Custom Resource object to be used for deployments.
    """

    def __init__(self):
        """
        Initializes a CR object with the given json.
        """
        super().__init__()

    class Spec(CustomResource.Spec):
        """
        @override CustomResource.spec
        """

        def __init__(self):
            super().__init__()
            self._active_directory = self.ActiveDirectory()
            self._dns = self.Dns()

        class ActiveDirectory(SerializationUtils):
            def __init__(
                self,
                realm: str = None,
                netbios_domain_name: str = None,
                domain_service_account_secret: str = None,
                service_account_provisioning: str = None,
                ou_distinguished_name: str = None,
                domain_controllers: DomainControllers = DomainControllers(),
            ):
                self._realm = realm
                self._netbios_domain_name = netbios_domain_name
                self._domain_service_account_secret = (
                    domain_service_account_secret
                )
                self._service_account_provisioning = (
                    service_account_provisioning
                )
                self._ou_distinguished_name = ou_distinguished_name
                self._domain_controllers = domain_controllers

            @property
            def realm(self) -> str:
                return self._realm

            @realm.setter
            def realm(self, value: str):
                self._realm = value

            @property
            def netbios_domain_name(self) -> str:
                return self._netbios_domain_name

            @netbios_domain_name.setter
            def netbios_domain_name(self, value: str):
                self._netbios_domain_name = value

            @property
            def ou_distinguished_name(self) -> str:
                return self._ou_distinguished_name

            @ou_distinguished_name.setter
            def ou_distinguished_name(self, value: str):
                self._ou_distinguished_name = value

            @property
            def domain_service_account_secret(self) -> str:
                return self._domain_service_account_secret

            @domain_service_account_secret.setter
            def domain_service_account_secret(self, value: str):
                self._domain_service_account_secret = value

            @property
            def service_account_provisioning(self) -> str:
                return self._service_account_provisioning

            @service_account_provisioning.setter
            def service_account_provisioning(self, value: str):
                self._service_account_provisioning = value

            @property
            def domain_controllers(self) -> str:
                return self._domain_controllers

            @domain_controllers.setter
            def domain_controllers(self, value: str):
                self._domain_controllers = value

            def _hydrate(self, d: dict):
                if "realm" in d:
                    self.realm = d["realm"]
                if "domainServiceAccountSecret" in d:
                    self.domain_service_account_secret = d[
                        "domainServiceAccountSecret"
                    ]
                if "serviceAccountProvisioning" in d:
                    self.service_account_provisioning = d[
                        "serviceAccountProvisioning"
                    ]
                if "ouDistinguishedName" in d:
                    self.ou_distinguished_name = d["ouDistinguishedName"]
                if "netbiosDomainName" in d:
                    self.netbios_domain_name = d["netbiosDomainName"]
                if "domainControllers" in d:
                    self.domain_controllers._hydrate(d["domainControllers"])

            def _to_dict(self) -> dict:
                return {
                    "realm": self.realm,
                    "netbiosDomainName": self.netbios_domain_name,
                    "ouDistinguishedName": self.ou_distinguished_name,
                    "serviceAccountProvisioning": self.service_account_provisioning,
                    "domainServiceAccountSecret": self.domain_service_account_secret,
                    "domainControllers": self._domain_controllers._to_dict(),
                }

        class Dns(SerializationUtils):
            def __init__(
                self,
                domain_name: str = None,
                replicas: int = 1,
                nameserver_addresses: List[str] = [],
                prefer_k8s_dns_ptr_lookups: bool = True,
            ):
                self._domain_name = domain_name
                self._replicas = replicas
                self._nameserver_addresses = (nameserver_addresses,)
                self._prefer_k8s_dns_ptr_lookups = prefer_k8s_dns_ptr_lookups

            @property
            def domain_name(self) -> str:
                return self._domain_name

            @domain_name.setter
            def domain_name(self, value: str):
                self._domain_name = value

            @property
            def replicas(self) -> int:
                return self._replicas

            @replicas.setter
            def replicas(self, value: int):
                self._replicas = value

            @property
            def nameserver_addresses(self) -> List[str]:
                return self._nameserver_addresses

            @nameserver_addresses.setter
            def nameserver_addresses(self, value: List[str]):
                self._nameserver_addresses = value

            @property
            def prefer_k8s_dns_ptr_lookups(self) -> bool:
                return self._prefer_k8s_dns_ptr_lookups

            @prefer_k8s_dns_ptr_lookups.setter
            def prefer_k8s_dns_ptr_lookups(self, value: bool):
                self._prefer_k8s_dns_ptr_lookups = value

            def _hydrate(self, d: dict):
                if "domainName" in d:
                    self.domain_name = d["domainName"]
                if "nameserverIPAddresses" in d:
                    self.nameserver_addresses = d["nameserverIPAddresses"]
                if "replicas" in d:
                    self.replicas = d["replicas"]
                if "preferK8sDnsForPtrLookups" in d:
                    self.prefer_k8s_dns_ptr_lookups = d[
                        "preferK8sDnsForPtrLookups"
                    ]

            def _to_dict(self) -> dict:
                return {
                    "domainName": self.domain_name,
                    "nameserverIPAddresses": self.nameserver_addresses,
                    "replicas": self.replicas,
                    "preferK8sDnsForPtrLookups": self.prefer_k8s_dns_ptr_lookups,
                }

        @property
        def active_directory(self) -> ActiveDirectory:
            return self._active_directory

        @active_directory.setter
        def activeDirectory(self, value: ActiveDirectory):
            self._active_directory = value

        @property
        def dns(self) -> Dns:
            return self._dns

        @dns.setter
        def dns(self, value: Dns):
            self._dns = value

        def _to_dict(self) -> dict:
            return {
                "activeDirectory": self.active_directory._to_dict(),
                "dns": self.dns._to_dict(),
            }

        def _hydrate(self, d: dict):
            super()._hydrate(d)
            if "activeDirectory" in d:
                self.active_directory._hydrate(d["activeDirectory"])

            if "dns" in d:
                self.dns._hydrate(d["dns"])

    class Metadata(CustomResource.Metadata):
        """
        @override CustomResource.metadata
        """

        ad_connector_name_max_length = 40

        @CustomResource.Metadata.name.setter
        def name(self, n: str):
            if not n:
                raise ValueError(
                    "Active Directory connector name cannot be empty"
                )

            if len(n) > self.ad_connector_name_max_length:
                raise ValueError(
                    "Active Directory connector name '{}' exceeds {} character length limit".format(
                        n, self.ad_connector_name_max_length
                    )
                )

            if not name_meets_dns_requirements(n):
                raise ValueError(
                    "Active Directory connector name '{}' does not follow DNS requirements: {}".format(
                        n, DNS_NAME_REQUIREMENTS
                    )
                )

            self._name = n

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

        def _hydrate(self, d: dict):
            """
            @override
            """
            super()._hydrate(d)
            if "state" in d:
                self.state = d["state"]
            if "observedGeneration" in d:
                self.observed_generation = d["observedGeneration"]
            if "message" in d:
                self.message = d["message"]

        def _to_dict(self):
            """
            @override
            """
            return {
                "state": self.state,
                "observedGeneration": self.observed_generation,
                "message": self.message,
            }

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
