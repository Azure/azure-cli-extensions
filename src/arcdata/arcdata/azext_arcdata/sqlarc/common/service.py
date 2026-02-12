# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------
import json
import re
import requests
from knack.log import get_logger
from azext_arcdata.vendored_sdks.arm_sdk.swagger.swagger_latest import (
    AzureArcDataManagementClient,
)
from azext_arcdata.vendored_sdks.arm_sdk.swagger.swagger_latest.models import (
    AvailabilityGroupCreateUpdateConfiguration,
    SqlServerAvailabilityGroupResource,
)
from azure.core.exceptions import HttpResponseError

__all__ = ["AzureArcSqlWebService"]
logger = get_logger(__name__)


class AzureArcSqlWebService:  # pylint: disable=too-many-instance-attributes
    logger = get_logger(__name__)

    # initialize the service for making Http Requests to ARM
    def __init__(self, azure_credential, subscription):
        self._azure_credential = azure_credential
        self._bearer = azure_credential.get_token().token
        self._subscription_id = subscription
        self._headers = {
            "Authorization": "Bearer {}".format(self._bearer),
            "Content-Type": "application/json",
        }
        self._client = AzureArcDataManagementClient(
            self._azure_credential, self._subscription_id, headers=self._headers
        )

        self._api_version_instance = "2023-12-01-preview"
        self._api_version_server = "2023-03-15-preview"
        self._server_config_url = (
            "https://management.azure.com/{0}/extensions/{1}{2}"
        )
        self._instance_config_url = "https://management.azure.com/{0}/{1}"
        self._server_resource_id = (
            "/subscriptions/{0}/resourceGroups/{1}/providers/"
            "Microsoft.HybridCompute/machines/{2}"
        )
        self._instance_resource_id = (
            "/subscriptions/{0}/resourceGroups/{1}/providers/"
            "Microsoft.AzureArcData/sqlServerInstances/{2}"
        )

    def get_sqlarc_server_config_url(self, url_path):
        return self._server_config_url.format(
            url_path,
            "WindowsAgent.SqlServer",
            "?api-version={0}".format(self._api_version_server),
        )

    def get_sqlarc_server_config(self, url_path):
        url = self.get_sqlarc_server_config_url(url_path)
        response = requests.get(url=url, headers=self._headers)
        self.response_error_checking_with_status_code(
            response,
            404,
            "Error: Could not find SQL Server at '{0}'".format(url_path),
        )
        self.response_pass_checking(
            response,
            "Error: An Error has occurred while looking for the "
            "SQL Server - Azure Arc. Check logs for more information.",
        )
        return response.json()

    def get_sqlarc_instance_resource_url(self, url_path):
        return self._instance_config_url.format(
            url_path,
            "?api-version={0}".format(self._api_version_instance),
        )

    def get_sqlarc_instance_response_json(self, url_path):
        url = self.get_sqlarc_instance_resource_url(url_path)
        response = requests.get(url=url, headers=self._headers)
        self.response_error_checking_with_status_code(
            response,
            404,
            "Error: Could not find SQL Server - Azure Arc at '{0}'".format(
                url_path
            ),
        )
        self.response_pass_checking(
            response,
            "Error: An Error has occurred while looking for the "
            "SQL Server - Azure Arc. Check logs for more information.",
        )
        return response.json()

    def get_sqlarc_extension_details(self, resource_group, server_name):
        """
        This function gets current extension details for a given arc server.
        """
        resource_id = self._server_resource_id.format(
            self._subscription_id, resource_group, server_name
        )
        return self.get_sqlarc_server_config(resource_id)

    def put_sqlarc_extension_details(self, resource_group, server_name, config):
        """
        This function updates the extension details for a given arc server.
        """
        resource_id = self._server_resource_id.format(
            self._subscription_id, resource_group, server_name
        )
        url = self.get_sqlarc_server_config_url(resource_id)
        payload = json.dumps(config)
        response = requests.put(url=url, headers=self._headers, data=payload)

        # Raise exception if http request was not successful.
        if response.status_code < 200 or response.status_code > 299:
            if response.status_code == 409:
                raise RuntimeError(
                    '{"code":"HCRP409","message":"An extension of type '
                    'WindowsAgent.SqlServer is still processing. Only one '
                    'instance of an extension may be in progress at a time for '
                    'the same resource. Please retry after sometime."}'
                )

            raise RuntimeError(response.text)

    def get_license_type(self, url):
        config = self.get_sqlarc_server_config(url)
        try:
            return config["properties"]["settings"]["LicenseType"]
        except Exception as e:
            logger.info(e)
            raise RuntimeError(
                "LicenseType could not be found at the expected location. "
                "Please visit: https://learn.microsoft.com/en-us/sql/sql-server/"
                "azure-arc/manage-license-type?view=sql-server-ver16&tabs=azure"
                "#modify-license-type to fix this issue!"
            )

    # Gets the Config of an instance
    def get_sqlarc_instance_config(self, resource_group, instance_name):
        try:
            response = self._client.sql_server_instances.get(
                resource_group, instance_name
            )
            return response
        except HttpResponseError as e:
            logger.info(e)
            self.generic_raise_exception(e, resource_group, instance_name)

    # Executes a Puts on the Instance Config
    def put_sqlarc_instance_config(self, resource_group, instance, config):
        try:
            response = self._client.sql_server_instances.begin_create(
                resource_group, instance, config
            )
            return response
        except HttpResponseError as e:
            logger.info(e)
            self.generic_raise_exception(e, resource_group, instance)

    # Returns arc server host name for a sql instance.
    def get_arc_server_name(self, resource_group, instance_name):
        try:
            resource_id = self._instance_resource_id.format(
                self._subscription_id, resource_group, instance_name
            )

            response = self.get_sqlarc_instance_response_json(resource_id)
            container_resource_id = response["properties"][
                "containerResourceId"
            ]

            match = re.search(r"/machines/(.+)$", container_resource_id)
            host_name = match.group(1)
            return host_name

        except Exception as e:
            logger.info(e)
            raise RuntimeError(
                "Unable to find a arc server resource for the arc sql instance name provided."
            )

    def get_sqlarc_database_config(self, resource_group, instance, database):
        try:
            response = self._client.sql_server_databases.get(
                resource_group, instance, database
            )
            return response
        except HttpResponseError as e:
            logger.info(e)
            self.generic_raise_exception(e, resource_group, instance, database)

    # Executes a Puts on an Azure Database Arm Manifest
    def put_sqlarc_database_config(
        self, resource_group, instance, database, config
    ):
        try:
            response = self._client.sql_server_databases.create(
                resource_group, instance, database, config
            )
            return response
        except HttpResponseError as e:
            logger.info(e)
            self.generic_raise_exception(e, resource_group, instance)

    def create_sqlarc_database(
        self, resource_group, instance, database, config
    ):
        try:
            response = self._client.sql_server_databases.create(
                resource_group, instance, database, config
            )
            return response
        except HttpResponseError as e:
            logger.info(e)
            self.generic_raise_exception(e, resource_group, instance, database)

    def response_error_checking_with_status_code(
        self, response, status_code, error_message
    ):
        if response.status_code == status_code:
            logger.info(response.text)
            raise HttpResponseError(error_message)

    def response_pass_checking(self, response, error_message):
        if not (response.status_code >= 200 and response.status_code < 300):
            logger.info(response.text)
            raise HttpResponseError(error_message)

    def get_ag_details(
        self,
        resource_group: str,
        sql_server_instance_name: str,
        availability_group_name: str,
    ) -> SqlServerAvailabilityGroupResource:
        """
        Get a SQL Availability Group.
        :param resource_group: The name of the Azure resource group.
        :type resource_group: str
        :param sql_server_instance_name: The name of the SQL Server instance.
        :type sql_server_instance_name: str
        :param availability_group_name: The name of the SQL Availability Group.
        :type availability_group_name: str"""
        return self._client.sql_server_availability_groups.detail_view(
            resource_group_name=resource_group,
            sql_server_instance_name=sql_server_instance_name,
            availability_group_name=availability_group_name,
        )

    def create_ag(
        self,
        resource_group: str,
        sql_server_instance_name: str,
        availability_group_config: AvailabilityGroupCreateUpdateConfiguration,
        no_wait: bool,
    ):
        """
        Create a new SQL Availability Group.
        :param resource_group: The name of the Azure resource group.
        :type resource_group: str
        :param sql_server_instance_name: The name of the SQL Server instance.
        :type sql_server_instance_name: str
        :param availability_group_config: The availability group configuration.
        :type availability_group_config: AvailabilityGroupCreateUpdateConfiguration
        """
        polling = not no_wait
        return self._client.sql_server_availability_groups.begin_create_availability_group(
            resource_group_name=resource_group,
            sql_server_instance_name=sql_server_instance_name,
            create_ag_configuration=availability_group_config,
            polling=polling,
        )

    def failover_ag(
        self,
        resource_group_name: str,
        sql_server_instance_name: str,
        availability_group_name: str,
    ) -> SqlServerAvailabilityGroupResource:
        """
        Request manual failover of the availability group to the given server.
        :param resource_group_name: The name of the Azure resource group.
        :type resource_group_name: str
        :param sql_server_instance_name: Name of SQL Server Instance.
        :type sql_server_instance_name: str
        :param availability_group_name: Name of SQL Availability Group.
        :type availability_group_name: str
        """
        return self._client.sql_server_availability_groups.failover(
            resource_group_name=resource_group_name,
            sql_server_instance_name=sql_server_instance_name,
            availability_group_name=availability_group_name,
        )

    def generic_raise_exception(
        self, e, resource_group, instance_name, database_name=None
    ):
        if "(ResourceGroupNotFound)" in str(e):
            raise RuntimeError(
                'Could not find resource group "{0}".'.format(resource_group)
            )
        if "(ResourceNotFound)" in str(e) and "/Databases/" not in str(e):
            raise RuntimeError(
                'Could not find Sql Server instance "{0}" in the resource '
                'group "{1}". For more details please go to '
                'https://aka.ms/ARMResourceNotFoundFix'.format(
                    instance_name, resource_group
                )
            )
        if "(ResourceNotFound)" in str(e) and "/Databases/" in str(e):
            raise RuntimeError(
                'Could not find a database called "{0}" in the Sql Server '
                'Instance "{1}" in the resource group "{2}". For more details '
                'please go to https://aka.ms/ARMResourceNotFoundFix'.format(
                    database_name, instance_name, resource_group
                )
            )
        raise RuntimeError(
            f"An error has occured: {e} \nPlease look at the logs for more information."
        )
