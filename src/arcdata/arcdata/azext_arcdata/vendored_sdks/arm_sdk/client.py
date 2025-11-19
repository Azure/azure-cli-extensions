# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.ad_connector.constants import (
    ACCOUNT_PROVISIONING_MODE_AUTOMATIC,
)
from azext_arcdata.ad_connector.util import (
    _parse_nameserver_addresses,
    _parse_num_replicas,
    _parse_prefer_k8s_dns,
)
from azext_arcdata.core.constants import (
    DEFAULT_IMAGE_POLICY,
    DEFAULT_IMAGE_TAG,
    DEFAULT_REGISTRY,
    DEFAULT_REPOSITORY,
    INDIRECT,
)
from azext_arcdata.core.util import BOOLEAN_STATES
from azext_arcdata.vendored_sdks.arm_sdk.azure.constants import (
    API_VERSION,
    ARC_DATASERVICES_EXTENSION_RELEASE_TRAIN,
    ARC_DATASERVICES_EXTENSION_VERSION,
    EXT_VERSION_ARM_API_VERSION_MAP,
    IMAGE_TAG_EXT_VERSION_MAP,
    INSTANCE_TYPE_AD_CONNECTOR,
    INSTANCE_TYPE_DATA_CONTROLLER,
    INSTANCE_TYPE_FAILOVER_GROUP,
    INSTANCE_TYPE_SQL,
)
from azext_arcdata.sqlmi.constants import (
    SQLMI_BC_DEFAULT_REPLICAS,
    SQLMI_GP_DEFAULT_REPLICAS,
    SQLMI_TIER_BUSINESS_CRITICAL,
    SQLMI_TIER_BUSINESS_CRITICAL_SHORT,
    SQLMI_TIER_GENERAL_PURPOSE,
    SQLMI_TIERS_MAP,
    SQLMI_TIMEZONE,
    SQLMI_TRACEFLAGS,
    SQLMI_MEMORYLIMIT,
)
from azext_arcdata.sqlmi.settings import (
    parse_traceflags,
    parse_dataGitoIntInMb,
)
from azext_arcdata.sqlmi.util import _parse_supported_ad_encryption_types
from ._util import (
    conditional_retry,
    dict_to_dot_notation,
    wait,
    poll_provisioning_state,
)
from ._arm_template import ARMTemplate
from .azure.azure_resource_client import AzureResourceClient
from ._arm_client import arm_clients
from .swagger.swagger_1_2_0 import AzureArcDataManagementClient
from .swagger.swagger_1_2_0.models import (
    ActiveDirectoryConnectorResource,
    ActiveDirectoryConnectorProperties,
    ActiveDirectoryConnectorSpec,
    ActiveDirectoryConnectorDomainDetails,
    ActiveDirectoryConnectorDNSDetails,
    ActiveDirectoryDomainControllers,
    ActiveDirectoryDomainController,
    DataControllerResource,
    FailoverGroupResource,
    FailoverGroupProperties,
    FailoverGroupSpec,
    SqlManagedInstance,
    ExtendedLocation,
    SqlManagedInstanceProperties,
    SqlManagedInstanceSku,
    BasicLoginInformation,
    SqlManagedInstanceK8SRaw,
    SqlManagedInstanceK8SSpec,
    K8SScheduling,
    K8SSchedulingOptions,
    K8SResourceRequirements,
)

from azext_arcdata.core.env import Env
from azext_arcdata.core.prompt import prompt_assert
from knack.log import get_logger

import azure.core.exceptions as exceptions
import os
import json
import requests
import pydash as _
import time

__all__ = ["ArmClient"]

logger = get_logger(__name__)


