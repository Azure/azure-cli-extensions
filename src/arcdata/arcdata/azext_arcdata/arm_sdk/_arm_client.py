# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azext_arcdata.arm_sdk.azure.constants import (
    API_VERSION,
    ARC_DATA_SERVICES_EXTENSION_API_VERSION,
    ARC_DATASERVICES_EXTENSION_RELEASE_TRAIN,
    ARC_DATASERVICES_EXTENSION_VERSION,
    CONNECTED_CLUSTER_API_VERSION,
    CUSTOM_LOCATION_API_VERSION,
    EXT_VERSION_ARM_API_VERSION_MAP,
    IMAGE_TAG_EXT_VERSION_MAP,
    INSTANCE_TYPE_DATA_CONTROLLER,
    RESOURCE_HYDRATION_API_VERSION,
    RESOURCE_PROVIDER_NAMESPACE,
    RESOURCE_TYPE_EXT_VERSION_MAP,
    ROLE_ASSIGNMENTS_API_VERSION,
)
from azext_arcdata.core.constants import (
    DEFAULT_IMAGE_POLICY,
    DEFAULT_IMAGE_TAG,
    DEFAULT_REGISTRY,
    DEFAULT_REPOSITORY,
)
from .swagger.swagger_1_2_0 import AzureArcDataManagementClient
from .swagger.swagger_1_2_0.models import (
    DataControllerResource,
    DataControllerProperties,
    ExtendedLocation,
    BasicLoginInformation,
    LogAnalyticsWorkspaceConfig,
)
from ._util import (
    conditional_retry,
    dict_to_dot_notation,
    wait,
    wait_for_error,
    wait_for_upgrade,
    retry,
    poll_provisioning_state,
)
from knack.log import get_logger
from collections import namedtuple
from requests.adapters import HTTPAdapter

import azure.core.exceptions as exceptions
import json
import time
import packaging
import requests
import os
import urllib3

__all__ = ["arm_clients"]

logger = get_logger(__name__)


def arm_clients(subscription, credential):
    c = {"dc": DataControllerClient(subscription, credential)}

    return namedtuple("CommandValueObject", " ".join(list(c.keys())))(**c)


# ============================================================================ #
# ============================================================================ #
# ============================================================================ #


class BaseClient(object):
    _RETRY_ATTEMPTS = 12
    _RETRY_BACKOFF = 0.1
    _RETRY_STATUS = [414, 429, 500, 502, 503, 504]

    def __init__(self, subscription, credential):
        self._subscription = subscription
        self._mgmt_client = AzureArcDataManagementClient(
            subscription_id=subscription,
        )
        self._session = requests.Session()
        self._session.mount(
            "https://",
            HTTPAdapter(
                max_retries=urllib3.util.Retry(
                    total=self._RETRY_ATTEMPTS,
                    backoff_factor=self._RETRY_BACKOFF,
                    status_forcelist=self._RETRY_STATUS,
                )
            ),
        )

        self._session.headers.update(
            {
                "Authorization": "Bearer {}".format(
                    credential.get_token().token
                ),
                "Content-Type": "application/json",
            }
        )
        self.MGMT_URL = (
            f"https://management.azure.com/subscriptions/{self._subscription}"
        )

    @property
    def subscription(self):
        return self._subscription


# ============================================================================ #
# ============================================================================ #
# ============================================================================ #


