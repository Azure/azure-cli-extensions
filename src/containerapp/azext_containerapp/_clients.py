# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, no-else-return, useless-return, broad-except, no-else-raise

import json
import os
import requests

from azure.cli.core.azclierror import ResourceNotFoundError, CLIError
from azure.cli.core.util import send_raw_request
from azure.cli.core.commands.client_factory import get_subscription_id
from azure.cli.command_modules.containerapp._clients import (
    poll_status,
    poll_results,
    AuthClient,
    GitHubActionClient,
    ContainerAppClient,
    ContainerAppsJobClient,
    DaprComponentClient,
    ManagedEnvironmentClient,
    StorageClient)

from knack.log import get_logger

logger = get_logger(__name__)

PREVIEW_API_VERSION = "2025-02-02-preview"
POLLING_TIMEOUT = 1500  # how many seconds before exiting
POLLING_SECONDS = 2  # how many seconds between requests
POLLING_TIMEOUT_FOR_MANAGED_CERTIFICATE = 1500  # how many seconds before exiting
POLLING_INTERVAL_FOR_MANAGED_CERTIFICATE = 4  # how many seconds between requests
HEADER_AZURE_ASYNC_OPERATION = "azure-asyncoperation"
HEADER_LOCATION = "location"
SESSION_RESOURCE = "https://dynamicsessions.io"
MAINTENANCE_CONFIG_DEFAULT_NAME = "default"


class GitHubActionPreviewClient(GitHubActionClient):
    api_version = PREVIEW_API_VERSION


# Clients for preview
class ContainerAppPreviewClient(ContainerAppClient):
    api_version = PREVIEW_API_VERSION


class LabelHistoryPreviewClient:
    api_version = PREVIEW_API_VERSION

    @classmethod
    def list(cls, cmd, resource_group_name, name):
        history_list = []
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerapps/{}/labelhistory?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url, body=None)
        j = r.json()
        for route in j["value"]:
            history_list.append(route)
        return history_list

    @classmethod
    def show(cls, cmd, resource_group_name, name, label):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerapps/{}/labelhistory/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            label,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url, body=None)
        return r.json()


