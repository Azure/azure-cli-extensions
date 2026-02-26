# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from ..models import ExtensionAccessTokenRequest
from azure.core.utils import case_insensitive_dict
from azure.core.pipeline import PipelineResponse
from typing import Any
from msrest import Serializer
from azure.mgmt.core.exceptions import ARMErrorFormat
from azure.core.rest import HttpRequest
from azure.core.exceptions import (
    HttpResponseError,
    map_error,
)

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_get_extensions_request(
    resource_group: str,
    subscription_id: str,
    connected_cluster: str,
    **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    api_version: str = kwargs.pop("api_version", _params.pop("api-version", "2021-05-01-preview"))
    accept = _headers.pop("Accept", "application/json")
    content_type = _headers.pop("content_type", "application/json")

    _url = kwargs.pop(
        "template_url",
        "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Kubernetes/connectedClusters/{connectedCluster}/Providers/Microsoft.KubernetesConfiguration/extensions",
    )  # pylint: disable=line-too-long
    path_format_arguments = {
        "subscriptionId": _SERIALIZER.url("subscription_id", subscription_id, "str"),
        "resourceGroupName": _SERIALIZER.url("resource_group_name", resource_group, 'str'),
        "connectedCluster": _SERIALIZER.url("connected_cluster", connected_cluster, "str")
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore
    _params["api-version"] = _SERIALIZER.query("api_version", api_version, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")
    _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")

    return HttpRequest(method="GET", url=_url, params=_params, headers=_headers, **kwargs)

def build_get_extension_token_request(
    subscription_id: str,
    account_rg: str,
    account_name: str,
    **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    api_version: str = kwargs.pop("api_version", _params.pop("api-version", "2023-06-02-preview"))
    accept = _headers.pop("Accept", "application/json")
    content_type = _headers.pop("content_type", "application/json")

    _url = kwargs.pop(
        "template_url",
        "/subscriptions/{subscriptionId}/resourceGroups/{account_rg}/providers/Microsoft.VideoIndexer/accounts/{account_name}/generateExtensionAccessToken",
    )  # pylint: disable=line-too-long
    path_format_arguments = {
        "subscriptionId": _SERIALIZER.url("subscription_id", subscription_id, "str"),
        "account_rg": _SERIALIZER.url("account_rg", account_rg, "str"),
        "account_name": _SERIALIZER.url("account_name", account_name, "str"),
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore
    _params["api-version"] = _SERIALIZER.query("api_version", api_version, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")
    _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")

    return HttpRequest(method="POST", url=_url, params=_params, headers=_headers, **kwargs)

def get_extension_access_token_async(
    client: Any,
    serializer: Serializer,
    subscription_id: str,
    extension_id: str,
    account_rg: str,
    account_name: str,
    error_map=None,
    headers=None,
    params=None,
    **kwargs: Any):

    token_request = ExtensionAccessTokenRequest()
    token_request.permissionType = "Contributor"
    token_request.scope = "Account"
    token_request.extensionId = extension_id

    body_content = serializer.body(token_request, "ExtensionAccessTokenRequest")

    _request = build_get_extension_token_request(
        subscription_id=subscription_id,
        account_rg=account_rg,
        account_name=account_name,
        json=body_content,
        headers=headers,
        params=params,
    )

    _request.url = client.format_url(_request.url)
    _stream = False
    pipeline_response: PipelineResponse = client._pipeline.run(  # pylint: disable=protected-access
        _request, stream=_stream, **kwargs
    )

    response = pipeline_response.http_response
    if response.status_code not in [200]:
        map_error(status_code=response.status_code, response=response, error_map=error_map)
        raise HttpResponseError(response=response, error_format=ARMErrorFormat)

    return response.json().get("accessToken")



def extract_extension_info(extension):
    extension_id = extension.get('id')
    if extension_id is None:
        raise ValueError("Extension is missing 'id'.")

    properties = extension.get('properties')
    if properties is None:
        raise ValueError("Extension is missing 'properties'.")

    configuration = properties.get('configurationSettings')
    if configuration is None:
        raise ValueError("Extension properties are missing 'configurationSettings'.")

    account_id = configuration.get('videoIndexer.accountId')
    if account_id is None:
        raise ValueError("Configuration is missing 'videoIndexer.accountId'.")

    account_resource_id = configuration.get('videoIndexer.accountResourceId')
    if account_resource_id is None:
        raise ValueError("Configuration is missing 'videoIndexer.accountResourceId'.")

    base_extension_url = configuration.get('videoIndexer.endpointUri')
    if base_extension_url is None:
        raise ValueError("Configuration is missing 'videoIndexer.endpointUri'.")

    extension_url = f"{base_extension_url}/Accounts/{account_id}"
    parts = account_resource_id.strip("/").split("/")

    if len(parts) < 4:
        raise ValueError(f"Invalid account_resource_id format: {account_resource_id!r}")

    account_rg = parts[3]
    account_name = parts[-1]

    return extension_id, account_name, account_rg, extension_url
