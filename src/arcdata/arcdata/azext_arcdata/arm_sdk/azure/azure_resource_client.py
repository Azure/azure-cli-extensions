# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

from azure.mgmt.authorization import AuthorizationManagementClient
from azure.common.credentials import get_cli_profile
from azure.core.exceptions import HttpResponseError
from azure.mgmt.core.tools import is_valid_resource_id, parse_resource_id

from azext_arcdata.arm_sdk.azure.constants import (
    API_VERSION,
    INSTANCE_TYPE_DATA_CONTROLLER,
    MONITORING_METRICS_PUBLISHER_ROLE_ID,
    RESOURCE_PROVIDER_NAMESPACE,
    ROLE_DESCRIPTIONS,
)

from azure.cli.core.azclierror import (
    AzureResponseError,
    ResourceNotFoundError,
    ValidationError,
)
from azext_arcdata.core.identity import ArcDataCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.extendedlocation import CustomLocations
from . import constants as azure_constants
from azext_arcdata.arm_sdk.azure.ad_auth_util import acquire_token
from azext_arcdata.arm_sdk.azure.constants import (
    ARC_DATA_SERVICES_EXTENSION_API_VERSION,
    INSTANCE_TYPE_POSTGRES,
    INSTANCE_TYPE_SQL,
)
from azext_arcdata.arm_sdk.azure.export_util import (
    format_sqlmi_license_type_for_azure,
    format_sqlmi_tier_for_azure,
    get_log_workspace_credentials_from_env,
)
from azext_arcdata.sqlmi.constants import SQL_MI_SKU_NAME_VCORE
from azext_arcdata.kubernetes_sdk.client import http_status_codes
from azext_arcdata.dc.exceptions import (
    ServerError,
    RequestTimeoutError,
)
from azext_arcdata.core.output import OutputStream
from azext_arcdata.core.util import retry
from urllib3.exceptions import NewConnectionError, MaxRetryError, TimeoutError
from knack.log import get_logger
from requests.exceptions import HTTPError

import json
import os
import uuid
import pydash as _
import requests

CONNECTION_RETRY_ATTEMPTS = 12
RETRY_INTERVAL = 5

log = get_logger(__name__)

err_msg = '\tFailed to {} resource: "{}" with error: "{}"'

__all__ = ["AzureResourceClient"]


