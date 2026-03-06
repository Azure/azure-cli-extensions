##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##
"""
Module providing the WorkspaceMgmtClient class for managing workspace operations.
Created to do not add additional azure-mgmt-* dependencies that can conflict with existing ones.
"""

import logging
from http import HTTPStatus
from typing import Any, Dict, Optional, cast
from azure.core import PipelineClient
from azure.core.credentials import TokenProvider
from azure.core.pipeline import policies
from azure.core.rest import HttpRequest
from azure.core.exceptions import HttpResponseError
# from azure.quantum._workspace_connection_params import WorkspaceConnectionParams
from ._workspace_connection_params import WorkspaceConnectionParams
# from azure.quantum._constants import ConnectionConstants
from ._constants import ConnectionConstants
# from azure.quantum._client._configuration import VERSION
from ._client._configuration import VERSION

logger = logging.getLogger(__name__)

__all__ = ["WorkspaceMgmtClient"]


class WorkspaceMgmtClient():
    """
    Client for Azure Quantum Workspace related ARM/ARG operations.
    Uses PipelineClient under the hood which is standard for all Azure SDK clients,
    see https://learn.microsoft.com/en-us/azure/developer/python/sdk/fundamentals/http-pipeline-retries.
    
    :param credential:
        The credential to use to connect to Azure services.
    
    :param base_url:
        The base URL for the ARM endpoint.
    
    :param user_agent:
        Add the specified value as a prefix to the HTTP User-Agent header.
    """

    # Constants
    DEFAULT_RETRY_TOTAL = 3
    CONTENT_TYPE_JSON = "application/json"
    CONNECT_DOC_LINK = "https://learn.microsoft.com/en-us/azure/quantum/how-to-connect-workspace"
    CONNECT_DOC_MESSAGE = f"To find details on how to connect to your workspace, please see {CONNECT_DOC_LINK}."
    
    def __init__(self, credential: TokenProvider, base_url: str, user_agent: Optional[str] = None) -> None:
        """
        Initialize the WorkspaceMgmtClient.
        
        :param credential:
            The credential to use to connect to Azure services.
        
        :param base_url:
            The base URL for the ARM endpoint.
        """
        self._credential = credential
        self._base_url = base_url
        self._policies = [
            policies.RequestIdPolicy(),
            policies.HeadersPolicy({
                "Content-Type": self.CONTENT_TYPE_JSON,
                "Accept": self.CONTENT_TYPE_JSON,
            }),
            policies.UserAgentPolicy(user_agent=user_agent, sdk_moniker="quantum/{}".format(VERSION)),
            policies.RetryPolicy(retry_total=self.DEFAULT_RETRY_TOTAL),
            policies.BearerTokenCredentialPolicy(self._credential, ConnectionConstants.ARM_CREDENTIAL_SCOPE),
        ]
        self._client: PipelineClient = PipelineClient(base_url=cast(str, base_url), policies=self._policies)
    
    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> 'WorkspaceMgmtClient':
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._client.__exit__(*exc_details)

    def load_workspace_from_arg(self, connection_params: WorkspaceConnectionParams) -> None:
        """
        Queries Azure Resource Graph to find a workspace by name and optionally location, resource group, subscription.
        Provided workspace name, location, resource group, and subscription in connection params must be validated beforehand.
        
        :param connection_params:
            The workspace connection parameters to use and update.
        """
        if not connection_params.workspace_name:
            raise ValueError("Workspace name must be specified to try to load workspace details from ARG.")

        query = f"""
            Resources
            | where type =~ 'microsoft.quantum/workspaces'
            | where name =~ '{connection_params.workspace_name}'
        """
        
        if connection_params.resource_group:
            query += f"\n                | where resourceGroup =~ '{connection_params.resource_group}'"
        
        if connection_params.location:
            query += f"\n                | where location =~ '{connection_params.location}'"

        query += """
            | extend endpointUri = tostring(properties.endpointUri), workspaceKind = tostring(properties.workspaceKind)
            | project name, subscriptionId, resourceGroup, location, endpointUri, workspaceKind
        """

        request_body = {
            "query": query
        }

        if connection_params.subscription_id:
            request_body["subscriptions"] = [connection_params.subscription_id]

        # Create request to Azure Resource Graph API
        request = HttpRequest(
            method="POST",
            url=self._client.format_url("/providers/Microsoft.ResourceGraph/resources"),
            params={"api-version": ConnectionConstants.DEFAULT_ARG_API_VERSION},
            json=request_body
        )
        
        try:
            response = self._client.send_request(request)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            raise RuntimeError(
                f"Could not load workspace details from Azure Resource Graph: {str(e)}.\n{self.CONNECT_DOC_MESSAGE}"
            ) from e
        
        data = result.get('data', [])
        
        if not data:
            raise ValueError(f"No matching workspace found with name '{connection_params.workspace_name}'. {self.CONNECT_DOC_MESSAGE}")
        
        if len(data) > 1:
            raise ValueError(
                f"Multiple Azure Quantum workspaces found with name '{connection_params.workspace_name}'. "
                f"Please specify additional connection parameters. {self.CONNECT_DOC_MESSAGE}"
            )
        
        workspace_data: Dict[str, Any] = data[0]
        
        connection_params.subscription_id = workspace_data.get('subscriptionId')
        connection_params.resource_group = workspace_data.get('resourceGroup')
        connection_params.location = workspace_data.get('location')
        connection_params.quantum_endpoint = workspace_data.get('endpointUri')
        connection_params.workspace_kind = workspace_data.get('workspaceKind')

        logger.debug(
            "Found workspace '%s' in subscription '%s', resource group '%s', location '%s', endpoint '%s', kind '%s'.",
            connection_params.workspace_name,
            connection_params.subscription_id,
            connection_params.resource_group,
            connection_params.location,
            connection_params.quantum_endpoint,
            connection_params.workspace_kind
        )

        # If one of the required parameters is missing, probably workspace in failed provisioning state
        if not connection_params.is_complete():
            raise ValueError(
                f"Failed to retrieve complete workspace details for workspace '{connection_params.workspace_name}'. "
                "Please check that workspace is in valid state."
            )
        
    def load_workspace_from_arm(self, connection_params: WorkspaceConnectionParams) -> None:
        """
        Fetches the workspace resource from ARM and sets location and endpoint URI params.
        Provided workspace name, resource group, and subscription in connection params must be validated beforehand.
        
        :param connection_params:
            The workspace connection parameters to use and update.
        """
        if not all([connection_params.subscription_id, connection_params.resource_group, connection_params.workspace_name]):
            raise ValueError("Missing required connection parameters to load workspace details from ARM.")
        
        api_version = connection_params.api_version or ConnectionConstants.DEFAULT_WORKSPACE_API_VERSION
        
        url = (
            f"/subscriptions/{connection_params.subscription_id}"
            f"/resourceGroups/{connection_params.resource_group}"
            f"/providers/Microsoft.Quantum/workspaces/{connection_params.workspace_name}"
        )

        request = HttpRequest(
            method="GET",
            url=self._client.format_url(url),
            params={"api-version": api_version},
        )
        
        try:
            response = self._client.send_request(request)
            response.raise_for_status()
            workspace_data: Dict[str, Any] = response.json()
        except HttpResponseError as e:
            if e.status_code == HTTPStatus.NOT_FOUND:
                raise ValueError(
                    f"Azure Quantum workspace '{connection_params.workspace_name}' "
                    f"not found in resource group '{connection_params.resource_group}' "
                    f"and subscription '{connection_params.subscription_id}'. "
                    f"{self.CONNECT_DOC_MESSAGE}"
                ) from e
            # Re-raise for other HTTP errors
            raise
        except Exception as e:
            raise RuntimeError(
                f"Could not load workspace details from ARM: {str(e)}.\n{self.CONNECT_DOC_MESSAGE}"
            ) from e

        # Extract and apply location
        location = workspace_data.get("location")
        if location:
            connection_params.location = location
            logger.debug(
                "Updated workspace location from ARM: %s",
                location
            )
        else:
            raise ValueError(
                f"Failed to retrieve location for workspace '{connection_params.workspace_name}'. "
                f"Please check that workspace is in valid state."
            )

        # Extract and apply endpoint URI from properties
        properties: Dict[str, Any] = workspace_data.get("properties", {})
        endpoint_uri = properties.get("endpointUri")
        if endpoint_uri:
            connection_params.quantum_endpoint = endpoint_uri
            logger.debug(
                "Updated workspace endpoint from ARM: %s", connection_params.quantum_endpoint
            )
        else:
            raise ValueError(
                f"Failed to retrieve endpoint uri for workspace '{connection_params.workspace_name}'. "
                f"Please check that workspace is in valid state."
            )
        
        # Set workspaceKind if available
        workspace_kind = properties.get("workspaceKind")
        if workspace_kind:
            connection_params.workspace_kind = workspace_kind
            logger.debug(
                "Updated workspace kind from ARM: %s", connection_params.workspace_kind
            )
