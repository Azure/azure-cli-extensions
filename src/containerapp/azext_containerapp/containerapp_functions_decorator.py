# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, broad-except, logging-format-interpolation, too-many-public-methods, too-many-boolean-expressions, logging-fstring-interpolation

import json
from knack.log import get_logger

from azure.cli.core.azclierror import ValidationError, CLIError
from azure.cli.core.util import send_raw_request
from azure.cli.command_modules.containerapp.base_resource import BaseResource

from ._client_factory import handle_raw_exception
from ._validators import validate_basic_arguments, validate_revision_and_get_name, validate_functionapp_kind
from ._transformers import process_app_insights_response
from ._clients import ContainerAppPreviewClient

logger = get_logger(__name__)


class ContainerAppFunctionsDecorator(BaseResource):
    """Base decorator for Container App Functions operations"""

    def get_argument_resource_group_name(self):
        return self.get_param('resource_group_name')

    def get_argument_container_app_name(self):
        return self.get_param('container_app_name')

    def get_argument_revision_name(self):
        return self.get_param("revision_name")

    def get_argument_function_name(self):
        return self.get_param('function_name')

    def get_argument_timespan(self):
        return self.get_param('timespan')

    def get_argument_limit(self):
        return self.get_param('limit')

    def set_argument_resource_group_name(self, resource_group_name):
        self.set_param("resource_group_name", resource_group_name)

    def set_argument_container_app_name(self, container_app_name):
        self.set_param("container_app_name", container_app_name)

    def set_argument_revision_name(self, revision_name):
        self.set_param("revision_name", revision_name)

    def set_argument_function_name(self, function_name):
        self.set_param("function_name", function_name)

    def set_argument_timespan(self, timespan):
        self.set_param("timespan", timespan)

    def set_argument_limit(self, limit):
        self.set_param("limit", limit)

    def validate_common_arguments(self):
        """Validate common arguments required for all function operations"""
        resource_group_name = self.get_argument_resource_group_name()
        name = self.get_argument_container_app_name()
        revision_name = self.get_argument_revision_name()

        # Validate basic arguments
        validate_basic_arguments(
            resource_group_name=resource_group_name,
            container_app_name=name
        )

        # Validate revision and get the appropriate revision name
        revision_name, _ = validate_revision_and_get_name(
            cmd=self.cmd,
            resource_group_name=resource_group_name,
            container_app_name=name,
            provided_revision_name=revision_name
        )

        return resource_group_name, name, revision_name

    def validate_function_name_requirement(self):
        """Validate function name is provided when required"""
        function_name = self.get_argument_function_name()

        if not function_name:
            raise ValidationError("Function name is required.")

        return function_name


class ContainerAppFunctionsListDecorator(ContainerAppFunctionsDecorator):
    """Decorator for listing functions"""

    def list(self):
        """List functions for a container app or revision"""
        try:
            resource_group_name, name, revision_name = self.validate_common_arguments()

            # Validate that the Container App has kind 'functionapp'
            validate_functionapp_kind(
                cmd=self.cmd,
                resource_group_name=resource_group_name,
                container_app_name=name
            )

            if revision_name and revision_name is not None:
                # List functions for a specific revision
                return self.client.list_functions_by_revision(
                    cmd=self.cmd,
                    resource_group_name=resource_group_name,
                    container_app_name=name,
                    revision_name=revision_name
                )
            # List functions for latest active revision
            return self.client.list_functions(
                cmd=self.cmd,
                resource_group_name=resource_group_name,
                container_app_name=name
            )
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppFunctionsShowDecorator(ContainerAppFunctionsDecorator):
    """Decorator for showing a specific function"""

    def validate_show_arguments(self):
        """Validate arguments required for showing a function"""
        resource_group_name, name, revision_name = self.validate_common_arguments()
        function_name = self.validate_function_name_requirement()
        return resource_group_name, name, revision_name, function_name

    def show(self):
        """Show details of a specific function"""
        try:
            resource_group_name, name, revision_name, function_name = self.validate_show_arguments()

            # Validate that the Container App has kind 'functionapp'
            validate_functionapp_kind(
                cmd=self.cmd,
                resource_group_name=resource_group_name,
                container_app_name=name
            )

            if revision_name and revision_name is not None:
                # Get function for a specific revision
                return self.client.get_function_by_revision(
                    cmd=self.cmd,
                    resource_group_name=resource_group_name,
                    container_app_name=name,
                    revision_name=revision_name,
                    function_name=function_name
                )
            # Get function for the entire container app
            return self.client.get_function(
                cmd=self.cmd,
                resource_group_name=resource_group_name,
                container_app_name=name,
                function_name=function_name
            )
        except Exception as e:
            handle_raw_exception(e)