class DataControllerClient(BaseClient):
    def __init__(self, subscription, credential):
        super(DataControllerClient, self).__init__(subscription, credential)

    def create(self, name, resource_group, arm_tmpl, polling=True):
        url = (
            f"{self.MGMT_URL}"
            f"/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Resources"
            f"/deployments/{name}?api-version=2020-06-01"
        )

        logger.debug(url)
        response = self._session.put(url=url, json=arm_tmpl)
        logger.debug(response.text)
        logger.debug(response.status_code)

        if not response.ok:
            raise Exception(response.reason)

        return self._deployment_wait(name, resource_group) if polling else {}

    def get(self, name, resource_group):
        try:
            result = self._mgmt_client.data_controllers.get_data_controller(
                resource_group_name=resource_group,
                data_controller_name=name,
                headers=self._session.headers,
            )

            logger.debug(json.dumps(result.as_dict(), indent=4))

            return result
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            message = e.message.split("Message: ")[-1]
            raise exceptions.HttpResponseError(message)
        except Exception as e:
            raise e

    def check_if_dc_exists(self, name, resource_group):
        try:
            result = self._mgmt_client.data_controllers.get_data_controller(
                resource_group_name=resource_group,
                data_controller_name=name,
                headers=self._session.headers,
            )

            logger.debug(json.dumps(result.as_dict(), indent=4))

            return result
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            return

    def get_status(self, name, resource_group):
        result = retry(
            self.get,
            name,
            resource_group,
            max_tries=2000,
            e=exceptions.HttpResponseError,
        )

        if (
            result
            and result.properties
            and result.properties.k8_s_raw
            and "status" in result.properties.k8_s_raw
            and "state" in result.properties.k8_s_raw["status"]
        ):
            return result.properties.k8_s_raw["status"]
        else:
            # Status is unknown, so we we continue to wait.
            return None

    def delete(self, name, resource_group, polling=True):
        def is_data_controller_deleted_in_arm():
            return not self.check_if_dc_exists(name, resource_group)

        try:
            custom_location = self.get_custom_location_name(
                name, resource_group
            )

            conditional_retry(
                condition_func=is_data_controller_deleted_in_arm,
                func=self._mgmt_client.data_controllers.begin_delete_data_controller,
                resource_group_name=resource_group,
                data_controller_name=name,
                headers=self._session.headers,
                polling=polling,
                exception_type=exceptions.HttpResponseError,
            )

            # Delete resource hydration
            if self.has_hydration(resource_group, custom_location):
                self.disable_hydration(resource_group, custom_location)

            if polling:
                wait_for_error(
                    self.get,
                    name,
                    resource_group,
                    e=exceptions.HttpResponseError,
                )
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def list(self, resource_group=None, cl_name=None):
        try:
            if resource_group:
                result = self._mgmt_client.data_controllers.list_in_group(
                    resource_group, headers=self._session.headers
                )
            else:
                result = (
                    self._mgmt_client.data_controllers.list_in_subscription(
                        headers=self._session.headers
                    )
                )

            # Iterate over the list of data controllers and convert to a list
            result = [dc for dc in result]

            # Filter by custom location if provided
            if cl_name:
                cl_resource_id = self.get_custom_location(
                    custom_location=cl_name, resource_group=resource_group
                )["id"]

                result = [
                    dc
                    for dc in result
                    if dc.extended_location
                    and dc.extended_location.name
                    and dc.extended_location.name.lower()
                    == cl_resource_id.lower()
                ]

            return result
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def patch(
        self, name, resource_group, properties: dict, api_version=API_VERSION
    ):
        try:
            result = (
                self._mgmt_client.data_controllers.begin_patch_data_controller(
                    resource_group_name=resource_group,
                    data_controller_name=name,
                    data_controller_resource=properties,
                    headers=self._session.headers,
                    api_version=api_version,
                )
            )

            return result
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def upgrade(
        self,
        name,
        resource_group,
        target,
        dry_run=False,
        polling=True,
    ):
        try:

            def _upgrade_completed():
                status = self.get_status(name, resource_group)
                return status["runningVersion"] if status else None

            dc = self.get(name, resource_group)

            # Get latest API version supported by extension
            custom_location = dc.extended_location.name.split("/")[-1]
            api_version = self.resolve_api_version(
                INSTANCE_TYPE_DATA_CONTROLLER, custom_location, resource_group
            )

            dc_docker = dc.properties.k8_s_raw["spec"]["docker"]
            current_registry = dc_docker.get("registry")

            if current_registry == "mcr.microsoft.com":
                current_image_tag = dc_docker.get("imageTag")

                # Sorted in descending order (latest version first)
                sorted_image_tags = list(IMAGE_TAG_EXT_VERSION_MAP.keys())

                if current_image_tag == sorted_image_tags[0]:
                    # Already at the latest version
                    print(
                        "Data controller is already running the latest image "
                        "released with the current version of the arcdata CLI extension."
                    )
                    print(
                        "Please see https://aka.ms/arc-data-services-version-log for more details."
                    )
                    return

                # Get the next image tag
                next_image_tag = sorted_image_tags[
                    sorted_image_tags.index(current_image_tag) - 1
                ]

                if target:
                    if target not in sorted_image_tags:
                        raise Exception(
                            "Invalid desired image version provided {0} \n".format(
                                target
                            )
                            + "Please see https://aka.ms/arc-data-services-version-log to view released image versions."
                        )

                    if target != next_image_tag:
                        raise Exception(
                            "Invalid desired image version provided. "
                            "You must upgrade to the next image version in the sequence: {0}\n".format(
                                next_image_tag
                            )
                            + "Please see https://aka.ms/arc-data-services-version-log to view released image versions."
                        )

                # Use the next image tag in the sequence
                target = next_image_tag

            else:
                # Private registry
                # We do not know the next image tag in the private registry
                # Use latest image if not provided
                target = target or DEFAULT_IMAGE_TAG

            # We cannot initiate a new PUT request if a previous request is
            # still in the Accepted state.
            #
            if dc.properties.provisioning_state == "Accepted":
                raise Exception(
                    "An existing operation is in progress. Please check your "
                    "data controller's status in the Azure Portal."
                )

            # if dry_run is specified, we will simply print and return.
            if dry_run:
                print("****Dry Run****")
                print(
                    "The Arc data controller would be upgraded to the following image version: {0}".format(
                        target
                    )
                )
                return

            cluster_name = self.get_cluster_name(name, resource_group)
            custom_location = self.get_custom_location_name(
                name, resource_group
            )
            extension = self.get_extension(cluster_name, resource_group)

            # Enable resource hydration
            if not self.has_hydration(resource_group, custom_location):
                self.enable_hydration(resource_group, custom_location)

            # Upgrade boostrapper extension
            self.upgrade_bootstrapper_extension(
                cluster_name, extension, resource_group, dc, target, polling
            )

            # - Patch DC resource with new image tag
            patch_payload = {
                "properties": {
                    "k8sRaw": {"spec": {"docker": {"imageTag": target}}}
                }
            }

            print("Upgrading data controller to version {0}...".format(target))
            try:
                self.patch(
                    name,
                    resource_group,
                    properties=patch_payload,
                    api_version=api_version,
                )
            except:
                # AzureArcData API 2021-11-01 doesn't support patch
                dc.properties.k8s_raw["spec"]["docker"]["imageTag"] = target
                self._mgmt_client.data_controllers.begin_put_data_controller(
                    resource_group_name=resource_group,
                    data_controller_name=name,
                    data_controller_resource=dc,
                    polling=polling,
                    headers=self._session.headers,
                    api_version=api_version,
                )

            if polling:
                wait_for_upgrade(target, self.get_status, name, resource_group)
                if _upgrade_completed() != target:
                    raise Exception(
                        "Data controller upgrade failed. Please check your data controller's status in "
                        "the Azure Portal or restart the upgrade process."
                    )

                print(
                    "Data controller {0} has been successfully upgraded.".format(
                        name
                    )
                )
                return self.get(name, resource_group)
            else:
                print(
                    "Data controller {} is being upgraded. Please check your "
                    "data controller's status in the Azure Portal.".format(name)
                )

        except exceptions.HttpResponseError as e:
            logger.debug(e)
            message = e.message.split("Message: ")[-1]
            raise exceptions.HttpResponseError(message)

    def get_connected_cluster_location(self, cluster_name, resource_group):
        cluster = self.get_connected_cluster(cluster_name, resource_group)
        return cluster["location"]

    def get_connected_cluster(self, cluster_name, resource_group):
        try:
            url = (
                f"{self.MGMT_URL}/resourceGroups/{resource_group}"
                f"/providers/Microsoft.Kubernetes"
                f"/connectedClusters"
                f"?api-version={CONNECTED_CLUSTER_API_VERSION}"
            )

            logger.debug(url)
            response = self._session.get(url=url)

            if (
                response.status_code == 404
                or len(response.json()["value"]) == 0
            ):
                raise Exception(
                    f"No connected cluster was found under the resource group "
                    f"{resource_group}. Please create a connected cluster first."
                )
            else:
                connected_clusters = response.json()
                for resource in connected_clusters["value"]:
                    if cluster_name == resource["name"]:
                        # log cluster properties
                        for key, value in resource["properties"].items():
                            if key != "agentPublicKeyCertificate":
                                logger.debug(f"{key} = {value}")
                        logger.debug(f"location = {resource['location']}")
                        return resource

                raise Exception(
                    f"The cluster {cluster_name} was not found in the resource "
                    f"group {resource_group}."
                )
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def get_cluster_name(
        self, dc_name, resource_group, custom_location_name=None
    ):
        if not custom_location_name:
            custom_location_name = self.get_custom_location_name(
                dc_name, resource_group
            )
        cl = self.get_custom_location(custom_location_name, resource_group)
        _, cluster_name = os.path.split(cl["properties"]["hostResourceId"])

        return cluster_name

    def get_custom_location_name(self, dc_name, resource_group):
        try:
            dc = self.get(dc_name, resource_group)
            _, custom_location_name = os.path.split(dc.extended_location.name)
            return custom_location_name
        except exceptions.HttpResponseError as e:
            return

    def get_custom_location(self, custom_location, resource_group):
        try:
            url = (
                f"{self.MGMT_URL}/resourceGroups/{resource_group}"
                f"/providers/Microsoft.ExtendedLocation"
                f"/customLocations/{custom_location}"
                f"?api-version={CUSTOM_LOCATION_API_VERSION}"
            )

            logger.debug(url)
            response = self._session.get(url=url)

            if response.status_code == 404:
                raise Exception(
                    f"Custom location '{custom_location}' was not found under the resource group "
                    f"'{resource_group}'"
                )

            custom_location = response.json()
            logger.debug(json.dumps(custom_location, indent=4))

            return custom_location
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def get_extension(self, cluster_name, resource_group):
        try:
            url = (
                "{url}/resourceGroups/{resource_group}/providers"
                "/Microsoft.Kubernetes/connectedClusters/{cluster_name}"
                "/providers/Microsoft.KubernetesConfiguration/extensions"
                "?api-version={version}".format(
                    url=self.MGMT_URL,
                    resource_group=resource_group,
                    cluster_name=cluster_name,
                    version=ARC_DATA_SERVICES_EXTENSION_API_VERSION,
                )
            )

            logger.debug(url)
            res = self._session.get(url=url)
            if res.status_code == 404:
                raise exceptions.HttpResponseError(
                    "404 error while calling: {}".format(url)
                )

            res = res.json()
            for extension in [] if len(res["value"]) == 0 else res["value"]:
                logger.debug(json.dumps(extension, indent=4))
                properties = extension["properties"]
                if properties["extensionType"] == "microsoft.arcdataservices":
                    return extension

            return None
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)

    def _get_extension_state(self, cluster_name, resource_group):
        extension = self.get_extension(cluster_name, resource_group)
        if extension:
            return extension["properties"]["provisioningState"]
        else:
            # Will never hit this since a DC by definition has an extension
            raise Exception(
                f"No extension found in cluster '{cluster_name}' "
                f"under the resource group '{resource_group}'."
            )

    def get_docker_details_from_extension(self, cluster_name, resource_group):
        try:
            extension = self.get_extension(cluster_name, resource_group)
            if not extension:
                logger.debug("No Arc data services extension found")
                return {}

            properties = extension["properties"]
            configuration_settings = properties["configurationSettings"]

            version = properties.get(
                "version", ARC_DATASERVICES_EXTENSION_VERSION
            )
            image_full_path = configuration_settings.get(
                "systemDefaultValues.image", None
            )
            image_pull_policy = configuration_settings.get(
                "systemDefaultValues.imagePullPolicy", DEFAULT_IMAGE_POLICY
            )

            # Often image_full_path is not set, so we need to use defaults
            if not image_full_path:
                registry = DEFAULT_REGISTRY
                repository = DEFAULT_REPOSITORY

                # Reverse lookup image tag by current extension version
                # This ensures that the DC and helm chart are aligned
                image_tag = {
                    version: image_tag
                    for image_tag, version in IMAGE_TAG_EXT_VERSION_MAP.items()
                }.get(version, DEFAULT_IMAGE_TAG)
            else:
                # -- image_full_path is of the form <registry>/<repository>/<image_name>:<image_tag>
                # -- note: repository can have multiple levels of nesting, e.g arcdata/preview
                tokens = image_full_path.split("/")
                registry, repository, image_tag = (
                    tokens[0],
                    "/".join(tokens[1:-1]),
                    tokens[-1].split(":")[-1],
                )

            return {
                "registry": registry,
                "repository": repository,
                "imageTag": image_tag,
                "imagePullPolicy": image_pull_policy,
            }
        except Exception as e:
            logger.debug(e)
            return {}

    def upgrade_bootstrapper_extension(
        self,
        cluster_name,
        extension,
        resource_group,
        data_controller,
        image_tag,
        polling=True,
    ):
        if not extension:
            raise Exception("The Arc data services extension was not found.")

        url = (
            "{url}/resourceGroups/{resource_group}/providers"
            "/Microsoft.Kubernetes/connectedClusters/{cluster_name}"
            "/providers/Microsoft.KubernetesConfiguration/extensions/{ext_name}"
            "?api-version={version}".format(
                url=self.MGMT_URL,
                resource_group=resource_group,
                cluster_name=cluster_name,
                ext_name=extension["name"],
                version=ARC_DATA_SERVICES_EXTENSION_API_VERSION,
            )
        )
        data_controller_cr = dict_to_dot_notation(
            data_controller.properties.k8_s_raw
        )
        registry = data_controller_cr.spec.docker.registry
        repository = data_controller_cr.spec.docker.repository
        full_image_path = (
            f"{registry}/{repository}/arc-bootstrapper:{image_tag}"
        )

        if registry and registry != "mcr.microsoft.com":
            # Private registry
            ext_train = (
                os.getenv("ARC_DATASERVICES_EXTENSION_RELEASE_TRAIN")
                or ARC_DATASERVICES_EXTENSION_RELEASE_TRAIN
            )
            ext_tag = (
                os.getenv("ARC_DATASERVICES_EXTENSION_VERSION_TAG")
                or ARC_DATASERVICES_EXTENSION_VERSION
            )
        else:
            # MCR registry
            ext_train = extension["properties"].get(
                "releaseTrain", ARC_DATASERVICES_EXTENSION_RELEASE_TRAIN
            )
            ext_tag = (
                IMAGE_TAG_EXT_VERSION_MAP[image_tag]
                if image_tag in IMAGE_TAG_EXT_VERSION_MAP
                else ARC_DATASERVICES_EXTENSION_VERSION
            )

        print(
            "Using release train '{0}' and extension version '{1}'".format(
                ext_train, ext_tag
            )
        )

        payload = {
            "properties": {
                "releaseTrain": ext_train,
                "version": ext_tag,
                "configurationSettings": {
                    "systemDefaultValues.image": full_image_path
                },
            }
        }

        print("Upgrading the arcdataservices extension...")

        res = self._session.patch(url=url, data=json.dumps(payload))
        logger.debug(res.status_code)
        logger.debug(res.text)
        res.raise_for_status()

        if polling:
            state = self._get_extension_state(cluster_name, resource_group)
            cnt = 0
            timeout = 300  # 5 minutes
            while state != "Succeeded":
                if state == "Failed":
                    raise Exception(
                        "Failed to upgrade bootstrapper extension. Please retry this upgrade operation."
                    )
                if cnt < timeout:
                    time.sleep(5)
                    cnt += 5
                else:
                    raise Exception(
                        "Arcdataservices extension upgrade has timed out. "
                        "Please check the status of "
                        "the bootstrapper pod in your cluster."
                    )
                state = self._get_extension_state(cluster_name, resource_group)

            print("Successfully upgraded bootstrapper extension.")
            return self.get_extension(cluster_name, resource_group)

        else:
            print(
                "Initiated extension upgrade. Please check the status of "
                "the bootstrapper pod in your cluster."
            )

    def get_role_assignments(self, cluster_name, resource_group):
        try:
            extension = self.get_extension(cluster_name, resource_group)
            url = (
                "{url}/resourceGroups/{resource_group}/providers/"
                "Microsoft.Authorization/roleAssignments?"
                "api-version={version}&%24filter=assignedTo(%27{id}%27)".format(
                    url=self.MGMT_URL,
                    resource_group=resource_group,
                    version=ROLE_ASSIGNMENTS_API_VERSION,
                    id=extension["identity"]["principalId"],
                )
            )

            logger.debug(url)
            response = self._session.get(url=url)
            if response.status_code == 404:
                raise exceptions.HttpResponseError(
                    "404 error while calling: {}".format(url)
                )
            else:
                return response.json()
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def resolve_namespace(
        self, namespace, custom_location, cluster_name, resource_group
    ):
        ext = self.get_extension(cluster_name, resource_group)

        if not ext:
            # No CL yet so just make namespace == CL or use the one provided
            namespace = namespace or custom_location
        else:
            # use the namespace defined in the existing CL
            logger.debug(json.dumps(ext, indent=4))
            ext = dict_to_dot_notation(ext)
            ext_namespace = ext.properties.scope.cluster.releaseNamespace

            if namespace and namespace != ext_namespace:
                raise ValueError(
                    f"The namespace provided {namespace} "
                    f"does not match the namespace {ext_namespace}"
                    f" in the existing custom location "
                    f"{custom_location}."
                )
            else:
                namespace = ext_namespace

        return namespace

    def get_custom_location_namespace(self, custom_location, resource_group):
        custom_location_resource = self.get_custom_location(
            custom_location, resource_group
        )
        try:
            return custom_location_resource["properties"]["namespace"]
        except:
            raise ValueError(
                "Unable to retrieve Kubernetes namespace from custom location"
            )

    def get_custom_location_region(self, custom_location, resource_group):
        custom_location_resource = self.get_custom_location(
            custom_location, resource_group
        )
        try:
            return custom_location_resource["location"]
        except:
            raise ValueError(
                "Unable to retrieve Azure region from custom location"
            )

    def get_resource_graph(self, cluster_name, resource_group, namespace):
        try:
            url = (
                "https://management.azure.com/providers/Microsoft."
                "ResourceGraph/resources?api-version=2021-03-01"
            )

            logger.debug(url)
            query = "\
                resources\
                | where subscriptionId =~ '{subscriptionId}'\
                | where resourceGroup == '{resourceGroup}'\
                | where type =~ 'microsoft.kubernetes/connectedclusters'\
                | where properties.provisioningState =~ 'succeeded'\
                | where name == '{cluster}'\
                | project clusterId=id, subscriptionId, clusterName=name\
                | join kind=leftouter (kubernetesconfigurationresources\
                    | where subscriptionId =~ '{subscriptionId}'\
                    | where resourceGroup == '{resourceGroup}'\
                    | where type =~ 'microsoft.kubernetesconfiguration/extensions'\
                    | where properties.ExtensionType =~ 'microsoft.arcdataservices'\
                    | where (properties.ProvisioningState =~ 'succeeded' or properties.InstallState =~ 'installed')\
                    | project extensionId=id, subscriptionId, namespace=properties.Scope.cluster.ReleaseNamespace)\
                on $left.subscriptionId == $right.subscriptionId\
                | where extensionId contains clusterId\
                | extend namespace=tostring(namespace)\
                | where namespace =~ '{namespace}'\
                | join (resources\
                    | where subscriptionId =~ '{subscriptionId}'\
                    | where resourceGroup == '{resourceGroup}'\
                    | where type =~ 'microsoft.extendedLocation/customLocations'\
                    | where properties.provisioningState =~ 'succeeded'\
                    | extend hostClusterId = tostring(properties.hostResourceId)\
                    | extend namespace = tostring(properties.namespace)\
                    | project hostClusterId, customLocationName=name, namespace)\
                on $left.clusterId == $right.hostClusterId and $left.namespace == $right.namespace\
                | project clusterName, namespace, customLocationName\
            ".format(
                subscriptionId=self.subscription,
                resourceGroup=resource_group,
                cluster=cluster_name,
                namespace=namespace,
            )

            payload = {"subscriptions": [self.subscription], "query": query}
            payload = json.dumps(payload, indent=4)

            response = self._session.post(url=url, data=payload).json()
            logger.debug(json.dumps(response, indent=4))
            return response
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def _deployment_wait(self, name, resource_group):
        def _dc_provisioning_completed(name, resource_group):
            try:
                result = self.get(name, resource_group)
            except exceptions.HttpResponseError as e:
                result = None

            if (
                result
                and result.properties
                and result.properties.provisioning_state
            ):
                return result.properties.provisioning_state
            else:
                # Status is unknown, so we we continue to wait.
                return "Accepted"

        def _dc_deployment_completed():
            result = retry(
                self.get,
                name,
                resource_group,
                max_tries=200,
                e=exceptions.HttpResponseError,
            )

            if (
                result
                and result.properties
                and result.properties.k8_s_raw
                and "status" in result.properties.k8_s_raw
                and "state" in result.properties.k8_s_raw["status"]
            ):
                return result.properties.k8_s_raw["status"]["state"]
            else:
                # Status is unknown, so we we continue to wait.
                return None

        # Verify that DC ARM resource has provisioned
        poll_provisioning_state(
            _dc_provisioning_completed,
            name,
            resource_group,
            wait_time=300,
        )

        # Setting a total wait time of 1800 sec with a step of 5 sec
        wait(_dc_deployment_completed)
        if _dc_deployment_completed() != "Ready":
            raise Exception(
                "Arc data controller deployment failed. Please check your data controller's status in the Azure Portal \
                or restart this create process."
            )
        return self.get(name, resource_group)

    def __create_depreciated_dc__(
        self,
        control,
        resource_group,
        custom_location,
        cred,
        log_analytics,
        polling=True,
        api_version=API_VERSION,
    ):
        try:
            spec = control.spec
            name = spec.settings.controller.displayName

            # -- extended-location --
            extended_location = ExtendedLocation(
                name=(
                    "/subscriptions/"
                    + self._subscription
                    + "/resourcegroups/"
                    + resource_group
                    + "/providers/microsoft.extendedlocation/customlocations/"
                    + custom_location
                ),
                type="CustomLocation",
            )

            # -- properties --
            metrics_dashboard_credential = BasicLoginInformation(
                username=cred.metrics_username, password=cred.metrics_password
            )
            logs_dashboard_credential = BasicLoginInformation(
                username=cred.log_username, password=cred.log_password
            )
            log_analytics_workspace_config = None
            if log_analytics:
                log_analytics_workspace_config = LogAnalyticsWorkspaceConfig(
                    workspace_id=log_analytics["workspace_id"],
                    primary_key=log_analytics["primary_key"],
                )
            k8sRaw = control.to_dict
            properties = DataControllerProperties(
                infrastructure=spec.infrastructure,
                k8_s_raw=k8sRaw,
                metrics_dashboard_credential=metrics_dashboard_credential,
                logs_dashboard_credential=logs_dashboard_credential,
                log_analytics_workspace_config=log_analytics_workspace_config,
            )
            data_controller_resource = DataControllerResource(
                location=spec.settings.azure.location,
                extended_location=extended_location,
                properties=properties,
            )

            # -- log --
            d = data_controller_resource.as_dict().copy()
            d["properties"]["metrics_dashboard_credential"]["password"] = "*"
            d["properties"]["logs_dashboard_credential"]["password"] = "*"

            logger.debug("<DataControllerResource>")
            logger.debug(json.dumps(d, indent=4))

            self._mgmt_client.data_controllers.begin_put_data_controller(
                resource_group_name=resource_group,
                data_controller_name=name,
                data_controller_resource=data_controller_resource,
                polling=polling,
                headers=self._session.headers,
                api_version=api_version,
            )

            if polling:
                return self._deployment_wait(name, resource_group)
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)
        except Exception as e:
            raise e

    def get_sync_rules(self, resource_group, custom_location):
        """
        Gets all resource sync rules of a custom location
        """
        try:
            url = (
                f"{self.MGMT_URL}"
                f"/resourceGroups/{resource_group}"
                f"/providers/Microsoft.ExtendedLocation"
                f"/customLocations/{custom_location}"
                f"/resourceSyncRules"
                f"?api-version={RESOURCE_HYDRATION_API_VERSION}"
            )
            res = self._session.get(url=url)
            logger.debug(res.status_code)
            logger.debug(res.text)
            res = res.json().get("value") or []
            return res
        except exceptions.HttpResponseError as e:
            logger.debug(e)
            raise exceptions.HttpResponseError(e.message)

    def has_hydration(self, resource_group, custom_location):
        """
        Returns the Arc data services resource hydration rule if enabled on the
        provided `custom_location`.
        """

        def _is_valid_priority(properties):
            priority = properties.priority
            return priority == 100

        def _is_valid_match_labels(properties):
            deprecated_label = properties.selector.matchLabels.to_dict.get(
                "management.azure.com/resourceProvider"
            )
            new_label = properties.selector.matchLabels.to_dict.get(
                "management.azure.com/provider-name"
            )
            label = new_label or deprecated_label
            return label and label == RESOURCE_PROVIDER_NAMESPACE

        def _is_valid_target_resource_group(properties):
            return (
                properties.targetResourceGroup
                == f"/subscriptions/{self.subscription}"
                f"/resourceGroups/{resource_group}"
            )

        for rule in self.get_sync_rules(resource_group, custom_location):
            p = dict_to_dot_notation(rule).properties
            if (
                _is_valid_priority(p)
                and _is_valid_match_labels(p)
                and _is_valid_target_resource_group(p)
            ):
                logger.debug("Hydration rule exists.")
                return rule

        return False

    def enable_hydration(self, resource_group, custom_location):
        """
        Adds the resource sync rule to the given custom location
        """

        try:
            url = (
                f"{self.MGMT_URL}"
                f"/resourceGroups/{resource_group}"
                f"/providers/Microsoft.ExtendedLocation"
                f"/customLocations/{custom_location}"
                f"/resourceSyncRules/defaultResourceSyncRule"
                f"?api-version={RESOURCE_HYDRATION_API_VERSION}"
            )

            location = self.get_custom_location_region(
                custom_location, resource_group
            )

            target_resource_group = f"/subscriptions/{self.subscription}/resourceGroups/{resource_group}"

            payload = {
                "location": location,
                "type": "Microsoft.ExtendedLocation/customLocations/resourceSyncRules",
                "properties": {
                    "priority": 100,
                    "targetResourceGroup": target_resource_group,
                    "selector": {
                        "matchLabels": {
                            "management.azure.com/provider-name": RESOURCE_PROVIDER_NAMESPACE
                        }
                    },
                },
            }

            res = self._session.put(url, data=json.dumps(payload))
            logger.debug(res.status_code)
            logger.debug(res.text)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as e:
            logger.debug(e)

    def disable_hydration(self, resource_group, custom_location):
        """
        Deletes the Arc data services resource sync rule in the given custom location
        """
        try:
            rule = self.has_hydration(resource_group, custom_location)
            if rule and "name" in rule:
                name = rule["name"]
                url = (
                    f"{self.MGMT_URL}"
                    f"/resourceGroups/{resource_group}"
                    f"/providers/Microsoft.ExtendedLocation"
                    f"/customLocations/{custom_location}"
                    f"/resourceSyncRules/{name}"
                    f"?api-version={RESOURCE_HYDRATION_API_VERSION}"
                )

                res = self._session.delete(url)
                logger.debug(res.status_code)
                logger.debug(res.text)
                res.raise_for_status()
                return res
        except requests.exceptions.HTTPError as e:
            logger.debug(e)

    def resolve_api_version(
        self, resource_type, custom_location_name, resource_group
    ):
        """
        Resolves the API version for the given resource type and helm chart extension
        """

        # Get current extension
        custom_location_resource = self.get_custom_location(
            custom_location_name, resource_group
        )
        cluster_name = (
            custom_location_resource["properties"]
            .get("hostResourceId")
            .split("/")[-1]
        )
        extension = self.get_extension(cluster_name, resource_group)

        if not extension:
            raise Exception(
                "Unable to retrieve Arc data services extension associated with custom location {0}".format(
                    custom_location_name
                )
            )

        current_version = extension["properties"].get(
            "version", ARC_DATASERVICES_EXTENSION_VERSION
        )

        # Helm tags are often in the form of 1.13.0-2022-11-08-master-426b7484e
        # Only the part before the first dash follows semantic versioning
        current_version = current_version.split("-")[0]

        # Check that resource CRUD is supported by the current extension version
        earliest_supported_version = RESOURCE_TYPE_EXT_VERSION_MAP[
            resource_type
        ]

        if not (
            packaging.version.parse(current_version)
            >= packaging.version.parse(earliest_supported_version)
        ):
            raise ValueError(
                "This cluster's Arc data services extension must be updated to "
                "version {0} or later in order to create or update {1}.".format(
                    earliest_supported_version, resource_type
                )
            )

        # Get latest ARM API supported by current extension
        api_version = EXT_VERSION_ARM_API_VERSION_MAP.get(
            current_version, API_VERSION
        )
        logger.debug("Resolved API version: " + api_version)
        return api_version