class AzureResourceClient(object):
    """
    Azure Resource Client
    """

    def __init__(self, subscription):
        self._subscription = subscription

    @property
    def stderr(self):
        return OutputStream().stderr.write

    @property
    def stdout(self):
        return OutputStream().stdout.write

    def update_dc_resource(
        self,
        name,
        resource_group_name,
        auto_upload_logs=None,
        auto_upload_metrics=None,
        polling=True,
        api_version=API_VERSION,
    ):
        """
        Update data controller properties.
        """

        # get dc resource from Azure
        dc_resource = self.get_generic_azure_resource(
            resource_group_name=resource_group_name,
            resource_provider_namespace=RESOURCE_PROVIDER_NAMESPACE,
            resource_type=INSTANCE_TYPE_DATA_CONTROLLER,
            resource_name=name,
            api_version=API_VERSION,
        )

        is_dc_directly_connected = self._is_dc_directly_connected(dc_resource)

        if auto_upload_logs is not None:
            if not is_dc_directly_connected:
                raise ValidationError(
                    "Automatic upload of logs is only supported for data "
                    "controllers in direct connectivity mode"
                )

            self._update_auto_upload_logs(dc_resource, auto_upload_logs)

        if auto_upload_metrics is not None:
            if not is_dc_directly_connected:
                raise ValidationError(
                    "Automatic upload of metrics is only supported for data "
                    "controllers in direct connectivity mode"
                )

            self._update_auto_upload_metrics(
                dc_resource, resource_group_name, auto_upload_metrics
            )

        # update dc Azure resource
        response = self.create_or_update_generic_azure_resource(
            resource_group_name=resource_group_name,
            resource_provider_namespace=RESOURCE_PROVIDER_NAMESPACE,
            resource_type=INSTANCE_TYPE_DATA_CONTROLLER,
            resource_name=name,
            api_version=api_version,
            parameters=dc_resource,
            wait_for_response=polling,
        )

        self.stdout("Updated Arc Data Controller {}.".format(name))
        return response

    def create_azure_resource(
        self,
        instance_type,
        data_controller_name,
        resource_name,
        subscription_id,
        resource_group_name,
        location,
        extended_properties=None,
    ):
        """
        Create Azure resource by instance
        :param location: Azure location
        :param resource_group_name: resource group name
        :param subscription_id: Azure subscription ID
        :param resource_name: resource name
        :param data_controller_name: data controller name
        :param instance_type: Azure resource type
        :param extended_properties: Dict or object containing addional
        properties to be included in the properties bag.
        :return:
        """

        data_controller_id = azure_constants.RESOURCE_URI.format(
            subscription_id,
            resource_group_name,
            "dataControllers",
            data_controller_name,
        )

        params = {
            "location": location,
            "properties": {"dataControllerId": data_controller_id},
        }

        if extended_properties:
            params["properties"].update(extended_properties)
            if instance_type == INSTANCE_TYPE_SQL:
                self.populate_sql_properties(params, extended_properties)

        url, resource_uri = self._get_request_url(
            subscription_id, resource_group_name, instance_type, resource_name
        )
        try:
            response = requests.put(
                url,
                headers=self._get_header(resource_uri),
                data=json.dumps(params),
            )
            response.raise_for_status()
            print(
                '\t"{}" has been uploaded to Azure "{}".'.format(
                    resource_name, resource_uri
                )
            )
            log.info(
                "Create Azure resource {} response header: {}".format(
                    resource_uri, response.headers
                )
            )
        except requests.exceptions.HTTPError as e:
            response_json_string = json.loads(response.text)
            if (
                "error" in response_json_string
                and "message" in response_json_string["error"]
            ):
                self.stderr(response_json_string["error"]["message"])
            log.error(err_msg.format("Create", resource_name, e.response.text))

    def _get_azure_resource(
        self, resource_name, instance_type, subscription_id, resource_group_name
    ):
        url, resource_uri = self._get_request_url(
            subscription_id, resource_group_name, instance_type, resource_name
        )
        try:
            response = requests.get(url, headers=self._get_header(resource_uri))
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            log.error(err_msg.format("Get", resource_name, e.response.text))

    def get_azure_resource(
        self, resource_name, instance_type, subscription_id, resource_group_name
    ):
        """
        Get an azure resource
        :return: The resource, if found, None if not found (http 404). Raise an
        error otherwise.
        """
        url, resource_uri = self._get_request_url(
            subscription_id, resource_group_name, instance_type, resource_name
        )
        try:
            response = requests.get(url, headers=self._get_header(resource_uri))
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return None

            log.error(err_msg.format("Get", resource_name, e.response.text))

        if response.ok:
            return response.json()

        raise Exception(
            "Failed getting Azure resource. Resource name: "
            "'{resource_name}', type: '{instance_type}', "
            "subscription id: '{subscription_id}', "
            "resource group: '{resource_group_name}'. Http response: "
            "({status_code}) {text}".format(
                resource_name=resource_name,
                instance_type=instance_type,
                subscription_id=subscription_id,
                resource_group_name=resource_group_name,
                status_code=response.status_code,
                text=response.text,
            )
        )

    def delete_azure_resource(
        self, resource_name, instance_type, subscription_id, resource_group_name
    ):
        """
        Delete Azure resource
        :param resource_name:
        :param instance_type:
        :param subscription_id:
        :param resource_group_name:
        :return:
        """
        try:
            url, resource_uri = self._get_request_url(
                subscription_id,
                resource_group_name,
                instance_type,
                resource_name,
            )

            response = requests.delete(
                url, headers=self._get_header(resource_uri)
            )
            response.raise_for_status()

            if response.status_code != requests.codes["no_content"]:
                print(
                    '\t"{}" has been deleted from Azure "{}".'.format(
                        resource_name, resource_uri
                    )
                )
                log.info(
                    "Delete Azure resource {} response header: {}".format(
                        resource_uri, response.headers
                    )
                )

        except requests.exceptions.HTTPError as e:
            log.error(err_msg.format("Delete", resource_name, e.response.text))

    def create_azure_data_controller(
        self,
        uid,
        resource_name,
        subscription_id,
        resource_group_name,
        location,
        public_key,
        extended_properties=None,
    ):
        """
        Create Azure resource by instance
        :param public_key:
        :param uid: uid
        :param resource_name: resource name
        :param location: Azure location
        :param subscription_id: Azure subscription ID
        :param resource_group_name: resource group name
        :param extended_properties: Dict or object containing additional
        properties to be included in properties bag.
        :return:
        """

        params = {
            "location": location,
            "properties": {
                "onPremiseProperty": {"id": uid, "publicSigningKey": public_key}
            },
        }

        if extended_properties:
            params["properties"].update(extended_properties)

        url, resource_uri = self._get_request_url(
            subscription_id,
            resource_group_name,
            azure_constants.INSTANCE_TYPE_DATA_CONTROLLER,
            resource_name,
        )

        response = requests.put(
            url, headers=self._get_header(resource_uri), data=json.dumps(params)
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            response_json_string = json.loads(response.text)
            if (
                "error" in response_json_string
                and "message" in response_json_string["error"]
            ):
                self.stderr(response_json_string["error"]["message"])
            log.error(err_msg.format("Create", resource_name, e.response.text))
            raise
        print(
            '\t"{}" is uploaded to Azure "{}"'.format(
                resource_name, resource_uri
            )
        )
        log.info(
            "Create data controller {} response header: {}".format(
                resource_uri, response.headers
            )
        )

    @staticmethod
    def _get_rp_endpoint():
        endpoint = azure_constants.AZURE_ARM_URL
        if "RP_TEST_ENDPOINT" in os.environ:
            endpoint = os.environ["RP_TEST_ENDPOINT"]
        return endpoint

    def _build_dps_header(self, correlation_vector):
        access_token = acquire_token(azure_constants.AZURE_AF_SCOPE)

        request_id = str(uuid.uuid4())
        headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json",
            "Content-Encoding": "gzip",
            "X-Request-Id": request_id,
            "X-Correlation-Vector": correlation_vector,
        }
        log.info(
            "Usage upload correlation_vector: {}, request_id: {}".format(
                correlation_vector, request_id
            )
        )
        return headers

    def _get_header(self, resource_uri):
        request_id = str(uuid.uuid4())
        log.info(
            "Resource uri: {}, request_id: {}".format(resource_uri, request_id)
        )
        return {
            "Authorization": "Bearer "
            + acquire_token(azure_constants.AZURE_ARM_SCOPE),
            "Content-Type": "application/json",
            "x-ms-client-request-id": request_id,
            "x-ms-return-client-request-id": "true",
        }

    def _get_request_url(
        self, subscription_id, resource_group_name, instance_type, resource_name
    ):
        resource_uri = azure_constants.RESOURCE_URI.format(
            subscription_id, resource_group_name, instance_type, resource_name
        )

        api_version = azure_constants.API_VERSION

        if instance_type == INSTANCE_TYPE_SQL:
            api_version = azure_constants.API_VERSION
        elif instance_type == INSTANCE_TYPE_POSTGRES:
            api_version = azure_constants.PG_API_VERSION

        return (
            self._get_rp_endpoint()
            + resource_uri
            + azure_constants.AZURE_ARM_API_VERSION_STR
            + api_version
        ), resource_uri

    @staticmethod
    def _post(url, body, headers):
        response = requests.post(url, data=body, headers=headers)

        try:
            response.raise_for_status()
        except HTTPError as ex:
            if response.status_code == http_status_codes.request_timeout:
                raise RequestTimeoutError(ex)
            elif response.status_code >= 500:
                raise ServerError(ex)
            else:
                raise

        return response

    def upload_usages_dps(
        self,
        cluster_id,
        correlation_vector,
        name,
        subscription_id,
        resource_group_name,
        location,
        connection_mode,
        infrastructure,
        timestamp,
        usages,
        signature,
    ):
        import base64

        blob = {
            "requestType": "usageUpload",
            "clusterId": cluster_id,
            "name": name,
            "subscriptionId": subscription_id,
            "resourceGroup": resource_group_name,
            "location": location,
            "connectivityMode": connection_mode,
            "infrastructure": infrastructure,
            "uploadRequest": {
                "exportType": "usages",
                "dataTimestamp": timestamp,
                # Sort by keys to retain the same order as originally signed.
                "data": json.dumps(usages, sort_keys=True).replace(" ", ""),
                "signature": signature,
            },
        }

        data_base64 = base64.b64encode(json.dumps(blob).encode("utf-8"))
        headers = self._build_dps_header(correlation_vector)
        url = (
            "https://dataprocessingservice.{}.arcdataservices.com/api/subscriptions"
            "/{}/resourcegroups/{}/providers"
            "/Microsoft.AzureArcData/dataControllers"
            "/{}?api-version=2022-05-25".format(
                location, subscription_id, resource_group_name, name
            )
        )

        body = (
            b'{"$schema": "https://microsoft.azuredata.com/azurearc/pipeline'
            b'/usagerecordsrequest.03-2022.schema.json","blob": "'
            + data_base64
            + b'"}'
        )

        log.info("Usage upload request_url: {}".format(url))

        response = retry(
            lambda: self._post(url, body, headers),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="upload usages dps",
            retry_on_exceptions=(
                NewConnectionError,
                MaxRetryError,
                TimeoutError,
                RequestTimeoutError,
                ServerError,
            ),
        )

        if response.ok:
            success_msg = "Uploaded {} usage records to Azure {}.".format(
                len(usages), url
            )
            print("\t" + success_msg)
            log.info(success_msg)
            if response.headers:
                log.info(
                    "Usage upload response header: {}".format(response.headers)
                )
            return True
        else:
            # Re-try upload with fallback URI
            # TODO: Remove this fallback logic in the future
            # PBI: https://msdata.visualstudio.com/Tina/_workitems/edit/2988226
            url = (
                "https://san-af-{}-prod.azurewebsites.net/api/subscriptions"
                "/{}/resourcegroups/{}/providers"
                "/Microsoft.AzureArcData/dataControllers"
                "/{}?api-version=2022-05-25".format(
                    location, subscription_id, resource_group_name, name
                )
            )

            response = retry(
                lambda: self._post(url, body, headers),
                retry_count=CONNECTION_RETRY_ATTEMPTS,
                retry_delay=RETRY_INTERVAL,
                retry_method="upload usages dps",
                retry_on_exceptions=(
                    NewConnectionError,
                    MaxRetryError,
                    TimeoutError,
                    RequestTimeoutError,
                    ServerError,
                ),
            )

            if response.ok:
                success_msg = "Uploaded {} usage records using fallback DPS URI {}.".format(
                    len(usages), url
                )
                
                print("\t" + success_msg)
                log.info(success_msg)
                if response.headers:
                    log.info(
                        "Fallback URI usage upload response header: {}".format(response.headers)
                    )
                return True

            return False

    def populate_sql_properties(self, params, extended_properties):
        """
        Populate sql instance properties.
        :param params: Add sql specific properties here.
        :param extended_properties: Extract sql specific properties from this.
        """
        tier = _.get(extended_properties, "k8sRaw.spec.tier")
        license_type = _.get(extended_properties, "k8sRaw.spec.licenseType")
        skuName = SQL_MI_SKU_NAME_VCORE

        sku = {"name": skuName, "tier": format_sqlmi_tier_for_azure(tier)}

        params["sku"] = sku
        params["properties"][
            "licenseType"
        ] = format_sqlmi_license_type_for_azure(license_type)

    def get_generic_azure_resource(
        self,
        resource_provider_namespace,
        resource_type,
        resource_group_name,
        resource_name,
        api_version,
    ):
        """
        Get a generic azure resource using ArcDataCliCredential and
        ResourceManagementClient
        """

        subscription = self._subscription

        arm_id = (
            f"/subscriptions/{subscription}"
            f"/resourcegroups/{resource_group_name}"
            f"/providers/{resource_provider_namespace}"
            f"/{resource_type}/{resource_name}"
        )
        resource = self.get_generic_azure_resource_by_id(arm_id, api_version)

        return resource

    def get_generic_azure_resource_by_id(
        self,
        resource_id,
        api_version,
    ):
        """
        Get a generic azure resource using ArcDataCliCredential and
        ResourceManagementClient
        """

        if not is_valid_resource_id(resource_id):
            raise ValidationError(
                f"Unable to get Azure resource. Invalid resource id: "
                f"'{resource_id}'"
            )

        parsed_id = parse_resource_id(resource_id)

        credential = ArcDataCliCredential()

        resource_client = ResourceManagementClient(
            credential, parsed_id["subscription"]
        )

        log.debug(
            f"Getting Azure resource: '{resource_id}', api version: "
            f"'{api_version}'"
        )

        resource = resource_client.resources.get_by_id(
            resource_id, api_version=api_version
        )

        return resource

    @staticmethod
    def get_first_extension_id_from_custom_location(
        custom_location_id,
        extension_type,
    ):
        """
        Get the first extension id match (given an extension type) from the
        custom location.

        :param custom_location_id: The custom location ARM id.
        :param extension_type: The extension type
              (e.g 'microsoft.arcdataservices').
        :returns: The first extension id matching the extension type.
        """

        arm_id = parse_resource_id(custom_location_id)
        resource_group_name = arm_id["resource_group"]
        resource_name = arm_id["resource_name"]
        subscription = arm_id["subscription"]

        credential = ArcDataCliCredential()
        client = CustomLocations(credential, subscription)
        enabled_resource_types = (
            client.custom_locations.list_enabled_resource_types(
                resource_group_name=resource_group_name,
                resource_name=resource_name,
            )
        )

        log.debug(
            f"Getting extension of type '{extension_type}' from custom "
            f"location '{custom_location_id}'"
        )

        for enabled_resource_type in enabled_resource_types:
            et = enabled_resource_type.extension_type
            if et.lower() == extension_type.lower():
                log.debug(
                    f"Found extension id "
                    f"({enabled_resource_type.cluster_extension_id}) for "
                    f"custom location ({custom_location_id})."
                )
                return enabled_resource_type.cluster_extension_id

        log.warning(
            f"Extension of type '{extension_type}'' not found in custom "
            f"location '{custom_location_id}'"
        )

    def get_bootstrapper_extension_id_from_custom_location(
        self, custom_location_id
    ):
        """
        Get the first bootstrapper extension id from the custom location.

        :param custom_location_id: The custom location ARM id.
        :returns: The first extension id matching the extension type.
        """

        if not is_valid_resource_id(custom_location_id):
            raise ValidationError(
                f"Found invalid custom location ARM id: '{custom_location_id}'"
            )

        extension_id = self.get_first_extension_id_from_custom_location(
            custom_location_id=custom_location_id,
            extension_type="microsoft.arcdataservices",
        )

        if not extension_id:
            raise ResourceNotFoundError(
                "Unable to find bootstrapper extension resource for custom "
                "location '{custom_location_id}'"
            )

        return extension_id

    def get_extension_resource(self, extension_resource_id):
        """
        Given an extension resource id, return the generic azure resource.
        """

        log.debug(f"Getting bootstrapper extension Azure resource")

        resource = self.get_generic_azure_resource_by_id(
            resource_id=extension_resource_id,
            api_version=ARC_DATA_SERVICES_EXTENSION_API_VERSION,
        )

        return resource

    def get_extension_identity(self, custom_location_id):
        """
        Given a custom location id, get the principal id of the bootstrapper's
        identity.
        """

        log.debug(f"Data controller's custom location id: {custom_location_id}")

        extension_resource_id = (
            self.get_bootstrapper_extension_id_from_custom_location(
                custom_location_id
            )
        )
        extension = self.get_extension_resource(extension_resource_id)
        extension_identity_principal_id = extension.identity.principal_id

        return extension_identity_principal_id

    def create_or_update_generic_azure_resource(
        self,
        resource_provider_namespace,
        resource_type,
        resource_group_name,
        resource_name,
        api_version,
        parameters,
        wait_for_response=True,
        timeout=None,
    ):
        """
        Create or update a generic azure resource using ArcDataCliCredential and
        ResourceManagementClient
        """
        subscription = self._subscription

        credential = ArcDataCliCredential()
        resource_client = ResourceManagementClient(credential, subscription)
        arm_id = (
            f"/subscriptions/{subscription}"
            f"/resourcegroups/{resource_group_name}"
            f"/providers/{resource_provider_namespace}"
            f"/{resource_type}/{resource_name}"
        )

        log.debug(f"Create or update azure resource: {arm_id}")

        try:
            response = resource_client.resources.begin_create_or_update(
                resource_group_name=resource_group_name,
                resource_provider_namespace=resource_provider_namespace,
                resource_type=resource_type,
                resource_name=resource_name,
                api_version=api_version,
                parameters=parameters,
                parent_resource_path="",
                polling=wait_for_response,
            )

            if not wait_for_response:
                return response

            response.wait(timeout)

            if not response.done():
                raise AzureResponseError(
                    f"Create or update Azure resource request timed out ({arm_id})."
                )

            return response.result()

        except HttpResponseError as ex:
            raise AzureResponseError(
                f"Failed creating or updating Azure resource "
                f"({arm_id}).{os.linesep}{ex.message}"
            ) from ex
        except Exception as ex:
            raise AzureResponseError(
                f"Failed creating or updating Azure resource "
                f"({arm_id}).{os.linesep}{ex}"
            ) from ex

    def _update_auto_upload_metrics(
        self, dc, resource_group_name, auto_upload_metrics
    ):
        """
        Update auto upload metrics property. This includes creating the necessary
        role assignments if needed.
        :param dc: The data controller. The updated property is changed on this
                object.
        :param resource_group_name: The data controller's resource group name.
        :param auto_upload_metrics: "true"/"false" (string, not boolean) indicating
        whether or not to enable auto upload.
        """

        if auto_upload_metrics == "true":
            self.assign_metrics_role_if_missing(
                dc.extended_location.name,
                resource_group_name,
            )

        dc.properties["k8sRaw"]["spec"]["settings"]["azure"][
            "autoUploadMetrics"
        ] = auto_upload_metrics

    def assign_metrics_role_if_missing(
        self,
        custom_location_id,
        resource_group_name,
    ):
        """
        Assign metrics publisher role to the extension identity.
        :param custom_location_id: Assign the role to the bootstrapper extension
            on this custom location.
        :param resource_group_name: The resource group name.

        """
        metrics_role_description = ROLE_DESCRIPTIONS[
            MONITORING_METRICS_PUBLISHER_ROLE_ID
        ]

        extension_identity_principal_id = self.get_extension_identity(
            custom_location_id
        )

        log.debug(
            f"Bootstrapper extension identity (principal id): "
            f"'{extension_identity_principal_id}'"
        )

        if self.has_role_assignment(
            extension_identity_principal_id,
            resource_group_name,
            MONITORING_METRICS_PUBLISHER_ROLE_ID,
            metrics_role_description,
        ):
            log.debug(
                "Bootstrapper extension identity already has metrics publisher "
                "role."
            )
        else:
            log.debug(
                f"Assigning '{metrics_role_description}' role to bootstrapper "
                f"extension identity..."
            )

            self.create_role_assignment(
                extension_identity_principal_id,
                resource_group_name,
                MONITORING_METRICS_PUBLISHER_ROLE_ID,
                metrics_role_description,
            )

    @staticmethod
    def has_role_assignment(
        identity_principal_id,
        resource_group_name,
        role_id,
        role_description,
    ):

        """
        Check if a role (role_id) is assigned to identity_principal_id with
        resource group scope.
        """
        (
            login_credentials,
            subscription_id,
            tenant_id,
        ) = get_cli_profile().get_login_credentials()

        authorization_client = AuthorizationManagementClient(
            login_credentials, subscription_id
        )

        log.debug(
            f"Checking if role id '{role_id}' ({role_description}) is "
            f"assigned to principal id {identity_principal_id} at resource "
            f"group ({resource_group_name}) scope"
        )

        role_assignments = (
            authorization_client.role_assignments.list_for_resource_group(
                resource_group_name,
                filter=f"assignedTo('{identity_principal_id}')",
            )
        )

        for role_assignment in role_assignments:
            role_definition_id = role_assignment.role_definition_id

            if role_definition_id.lower().endswith(role_id):
                log.debug(
                    f"Role assignment found. Role id '{role_id}' "
                    f"({role_description}) is assigned to principal id "
                    f"{identity_principal_id} at resource group "
                    f"({resource_group_name}) scope"
                )
                return True

        log.debug(
            f"Role assignment NOT found. Role id '{role_id}' "
            f"({role_description}) is NOT assigned to principal id "
            f"{identity_principal_id} at resource group "
            f"({resource_group_name}) scope"
        )

        return False

    @staticmethod
    def create_role_assignment(
        identity_principal_id,
        resource_group_name,
        role_id,
        role_description,
    ):
        """
        Create a role assignment.
        :param identity_principal_id: The identity principal we are assigning
        the role to.
        :param resource_group_name: The resource group to scope the assignment
         to.
        :param role_id: The role id to assign.
        :param role_description: The role description.
        :raises: AzureResponseError: If there is an error creating the role
        assignment.
        """

        (
            login_credentials,
            subscription,
            tenant_id,
        ) = get_cli_profile().get_login_credentials()

        authorization_client = AuthorizationManagementClient(
            login_credentials, subscription
        )

        scope = (
            f"/subscriptions/{subscription}"
            f"/resourceGroups/{resource_group_name}"
        )
        role_assignment_name = uuid.uuid4()

        params = {
            "properties": {
                "roleDefinitionId": f"/subscriptions"
                f"/{subscription}"
                f"/providers/Microsoft.Authorization"
                f"/roleDefinitions/{role_id}",
                "principalId": identity_principal_id,
            }
        }

        log.debug(
            f"Creating role assignment. Role assignment name: "
            f"'{role_assignment_name}'', scope: '{scope}', role id: "
            f"'{role_id}' ({role_description})"
        )

        try:
            authorization_client.role_assignments.create(
                scope, role_assignment_name, params
            )
        except HttpResponseError as ex:
            error_msg = (
                f"Failed to create role assignment. Role id: "
                f"'{role_id}' ({role_description}), scope: '{scope}', "
                f"identity principal: {identity_principal_id}. "
                f"Error: {ex}"
            )
            raise AzureResponseError(error_msg) from ex

    @staticmethod
    def _update_auto_upload_logs(dc, auto_upload_logs):
        """
        Update auto upload logs properties. This includes asking for the
        log analytics workspace id/key if needed.
        :param dc: The data controller. The updated properties are changed on
                   this object.
        :param auto_upload_logs: "true"/"false" (string, not boolean) indicating
        whether or not to enable auto upload.
        """

        dc.properties["k8sRaw"]["spec"]["settings"]["azure"][
            "autoUploadLogs"
        ] = auto_upload_logs

        if auto_upload_logs == "false":
            dc.properties["logAnalyticsWorkspaceConfig"] = None
            return

        if (
            "logAnalyticsWorkspaceConfig" not in dc.properties
            or dc.properties["logAnalyticsWorkspaceConfig"] is None
        ):
            dc.properties["logAnalyticsWorkspaceConfig"] = dict()

        (
            workspace_id,
            workspace_shared_key,
        ) = get_log_workspace_credentials_from_env()

        dc.properties["logAnalyticsWorkspaceConfig"][
            "workspaceId"
        ] = workspace_id
        dc.properties["logAnalyticsWorkspaceConfig"][
            "primaryKey"
        ] = workspace_shared_key

    @staticmethod
    def _is_dc_directly_connected(dc):
        """
        Return True if dc is directly connected mode. False otherwise.
        (this is determined by checking at the extended_location,
        "ConnectionMode" property is ignored, this is the same logic performed
        in the RP)
        """

        if dc.extended_location is None:
            return False

        if dc.extended_location.type.lower() != "customlocation":
            return False

        return True

    def upload_dc_resource(self, path):
        """
        Upload data file exported from a data controller to Azure.
        """

        import uuid
        from datetime import datetime
        from jsonschema import validate
        from azext_arcdata.core.serialization import Sanitizer
        from azext_arcdata.dc.constants import LAST_USAGE_UPLOAD_FLAG
        from azext_arcdata.arm_sdk.azure.export_util import (
            ExportType,
            logs_upload,
            metrics_upload,
            EXPORT_DATA_JSON_SCHEMA,
            EXPORT_FILE_DICT_KEY,
            EXPORT_SANITIZERS,
            get_export_timestamp_from_file,
            set_azure_upload_status,
            update_upload_status_file,
            update_azure_upload_status,
        )

        log.debug("Uploading file: '%s'", path)
        with open(path, encoding="utf-8") as input_file:
            data = json.load(input_file)
            data = Sanitizer.sanitize_object(data, EXPORT_SANITIZERS)
            validate(data, EXPORT_DATA_JSON_SCHEMA)

        # Check expected properties
        #
        for expected_key in EXPORT_FILE_DICT_KEY:
            if expected_key not in data:
                raise ValueError(
                    '"{}" is not found in the input file "{}".'.format(
                        expected_key, path
                    )
                )

        export_type = data["exportType"]

        if not ExportType.has_value(export_type):
            raise ValueError(
                '"{}" is not a supported type. Please check your input file '
                '"{}".'.format(export_type, path)
            )

        # Create/Update shadow resource for data controller
        #
        data_controller = data["dataController"]

        try:
            data_controller_azure = self._get_dc_azure_resource(data_controller)
        except Exception as e:
            raise Exception(
                "Upload failed. Unable to read data controller resource from "
                "Azure"
            )

        set_azure_upload_status(data_controller, data_controller_azure)
        self._create_dc_azure_resource(data_controller)

        # Delete shadow resources for resource instances deleted from the
        # cluster in k8s
        #
        deleted = dict()

        for instance in data["deletedInstances"]:
            instance_key = "{}/{}.{}".format(
                instance["kind"],
                instance["instanceName"],
                instance["instanceNamespace"],
            )

            if instance_key not in deleted.keys():
                try:
                    self._delete_azure_resource(instance, data_controller)
                    deleted[instance_key] = True
                except Exception as e:
                    self.stdout(
                        'Failed to delete Azure resource for "{}" in "{}".'.format(
                            instance["instanceName"],
                            instance["instanceNamespace"],
                        )
                    )
                    self.stderr(e)
                    continue

        # Create/Update shadow resources for resource instances still active in
        # the cluster in k8s
        #
        for instance in data["instances"]:
            self._create_azure_resource(instance, data_controller)

        data_timestamp = datetime.strptime(
            data["dataTimestamp"], "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        # Upload metrics, logs or usage
        #
        try:
            if export_type == ExportType.metrics.value:
                metrics_upload(data["data"])
            elif export_type == ExportType.logs.value:
                (
                    customer_id,
                    shared_key,
                ) = get_log_workspace_credentials_from_env()
                self.stdout('Log Analytics workspace: "{}"'.format(customer_id))
                for file in data["data"]:
                    with open(file, encoding="utf-8") as input_file:
                        data = json.load(input_file)
                    logs_upload(data["data"], customer_id, shared_key)
            elif export_type == "usage":
                if data_controller:
                    self.stdout("\n")
                    self.stdout("Start uploading usage...")
                    correlation_vector = str(uuid.uuid4())
                    for usage in data["data"]:
                        self._upload_usages_dps(
                            data_controller,
                            usage,
                            data["dataTimestamp"],
                            correlation_vector,
                        )

                    if (
                        LAST_USAGE_UPLOAD_FLAG in data
                        and data[LAST_USAGE_UPLOAD_FLAG]
                    ):
                        # Delete DC shadow resource to close out billing
                        #
                        self._delete_azure_resource(
                            resource=data_controller,
                            data_controller=data_controller,
                        )

                    self.stdout("Usage upload is done.")
                else:
                    self.stdout(
                        "No usage has been reported. Please wait for 24 hours "
                        "if you just deployed the Azure Arc enabled data "
                        "services."
                    )
            else:
                raise ValueError(
                    '"{}" is not a supported type. Please check your input'
                    ' file "{}".'.format(export_type, path)
                )
        except Exception as ex:
            update_azure_upload_status(
                data_controller, export_type, datetime.utcnow(), ex
            )
            self._create_dc_azure_resource(data_controller)
            raise

        update_azure_upload_status(
            data_controller, export_type, datetime.utcnow(), None
        )
        self._create_dc_azure_resource(data_controller)

        # Update watermark after upload succeed for all three types of data
        timestamp_from_status_file = get_export_timestamp_from_file(export_type)
        timestamp_from_export_file = data_timestamp

        if timestamp_from_status_file < timestamp_from_export_file:
            update_upload_status_file(
                export_type,
                data_timestamp=timestamp_from_export_file.isoformat(
                    sep=" ", timespec="milliseconds"
                ),
            )

    def _get_dc_azure_resource(self, data_controller):
        """
        Get a shadow resource for the data controller.
        """
        response = retry(
            lambda: self.get_azure_resource(
                resource_name=data_controller["instanceName"],
                instance_type="dataControllers",
                subscription_id=data_controller["subscriptionId"],
                resource_group_name=data_controller["resourceGroupName"],
            ),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="get Azure data controller",
            retry_on_exceptions=(
                ConnectionError,
                NewConnectionError,
                MaxRetryError,
            ),
        )

        # no data controller was returned
        if response is True:
            return None

        return response

    def _create_dc_azure_resource(self, data_controller):
        """
        Create a shadow resource for the data controller.
        """
        retry(
            lambda: self.create_azure_data_controller(
                uid=data_controller["k8sRaw"]["metadata"]["uid"],
                resource_name=data_controller["instanceName"],
                subscription_id=data_controller["subscriptionId"],
                resource_group_name=data_controller["resourceGroupName"],
                location=data_controller["location"],
                public_key=data_controller["publicKey"],
                extended_properties={
                    "k8sRaw": _.get(data_controller, "k8sRaw"),
                    "infrastructure": _.get(data_controller, "infrastructure"),
                },
            ),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="create Azure data controller",
            retry_on_exceptions=(
                ConnectionError,
                NewConnectionError,
                MaxRetryError,
            ),
        )

    def _create_azure_resource(self, resource, data_controller):
        """
        Create a shadow resource for custom resource.
        """
        retry(
            lambda: self.create_azure_resource(
                instance_type=azure_constants.RESOURCE_TYPE_FOR_KIND[
                    resource["kind"]
                ],
                data_controller_name=data_controller["instanceName"],
                resource_name=resource["instanceName"],
                subscription_id=data_controller["subscriptionId"],
                resource_group_name=data_controller["resourceGroupName"],
                location=data_controller["location"],
                extended_properties={"k8sRaw": _.get(resource, "k8sRaw")},
            ),
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="create Azure resource",
            retry_on_exceptions=(
                ConnectionError,
                NewConnectionError,
                MaxRetryError,
            ),
        )

    def _delete_azure_resource(self, resource, data_controller):
        """
        Delete the shadow resource for custom resource.
        """
        resource_name = resource["instanceName"]
        instance_type = azure_constants.RESOURCE_TYPE_FOR_KIND[resource["kind"]]
        subscription_id = data_controller["subscriptionId"]
        resource_group_name = data_controller["resourceGroupName"]

        retry(
            self.delete_azure_resource,
            resource_name,
            instance_type,
            subscription_id,
            resource_group_name,
            retry_count=CONNECTION_RETRY_ATTEMPTS,
            retry_delay=RETRY_INTERVAL,
            retry_method="delete Azure resource",
            retry_on_exceptions=(
                ConnectionError,
                NewConnectionError,
                MaxRetryError,
            ),
        )

    def _upload_usages_dps(
        self, data_controller, usage, timestamp, correlation_vector
    ):
        import zlib
        import base64
        import json

        uncompressed_usage = json.loads(
            str(
                zlib.decompress(
                    base64.b64decode(usage["usages"]), -zlib.MAX_WBITS
                ),
                "utf-8",
            )
        )

        return self.upload_usages_dps(
            cluster_id=data_controller["k8sRaw"]["metadata"]["uid"],
            correlation_vector=correlation_vector,
            name=data_controller["instanceName"],
            subscription_id=data_controller["subscriptionId"],
            resource_group_name=data_controller["resourceGroupName"],
            location=data_controller["location"],
            connection_mode=data_controller["connectionMode"],
            infrastructure=data_controller["infrastructure"],
            timestamp=timestamp,
            usages=uncompressed_usage,
            signature=usage["signature"],
        )
