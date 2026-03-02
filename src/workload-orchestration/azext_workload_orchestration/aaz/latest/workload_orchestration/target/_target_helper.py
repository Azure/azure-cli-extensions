# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: skip-file
# flake8: noqa


class TargetHelper:
    """Shared helper for target commands."""

    @staticmethod
    def get_solution_template_unique_identifier(subscription_id, resource_group_name, template_name, client):
        """Fetch the solution template and return its uniqueIdentifier from properties.

        Args:
            subscription_id: The subscription ID
            resource_group_name: The resource group name
            template_name: The solution template name
            client: HTTP client for making the request

        Returns:
            str: The uniqueIdentifier from template properties, or template_name as fallback

        Raises:
            CLIInternalError: If the template does not exist or the request fails
        """
        from azure.cli.core.azclierror import CLIInternalError
        import json

        template_url = client.format_url(
            "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Edge/solutionTemplates/{solutionTemplateName}",
            subscriptionId=subscription_id,
            resourceGroupName=resource_group_name,
            solutionTemplateName=template_name
        )
        request = client._request("GET", template_url, {
            "api-version": "2025-08-01"
        }, {
            "Accept": "application/json"
        }, None, {}, None)

        response = client.send_request(request=request, stream=False)

        if response.http_response.status_code == 404:
            raise CLIInternalError(
                f"Solution template '{template_name}' not found in resource group '{resource_group_name}'."
            )
        if response.http_response.status_code != 200:
            raise CLIInternalError(
                f"Failed to get solution template '{template_name}': HTTP {response.http_response.status_code}"
            )

        data = json.loads(response.http_response.text())
        unique_identifier = data.get("properties", {}).get("uniqueIdentifier")

        if unique_identifier and unique_identifier.strip():
            return unique_identifier
        return template_name