class ContainerAppFunctionInvocationsDecorator(ContainerAppFunctionsDecorator):
    """Decorator for showing function invocation"""

    APP_INSIGHTS_API_VERSION = "2018-04-20"

    def __init__(self, cmd, client, raw_parameters, models):
        super().__init__(cmd, client, raw_parameters, models)
        self.active_revision_mode = None

    def validate_arguments(self):
        """Validate arguments required for function invocation operations"""
        validate_basic_arguments(
            resource_group_name=self.get_argument_resource_group_name(),
            container_app_name=self.get_argument_container_app_name()
        )

        # Validate that the Container App has kind 'functionapp'
        validate_functionapp_kind(
            cmd=self.cmd,
            resource_group_name=self.get_argument_resource_group_name(),
            container_app_name=self.get_argument_container_app_name()
        )

        revision_name = self.get_argument_revision_name()
        revision_name, active_revision_mode = validate_revision_and_get_name(
            cmd=self.cmd,
            resource_group_name=self.get_argument_resource_group_name(),
            container_app_name=self.get_argument_container_app_name(),
            provided_revision_name=revision_name
        )

        # Update the revision name with the validated value
        self.set_argument_revision_name(revision_name)
        # Store active revision mode for use in query building
        self.active_revision_mode = active_revision_mode
        self.validate_function_name_requirement()

    def _get_app_insights_id(self, resource_group_name, container_app_name, revision_name):
        # Fetch the revision details using the container app client
        revision = ContainerAppPreviewClient.show_revision(self.cmd, resource_group_name, container_app_name, revision_name)
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

    def _execute_app_insights_query(self, app_id, query, query_type, timespan="30D"):
        # Application Insights REST API endpoint
        api_endpoint = "https://api.applicationinsights.io"
        url = f"{api_endpoint}/v1/apps/{app_id}/query?api-version={self.APP_INSIGHTS_API_VERSION}&queryType={query_type}"

        # Prepare the request body
        body = {
            "query": query,
            "timespan": f"P{timespan}"
        }

        # Execute the query using Azure CLI's send_raw_request
        response = send_raw_request(
            self.cmd.cli_ctx,
            "POST",
            url,
            body=json.dumps(body),
            headers=["Content-Type=application/json"]
        )

        result = response.json()
        if isinstance(result, dict) and 'error' in result:
            raise CLIError(f"Error retrieving invocations details: {result['error']}")
        return result

    def get_summary(self):
        """Get function invocation summary using the client"""
        try:
            self.validate_arguments()

            # Get arguments
            resource_group_name = self.get_argument_resource_group_name()
            container_app_name = self.get_argument_container_app_name()
            revision_name = self.get_argument_revision_name()
            function_name = self.get_argument_function_name()
            timespan = self.get_argument_timespan() or "30d"

            # Fetch the app insights resource app id
            app_id = self._get_app_insights_id(resource_group_name, container_app_name, revision_name)

            # Set revision_name to empty string for single mode, keep it for multiple mode
            revision_name = "" if self.active_revision_mode.lower() == "single" else revision_name

            invocation_summary_query = (
                f"requests | extend functionNameFromCustomDimension = tostring(customDimensions['faas.name']) "
                f"| where timestamp >= ago({timespan}) "
                f"| where cloud_RoleName =~ '{container_app_name}' "
                f"| where isempty(\"{revision_name}\") or cloud_RoleInstance contains '{revision_name}' "
                f"| where operation_Name =~ '{function_name}' or functionNameFromCustomDimension =~ '{function_name}' "
                f"| summarize SuccessCount = coalesce(countif(success == true), 0), ErrorCount = coalesce(countif(success == false), 0)"
            )

            result = self._execute_app_insights_query(app_id, invocation_summary_query, "getLast30DaySummary")

            return process_app_insights_response(result)
        except Exception as e:
            handle_raw_exception(e)

    def get_traces(self):
        """Get function invocation traces using the client"""
        try:
            self.validate_arguments()

            # Get all arguments
            resource_group_name = self.get_argument_resource_group_name()
            container_app_name = self.get_argument_container_app_name()
            revision_name = self.get_argument_revision_name()
            function_name = self.get_argument_function_name()
            timespan = self.get_argument_timespan() or "30d"
            limit = self.get_argument_limit() or 20

            # Fetch the app insights resource app id
            app_id = self._get_app_insights_id(resource_group_name, container_app_name, revision_name)

            # Set revision_name to empty string for single mode, keep it for multiple mode
            revision_name = "" if self.active_revision_mode.lower() == "single" else revision_name

            invocation_traces_query = (
                f"requests | extend functionNameFromCustomDimension = tostring(customDimensions['faas.name']) "
                f"| project timestamp, id, operation_Name, success, resultCode, duration, operation_Id, functionNameFromCustomDimension, "
                f"cloud_RoleName, cloud_RoleInstance, invocationId=coalesce(tostring(customDimensions['InvocationId']), tostring(customDimensions['faas.invocation_id'])) "
                f"| where timestamp > ago({timespan}) "
                f"| where cloud_RoleName =~ '{container_app_name}' "
                f"| where isempty(\"{revision_name}\") or cloud_RoleInstance contains '{revision_name}' "
                f"| where operation_Name =~ '{function_name}' or functionNameFromCustomDimension =~ '{function_name}' "
                f"| order by timestamp desc | take {limit} "
                f"| project timestamp, success, resultCode, durationInMilliSeconds=duration, invocationId, operationId=operation_Id, operationName=operation_Name, functionNameFromCustomDimension "
            )

            result = self._execute_app_insights_query(app_id, invocation_traces_query, "getInvocationTraces")

            return process_app_insights_response(result)
        except Exception as e:
            handle_raw_exception(e)
