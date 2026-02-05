# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Test utilities and mock helpers for managedcleanroom frontend tests.
"""

from unittest.mock import Mock


def create_mock_response(status_code=200, json_data=None, ok=True):
    """
    Create a mock HTTP response object.

    Args:
        status_code: HTTP status code (default: 200)
        json_data: Data to return from .json() call
        ok: Boolean indicating if request was successful

    Returns:
        Mock response object
    """
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.ok = ok

    if json_data is not None:
        mock_response.json.return_value = json_data
    else:
        mock_response.json.return_value = {}

    return mock_response


def create_mock_client(
        get_response=None,
        post_response=None,
        put_response=None):
    """
    Create a mock HTTP client with configurable responses.

    Args:
        get_response: Response to return for GET requests
        post_response: Response to return for POST requests
        put_response: Response to return for PUT requests

    Returns:
        Mock client object
    """
    mock_client = Mock()

    if get_response is not None:
        mock_client.get.return_value = get_response
    else:
        mock_client.get.return_value = create_mock_response()

    if post_response is not None:
        mock_client.post.return_value = post_response
    else:
        mock_client.post.return_value = create_mock_response()

    if put_response is not None:
        mock_client.put.return_value = put_response
    else:
        mock_client.put.return_value = create_mock_response()

    return mock_client


def create_mock_msal_token(
        access_token="mock_msal_token_abc123",
        expires_in=3600,
        name="Test User",
        email="test@example.com",
        oid="test-oid-123"):
    """
    Create a mock MSAL token response.

    Args:
        access_token: The access token string
        expires_in: Token expiration time in seconds
        name: User's display name
        email: User's email
        oid: User's object ID

    Returns:
        Dictionary with MSAL token structure
    """
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": expires_in,
        "id_token_claims": {
            "name": name,
            "email": email,
            "preferred_username": email,
            "oid": oid
        }
    }


def create_mock_azure_cli_token(token="mock_az_cli_token_xyz789"):
    """
    Create a mock Azure CLI credential token.

    Args:
        token: The token string

    Returns:
        Mock token object with .token attribute
    """
    mock_token = Mock()
    mock_token.token = token
    return mock_token


def create_mock_msal_config(
        client_id="test-client-id",
        tenant_id="test-tenant-id",
        scopes=None):
    """
    Create a mock MSAL configuration.

    Args:
        client_id: Azure AD application client ID
        tenant_id: Azure AD tenant ID
        scopes: List of OAuth scopes

    Returns:
        Dictionary with MSAL config structure
    """
    if scopes is None:
        scopes = ["User.Read"]
    elif isinstance(scopes, str):
        scopes = [scopes]

    return {
        "client_id": client_id,
        "tenant_id": tenant_id,
        "scopes": scopes
    }


# Mock test data fixtures

MOCK_COLLABORATION = {
    "collaborationId": "test-collab-123",
    "name": "Test Collaboration",
    "description": "A test collaboration for unit tests",
    "status": "active"
}

MOCK_COLLABORATION_LIST = [
    {
        "collaborationId": "collab-1",
        "name": "Collaboration 1",
        "status": "active"
    },
    {
        "collaborationId": "collab-2",
        "name": "Collaboration 2",
        "status": "active"
    }
]

MOCK_DATASET = {
    "datasetId": "test-dataset-123",
    "name": "Customer Data",
    "description": "Test customer dataset",
    "status": "published"
}

MOCK_DATASET_LIST = [
    {
        "datasetId": "dataset-1",
        "name": "Dataset 1",
        "status": "published"
    },
    {
        "datasetId": "dataset-2",
        "name": "Dataset 2",
        "status": "draft"
    }
]

MOCK_QUERY = {
    "queryId": "test-query-123",
    "name": "Revenue Analysis",
    "sql": "SELECT * FROM revenue",
    "status": "approved"
}

MOCK_QUERY_LIST = [
    {
        "queryId": "query-1",
        "name": "Query 1",
        "status": "approved"
    },
    {
        "queryId": "query-2",
        "name": "Query 2",
        "status": "pending"
    }
]

MOCK_INVITATION = {
    "invitationId": "test-invitation-123",
    "collaborationId": "test-collab-123",
    "inviteeEmail": "invitee@example.com",
    "status": "pending"
}

MOCK_QUERY_RUN = {
    "runId": "test-run-123",
    "queryId": "test-query-123",
    "status": "completed",
    "startTime": "2024-01-01T00:00:00Z",
    "endTime": "2024-01-01T00:05:00Z"
}

MOCK_ANALYTICS = {
    "analyticsId": "test-analytics-123",
    "status": "ready",
    "endpoint": "https://analytics.example.com"
}

MOCK_AUDIT_LOG = {
    "logId": "test-log-123",
    "timestamp": "2024-01-01T00:00:00Z",
    "action": "dataset_published",
    "userId": "user-123"
}