class ArmClient(object):
    def __init__(self, azure_credential, subscription):
        self._arm_clients = arm_clients(subscription, azure_credential)
        self._azure_credential = azure_credential
        self._bearer = azure_credential.get_token().token
        self._subscription_id = subscription
        self._mgmt_client = AzureArcDataManagementClient(
            subscription_id=self._subscription_id,
        )
        self._resource_client = AzureResourceClient(self._subscription_id)
        self._headers = {
            "Authorization": "Bearer {}".format(self._bearer),
            "Content-Type": "application/json",
        }

    # ======================================================================== #
    # == DC ================================================================== #
    # ======================================================================== #

    def create_dc(
        self,
        resource_group,
        name,
        custom_location,
        connectivity_mode,
        cluster_name,
        namespace,
        path,
        storage_class=None,
        infrastructure=None,
        image_tag=None,
        auto_upload_metrics=None,
        auto_upload_logs=None,
        polling=True,
        least_privilege=None,
    ):
        dc_client = self._arm_clients.dc
        try:
            # -- check existing dc to avoid dc recreate --
            result = dc_client.check_if_dc_exists(name, resource_group)
            if result:
                raise Exception(
                    f"A Data Controller {name} has already been created."
                )

            config_file = os.path.join(path, "control.json")
            logger.debug("Configuration profile: %s", config_file)

            with open(config_file, encoding="utf-8") as input_file:
                control = dict_to_dot_notation(json.load(input_file))

            # -- high order control.json, merge in input to control.json --
            spec = control.spec
            spec.settings.controller.displayName = name
            spec.credentials.controllerAdmin = "controller-login-secret"

            # -- docker --

            # Set to null initially if not specified anywhere
            image_tag = (
                image_tag
                or Env.get("DOCKER_IMAGE_TAG")
                or (spec.docker.imageTag if hasattr(spec, "docker") else None)
            )

            extension = dc_client.get_extension(cluster_name, resource_group)
            if extension:
                # Extension exists

                extension_name = extension["name"]
                train = extension["properties"].get(
                    "releaseTrain", ARC_DATASERVICES_EXTENSION_RELEASE_TRAIN
                )

                # NOTE: We disregard the EXTENSION_VERSION env var if the extension exists
                version = extension["properties"].get("version")

                extension_docker_spec: dict = (
                    dc_client.get_docker_details_from_extension(
                        cluster_name, resource_group
                    )
                )

                # These settings may not be in the extension ARM resource so use defaults
                registry = extension_docker_spec.get(
                    "registry", DEFAULT_REGISTRY
                )
                repository = extension_docker_spec.get(
                    "repository", DEFAULT_REPOSITORY
                )
                image_pull_policy = extension_docker_spec.get(
                    "imagePullPolicy", DEFAULT_IMAGE_POLICY
                )

                if image_tag:
                    # User specified a docker image tag via either CLI arg or env var or control.json

                    # MCR
                    if registry == DEFAULT_REGISTRY:
                        # Check if the image tag is supported
                        if image_tag not in IMAGE_TAG_EXT_VERSION_MAP.keys():
                            raise Exception(
                                f"Image tag {image_tag} is not supported by this version of the arcdata extension."
                            )

                        # Check if the extension version is aligned with the docker image tag
                        if version != IMAGE_TAG_EXT_VERSION_MAP.get(image_tag):
                            raise Exception(
                                f"The currently installed Arc data services extension is using version {version} "
                                f"The docker image tag needs to be aligned to this version."
                                f"Please use the corresponding docker image tag for this extension version: {self._get_image_tag_from_extension_version(version)}.\n "
                                f"See https://aka.ms/arc-data-services-version-log for more information."
                            )
                    else:
                        # Get the extension's docker image tag
                        extension_image_tag = extension_docker_spec.get(
                            "imageTag"
                        )

                        # Make sure the user specified docker image tag is aligned with the extension's docker image tag
                        if image_tag != extension_image_tag:
                            raise Exception(
                                f"The currently installed Arc data services extension is using image tag {extension_image_tag} \n"
                                f"The specified Arc data controller image tag needs to be the same. "
                            )
                else:
                    # User did not specify a docker image tag via either CLI arg or env var

                    extension_image_tag = extension_docker_spec.get(
                        "imageTag", None
                    )

                    if extension_image_tag:
                        # Use the extension's docker image tag to deploy the DC if it exists
                        image_tag = extension_image_tag
                    else:
                        # Find a docker image tag that is supported by the extension
                        image_tag = self._get_image_tag_from_extension_version(
                            version
                        )

            else:
                # Extension does not exist

                registry = (
                    Env.get("DOCKER_REGISTRY")
                    or (
                        spec.docker.registry
                        if hasattr(spec, "docker")
                        else None
                    )
                    or DEFAULT_REGISTRY
                )
                repository = (
                    Env.get("DOCKER_REPOSITORY")
                    or (
                        spec.docker.repository
                        if hasattr(spec, "docker")
                        else None
                    )
                    or DEFAULT_REPOSITORY
                )
                image_pull_policy = (
                    Env.get("DOCKER_IMAGE_POLICY")
                    or (
                        spec.docker.imagePullPolicy
                        if hasattr(spec, "docker")
                        else None
                    )
                    or DEFAULT_IMAGE_POLICY
                )

                extension_name = f"{custom_location}-ext"
                train = os.getenv(
                    "ARC_DATASERVICES_EXTENSION_RELEASE_TRAIN",
                    ARC_DATASERVICES_EXTENSION_RELEASE_TRAIN,
                )

                if image_tag:
                    # User specified a docker image tag via either CLI arg or env var or control.json

                    if registry == DEFAULT_REGISTRY:
                        # User is using MCR

                        # Check if the image tag is supported
                        if image_tag not in IMAGE_TAG_EXT_VERSION_MAP.keys():
                            raise Exception(
                                f"Image tag {image_tag} is not supported by this version of the arcdata extension."
                            )

                        # Get extension version if specified via env var
                        version = os.getenv(
                            "ARC_DATASERVICES_EXTENSION_VERSION_TAG"
                        )

                        # Check if the extension version is aligned with the docker image tag
                        if (
                            version
                            and version
                            != IMAGE_TAG_EXT_VERSION_MAP.get(image_tag)
                        ):
                            raise Exception(
                                f"The specified Arc data controller image tag {image_tag} is not aligned "
                                f"to the given Arc data services extension version {version} \n"
                                f"Please see https://aka.ms/arc-data-services-version-log for more information."
                            )
                        else:
                            # If not specified, we get the corresponding extension version from the docker image tag
                            version = IMAGE_TAG_EXT_VERSION_MAP.get(
                                image_tag, ARC_DATASERVICES_EXTENSION_VERSION
                            )
                    else:
                        # User is using a private registry
                        # Extension doesn't exist

                        # Get extension version if specified via env var
                        version = os.getenv(
                            "ARC_DATASERVICES_EXTENSION_VERSION_TAG", None
                        )

                        if not version:
                            # If not specified, we try to get the corresponding extension version from the docker image tag
                            version = IMAGE_TAG_EXT_VERSION_MAP.get(
                                image_tag, ARC_DATASERVICES_EXTENSION_VERSION
                            )

                else:
                    # User did not specify a docker image tag via either CLI arg or env var
                    # Nor could we find the Arc data services extension in the cluster

                    # Get extension version if specified via env var
                    version = os.getenv(
                        "ARC_DATASERVICES_EXTENSION_VERSION_TAG",
                        ARC_DATASERVICES_EXTENSION_VERSION,
                    )

                    # Try to the corresponding image tag so that the DC and helm chart are aligned
                    image_tag = self._get_image_tag_from_extension_version(
                        version
                    )

            spec.docker = dict_to_dot_notation(
                {
                    "registry": registry,
                    "repository": repository,
                    "imageTag": image_tag,
                    "imagePullPolicy": image_pull_policy,
                }
            )

            # -- azure --
            azure = spec.settings.azure
            azure.connectionMode = connectivity_mode
            azure.location = dc_client.get_connected_cluster_location(
                cluster_name, resource_group
            )
            azure.resourceGroup = resource_group
            azure.subscription = self._subscription_id

            # -- log analytics --
            log_analytics = {"workspace_id": "", "primary_key": ""}

            if auto_upload_metrics is not None:
                azure.autoUploadMetrics = auto_upload_metrics
            if auto_upload_logs is not None:
                azure.autoUploadLogs = auto_upload_logs

                if BOOLEAN_STATES(auto_upload_logs):
                    w_id = Env.get("WORKSPACE_ID")
                    w_key = Env.get("WORKSPACE_SHARED_KEY")
                    if not w_id:
                        w_id = prompt_assert("Log Analytics workspace ID: ")
                    if not w_key:
                        w_key = prompt_assert("Log Analytics primary key: ")

                    log_analytics["workspace_id"] = w_id
                    log_analytics["primary_key"] = w_key

            # -- infrastructure --
            spec.infrastructure = infrastructure or spec.infrastructure
            spec.infrastructure = spec.infrastructure or "onpremises"

            # -- storage --
            storage = spec.storage
            storage.data.className = storage_class or storage.data.className
            storage.logs.className = storage_class or storage.logs.className

            if not storage.data.className or not storage.logs.className:
                storage_class = prompt_assert("Storage class: ")
                storage.data.className = storage_class
                storage.logs.className = storage_class

            # -- least privilege --
            is_least_privilege = str(least_privilege).lower() == "true"
            if is_least_privilege:
                print(
                    "Onboarding in least privileges mode, please ensure you have "
                    "pre-created the kubernetes \nservice accounts with the access "
                    "control pre-requisites.\n"
                    "More details:\n"
                    "https://aka.ms/arcdata_least_privilege"
                )

            # -- set api version --
            api_version = EXT_VERSION_ARM_API_VERSION_MAP.get(
                version, API_VERSION
            )

            properties = {
                "metrics_credentials": Env.get_log_and_metrics_credentials(),
                "custom_location": custom_location,
                "cluster_name": cluster_name,
                "extension_name": extension_name,
                "extension_train": train,
                "extension_version": version,
                "is_least_privilege": is_least_privilege,
                "resource_group": resource_group,
                "api_version": api_version,
                "log_analytics": log_analytics,
                "namespace": dc_client.resolve_namespace(
                    namespace,
                    custom_location,
                    cluster_name,
                    resource_group,
                ),
                "dc_name": name,
            }

            # -- attempt to create cluster --
            print("")
            print("Deploying data controller")
            print("")
            print(
                "NOTE: Data controller creation can take a significant "
                "amount of time depending \non configuration, network "
                "speed, and the number of nodes in the cluster."
            )
            print("")

            # -- make dc create request via ARM --
            tmpl = ARMTemplate(dc_client).render_dc(control.to_dict, properties)

            return dc_client.create(name, resource_group, tmpl, polling=polling)
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def __create_depreciated_dc__(
        self,
        resource_group,
        name,
        location,
        custom_location,
        connectivity_mode,
        path,
        storage_class=None,
        infrastructure=None,
        image_tag=None,
        auto_upload_metrics=None,
        auto_upload_logs=None,
        polling=True,
    ):
        """
        This is the original dc create that expected the following to already
        be created:
        - extensions
        - roll assignments
        - custom-location

        This will eventually be removed.
        """
        dc_client = self._arm_clients.dc
        try:
            # -- check existing dc to avoid dc recreate --
            result = dc_client.check_if_dc_exists(name, resource_group)
            if result:
                raise Exception(
                    f"A Data Controller {name} has already been created."
                )

            # -- check that the extension is installed and get supported ARM API version--
            api_version = dc_client.resolve_api_version(
                INSTANCE_TYPE_DATA_CONTROLLER, custom_location, resource_group
            )

            config_file = os.path.join(path, "control.json")
            logger.debug("Configuration profile: %s", config_file)

            with open(config_file, encoding="utf-8") as input_file:
                control = dict_to_dot_notation(json.load(input_file))

            # -- high order control.json, merge in input to control.json --
            spec = control.spec
            spec.settings.controller.displayName = name
            spec.credentials.controllerAdmin = "controller-login-secret"

            # -- docker --
            user_specified_image_tag = (
                image_tag
                or Env.get("DOCKER_IMAGE_TAG")
                or (spec.docker.imageTag if hasattr(spec, "docker") else None)
            )

            cluster_name = dc_client.get_cluster_name(
                name, resource_group, custom_location
            )
            extension_docker_spec: dict = (
                dc_client.get_docker_details_from_extension(
                    cluster_name, resource_group
                )
            )
            extension_image_tag = extension_docker_spec.get("imageTag")

            # Check if the user specified image tag is aligned with the extension image tag
            if (
                user_specified_image_tag
                and user_specified_image_tag != extension_image_tag
            ):
                raise Exception(
                    f"The specified Arc data controller image tag {user_specified_image_tag} does not match the Arc data services extension image tag {extension_image_tag}"
                )

            spec.docker = dict_to_dot_notation(extension_docker_spec)

            # -- azure --
            azure = spec.settings.azure
            azure.connectionMode = connectivity_mode
            azure.location = location
            azure.resourceGroup = resource_group
            azure.subscription = self._subscription_id

            # -- log analytics --
            log_analytics = None
            if auto_upload_metrics is not None:
                azure.autoUploadMetrics = auto_upload_metrics
            if auto_upload_logs is not None:
                azure.autoUploadLogs = auto_upload_logs

                if BOOLEAN_STATES(auto_upload_logs):
                    w_id = Env.get("WORKSPACE_ID")
                    w_key = Env.get("WORKSPACE_SHARED_KEY")
                    if not w_id:
                        w_id = prompt_assert("Log Analytics workspace ID: ")
                    if not w_key:
                        w_key = prompt_assert("Log Analytics primary key: ")
                    log_analytics = {"workspace_id": w_id, "primary_key": w_key}

            # -- infrastructure --
            spec.infrastructure = infrastructure or spec.infrastructure
            spec.infrastructure = spec.infrastructure or "onpremises"

            # -- storage --
            storage = spec.storage
            storage.data.className = storage_class or storage.data.className
            storage.logs.className = storage_class or storage.logs.className

            if not storage.data.className or not storage.logs.className:
                storage_class = prompt_assert("Storage class: ")
                storage.data.className = storage_class
                storage.logs.className = storage_class

            # -- attempt to create cluster --
            print("")
            print("Deploying data controller")
            print("")
            print(
                "NOTE: Data controller creation can take a significant "
                "amount of time depending \non configuration, network "
                "speed, and the number of nodes in the cluster."
            )
            print("")

            return dc_client.__create_depreciated_dc__(
                control,
                resource_group,
                custom_location,
                Env.get_log_and_metrics_credentials(),
                log_analytics,
                polling=polling,
                api_version=api_version,
            )
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def get_dc(self, resource_group, name):
        return self._arm_clients.dc.get(name, resource_group)

    def list_dc(self, resource_group=None, custom_location=None):
        return self._arm_clients.dc.list(resource_group, custom_location)

    def update_dc(
        self,
        resource_group,
        name,
        polling=True,
        auto_upload_logs=None,
        auto_upload_metrics=None,
        desired_version=None,
    ):
        dc_client = self._arm_clients.dc

        # Apply the upgrade first if specified
        if desired_version:
            self.upgrade_dc(
                name=name,
                resource_group=resource_group,
                target=desired_version,
                polling=polling,
            )

        # Get the API version for the DC resource
        dc = self.get_dc(name=name, resource_group=resource_group)

        # Get latest API version supported by extension
        custom_location = dc.extended_location.name.split("/")[-1]
        api_version = dc_client.resolve_api_version(
            INSTANCE_TYPE_DATA_CONTROLLER, custom_location, resource_group
        )

        return self._resource_client.update_dc_resource(
            name,
            resource_group,
            auto_upload_logs=auto_upload_logs,
            auto_upload_metrics=auto_upload_metrics,
            polling=polling,
            api_version=api_version,
        )

    def delete_dc(self, resource_group, name, polling=True):
        return self._arm_clients.dc.delete(
            name, resource_group, polling=polling
        )

    def upgrade_dc(
        self,
        resource_group,
        name,
        target,
        dry_run=False,
        polling=True,
    ):
        self._validate_dc_child_mi_versions(resource_group, name)

        return self._arm_clients.dc.upgrade(
            name,
            resource_group,
            target,
            dry_run=dry_run,
            polling=polling,
        )

    def export_upload_log_and_metrics_dc(self, path):
        self._resource_client.upload_dc_resource(path)

    def _get_image_tag_from_extension_version(self, version):
        # Reverse lookup image tag by given extension version
        return {
            version: image_tag
            for image_tag, version in IMAGE_TAG_EXT_VERSION_MAP.items()
        }.get(version, DEFAULT_IMAGE_TAG)

    def _validate_dc_child_mi_versions(self, resource_group, name):
        """
        Validates that all Arc-enabled SQL Managed Instances in the cluster
        are aligned to the same image version as the data controller.
        """

        dc = self.get_dc(name=name, resource_group=resource_group)
        dc_image_version = dc.properties.k8_s_raw["spec"]["docker"]["imageTag"]

        custom_location = dc.extended_location.name.split("/")[-1]

        sqls = self.list_sqlmi(resource_group, custom_location)
        for sql in sqls:
            sql_version = sql.properties.k8_s_raw.additional_properties.get(
                "status", []
            ).get("runningVersion")

            if sql_version and sql_version != dc_image_version:
                raise Exception(
                    "All Arc-enabled SQL Managed Instances in the cluster must first be "
                    "aligned to the same image version as the data controller ({0}) "
                    "before the data controller can be upgraded.".format(
                        dc_image_version
                    )
                )

    # ======================================================================== #
    # == SQL MI ============================================================== #
    # ======================================================================== #

    def get_mi_resource_url(
        self, resource_group, resource_name, api_version=API_VERSION
    ):
        return (
            "https://management.azure.com/subscriptions/{}/resourceGroups"
            "/{}/providers/Microsoft.AzureArcData/sqlManagedInstances/{}"
            "?api-version={}".format(
                self._subscription_id,
                resource_group,
                resource_name,
                api_version,
            )
        )

    def create_sqlmi(
        self,
        name,
        location,
        custom_location,
        resource_group,
        path=None,
        replicas=None,
        orchestrator_replicas=None,
        readable_secondaries=None,
        sync_secondary_to_commit=None,
        cores_limit=None,
        cores_request=None,
        memory_limit=None,
        memory_request=None,
        storage_class_data=None,
        storage_class_logs=None,
        storage_class_datalogs=None,
        storage_class_backups=None,
        storage_class_orchestrator_logs=None,
        volume_size_data=None,
        volume_size_logs=None,
        volume_size_datalogs=None,
        volume_size_backups=None,
        volume_size_orchestrator_logs=None,
        license_type=None,
        tier=None,
        dev=None,
        ad_connector_name=None,
        ad_connector_namespace=None,
        ad_account_name=None,
        keytab_secret=None,
        ad_encryption_types=None,
        tde_mode=None,
        tde_protector_secret=None,
        primary_dns_name=None,
        primary_port_number=None,
        secondary_dns_name=None,
        secondary_port_number=None,
        polling=True,
        retention_days=None,
        time_zone=None,
        service_type=None,
        trace_flags=None,
        private_key_file=None,
        # -- Not Support for now --
        # tde_protector_public_key_file=None,
        # tde_protector_private_key_file=None,
        # noexternal_endpoint=None,
        # certificate_public_key_file=None,
        # certificate_private_key_file=None,
        # service_certificate_secret=None,
        # admin_login_secret=None,
        # collation=None,
        # language=None,
        # agent_enabled=None,
        # labels=None,
        # annotations=None,
        # service_labels=None,
        # service_annotations=None,
        # storage_labels=None,
        # storage_annotations=None,
    ):
        dc_client = self._arm_clients.dc
        try:
            # -- check existing sqlmi's to avoid duplicate sqlmi create --
            sqlmi_names = []
            for mi in self.list_sqlmi(resource_group):
                sqlmi_names.append(mi.as_dict()["name"])
            if name in sqlmi_names:
                raise ValueError(
                    "A Managed SQL Instance {name} has already been "
                    "created.".format(name=name)
                )

            # -- acquire sqlmi username/password --
            cred = Env.get_sqlmi_credentials()

            # Get latest API version supported by extension
            api_version = dc_client.resolve_api_version(
                INSTANCE_TYPE_SQL, custom_location, resource_group
            )

            # -- properties --
            #
            BASE = os.path.dirname(os.path.realpath(__file__))
            TEMPLATE_DIR = os.path.join(BASE, "templates")
            SQLMI_SPEC_MERGE = os.path.join(
                TEMPLATE_DIR, "sqlmi-create-properties.json"
            )
            with open(path or SQLMI_SPEC_MERGE, encoding="utf-8") as input_file:
                all_prop = json.load(input_file)
                logger.debug(json.dumps(all_prop, indent=4))
            k8s = all_prop["properties"]["k8sRaw"]

            # -- storage --
            if storage_class_data:
                k8s["spec"]["storage"]["data"]["volumes"][0][
                    "className"
                ] = storage_class_data
            if storage_class_logs:
                k8s["spec"]["storage"]["logs"]["volumes"][0][
                    "className"
                ] = storage_class_logs
            if storage_class_datalogs:
                k8s["spec"]["storage"]["datalogs"]["volumes"][0][
                    "className"
                ] = storage_class_datalogs
            if storage_class_backups:
                k8s["spec"]["storage"]["backups"]["volumes"][0][
                    "className"
                ] = storage_class_backups
            if storage_class_orchestrator_logs:
                k8s["spec"]["storage"]["haOrchestratorLogs"]["volumes"][0][
                    "className"
                ] = storage_class_orchestrator_logs
            if volume_size_data:
                k8s["spec"]["storage"]["data"]["volumes"][0][
                    "size"
                ] = volume_size_data
            if volume_size_logs:
                k8s["spec"]["storage"]["logs"]["volumes"][0][
                    "size"
                ] = volume_size_logs
            if volume_size_datalogs:
                k8s["spec"]["storage"]["datalogs"]["volumes"][0][
                    "size"
                ] = volume_size_datalogs
            if volume_size_backups:
                k8s["spec"]["storage"]["backups"]["volumes"][0][
                    "size"
                ] = volume_size_backups
            if volume_size_orchestrator_logs:
                k8s["spec"]["storage"]["haOrchestratorLogs"]["volumes"][0][
                    "size"
                ] = volume_size_orchestrator_logs

            # ==== Billing ====================================================

            # -- dev --
            if dev:
                k8s["spec"]["dev"] = True

            # -- scheduling --
            if cores_limit:
                k8s["spec"]["scheduling"]["default"]["resources"]["limits"][
                    "cpu"
                ] = cores_limit
            if cores_request:
                k8s["spec"]["scheduling"]["default"]["resources"]["requests"][
                    "cpu"
                ] = cores_request
            if memory_limit:
                k8s["spec"]["scheduling"]["default"]["resources"]["limits"][
                    "memory"
                ] = memory_limit
            if memory_request:
                k8s["spec"]["scheduling"]["default"]["resources"]["requests"][
                    "memory"
                ] = memory_request

            # -- tier & replicas --
            if tier and tier in [
                SQLMI_TIER_BUSINESS_CRITICAL,
                SQLMI_TIER_BUSINESS_CRITICAL_SHORT,
            ]:
                tier = SQLMI_TIER_BUSINESS_CRITICAL
                replicas = int(replicas or SQLMI_BC_DEFAULT_REPLICAS)
            else:
                tier = SQLMI_TIER_GENERAL_PURPOSE
                replicas = SQLMI_GP_DEFAULT_REPLICAS

            k8s["spec"]["replicas"] = replicas
            all_prop["sku"]["tier"] = tier

            if orchestrator_replicas:
                k8s["spec"]["orchestratorReplicas"] = int(orchestrator_replicas)
            # -- readable secondaries --
            if readable_secondaries:
                k8s["spec"]["readableSecondaries"] = int(readable_secondaries)

            # -- synchronized secondary to commit --
            if sync_secondary_to_commit:
                k8s["spec"]["syncSecondaryToCommit"] = int(
                    sync_secondary_to_commit
                )

            # -- license type --
            if license_type:
                all_prop["properties"]["licenseType"] = license_type

            if retention_days is not None:
                k8s["spec"]["backup"]["retentionPeriodInDays"] = int(
                    retention_days
                )

            # -- administrative --
            if time_zone:
                k8s["spec"]["settings"][SQLMI_TIMEZONE] = time_zone

            if memory_limit:
                k8s["spec"]["settings"][SQLMI_MEMORYLIMIT] = (
                    parse_dataGitoIntInMb(memory_limit)
                )
            if trace_flags:
                k8s["spec"]["settings"][SQLMI_TRACEFLAGS] = parse_traceflags(
                    trace_flags
                )

            # -- Allow user to set DNS names and port numbers --
            if primary_port_number:
                k8s["spec"]["services"]["primary"]["port"] = int(
                    primary_port_number
                )
            if primary_dns_name:
                k8s["spec"]["services"]["primary"]["dnsName"] = primary_dns_name

            if secondary_dns_name:
                k8s["spec"]["services"]["readableSecondaries"][
                    "dnsName"
                ] = secondary_dns_name
            if secondary_port_number:
                k8s["spec"]["services"]["readableSecondaries"]["port"] = int(
                    secondary_port_number
                )

            # ===================== Active Directory ======================= #
            if ad_connector_name:
                k8s["spec"]["security"] = {
                    "activeDirectory": {
                        "accountName": ad_account_name,
                        "connector": {
                            "name": ad_connector_name,
                            "namespace": ad_connector_namespace,
                        },
                    }
                }

                if keytab_secret:
                    k8s["spec"]["security"]["activeDirectory"][
                        "keytabSecret"
                    ] = keytab_secret

                if ad_encryption_types:
                    k8s["spec"]["security"]["activeDirectory"][
                        "encryptionTypes"
                    ] = _parse_supported_ad_encryption_types(
                        ad_encryption_types
                    )

            # ================== Transparent Data Encryption ================= #
            if tde_mode:
                k8s["spec"]["security"] = {
                    "transparentDataEncryption": {
                        "mode": tde_mode,
                    }
                }

            if tde_protector_secret:
                k8s["spec"]["security"]["transparentDataEncryption"] = {
                    "protectorSecret": tde_protector_secret,
                }

            all_dcs = self.list_dc(
                resource_group=resource_group, custom_location=custom_location
            )
            dc_name_list = []
            dc_in_rg = {}
            for curr_dc in all_dcs:
                dc_name_list.append(curr_dc.as_dict()["name"])
            if not dc_name_list:
                raise Exception(
                    "No data controller was found in the resource group."
                )
            else:
                dc_in_rg = self.get_dc(resource_group, dc_name_list[0])
                if not service_type:
                    service_type = dc_in_rg.properties.k8_s_raw["spec"][
                        "services"
                    ][0]["serviceType"]

                k8s["spec"]["services"]["primary"]["type"] = service_type
                k8s["spec"]["services"]["readableSecondaries"][
                    "type"
                ] = service_type

            # Force the namespace to be aligned with dc
            #
            if (
                dc_in_rg
                and dc_in_rg.properties
                and dc_in_rg.properties.k8_s_raw
                and "metadata" in dc_in_rg.properties.k8_s_raw
                and "namespace" in dc_in_rg.properties.k8_s_raw["metadata"]
            ):
                k8s["spec"]["metadata"]["namespace"] = (
                    dc_in_rg.properties.k8_s_raw["metadata"]["namespace"]
                )

            # -- TODO: Remove Validation check --
            #
            self._is_valid_sqlmi_create(
                cores_limit=k8s["spec"]["scheduling"]["default"]["resources"][
                    "limits"
                ]["cpu"],
                cores_request=k8s["spec"]["scheduling"]["default"]["resources"][
                    "requests"
                ]["cpu"],
                memory_limit=k8s["spec"]["scheduling"]["default"]["resources"][
                    "limits"
                ]["memory"],
                memory_request=k8s["spec"]["scheduling"]["default"][
                    "resources"
                ]["requests"]["memory"],
                storage=k8s["spec"]["storage"],
                license_type=all_prop["properties"]["licenseType"],
                tier=all_prop["sku"]["tier"],
            )

            # TODO: Remove Compose additional properties. Values have been
            #  verified in the set
            #
            safe_set = {
                "dev",
                "storage",
                "license_type",
                "services",
                "backup",
                "settings",
                "metadata",
                "dev",
                "readableSecondaries",
                "syncSecondaryToCommit",
                "security",
            }
            additional_properties = {}
            for key in k8s["spec"]:
                if key in safe_set:
                    additional_properties[key] = k8s["spec"][key]

            resources = k8s["spec"]["scheduling"]["default"]["resources"]

            # -- Build properties --
            properties = SqlManagedInstanceProperties(
                data_controller_id=dc_in_rg.name,
                admin=cred.username,
                basic_login_information=BasicLoginInformation(
                    username=cred.username,
                    password=cred.password,
                ),
                license_type=all_prop["properties"]["licenseType"],
                k8_s_raw=SqlManagedInstanceK8SRaw(
                    spec=SqlManagedInstanceK8SSpec(
                        additional_properties=additional_properties,
                        replicas=k8s["spec"]["replicas"],
                        scheduling=K8SScheduling(
                            default=K8SSchedulingOptions(
                                resources=K8SResourceRequirements(
                                    limits={
                                        "cpu": resources["limits"]["cpu"],
                                        "memory": resources["limits"]["memory"],
                                    },
                                    requests={
                                        "cpu": resources["requests"]["cpu"],
                                        "memory": resources["requests"][
                                            "memory"
                                        ],
                                    },
                                )
                            )
                        ),
                    )
                ),
            )

            # -- Build final mi request model --
            sql_managed_instance = SqlManagedInstance(
                location=location,
                properties=properties,
                extended_location=ExtendedLocation(
                    name=(
                        "/subscriptions/"
                        + self._subscription_id
                        + "/resourcegroups/"
                        + resource_group
                        + "/providers/microsoft.extendedlocation/"
                        "customlocations/" + custom_location
                    ),
                    type="CustomLocation",
                ),
                sku=SqlManagedInstanceSku(
                    tier=all_prop["sku"]["tier"], dev=None
                ),
                tags=all_prop["tags"],
            )

            print(
                "Creating Arc-enabled SQL Managed Instance {}...".format(name)
            )

            self._mgmt_client.sql_managed_instances.begin_create(
                resource_group_name=resource_group,
                sql_managed_instance_name=name,
                sql_managed_instance=sql_managed_instance,
                polling=polling,
                headers=self._headers,
                api_version=api_version,
            )

            if polling:
                poll_provisioning_state(
                    self.sqlmi_provisioning_completed,
                    resource_group,
                    name,
                    wait_time=300,
                )

                result = wait(
                    self.sqlmi_deployment_completed,
                    resource_group,
                    name,
                )

                if result != "Ready":
                    raise Exception("Deployment has timed out.")

                print(
                    "Successfully deployed Arc-enabled SQL Managed Instance {}".format(
                        name
                    )
                )
                return self.get_sqlmi(resource_group, name)
            else:
                print(
                    "Arc-enabled SQL Managed Instance {0} is being created. "
                    "Use `az sql mi-arc show -n {0} -g {1}` or the Azure Portal "
                    "to monitor the status of this instance.".format(
                        name, resource_group
                    )
                )

        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise Exception(
                "Arc-enabled SQL Managed Instance deployment failed. "
                "Please check the status of this instance "
                "in the Azure portal or restart this create process."
                "\nError: {}".format(str(e))
            )

    def sqlmi_deployment_completed(self, resource_group, name):
        get_result = self.get_sqlmi(resource_group, name)
        if (
            get_result
            and get_result["properties"]
            and get_result["properties"]["k8_s_raw"]
            and "status" in get_result["properties"]["k8_s_raw"]
            and "state" in get_result["properties"]["k8_s_raw"]["status"]
        ):
            return get_result["properties"]["k8_s_raw"]["status"]["state"]
        else:
            # Status is unknow, so we set it to "Wait" for now.
            return "Wait"

    def sqlmi_provisioning_completed(self, resource_group, name):
        get_result = self.get_sqlmi(resource_group, name)
        if (
            get_result
            and "properties" in get_result
            and "provisioning_state" in get_result["properties"]
        ):
            return get_result["properties"]["provisioning_state"]
        else:
            # Default status
            return "Accepted"

    def delete_sqlmi(self, rg_name, sqlmi_name, polling=True):
        def is_sqlmi_deleted_in_arm():
            try:
                return not self.get_sqlmi(rg_name, sqlmi_name)
            except exceptions.HttpResponseError as e:
                return True

        try:
            print("Deleting Arc-enabled SQL Managed Instance...")

            result = conditional_retry(
                condition_func=is_sqlmi_deleted_in_arm,
                func=self._mgmt_client.sql_managed_instances.begin_delete,
                resource_group_name=rg_name,
                sql_managed_instance_name=sqlmi_name,
                headers=self._headers,
                polling=polling,
                exception_type=exceptions.HttpResponseError,
            )

            if not result:
                # Delete immediately succeeded
                print(
                    f"Arc-enabled SQL Managed Instance {sqlmi_name} deleted successfully."
                )
                return

            if polling:
                # Polling
                cnt = 0
                while not is_sqlmi_deleted_in_arm() and cnt < 300:
                    time.sleep(5)
                    cnt += 5

                if not is_sqlmi_deleted_in_arm():
                    raise Exception(
                        "Failed to delete the given Arc-enabled SQL Managed Instance. "
                        "Please check the status of this resource "
                        "in the Azure Portal or retry this operation."
                    )
                else:
                    print(
                        f"Arc-enabled SQL Managed Instance {sqlmi_name} deleted successfully."
                    )
            else:
                print(
                    "Arc-enabled SQL Managed Instance {} is being deleted. "
                    "Use `az sql mi-arc show` or the Azure Portal "
                    "to monitor the status of the resource.".format(sqlmi_name)
                )
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def get_sqlmi(self, rg_name, sqlmi_name):
        try:
            result = self._mgmt_client.sql_managed_instances.get(
                resource_group_name=rg_name,
                sql_managed_instance_name=sqlmi_name,
                headers=self._headers,
            ).as_dict()

            logger.debug(json.dumps(result, indent=4))

            return result
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def get_sqlmi_as_obj(self, rg_name, sqlmi_name):
        try:
            result = self._mgmt_client.sql_managed_instances.get(
                resource_group_name=rg_name,
                sql_managed_instance_name=sqlmi_name,
                headers=self._headers,
            )

            logger.debug(json.dumps(result.as_dict(), indent=4))

            return result
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def get_arc_datacontroller(self, resource_group):
        """
        TODO: It is possible to have more than one data controller in a resource group.
        This should be updated to query Azure once workitem #1316334 has been completed
        """
        all_dcs = self.list_dc(resource_group=resource_group)
        for curr_dc in all_dcs:
            dc = curr_dc.as_dict()
            dc_spec = dc["properties"]["k8_s_raw"]
            if "status" in dc_spec and "state" in dc_spec["status"]:
                if dc_spec["status"]["state"].lower() != "duplicateerror":
                    return dc_spec

    def upgrade_sqlmi(
        self,
        resource_group,
        name,
        desired_version,
        dry_run=False,
        no_wait=True,
    ):
        dc_client = self._arm_clients.dc
        try:
            if not desired_version:
                dc = self.get_arc_datacontroller(resource_group)
                desired_version = dc["spec"]["docker"]["imageTag"]

            # if dry_run is specified, we will simply print and return.
            if dry_run:
                if desired_version == "auto":
                    print("****Dry Run****\n")
                    print(
                        f"{name} would continually be upgraded automatically to the latest valid version.\n"
                    )
                else:
                    print("****Dry Run****\n")
                    print(f"{name} would be upgraded to {desired_version}.\n")
                return

            url = self.get_mi_resource_url(resource_group, name)

            headers = {
                "Authorization": "Bearer {}".format(self._bearer),
                "Content-Type": "application/json",
            }

            response = requests.get(url=url, headers=headers)

            if response.status_code == 404:
                logger.debug(response.text)
                raise Exception(
                    "Error while retrieving SQL MI instance with name '{}' in resource group '{}'".format(
                        name, resource_group
                    )
                )

            sqlmi = response.json()

            # Get latest API version supported by extension
            custom_location = (
                sqlmi.get("extendedLocation").get("name").split("/")[-1]
            )
            api_version = dc_client.resolve_api_version(
                INSTANCE_TYPE_SQL, custom_location, resource_group
            )

            url = self.get_mi_resource_url(
                resource_group, name, api_version=api_version
            )

            # We cannot initiate a new PUT request if a previous request is still
            # in the Accepted state.
            #
            if sqlmi["properties"]["provisioningState"] == "Accepted":
                raise Exception(
                    "An existing operation is in progress. Please check your SQL MI's status in the Azure Portal."
                )

            if "update" not in sqlmi["properties"]["k8sRaw"]["spec"]:
                sqlmi["properties"]["k8sRaw"]["spec"]["update"] = {}

            sqlmi["properties"]["k8sRaw"]["spec"]["update"][
                "desiredVersion"
            ] = desired_version

            template = {}
            template["location"] = sqlmi["location"]
            template["extendedLocation"] = sqlmi["extendedLocation"]
            template["properties"] = sqlmi["properties"]
            template["sku"] = sqlmi["sku"]

            payload = json.dumps(template)

            # The mgmt library will currently strip away most of the spec when it converts the json payload to a ManagementInstance object.
            # This not only removes the update section, but most of the rest of the spec as well. For now we will need to manually submit the ARM request.
            #
            response = requests.put(url=url, headers=headers, data=payload)
            if response.status_code != 201:
                logger.debug(response.text)
                raise Exception("Error while upgrading SQL MI instance.")

            # Wait for the operation to be accepted
            #
            for _ in range(0, 60, 5):
                mi = self.get_sqlmi(resource_group, name)
                if mi["properties"]["provisioning_state"] != "Accepted":
                    break
                else:
                    time.sleep(5)

            if mi["properties"]["provisioning_state"] == "Failed":
                raise Exception(
                    "The ARM request to upgrade the SQL MI instance failed. Please check your SQL MI's status in the Azure Portal for more information."
                )

            if not no_wait:
                # Wait for SQL MI status change to sync to Azure
                time.sleep(15)

                # Setting a total wait time of 600 sec with a step of 5 sec
                for _ in range(0, 600, 5):
                    if self.sqlmi_upgrade_completed(resource_group, name):
                        break
                    else:
                        time.sleep(5)

                if not self.sqlmi_upgrade_completed(resource_group, name):
                    raise Exception(
                        "SQLMI upgrade failed. Please check your SQL MI's status in the Azure Portal for more information."
                    )

        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def sqlmi_upgrade_completed(self, resource_group, name):
        url = self.get_mi_resource_url(resource_group, name)

        headers = {
            "Authorization": "Bearer {}".format(self._bearer),
            "Content-Type": "application/json",
        }

        get_result = requests.get(url=url, headers=headers).json()

        return (
            _.get(get_result, "properties.k8sRaw.status.state", False)
            == "Ready"
        )

    def update_sqlmi(
        self,
        name,
        replicas=None,
        orchestrator_replicas=None,
        readable_secondaries=None,
        sync_secondary_to_commit=None,
        cores_limit=None,
        cores_request=None,
        memory_limit=None,
        memory_request=None,
        license_type=None,
        tier=None,
        polling=True,
        labels=None,
        annotations=None,
        service_labels=None,
        service_annotations=None,
        agent_enabled=None,
        trace_flags=None,
        retention_days=None,
        resource_group=None,
        keytab_secret=None,
        ad_encryption_types=None,
        tde_mode=None,
        tde_protector_secret=None,
    ):
        dc_client = self._arm_clients.dc
        try:
            # get_sqmlmi then mixin properties
            response = self.get_sqlmi_as_obj(resource_group, name)
            resources = (
                response.properties.k8_s_raw.spec.scheduling.default.resources
            )
            additional_properties = (
                response.properties.k8_s_raw.spec.additional_properties
            )
            if (
                response.properties.provisioning_state == "Accepted"
                or response.properties.provisioning_state == "Deleting"
            ):
                raise Exception(
                    "An existing operation is in progress. Please check your "
                    "sqlmi's status in the Azure Portal."
                )
            if cores_limit and cores_limit != resources.limits["cpu"]:
                resources.limits["cpu"] = cores_limit
            if cores_request and cores_request != resources.requests["cpu"]:
                resources.requests["cpu"] = cores_request
            if memory_limit and memory_limit != resources.limits["memory"]:
                resources.limits["memory"] = memory_limit
            if (
                memory_request
                and memory_request != resources.requests["memory"]
            ):
                resources.requests["memory"] = memory_request
            if (
                agent_enabled
                and agent_enabled
                != additional_properties["settings"]["sqlagent"]["enabled"]
            ):
                additional_properties["settings"]["sqlagent"][
                    "enabled"
                ] = agent_enabled
            if (
                retention_days is not None
                and retention_days
                != additional_properties["backup"]["retentionPeriodInDays"]
            ):
                additional_properties["backup"]["retentionPeriodInDays"] = int(
                    retention_days
                )
            if labels:
                additional_properties["metadata"]["labels"] = labels
            if annotations:
                additional_properties["metadata"]["annotations"] = annotations
            if service_labels:
                additional_properties["services"]["primary"][
                    "labels"
                ] = service_labels
            if service_annotations:
                additional_properties["services"]["primary"][
                    "annotations"
                ] = service_annotations
            if replicas:
                if response.sku.tier == SQLMI_TIER_GENERAL_PURPOSE:
                    raise ValueError(
                        "Cannot update replica count. This Arc-enabled SQL Managed Instance is under the General Purpose pricing tier."
                    )

                replicas = int(replicas)
                prev_replicas = int(response.properties.k8_s_raw.spec.replicas)
                if not (
                    max(1, prev_replicas - 1)
                    <= replicas
                    <= min(3, prev_replicas + 1)
                ):
                    raise ValueError(
                        "New replicas value must be +1 or -1 previous value"
                    )
                response.properties.k8_s_raw.spec.replicas = replicas
            if orchestrator_replicas:
                additional_properties["orchestratorReplicas"] = int(
                    orchestrator_replicas
                )
            if readable_secondaries:
                additional_properties["readableSecondaries"] = int(
                    readable_secondaries
                )
            if sync_secondary_to_commit:
                additional_properties["syncSecondaryToCommit"] = int(
                    sync_secondary_to_commit
                )
            if license_type:
                additional_properties["licenseType"] = license_type
                response.properties.license_type = license_type
            if tier:
                if response.sku.tier == SQLMI_TIER_BUSINESS_CRITICAL:
                    raise ValueError(
                        "Cannot change SKU tier from Business Critical. "
                        "Changing tier is only supported from General Purpose "
                        "to Business Critical and when the number of replicas = 1"
                    )
                else:
                    tier = SQLMI_TIERS_MAP[tier]
                    additional_properties["tier"] = tier
                    response.sku.tier = tier
            if keytab_secret:
                additional_properties["security"]["activeDirectory"][
                    "keytabSecret"
                ] = keytab_secret

            if ad_encryption_types:
                additional_properties["security"]["activeDirectory"][
                    "encryptionTypes"
                ] = _parse_supported_ad_encryption_types(ad_encryption_types)

            if tde_mode:
                additional_properties["security"]["transparentDataEncryption"][
                    "mode"
                ] = tde_mode

            if tde_protector_secret:
                additional_properties["security"]["transparentDataEncryption"][
                    "protectorSecret"
                ] = tde_protector_secret

            # -- Validation check -- provisioning is very slow so we check here
            #
            self._is_valid_sqlmi_create(
                cores_limit=resources.limits.get("cpu", 4),
                cores_request=resources.requests.get("cpu", 2),
                memory_limit=resources.limits.get("memory", "8Gi"),
                memory_request=resources.requests.get("memory", "4Gi"),
                storage=additional_properties["storage"],
                license_type=response.properties.license_type,
                tier=response.sku.tier,
            )

            # Get latest API version supported by extension for PUT
            custom_location = response.extended_location.name.split("/")[-1]
            api_version = dc_client.resolve_api_version(
                INSTANCE_TYPE_SQL, custom_location, resource_group
            )

            print(
                "Updating Arc-enabled SQL Managed Instance {}...".format(name)
            )

            self._mgmt_client.sql_managed_instances.begin_create(
                resource_group_name=resource_group,
                sql_managed_instance_name=name,
                sql_managed_instance=response,
                headers=self._headers,
                polling=polling,
                api_version=api_version,
            )

            if polling:
                # Poll K8s CR state
                poll_provisioning_state(
                    self.sqlmi_provisioning_completed,
                    resource_group,
                    name,
                    wait_time=300,
                )

                # Wait for SQL MI status change to sync to Azure
                time.sleep(15)

                result = wait(
                    self.sqlmi_deployment_completed,
                    resource_group,
                    name,
                )

                if result != "Ready":
                    raise Exception("Update operation has timed out.")

                print(
                    "Successfully updated Arc-enabled SQL Managed Instance {}".format(
                        name
                    )
                )
                return self.get_sqlmi(resource_group, name)
            else:
                print(
                    "Arc-enabled SQL Managed Instance {0} is being updated. "
                    "Use `az sql mi-arc show -n {0} -g {1}` or the Azure Portal "
                    "to monitor the status of your instance.".format(
                        name, resource_group
                    )
                )
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise Exception(
                "Arc-enabled SQL Managed Instance update failed. "
                "Please check the instance's status "
                "in the Azure portal or restart this update process."
                "\nError: {}".format(str(e))
            )

    def list_sqlmi(self, rg_name, cl_name=None):
        try:
            result = (
                self._mgmt_client.sql_managed_instances.list_by_resource_group(
                    rg_name, headers=self._headers
                )
            )

            # Filter by custom location if provided
            if cl_name:
                cl_resource_id = self._arm_clients.dc.get_custom_location(
                    custom_location=cl_name, resource_group=rg_name
                )["id"]

                result = [
                    sql
                    for sql in result
                    if sql.extended_location is not None
                    and sql.extended_location.name.lower()
                    == cl_resource_id.lower()
                ]

            return result
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def _is_valid_sqlmi_create(
        self,
        cores_limit,
        cores_request,
        memory_limit,
        memory_request,
        storage,
        license_type,
        tier,
    ):
        tier_set = {"gp", "GeneralPurpose", "bc", "BusinessCritical"}
        license_type_set = {"BasePrice", "LicenseIncluded", "DisasterRecovery"}
        try:
            if tier not in tier_set:
                raise Exception(
                    "Tier {0} is not a supported input.".format(tier)
                )

            if license_type not in license_type_set:
                raise Exception(
                    "License type {0} is not a supported input.".format(
                        license_type
                    )
                )

            # Check the input end with Gi
            #
            Gi_val_list = [memory_limit, memory_request]

            Gi_name_list = ["Memory limit", "Memory request"]

            for storage_name, storage_type in [
                ("Volume size data", "data"),
                ("Volume size logs", "logs"),
                ("Volume size datalogs", "datalogs"),
                ("Volume size backups", "backups"),
            ]:
                if storage_type in storage:
                    Gi_val_list.append(
                        storage[storage_type]["volumes"][0]["size"]
                    )
                    Gi_name_list.append(storage_name)

            for i in range(len(Gi_val_list)):
                if "Gi" not in str(Gi_val_list[i]):
                    raise ValueError(
                        "{0} {1} is invalid. Unit Gi must be part of this input.".format(
                            Gi_name_list[i], Gi_val_list[i]
                        )
                    )

                # Check the number in the input
                #
                if not (str(Gi_val_list[i]).replace("Gi", "")).isdigit():
                    raise ValueError(
                        "{0} {1} is invalid. A number must be part of this input.".format(
                            Gi_name_list[i], Gi_val_list[i]
                        )
                    )
                else:
                    Gi_val_list[i] = int(str(Gi_val_list[i]).replace("Gi", ""))

            # Check the input which should be digits.
            #
            digit_val_list = [cores_limit, cores_request]
            digit_name_list = ["Cores limit", "Cores request"]
            for i in range(len(digit_val_list)):
                if not str(digit_val_list[i]).isdigit():
                    raise ValueError(
                        "{0} {1} is invalid. Only a number can be part of this input.".format(
                            digit_name_list[i], digit_val_list[i]
                        )
                    )
                else:
                    digit_val_list[i] = int(str(digit_val_list[i]))

            # Check the resource scheduling config
            #
            if Gi_val_list[0] < Gi_val_list[1]:
                raise ValueError(
                    "Memory request cannot be larger than memory limit."
                )
            if digit_val_list[0] < digit_val_list[1]:
                raise ValueError(
                    "Cores request cannot be larger than cores limit."
                )

            # Check the scheduling per tier
            #
            gp_tiers = {"gp", "GeneralPurpose"}
            if tier in gp_tiers:
                if Gi_val_list[0] > 128 or Gi_val_list[0] < 2:
                    raise ValueError(
                        "Invalid {0}. Tier {1} can only support an input in the range from 2 to 128Gi.".format(
                            Gi_name_list[0], tier
                        )
                    )
                if Gi_val_list[1] > 128 or Gi_val_list[1] < 2:
                    raise ValueError(
                        "Invalid {0}. Tier {1} can only support an input in the range from 2 to 128Gi.".format(
                            Gi_name_list[1], tier
                        )
                    )
                if digit_val_list[0] > 24 or digit_val_list[0] < 1:
                    raise ValueError(
                        "Invalid {0}. Tier {1} can only support an input in the range from 1 to 24.".format(
                            digit_name_list[0], tier
                        )
                    )
                if digit_val_list[1] > 24 or digit_val_list[1] < 1:
                    raise ValueError(
                        "Invalid {0}. Tier {1} can only support an input in the range from 1 to 24.".format(
                            digit_name_list[1], tier
                        )
                    )
            else:
                if Gi_val_list[0] < 2:
                    raise ValueError(
                        "Invalid {0}. Tier {1} can only support an input in the range >= 2Gi".format(
                            Gi_name_list[0], tier
                        )
                    )
                if Gi_val_list[1] < 2:
                    raise ValueError(
                        "Invalid {0}. Tier {1} can only support an input in the range >= 2Gi.".format(
                            Gi_name_list[1], tier
                        )
                    )
                if digit_val_list[0] < 1:
                    raise ValueError(
                        "Invalid {0}. Tier {1} can only support an input in the range >=1.".format(
                            digit_name_list[0], tier
                        )
                    )
                if digit_val_list[1] < 1:
                    raise ValueError(
                        "Invalid {0}. Tier {1} can only support an input in the range >=1.".format(
                            digit_name_list[1], tier
                        )
                    )

        except Exception as e:
            raise e

    # ======================================================================== #
    # == AD Connector ======================================================== #
    # ======================================================================== #

    def create_ad_connector(
        self,
        name,
        realm,
        nameserver_addresses,
        account_provisioning,
        data_controller_name,
        resource_group,
        primary_domain_controller=None,
        secondary_domain_controllers=None,
        netbios_domain_name=None,
        dns_domain_name=None,
        num_dns_replicas=None,
        prefer_k8s_dns=None,
        ou_distinguished_name=None,
        no_wait=False,
    ):
        dc_client = self._arm_clients.dc
        try:
            # Check that the deployed extension supports AD connector creation
            #
            dc_resource: DataControllerResource = self.get_dc(
                resource_group, data_controller_name
            )
            custom_location = dc_resource.extended_location.name.split("/")[-1]
            api_version = dc_client.resolve_api_version(
                INSTANCE_TYPE_AD_CONNECTOR, custom_location, resource_group
            )

            # -- check existing AD connectors to avoid duplicate creation --
            #
            result = self._get_ad_connector_resource(
                name, data_controller_name, resource_group
            )
            if result:
                raise ValueError(
                    "Active Directory connector '{name}' has already been created.".format(
                        name=name
                    )
                )

            domain_account = None
            if account_provisioning == ACCOUNT_PROVISIONING_MODE_AUTOMATIC:
                # -- acquire AD domain service account username/password --
                cred = Env.get_active_directory_domain_account_credentials()

                domain_account = BasicLoginInformation(
                    username=cred.username,
                    password=cred.password,
                )

            primary_dc = None
            if primary_domain_controller:
                primary_dc = ActiveDirectoryDomainController(
                    hostname=primary_domain_controller
                )

            secondary_dcs = []
            if secondary_domain_controllers:
                for dc in secondary_domain_controllers.replace(" ", "").split(
                    ","
                ):
                    if dc:
                        secondary_dcs.append(
                            ActiveDirectoryDomainController(hostname=dc)
                        )

            domain_controllers = ActiveDirectoryDomainControllers(
                primary_domain_controller=primary_dc,
                secondary_domain_controllers=secondary_dcs,
            )

            domain_details = ActiveDirectoryConnectorDomainDetails(
                realm=realm,
                domain_controllers=domain_controllers,
                netbios_domain_name=netbios_domain_name,
                service_account_provisioning=account_provisioning,
                ou_distinguished_name=ou_distinguished_name,
            )

            dns_details = ActiveDirectoryConnectorDNSDetails(
                nameserver_ip_addresses=_parse_nameserver_addresses(
                    nameserver_addresses
                ),
                domain_name=dns_domain_name,
                replicas=_parse_num_replicas(num_dns_replicas),
                prefer_k8_s_dns_for_ptr_lookups=_parse_prefer_k8s_dns(
                    prefer_k8s_dns
                ),
            )

            spec = ActiveDirectoryConnectorSpec(
                active_directory=domain_details, dns=dns_details
            )

            properties = ActiveDirectoryConnectorProperties(
                domain_service_account_login_information=domain_account,
                spec=spec,
            )

            # -- final request model --
            ad_connector_resource = ActiveDirectoryConnectorResource(
                properties=properties,
            )
            # -- send create PUT request
            self._mgmt_client.active_directory_connectors.begin_create(
                resource_group_name=resource_group,
                active_directory_connector_resource=ad_connector_resource,
                data_controller_name=data_controller_name,
                active_directory_connector_name=name,
                headers=self._headers,
                polling=(not no_wait),
                api_version=api_version,
            )

            if not no_wait:
                poll_provisioning_state(
                    self.ad_connector_provisioning_completed,
                    name,
                    data_controller_name,
                    resource_group,
                    wait_time=300,
                )

                wait(
                    self._get_ad_connector_status,
                    name,
                    data_controller_name,
                    resource_group,
                    retry_tol=300,
                )
                if (
                    self._get_ad_connector_status(
                        name, data_controller_name, resource_group
                    )
                    != "Ready"
                ):
                    raise Exception(
                        "Active Directory connector deployment failed. Please check your AD connector status "
                        "in the Azure portal or restart this create process."
                    )
                return self._get_ad_connector_resource(
                    name, data_controller_name, resource_group
                )
            else:
                print(
                    "Active Directory connector {} is being created. "
                    "Use `az arcdata ad-connector show` or the Azure Portal "
                    "to monitor the status of your AD connector.".format(name)
                )
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def list_ad_connectors(self, data_controller_name, resource_group):
        try:
            result = []
            connectors = self._mgmt_client.active_directory_connectors.list(
                resource_group_name=resource_group,
                data_controller_name=data_controller_name,
                headers=self._headers,
            )

            for connector in connectors:
                result.append(connector)

            print("Found {} Active Directory connector(s).".format(len(result)))

            return result if result else None
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def update_ad_connector(
        self,
        name,
        data_controller_name,
        resource_group,
        nameserver_addresses=None,
        primary_domain_controller=None,
        secondary_domain_controllers=None,
        num_dns_replicas=None,
        prefer_k8s_dns=None,
        domain_service_account_secret=None,
        no_wait=False,
    ):
        dc_client = self._arm_clients.dc
        try:
            response: ActiveDirectoryConnectorResource = (
                self._mgmt_client.active_directory_connectors.get(
                    resource_group_name=resource_group,
                    data_controller_name=data_controller_name,
                    active_directory_connector_name=name,
                    headers=self._headers,
                )
            )

            if (
                response.properties.provisioning_state == "Accepted"
                or response.properties.provisioning_state == "Deleting"
            ):
                raise Exception("An existing operation is in progress.")

            # -- get api version --
            dc_resource: DataControllerResource = self.get_dc(
                resource_group, data_controller_name
            )
            custom_location = dc_resource.extended_location.name.split("/")[-1]
            api_version = dc_client.resolve_api_version(
                INSTANCE_TYPE_AD_CONNECTOR, custom_location, resource_group
            )

            # Updating the AD connector in ARM is essentially re-creating it
            #
            new_resource: ActiveDirectoryConnectorResource = response

            account_provisioning = (
                response.properties.spec.active_directory.service_account_provisioning
            )
            domain_account = None
            if (
                domain_service_account_secret
                and account_provisioning == ACCOUNT_PROVISIONING_MODE_AUTOMATIC
            ):
                # -- acquire AD domain service account username/password --
                cred = Env.get_active_directory_domain_account_credentials()

                domain_account = BasicLoginInformation(
                    username=cred.username,
                    password=cred.password,
                )

            if domain_account:
                new_resource.properties.domain_service_account_login_information = (
                    domain_account
                )

            if nameserver_addresses:
                new_resource.properties.spec.dns.nameserver_ip_addresses = (
                    _parse_nameserver_addresses(nameserver_addresses)
                )

            if primary_domain_controller:
                new_resource.properties.spec.active_directory.domain_controllers.primary_domain_controller = ActiveDirectoryDomainController(
                    hostname=primary_domain_controller
                )

            if secondary_domain_controllers:
                secondary_dcs = []
                for dc in secondary_domain_controllers.replace(" ", "").split(
                    ","
                ):
                    if dc:
                        secondary_dcs.append(
                            ActiveDirectoryDomainController(hostname=dc)
                        )
                new_resource.properties.spec.active_directory.domain_controllers.secondary_domain_controllers = (
                    secondary_dcs
                )

            if num_dns_replicas:
                new_resource.properties.spec.dns.replicas = _parse_num_replicas(
                    num_dns_replicas
                )

            if prefer_k8s_dns:
                new_resource.properties.spec.dns.prefer_k8_s_dns_for_ptr_lookups = _parse_prefer_k8s_dns(
                    prefer_k8s_dns
                )

            # -- final request model --
            properties = ActiveDirectoryConnectorProperties(
                domain_service_account_login_information=domain_account,
                spec=new_resource.properties.spec,
            )

            updated_ad_connector_resource = ActiveDirectoryConnectorResource(
                properties=properties,
            )

            self._mgmt_client.active_directory_connectors.begin_create(
                resource_group_name=resource_group,
                active_directory_connector_resource=updated_ad_connector_resource,
                data_controller_name=data_controller_name,
                active_directory_connector_name=name,
                headers=self._headers,
                polling=(not no_wait),
                api_version=api_version,
            )

            if not no_wait:
                poll_provisioning_state(
                    self.ad_connector_provisioning_completed,
                    name,
                    data_controller_name,
                    resource_group,
                    wait_time=300,
                )

                wait(
                    self._get_ad_connector_status,
                    name,
                    data_controller_name,
                    resource_group,
                    retry_tol=300,
                )
                if (
                    self._get_ad_connector_status(
                        name, data_controller_name, resource_group
                    )
                    != "Ready"
                ):
                    raise Exception(
                        "Active Directory connector update failed. Please check your AD connector status "
                        "in the Azure portal or restart this update."
                    )
                return self._get_ad_connector_resource(
                    name, data_controller_name, resource_group
                )
            else:
                print(
                    "Active Directory connector {} is being updated. "
                    "Use `az arcdata ad-connector show` or the Azure Portal "
                    "to monitor the status of your AD connector.".format(name)
                )
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def _get_ad_connector_resource(
        self, name, data_controller_name, resource_group
    ):
        try:
            result = self._mgmt_client.active_directory_connectors.get(
                resource_group_name=resource_group,
                data_controller_name=data_controller_name,
                active_directory_connector_name=name,
                headers=self._headers,
            )

            logger.debug(json.dumps(result.as_dict(), indent=4))

            return result
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            return
        except Exception as e:
            raise e

    def get_ad_connector(self, name, data_controller_name, resource_group):
        result = self._get_ad_connector_resource(
            name, data_controller_name, resource_group
        )
        if result:
            return result
        else:
            raise Exception(
                "The Active Directory connector {} could not be found in Azure.".format(
                    name
                )
            )

    def _get_ad_connector_status(
        self, name, data_controller_name, resource_group
    ):
        response: ActiveDirectoryConnectorResource = (
            self._get_ad_connector_resource(
                name, data_controller_name, resource_group
            )
        )
        if (
            response
            and response.properties
            and response.properties.status
            and response.properties.status.state
        ):
            return response.properties.status.state
        else:
            # Status is unknown, so we set it to "Pending" for now.
            return "Pending"

    def ad_connector_provisioning_completed(
        self, name, data_controller_name, resource_group
    ):
        response: ActiveDirectoryConnectorResource = (
            self._get_ad_connector_resource(
                name, data_controller_name, resource_group
            )
        )
        if (
            response
            and response.properties
            and response.properties.provisioning_state
        ):
            return response.properties.provisioning_state
        else:
            # Default status
            return "Accepted"

    def delete_ad_connector(
        self, name, data_controller_name, resource_group, no_wait=False
    ):
        def is_ad_connector_deleted_in_arm():
            resource = self._get_ad_connector_resource(
                name, data_controller_name, resource_group
            )
            return not resource

        try:
            print("Deleting Active Directory connector...")

            result = conditional_retry(
                condition_func=is_ad_connector_deleted_in_arm,
                func=self._mgmt_client.active_directory_connectors.begin_delete,
                resource_group_name=resource_group,
                data_controller_name=data_controller_name,
                active_directory_connector_name=name,
                headers=self._headers,
                polling=(not no_wait),
                exception_type=exceptions.HttpResponseError,
            )

            if not result:
                # Delete immediately succeeded
                print("Active Directory connector deleted successfully.")
                return

            if not no_wait:
                # Polling
                cnt = 0
                while not is_ad_connector_deleted_in_arm() and cnt < 300:
                    time.sleep(5)
                    cnt += 5

                if not is_ad_connector_deleted_in_arm():
                    raise Exception(
                        "Failed to delete Active Directory connector. "
                        "Please check your AD connector status "
                        "in the Azure Portal or retry this operation."
                    )
                else:
                    print("Active Directory connector deleted successfully.")
            else:
                print(
                    "Active Directory connector {} is being deleted. "
                    "Use `az arcdata ad-connector show` or the Azure Portal "
                    "to monitor the status of the given AD connector.".format(
                        name
                    )
                )
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def _validate_connectivity_mode(self, data_controller_name, resource_group):
        dc_resource: DataControllerResource = self.get_dc(
            resource_group, data_controller_name
        )
        if (
            dc_resource.properties.k8_s_raw["spec"]["settings"]["azure"][
                "connectionMode"
            ]
            == INDIRECT
        ):
            raise ValueError(
                "This cluster's data controller is in indirect connectivity "
                "mode. Please use the --use-k8s parameter to perform this "
                "action."
            )

    # ======================================================================== #
    # == Failover Group ====================================================== #
    # ======================================================================== #

    def create_failover_group(
        self,
        name,
        mi,
        resource_group,
        primary_mirroring_url,
        partner_mirroring_url,
        partner_mi,
        partner_resource_group,
        partner_sync_mode=None,
        role=None,
        no_wait=False,
    ):
        dc_client = self._arm_clients.dc
        try:
            partner_sync_mode = partner_sync_mode or "async"

            # Check if the failover group already exists
            if self._get_failover_group_resource(name, mi, resource_group):
                raise Exception(
                    "Failover group {} already exists.".format(name)
                )

            # Check that primary SQL MI-AA exists
            try:
                primary_sql_resource = (
                    self._mgmt_client.sql_managed_instances.get(
                        resource_group_name=resource_group,
                        sql_managed_instance_name=mi,
                        headers=self._headers,
                    )
                )
            except exceptions.HttpResponseError as e:
                raise Exception(
                    "Primary Arc-enabled SQL Managed Instance {} does not exist in resource group {}.".format(
                        mi, resource_group
                    )
                )

            # Check that secondary SQL MI-AA exists
            try:
                partner_sql_resource = (
                    self._mgmt_client.sql_managed_instances.get(
                        resource_group_name=partner_resource_group,
                        sql_managed_instance_name=partner_mi,
                        headers=self._headers,
                    )
                )
            except exceptions.HttpResponseError as e:
                raise Exception(
                    "Partner Arc-enabled SQL Managed Instance {} does not exist in resource group {}.".format(
                        partner_mi, partner_resource_group
                    )
                )

            # Check that the deployed extensions both support failover group creation
            #
            primary_custom_location = (
                primary_sql_resource.extended_location.name.split("/")[-1]
            )
            api_version = dc_client.resolve_api_version(
                INSTANCE_TYPE_FAILOVER_GROUP,
                primary_custom_location,
                resource_group,
            )

            partner_custom_location = (
                partner_sql_resource.extended_location.name.split("/")[-1]
            )
            dc_client.resolve_api_version(
                INSTANCE_TYPE_FAILOVER_GROUP,
                partner_custom_location,
                partner_resource_group,
            )

            primary_failover_group_resource = FailoverGroupResource(
                properties=FailoverGroupProperties(
                    partner_managed_instance_id="/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AzureArcData/sqlManagedInstances/{}".format(
                        self._subscription_id,
                        partner_resource_group,
                        partner_mi,
                    ),
                    spec=FailoverGroupSpec(
                        partner_sync_mode=partner_sync_mode,
                        role="primary",
                        partner_mirroring_url=partner_mirroring_url,
                    ),
                ),
            )
            logger.debug(
                "Primary failover group resource: \n"
                + json.dumps(
                    primary_failover_group_resource.as_dict(), indent=4
                )
            )

            secondary_failover_group_resource = FailoverGroupResource(
                properties=FailoverGroupProperties(
                    partner_managed_instance_id="/subscriptions/{}/resourceGroups/{}/providers/Microsoft.AzureArcData/sqlManagedInstances/{}".format(
                        self._subscription_id,
                        resource_group,
                        mi,
                    ),
                    spec=FailoverGroupSpec(
                        partner_sync_mode=partner_sync_mode,
                        role="secondary",
                        partner_mirroring_url=primary_mirroring_url,
                    ),
                ),
            )
            logger.debug(
                "Secondary failover group resource: \n"
                + json.dumps(
                    secondary_failover_group_resource.as_dict(), indent=4
                )
            )

            print("Creating failover group...")

            # Failover Group on primary SQL MI-AA
            self._mgmt_client.failover_groups.begin_create(
                resource_group_name=resource_group,
                sql_managed_instance_name=mi,
                failover_group_name=name,
                failover_group_resource=primary_failover_group_resource,
                headers=self._headers,
                polling=(not no_wait),
                api_version=api_version,
            )

            # Failover Group on secondary SQL MI-AA
            self._mgmt_client.failover_groups.begin_create(
                resource_group_name=partner_resource_group,
                sql_managed_instance_name=partner_mi,
                failover_group_name=name,
                failover_group_resource=secondary_failover_group_resource,
                headers=self._headers,
                polling=(not no_wait),
                api_version=api_version,
            )

            if not no_wait:
                for instance_info in [
                    (mi, resource_group, "primary"),
                    (partner_mi, partner_resource_group, "secondary"),
                ]:
                    (instance_name, rg, role) = instance_info

                    poll_provisioning_state(
                        self.failover_group_provisioning_completed,
                        name,
                        instance_name,
                        rg,
                        wait_time=300,
                    )

                    wait(
                        self._get_failover_group_status,
                        name,
                        instance_name,
                        rg,
                        retry_tol=300,
                    )

                    if (
                        self._get_failover_group_status(name, instance_name, rg)
                        != "Succeeded"
                    ):
                        raise Exception(
                            "Failed to create {0} failover group associated with Arc-enabled SQL managed instance {1}."
                            "Please check your failover group status "
                            "in the Azure Portal or retry this operation.".format(
                                role, instance_name
                            )
                        )

                return self._get_failover_group_resource(
                    name, mi, resource_group
                )
            else:
                print(
                    "Failover group {} is being created. "
                    "Use `az sql instance-failover-group-arc show` or the Azure Portal "
                    "to monitor the status of this resource.".format(name)
                )
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def update_failover_group(
        self,
        name,
        mi,
        resource_group,
        partner_sync_mode=None,
        role=None,
        no_wait=False,
    ):
        dc_client = self._arm_clients.dc
        try:
            response: FailoverGroupResource = (
                self._mgmt_client.failover_groups.get(
                    resource_group_name=resource_group,
                    sql_managed_instance_name=mi,
                    failover_group_name=name,
                    headers=self._headers,
                )
            )

            if (
                response.properties.provisioning_state == "Accepted"
                or response.properties.provisioning_state == "Deleting"
            ):
                raise Exception("An existing operation is in progress.")

            parent_sql_resource = self._mgmt_client.sql_managed_instances.get(
                resource_group_name=resource_group,
                sql_managed_instance_name=mi,
                headers=self._headers,
            )

            custom_location = parent_sql_resource.extended_location.name.split(
                "/"
            )[-1]
            api_version = dc_client.resolve_api_version(
                INSTANCE_TYPE_FAILOVER_GROUP,
                custom_location,
                resource_group,
            )

            # Updating the AD connector in ARM is essentially re-creating it
            #
            new_resource: FailoverGroupResource = response
            if partner_sync_mode:
                new_resource.properties.spec.partner_sync_mode = (
                    partner_sync_mode
                )
            if role:
                new_resource.properties.spec.role = role

            print("Updating failover group...")

            self._mgmt_client.failover_groups.begin_create(
                resource_group_name=resource_group,
                sql_managed_instance_name=mi,
                failover_group_name=name,
                failover_group_resource=new_resource,
                headers=self._headers,
                polling=(not no_wait),
                api_version=api_version,
            )

            if not no_wait:
                poll_provisioning_state(
                    self.failover_group_provisioning_completed,
                    name,
                    mi,
                    resource_group,
                    wait_time=300,
                )

                # Wait for the failover group status to update
                time.sleep(10)

                wait(
                    self._get_failover_group_status,
                    name,
                    mi,
                    resource_group,
                    retry_tol=600,
                )
                if (
                    self._get_failover_group_status(name, mi, resource_group)
                    != "Succeeded"
                ):
                    raise Exception(
                        "Failed to update failover group {}. "
                        "Please check your failover group status "
                        "in the Azure Portal or retry this operation.".format(
                            name
                        )
                    )
                return self._get_failover_group_resource(
                    name, mi, resource_group
                )
            else:
                print(
                    "Failover group {} is being updated. "
                    "Use `az sql instance-failover-group-arc show` or the Azure Portal "
                    "to monitor the status of this resource.".format(name)
                )
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def delete_failover_group(self, name, mi, resource_group, no_wait=False):
        def is_failover_group_deleted_in_arm():
            resource = self._get_failover_group_resource(
                name, mi, resource_group
            )
            return not resource

        try:
            print("Deleting failover group...")

            result = conditional_retry(
                condition_func=is_failover_group_deleted_in_arm,
                func=self._mgmt_client.failover_groups.begin_delete,
                resource_group_name=resource_group,
                sql_managed_instance_name=mi,
                failover_group_name=name,
                headers=self._headers,
                polling=(not no_wait),
                exception_type=exceptions.HttpResponseError,
            )

            if not result:
                # Delete immediately succeeded
                print("Failover group deleted successfully.")
                return

            if not no_wait:
                # Polling
                cnt = 0
                while not is_failover_group_deleted_in_arm() and cnt < 300:
                    time.sleep(5)
                    cnt += 5

                if not is_failover_group_deleted_in_arm():
                    raise Exception(
                        "Failed to delete failover group. "
                        "Please check your failover group status "
                        "in the Azure Portal or retry this operation."
                    )
                else:
                    print("Failover group deleted successfully.")
            else:
                print(
                    "Failover group {} is being deleted. "
                    "Use `az arcdata failover-group show` or the Azure Portal "
                    "to monitor the status of the given failover group.".format(
                        name
                    )
                )
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def _get_failover_group_resource(self, name, mi, resource_group):
        try:
            result = self._mgmt_client.failover_groups.get(
                resource_group_name=resource_group,
                sql_managed_instance_name=mi,
                failover_group_name=name,
                headers=self._headers,
            )

            logger.debug(json.dumps(result.as_dict(), indent=4))
            return result

        except exceptions.HttpResponseError as e:
            logger.debug(e)
            return
        except Exception as e:
            raise e

    def get_failover_group(self, name, mi, resource_group):
        result = self._get_failover_group_resource(name, mi, resource_group)
        if result:
            return result
        else:
            raise Exception(
                "Failover group {0} associated with Arc-enabled SQL Managed Instance {1} does not exist in resource group {2}.".format(
                    name, mi, resource_group
                )
            )

    def failover_group_provisioning_completed(self, name, mi, resource_group):
        response: FailoverGroupResource = self._get_failover_group_resource(
            name, mi, resource_group
        )
        if (
            response
            and response.properties
            and response.properties.provisioning_state
        ):
            return response.properties.provisioning_state
        else:
            # Default status
            return "Accepted"

    def _get_failover_group_status(self, name, mi, resource_group):
        response: FailoverGroupResource = self._get_failover_group_resource(
            name, mi, resource_group
        )
        if (
            response
            and response.properties
            and response.properties.status
            and response.properties.status.state
        ):
            return response.properties.status.state
        else:
            # Default state
            return "Waiting"

    def list_failover_groups(self, mi, resource_group):
        try:
            result = []
            failover_groups = self._mgmt_client.failover_groups.list(
                resource_group_name=resource_group,
                sql_managed_instance_name=mi,
                headers=self._headers,
            )

            for fog in failover_groups:
                result.append(fog)

            print("Found {} failover group(s).".format(len(result)))
            return result if result else None

        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e