class ContainerAppsJobPreviewClient(ContainerAppsJobClient):
    api_version = PREVIEW_API_VERSION
    LOG_STREAM_API_VERSION = "2023-11-02-preview"

    @classmethod
    def get_replicas(cls, cmd, resource_group_name, name, execution_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/jobs/{}/executions/{}/replicas?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            execution_name,
            cls.LOG_STREAM_API_VERSION)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def get_auth_token(cls, cmd, resource_group_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/jobs/{}/getAuthToken?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.LOG_STREAM_API_VERSION)

        r = send_raw_request(cmd.cli_ctx, "POST", request_url)
        return r.json()

    @classmethod
    def list_by_subscription(cls, cmd, formatter=lambda x: x):
        app_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        request_url = "{}/subscriptions/{}/providers/Microsoft.App/jobs?api-version={}".format(
            management_hostname.strip('/'),
            sub_id,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for app in j["value"]:
            formatted = formatter(app)
            app_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for app in j["value"]:
                formatted = formatter(app)
                app_list.append(formatted)

        return app_list

    @classmethod
    def list_by_resource_group(cls, cmd, resource_group_name, formatter=lambda x: x):
        app_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/jobs?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for app in j["value"]:
            formatted = formatter(app)
            app_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for app in j["value"]:
                formatted = formatter(app)
                app_list.append(formatted)

        return app_list


class ContainerAppsResiliencyPreviewClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create_or_update(cls, cmd, resource_group_name, name, container_app_name, container_app_resiliency_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(container_app_resiliency_envelope))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/resiliencyPolicies/{}?api-version={}"
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                container_app_name,
                name,
                cls.api_version)

            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def update(cls, cmd, resource_group_name, name, container_app_name, container_app_resiliency_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager

        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(container_app_resiliency_envelope))

        if no_wait:
            return
        elif r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            response = poll_results(cmd, operation_url)
            if response is None:
                raise ResourceNotFoundError("Could not find the app resiliency policy")
            else:
                return response

        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, name, container_app_name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code in [200, 201, 202, 204]:
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_LOCATION)
                poll_results(cmd, operation_url)
                logger.warning('App Resiliency Policy successfully deleted')

    @classmethod
    def show(cls, cmd, resource_group_name, name, container_app_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def list(cls, cmd, resource_group_name, container_app_name):
        policy_list = []
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/resiliencyPolicies?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        r = r.json()

        for policy in r["value"]:
            policy_list.append(policy)

        return policy_list


class ContainerAppFunctionsPreviewClient():
    api_version = "2025-10-02-preview"
    APP_INSIGHTS_API_VERSION = "2018-04-20"

    @classmethod
    def list_functions_by_revision(cls, cmd, resource_group_name, container_app_name, revision_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/revisions/{}/functions?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            revision_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        if not r:
            raise CLIError(f"Error retrieving functions for revision '{revision_name}' of container app '{container_app_name}'.")
        return r.json()

    @classmethod
    def get_function_by_revision(cls, cmd, resource_group_name, container_app_name, revision_name, function_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/revisions/{}/functions/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            revision_name,
            function_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        if not r:
            raise CLIError(f"Error retrieving function '{function_name}' for revision '{revision_name}' of container app '{container_app_name}'.")
        return r.json()

    @classmethod
    def list_functions(cls, cmd, resource_group_name, container_app_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/functions?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        if not r:
            raise CLIError(f"Error retrieving functions for container app '{container_app_name}'.")
        return r.json()

    @classmethod
    def get_function(cls, cmd, resource_group_name, container_app_name, function_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/containerApps/{}/functions/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            container_app_name,
            function_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        if not r:
            raise CLIError(f"Error retrieving function '{function_name}' for container app '{container_app_name}'.")
        return r.json()

    @classmethod
    def get_function_invocation_summary(cls, cmd, resource_group_name, container_app_name, revision_name, function_name, timespan="30d"):
        # Fetch the app insights resource app id
        app_id = cls._get_app_insights_id(cmd, resource_group_name, container_app_name, revision_name)

        # Use application insights query to get function invocations summary
        invocation_summary_query = (
            f"requests | extend functionNameFromCustomDimension = tostring(customDimensions['faas.name']) "
            f"| where timestamp >= ago({timespan}) "
            f"| where cloud_RoleName =~ '{container_app_name}' "
            f"| where cloud_RoleInstance contains '{revision_name}' "
            f"| where operation_Name =~ '{function_name}' or functionNameFromCustomDimension =~ '{function_name}' "
            f"| summarize SuccessCount = coalesce(countif(success == true), 0), ErrorCount = coalesce(countif(success == false), 0)"
        )

        try:
            result = cls._execute_app_insights_query(cmd, app_id, invocation_summary_query, "getLast30DaySummary")
            return result
        except Exception as ex:
            raise CLIError(f"Error retrieving function invocation summary: {str(ex)}")

    @classmethod
    def get_function_invocation_traces(cls, cmd, resource_group_name, container_app_name, revision_name, function_name, timespan="30d", limit=20):
        # Fetch the app insights resource app id
        app_id = cls._get_app_insights_id(cmd, resource_group_name, container_app_name, revision_name)

        # Use application insights query to get function invocations traces
        invocation_traces_query = (
            f"requests | extend functionNameFromCustomDimension = tostring(customDimensions['faas.name']) "
            f"| project timestamp, id, operation_Name, success, resultCode, duration, operation_Id, functionNameFromCustomDimension, "
            f"cloud_RoleName, cloud_RoleInstance, invocationId=coalesce(tostring(customDimensions['InvocationId']), tostring(customDimensions['faas.invocation_id'])) "
            f"| where timestamp > ago({timespan}) "
            f"| where cloud_RoleName =~ '{container_app_name}' "
            f"| where cloud_RoleInstance contains '{revision_name}' "
            f"| where operation_Name =~ '{function_name}' or functionNameFromCustomDimension =~ '{function_name}' "
            f"| order by timestamp desc | take {limit} "
            f"| project timestamp, success, resultCode, durationInMilliSeconds=duration, invocationId, operationId=operation_Id, operationName=operation_Name, functionNameFromCustomDimension "
        )

        try:
            result = cls._execute_app_insights_query(cmd, app_id, invocation_traces_query, "getInvocationTraces")
            return result
        except Exception as ex:
            raise CLIError(f"Error retrieving function invocation traces: {str(ex)}")

    @classmethod
    def _get_app_insights_id(cls, cmd, resource_group_name, container_app_name, revision_name):
        # Fetch the revision details using the container app client
        revision = ContainerAppPreviewClient.show_revision(cmd, resource_group_name, container_app_name, revision_name)
        # Extract the list of environment variables from the revision's properties
        env_vars = []
        if revision and "properties" in revision and "template" in revision["properties"]:
            containers = revision["properties"]["template"].get("containers", [])
            for container in containers:
                env_vars.extend(container.get("env", []))

        # Check for APPLICATIONINSIGHTS_CONNECTION_STRING
        ai_conn_str = None
        for env in env_vars:
            if env.get("name") == "APPLICATIONINSIGHTS_CONNECTION_STRING":
                ai_conn_str = env.get("value")
                break

        if not ai_conn_str:
            raise CLIError(f"Required application setting APPLICATIONINSIGHTS_CONNECTION_STRING not present in the containerapp '{container_app_name}'.")

        # Extract ApplicationId from the connection string
        app_id = None
        parts = ai_conn_str.split(";")
        for part in parts:
            if part.startswith("ApplicationId="):
                app_id = part.split("=", 1)[1]
                break

        if not app_id:
            raise CLIError(f"ApplicationId not found in APPLICATIONINSIGHTS_CONNECTION_STRING for containerapp '{container_app_name}'.")
        return app_id

    @classmethod
    def _execute_app_insights_query(cls, cmd, app_id, query, queryType, timespan="30D"):

        # Application Insights REST API endpoint
        api_endpoint = "https://api.applicationinsights.io"
        url = f"{api_endpoint}/v1/apps/{app_id}/query?api-version={cls.APP_INSIGHTS_API_VERSION}&queryType={queryType}"

        # Prepare the request body
        body = {
            "query": query,
            "timespan": f"P{timespan}"
        }

        # Execute the query using Azure CLI's send_raw_request
        response = send_raw_request(
            cmd.cli_ctx,
            "POST",
            url,
            body=json.dumps(body),
            headers=["Content-Type=application/json"]
        )

        result = response.json()
        if isinstance(result, dict) and 'error' in result:
            raise CLIError(f"Error retrieving invocations details: {result['error']}")
        return result

    @classmethod
    def show_function_keys(cls, cmd, resource_group_name, name, key_type, key_name, function_name=None, revision_name=None, replica_name=None, container_name=None):
        from .custom import containerapp_debug

        command_fmt = ""
        if key_type != "functionKey":
            command_fmt = "/bin/azure-functions-admin keys show --key-type {} --key-name {}"
            command = command_fmt.format(key_type, key_name)
        else:
            command_fmt = "/bin/azure-functions-admin keys show --key-type {} --key-name {} --function-name {}"
            command = command_fmt.format(key_type, key_name, function_name)

        r = containerapp_debug(
            cmd=cmd,
            resource_group_name=resource_group_name,
            name=name,
            container=container_name,
            revision=revision_name,
            replica=replica_name,
            debug_command=command
        )
        if not r:
            raise CLIError(f"Error retrieving function key '{key_name}' of type '{key_type}'.")
        return r

    @classmethod
    def list_function_keys(cls, cmd, resource_group_name, name, key_type, function_name=None, revision_name=None, replica_name=None, container_name=None):
        from .custom import containerapp_debug

        command_fmt = ""
        if key_type != "functionKey":
            command_fmt = "/bin/azure-functions-admin keys list --key-type {}"
            command = command_fmt.format(key_type)
        else:
            command_fmt = "/bin/azure-functions-admin keys list --key-type {} --function-name {}"
            command = command_fmt.format(key_type, function_name)

        r = containerapp_debug(
            cmd=cmd,
            resource_group_name=resource_group_name,
            name=name,
            container=container_name,
            revision=revision_name,
            replica=replica_name,
            debug_command=command
        )
        if not r:
            raise CLIError(f"Error retrieving function keys of type '{key_type}'.")
        return r

    @classmethod
    def set_function_keys(cls, cmd, resource_group_name, name, key_type, key_name, key_value, function_name=None, revision_name=None, replica_name=None, container_name=None):
        """Set/Update function keys based on key type"""
        from .custom import containerapp_debug

        command_fmt = ""
        if key_type != "functionKey":
            command_fmt = "/bin/azure-functions-admin keys set --key-type {} --key-name {}"
            command = command_fmt.format(key_type, key_name)
        else:
            command_fmt = "/bin/azure-functions-admin keys set --key-type {} --key-name {} --function-name {}"
            command = command_fmt.format(key_type, key_name, function_name)

        if key_value is not None:
            command += " --key-value {}".format(key_value)

        r = containerapp_debug(
            cmd=cmd,
            resource_group_name=resource_group_name,
            name=name,
            container=container_name,
            revision=revision_name,
            replica=replica_name,
            debug_command=command
        )
        if not r:
            raise CLIError(f"Error setting function key '{key_name}' of type '{key_type}'.")
        return r


class DaprComponentResiliencyPreviewClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create_or_update(cls, cmd, name, resource_group_name, dapr_component_name, environment_name, component_resiliency_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/daprComponents/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            dapr_component_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(component_resiliency_envelope))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/daprComponents/{}/resiliencyPolicies/{}?api-version={}"
            request_url = url_fmt.format(
                management_hostname.strip('/'),
                sub_id,
                resource_group_name,
                environment_name,
                dapr_component_name,
                name,
                cls.api_version)

            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def delete(cls, cmd, name, resource_group_name, dapr_component_name, environment_name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/daprComponents/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            dapr_component_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code in [200, 201, 202, 204]:
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_LOCATION)
                poll_results(cmd, operation_url)
                logger.warning('Dapr Component Resiliency Policy successfully deleted')

    @classmethod
    def show(cls, cmd, name, resource_group_name, dapr_component_name, environment_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/daprComponents/{}/resiliencyPolicies/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            dapr_component_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def list(cls, cmd, resource_group_name, dapr_component_name, environment_name):
        policy_list = []
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/daprComponents/{}/resiliencyPolicies?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            dapr_component_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        r = r.json()

        for policy in r["value"]:
            policy_list.append(policy)

        return policy_list


class StoragePreviewClient(StorageClient):
    api_version = PREVIEW_API_VERSION


class ManagedEnvironmentPreviewClient(ManagedEnvironmentClient):
    api_version = PREVIEW_API_VERSION

    @classmethod
    def update(cls, cmd, resource_group_name, name, managed_environment_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(managed_environment_envelope))

        if no_wait:
            return
        elif r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            response = poll_results(cmd, operation_url)
            if response is None:
                raise ResourceNotFoundError("Could not find a container app")
            else:
                return response

        return r.json()

    @classmethod
    def list_usages(cls, cmd, resource_group_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/usages?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()


class HttpRouteConfigPreviewClient:
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create(cls, cmd, resource_group_name, name, http_route_config_name, http_route_config_envelope):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/httpRouteConfigs/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            http_route_config_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(http_route_config_envelope))
        return r.json()

    @classmethod
    def update(cls, cmd, resource_group_name, name, http_route_config_name, http_route_config_envelope):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/httpRouteConfigs/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            http_route_config_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(http_route_config_envelope))
        return r.json()

    @classmethod
    def list(cls, cmd, resource_group_name, name):
        route_list = []
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/httpRouteConfigs?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url, body=None)
        j = r.json()
        for route in j["value"]:
            route_list.append(route)
        return route_list

    @classmethod
    def show(cls, cmd, resource_group_name, name, http_route_config_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/httpRouteConfigs/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            http_route_config_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url, body=None)
        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, name, http_route_config_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/httpRouteConfigs/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            http_route_config_name,
            cls.api_version)

        send_raw_request(cmd.cli_ctx, "DELETE", request_url, body=None)
        # API doesn't return JSON (it returns no content)
        return


class AuthPreviewClient(AuthClient):
    api_version = PREVIEW_API_VERSION


class ConnectedEnvironmentClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create(cls, cmd, resource_group_name, name, connected_environment_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(connected_environment_envelope))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def update(cls, cmd, resource_group_name, name, managed_environment_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(managed_environment_envelope))

        if no_wait:
            return
        elif r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            response = poll_results(cmd, operation_url)
            if response is None:
                raise ResourceNotFoundError("Could not find a connected environment")
            else:
                return response

        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code in [200, 201, 202, 204]:
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_LOCATION)
                poll_results(cmd, operation_url)
                logger.warning('Connected environment successfully deleted')
        return

    @classmethod
    def show(cls, cmd, resource_group_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def list_by_subscription(cls, cmd, formatter=lambda x: x):
        env_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        request_url = "{}/subscriptions/{}/providers/Microsoft.App/connectedEnvironments?api-version={}".format(
            management_hostname.strip('/'),
            sub_id,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for env in j["value"]:
            formatted = formatter(env)
            env_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for env in j["value"]:
                formatted = formatter(env)
                env_list.append(formatted)

        return env_list

    @classmethod
    def list_by_resource_group(cls, cmd, resource_group_name, formatter=lambda x: x):
        env_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for env in j["value"]:
            formatted = formatter(env)
            env_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for env in j["value"]:
                formatted = formatter(env)
                env_list.append(formatted)

        return env_list


class ConnectedEnvCertificateClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def show_certificate(cls, cmd, resource_group_name, name, certificate_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/certificates/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            certificate_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url, body=None)
        return r.json()

    @classmethod
    def list_certificates(cls, cmd, resource_group_name, name, formatter=lambda x: x):
        certs_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/certificates?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url, body=None)
        j = r.json()
        for cert in j["value"]:
            formatted = formatter(cert)
            certs_list.append(formatted)
        return certs_list

    @classmethod
    def create_or_update_certificate(cls, cmd, resource_group_name, name, certificate_name, certificate, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/certificates/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            certificate_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(certificate))
        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def delete_certificate(cls, cmd, resource_group_name, name, certificate_name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/certificates/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            certificate_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url, body=None)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            poll_results(cmd, operation_url)
            logger.warning('Certificate %s was successfully deleted', certificate_name)

        return

    @classmethod
    def check_name_availability(cls, cmd, resource_group_name, name, name_availability_request):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        api_version = PREVIEW_API_VERSION
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/checkNameAvailability?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            api_version)

        r = send_raw_request(cmd.cli_ctx, "POST", request_url, body=json.dumps(name_availability_request))
        return r.json()


class ConnectedEnvDaprComponentClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create_or_update(cls, cmd, resource_group_name, environment_name, name, dapr_component_envelope, no_wait=False):

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/daprComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(dapr_component_envelope))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, environment_name, name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/daprComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            poll_results(cmd, operation_url)
            logger.warning('Dapr component %s was successfully deleted', name)

        return

    @classmethod
    def show(cls, cmd, resource_group_name, environment_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/daprComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def list(cls, cmd, resource_group_name, environment_name, formatter=lambda x: x):
        app_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        request_url = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/daprComponents?api-version={}".format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for app in j["value"]:
            formatted = formatter(app)
            app_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for app in j["value"]:
                formatted = formatter(app)
                app_list.append(formatted)

        return app_list


class ConnectedEnvStorageClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create_or_update(cls, cmd, resource_group_name, env_name, name, storage_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/storages/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            env_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(storage_envelope))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, env_name, name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/storages/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            env_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            poll_results(cmd, operation_url)
            logger.warning('Storage %s was successfully deleted', name)

        return

    @classmethod
    def show(cls, cmd, resource_group_name, env_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/storages/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            env_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def list(cls, cmd, resource_group_name, env_name, formatter=lambda x: x):
        env_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/connectedEnvironments/{}/storages?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            env_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for env in j["value"]:
            formatted = formatter(env)
            env_list.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for env in j["value"]:
                formatted = formatter(env)
                env_list.append(formatted)

        return env_list


class DaprComponentPreviewClient(DaprComponentClient):
    api_version = PREVIEW_API_VERSION


class BuilderClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def list(cls, cmd, resource_group_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/builders?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            cls.api_version)
        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def create(cls, cmd, builder_name, resource_group_name, environment_name, location, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/builders/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            builder_name,
            cls.api_version)
        body_data = {
            "location": location,
            "properties": {
                "environmentId": f"/subscriptions/{sub_id}/resourceGroups/{resource_group_name}/providers/Microsoft.App/managedEnvironments/{environment_name}"
            }
        }

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(body_data))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()


class BuildClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create(cls, cmd, builder_name, build_name, resource_group_name, location, build_env_vars, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/builders/{}/builds/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            builder_name,
            build_name,
            cls.api_version)
        body_data = {
            "location": location,
            "properties": {
                "configuration": {
                    "environmentVariables": build_env_vars
                }
            }
        }

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(body_data))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def get(cls, cmd, builder_name, build_name, resource_group_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/builders/{}/builds/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            builder_name,
            build_name,
            cls.api_version)
        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        return r.json()

    @classmethod
    def list_auth_token(cls, cmd, builder_name, build_name, resource_group_name, location):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/builders/{}/builds/{}/listAuthToken?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            builder_name,
            build_name,
            cls.api_version)
        body_data = {
            "location": location,
            "properties": {}
        }
        r = send_raw_request(cmd.cli_ctx, "POST", request_url, body=json.dumps(body_data))
        return r.json()


class JavaComponentPreviewClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create(cls, cmd, resource_group_name, environment_name, name, java_component_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/javaComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(java_component_envelope))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def update(cls, cmd, resource_group_name, environment_name, name, java_component_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/javaComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(java_component_envelope))

        if no_wait:
            return
        elif r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            response = poll_results(cmd, operation_url)
            if response is None:
                raise ResourceNotFoundError("Could not find the Java component")
            else:
                return response

        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, environment_name, name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/javaComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code in [200, 201, 202, 204]:
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_LOCATION)
                poll_results(cmd, operation_url)
                logger.warning('Java component successfully deleted')

    @classmethod
    def show(cls, cmd, resource_group_name, environment_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/javaComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def list(cls, cmd, resource_group_name, environment_name):
        java_component_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/javaComponents?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        r = r.json()

        for component in r["value"]:
            java_component_list.append(component)

        return java_component_list


class SessionPoolPreviewClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create(cls, cmd, resource_group_name, name, session_pool_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/sessionPools/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(session_pool_envelope))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def update(cls, cmd, resource_group_name, name, session_pool_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/sessionPools/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(session_pool_envelope))

        if no_wait:
            return
        elif r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            response = poll_results(cmd, operation_url)
            if response is None:
                raise ResourceNotFoundError("Could not find the Session Pool")
            else:
                return response

        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/sessionPools/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code in [200, 201, 202, 204]:
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_LOCATION)
                poll_results(cmd, operation_url)
                logger.warning('Session pool successfully deleted')

    @classmethod
    def show(cls, cmd, resource_group_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/sessionPools/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def list_by_resource_group(cls, cmd, resource_group_name):
        session_pool_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/sessionPools?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        r = r.json()

        for session_pool in r["value"]:
            session_pool_list.append(session_pool)

        return session_pool_list

    @classmethod
    def list_by_subscription(cls, cmd, formatter=lambda x: x):
        sessionpools = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        request_url = "{}/subscriptions/{}/providers/Microsoft.App/sessionPools?api-version={}".format(
            management_hostname.strip('/'),
            sub_id,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        j = r.json()
        for env in j["value"]:
            formatted = formatter(env)
            sessionpools.append(formatted)

        while j.get("nextLink") is not None:
            request_url = j["nextLink"]
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
            j = r.json()
            for env in j["value"]:
                formatted = formatter(env)
                sessionpools.append(formatted)

        return sessionpools


class SessionCodeInterpreterPreviewClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def execute(cls, cmd, identifier, code_interpreter_envelope, session_pool_endpoint, no_wait=False):
        url_fmt = "{}/executions?identifier={}&api-version={}"
        request_url = url_fmt.format(
            session_pool_endpoint,
            identifier,
            cls.api_version)
        logger.warning(request_url)
        logger.warning(code_interpreter_envelope)
        r = send_raw_request(cmd.cli_ctx, "POST", request_url, body=json.dumps(code_interpreter_envelope), resource=SESSION_RESOURCE)

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def upload(cls, cmd, identifier, filepath, path, session_pool_endpoint, no_wait=False):
        url_fmt = "{}/files?{}identifier={}&api-version={}"
        request_url = url_fmt.format(
            session_pool_endpoint,
            f"path={path}&" if path is not None else "",
            identifier,
            cls.api_version)

        from azure.cli.core._profile import Profile
        profile = Profile(cli_ctx=cmd.cli_ctx)
        token_info, _, _ = profile.get_raw_token(resource=SESSION_RESOURCE)
        _, token, _ = token_info
        headers = {'Authorization': 'Bearer ' + token}

        try:
            data_file = open(filepath, "rb")
            file_name = os.path.basename(filepath)
            files = [("file", (file_name, data_file))]

            r = requests.post(
                request_url,
                files=files,
                headers=headers)

            data_file.close()
        except Exception as e:
            logger.error("error occurred while uploading file")
            return str(e)

        if no_wait:
            return r.json()
        elif r.status_code in [200, 201, 202, 204]:
            logger.warning("upload success")
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
                poll_status(cmd, operation_url)
                r = send_raw_request(cmd.cli_ctx, "GET", request_url, resource=SESSION_RESOURCE)

        return r.json()

    @classmethod
    def show_file_content(cls, cmd, identifier, filename, path, session_pool_endpoint):
        path, filename = cls.extract_path_from_filename(path, filename)
        url_fmt = "{}/files/{}/content?{}identifier={}&api-version={}"
        request_url = url_fmt.format(
            session_pool_endpoint,
            filename,
            f"path={path}&" if path is not None else "",
            identifier,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url, resource=SESSION_RESOURCE)
        # print out the file content as bytes decoded as string
        logger.warning(r.content.decode())

        return json.dumps(r.content.decode())

    @classmethod
    def show_file_metadata(cls, cmd, identifier, filename, path, session_pool_endpoint):
        path, filename = cls.extract_path_from_filename(path, filename)
        url_fmt = "{}/files/{}?{}identifier={}&api-version={}"
        request_url = url_fmt.format(
            session_pool_endpoint,
            filename,
            f"path={path}&" if path is not None else "",
            identifier,
            cls.api_version)
        logger.warning(request_url)
        r = send_raw_request(cmd.cli_ctx, "GET", request_url, resource=SESSION_RESOURCE)

        return r.json()

    @classmethod
    def delete_file(cls, cmd, identifier, filename, path, session_pool_endpoint, no_wait=False):
        path, filename = cls.extract_path_from_filename(path, filename)
        url_fmt = "{}/files/{}?{}identifier={}&api-version={}"
        request_url = url_fmt.format(
            session_pool_endpoint,
            filename,
            f"path={path}&" if path is not None else "",
            identifier,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url, resource=SESSION_RESOURCE)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code in [200, 201, 202, 204]:
            logger.warning('file successfully deleted')
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_LOCATION)
                poll_results(cmd, operation_url)

    @classmethod
    def list_files(cls, cmd, identifier, path, session_pool_endpoint):
        if path is None:
            path = ""

        url_fmt = "{}/files?identifier={}&path={}&api-version={}"
        request_url = url_fmt.format(
            session_pool_endpoint,
            identifier,
            path,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url, resource=SESSION_RESOURCE)
        return r.json()

    @staticmethod
    def extract_path_from_filename(path, filename):
        if '/' not in filename:
            return path, filename
        path_in_filename, filename = filename.rsplit('/', 1)
        if path is None:
            return path_in_filename, filename
        else:
            return path.rstrip("/") + "/" + path_in_filename.lstrip('/'), filename


class SessionCustomContainerPreviewClient():
    # pylint: disable=too-few-public-methods
    session_dp_api_version = "2025-02-02-preview"  # may be different from ACA CP

    @classmethod
    def stop_session(cls, cmd, identifier, session_pool_endpoint):
        url_fmt = "{}/.management/stopSession?identifier={}&api-version={}"
        request_url = url_fmt.format(
            session_pool_endpoint,
            identifier,
            cls.session_dp_api_version)

        r = send_raw_request(cmd.cli_ctx, "POST", request_url, resource=SESSION_RESOURCE)

        return r.text


class DotNetComponentPreviewClient():
    api_version = PREVIEW_API_VERSION

    @classmethod
    def create(cls, cmd, resource_group_name, environment_name, name, dotnet_component_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/dotNetComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(dotnet_component_envelope))

        if no_wait:
            return r.json()
        elif r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def update(cls, cmd, resource_group_name, environment_name, name, dotnet_component_envelope, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/dotNetComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PATCH", request_url, body=json.dumps(dotnet_component_envelope))

        if no_wait:
            return
        elif r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            response = poll_results(cmd, operation_url)
            if response is None:
                raise ResourceNotFoundError("Could not find the DotNet component")
            else:
                return response

        return r.json()

    @classmethod
    def delete(cls, cmd, resource_group_name, environment_name, name, no_wait=False):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/dotNetComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if no_wait:
            return  # API doesn't return JSON (it returns no content)
        elif r.status_code in [200, 201, 202, 204]:
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_LOCATION)
                poll_results(cmd, operation_url)

    @classmethod
    def show(cls, cmd, resource_group_name, environment_name, name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/dotNetComponents/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def list(cls, cmd, resource_group_name, environment_name):
        dotNet_component_list = []

        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/Microsoft.App/managedEnvironments/{}/dotNetComponents?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        r = r.json()

        for component in r["value"]:
            dotNet_component_list.append(component)

        return dotNet_component_list


class MaintenanceConfigPreviewClient():
    api_version = PREVIEW_API_VERSION
    maintenance_config_name = MAINTENANCE_CONFIG_DEFAULT_NAME

    @classmethod
    def list(cls, cmd, resource_group_name, environment_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/microsoft.app/managedenvironments/{}/maintenanceConfigurations/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            cls.maintenance_config_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "GET", request_url)

        return r.json()

    @classmethod
    def create_or_update(cls, cmd, resource_group_name, environment_name, maintenance_config_envelope):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/microsoft.app/managedenvironments/{}/maintenanceConfigurations/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            cls.maintenance_config_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "PUT", request_url, body=json.dumps(maintenance_config_envelope))

        if r.status_code == 201:
            operation_url = r.headers.get(HEADER_AZURE_ASYNC_OPERATION)
            poll_status(cmd, operation_url)
            r = send_raw_request(cmd.cli_ctx, "GET", request_url)
        if r.status_code == 202:
            operation_url = r.headers.get(HEADER_LOCATION)
            response = poll_results(cmd, operation_url)
            if response is None:
                raise ResourceNotFoundError("Could not find the maintenance config")
            else:
                return response

        return r.json()

    @classmethod
    def remove(cls, cmd, resource_group_name, environment_name):
        management_hostname = cmd.cli_ctx.cloud.endpoints.resource_manager
        sub_id = get_subscription_id(cmd.cli_ctx)
        url_fmt = "{}/subscriptions/{}/resourceGroups/{}/providers/microsoft.app/managedenvironments/{}/maintenanceConfigurations/{}?api-version={}"
        request_url = url_fmt.format(
            management_hostname.strip('/'),
            sub_id,
            resource_group_name,
            environment_name,
            cls.maintenance_config_name,
            cls.api_version)

        r = send_raw_request(cmd.cli_ctx, "DELETE", request_url)

        if r.status_code in [200, 201, 202, 204]:
            if r.status_code == 202:
                operation_url = r.headers.get(HEADER_LOCATION)
                poll_results(cmd, operation_url)
