# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Illustrative track2-style client + operations for the AIManager resource.

Mirrors what AutoRest generates: an ``ARMPipelineClient`` plus an operations
group whose methods build requests, send them through the pipeline, and (for
PUT/DELETE) return an ``LROPoller``. Condensed and hand-written for comparison
with the AAZ approach only.
"""

from azure.mgmt.core import ARMPipelineClient
from azure.mgmt.core.policies import ARMAutoResourceProviderRegistrationPolicy
from azure.core.polling import LROPoller
from azure.mgmt.core.polling.arm_polling import ARMPolling
from azure.core.pipeline.transport import HttpRequest
from msrest import Serializer, Deserializer

from . import models as _models

API_VERSION = "2026-04-02-preview"


class AIManagersOperations:
    """Operations for Microsoft.ContainerService/aiManagers."""

    def __init__(self, client, serializer, deserializer):
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer

    def _url(self, template, **kwargs):
        path_args = {k: self._serialize.url(k, v, "str") for k, v in kwargs.items()}
        return self._client.format_url(template, **path_args)

    def _query(self):
        return {"api-version": self._serialize.query("api_version", API_VERSION, "str")}

    def _headers(self, has_body):
        headers = {"Accept": "application/json"}
        if has_body:
            headers["Content-Type"] = "application/json"
        return headers

    def begin_create_or_update(self, resource_group_name, ai_manager_name, parameters, **kwargs):
        url = self._url(
            "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}"
            "/providers/Microsoft.ContainerService/aiManagers/{aiManagerName}",
            subscriptionId=self._client._subscription_id,
            resourceGroupName=resource_group_name,
            aiManagerName=ai_manager_name,
        )
        body = self._serialize.body(parameters, "AIManager")
        request = HttpRequest("PUT", url, headers=self._headers(True))
        request.format_parameters(self._query())
        request.set_json_body(body)

        def deserialization_callback(pipeline_response):
            return self._deserialize("AIManager", pipeline_response.http_response)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        return LROPoller(
            self._client, pipeline_response, deserialization_callback, ARMPolling(30, **kwargs)
        )

    def get(self, resource_group_name, ai_manager_name, **kwargs):
        url = self._url(
            "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}"
            "/providers/Microsoft.ContainerService/aiManagers/{aiManagerName}",
            subscriptionId=self._client._subscription_id,
            resourceGroupName=resource_group_name,
            aiManagerName=ai_manager_name,
        )
        request = HttpRequest("GET", url, headers=self._headers(False))
        request.format_parameters(self._query())
        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        return self._deserialize("AIManager", pipeline_response.http_response)

    def begin_delete(self, resource_group_name, ai_manager_name, **kwargs):
        url = self._url(
            "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}"
            "/providers/Microsoft.ContainerService/aiManagers/{aiManagerName}",
            subscriptionId=self._client._subscription_id,
            resourceGroupName=resource_group_name,
            aiManagerName=ai_manager_name,
        )
        request = HttpRequest("DELETE", url, headers=self._headers(False))
        request.format_parameters(self._query())
        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        return LROPoller(self._client, pipeline_response, lambda _: None, ARMPolling(30, **kwargs))

    def list_by_resource_group(self, resource_group_name, **kwargs):
        url = self._url(
            "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}"
            "/providers/Microsoft.ContainerService/aiManagers",
            subscriptionId=self._client._subscription_id,
            resourceGroupName=resource_group_name,
        )
        return self._list(url, **kwargs)

    def list_by_subscription(self, **kwargs):
        url = self._url(
            "/subscriptions/{subscriptionId}/providers/Microsoft.ContainerService/aiManagers",
            subscriptionId=self._client._subscription_id,
        )
        return self._list(url, **kwargs)

    def _list(self, url, **kwargs):
        request = HttpRequest("GET", url, headers=self._headers(False))
        request.format_parameters(self._query())
        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        body = self._deserialize.dependencies["object"](pipeline_response.http_response.text())
        return [self._deserialize("AIManager", item) for item in (body or {}).get("value", [])]


class AIManagerNamespacesOperations:
    """Operations for Microsoft.ContainerService/aiManagers/namespaces."""

    _BASE = ("/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}"
             "/providers/Microsoft.ContainerService/aiManagers/{aiManagerName}/namespaces")

    def __init__(self, client, serializer, deserializer):
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer

    def _url(self, template, **kwargs):
        path_args = {k: self._serialize.url(k, v, "str") for k, v in kwargs.items()}
        return self._client.format_url(template, **path_args)

    def _query(self):
        return {"api-version": self._serialize.query("api_version", API_VERSION, "str")}

    def _headers(self, has_body):
        headers = {"Accept": "application/json"}
        if has_body:
            headers["Content-Type"] = "application/json"
        return headers

    def begin_create_or_update(self, resource_group_name, ai_manager_name, namespace_name,
                               parameters, **kwargs):
        url = self._url(
            self._BASE + "/{namespaceName}",
            subscriptionId=self._client._subscription_id,
            resourceGroupName=resource_group_name,
            aiManagerName=ai_manager_name,
            namespaceName=namespace_name,
        )
        body = self._serialize.body(parameters, "AIManagerNamespace")
        request = HttpRequest("PUT", url, headers=self._headers(True))
        request.format_parameters(self._query())
        request.set_json_body(body)

        def deserialization_callback(pipeline_response):
            return self._deserialize("AIManagerNamespace", pipeline_response.http_response)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        return LROPoller(
            self._client, pipeline_response, deserialization_callback, ARMPolling(30, **kwargs)
        )

    def get(self, resource_group_name, ai_manager_name, namespace_name, **kwargs):
        url = self._url(
            self._BASE + "/{namespaceName}",
            subscriptionId=self._client._subscription_id,
            resourceGroupName=resource_group_name,
            aiManagerName=ai_manager_name,
            namespaceName=namespace_name,
        )
        request = HttpRequest("GET", url, headers=self._headers(False))
        request.format_parameters(self._query())
        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        return self._deserialize("AIManagerNamespace", pipeline_response.http_response)

    def begin_delete(self, resource_group_name, ai_manager_name, namespace_name, **kwargs):
        url = self._url(
            self._BASE + "/{namespaceName}",
            subscriptionId=self._client._subscription_id,
            resourceGroupName=resource_group_name,
            aiManagerName=ai_manager_name,
            namespaceName=namespace_name,
        )
        request = HttpRequest("DELETE", url, headers=self._headers(False))
        request.format_parameters(self._query())
        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        return LROPoller(self._client, pipeline_response, lambda _: None, ARMPolling(30, **kwargs))

    def list_by_ai_manager(self, resource_group_name, ai_manager_name, **kwargs):
        url = self._url(
            self._BASE,
            subscriptionId=self._client._subscription_id,
            resourceGroupName=resource_group_name,
            aiManagerName=ai_manager_name,
        )
        request = HttpRequest("GET", url, headers=self._headers(False))
        request.format_parameters(self._query())
        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        body = self._deserialize.dependencies["object"](pipeline_response.http_response.text())
        return [self._deserialize("AIManagerNamespace", item)
                for item in (body or {}).get("value", [])]


class AIManagerMgmtClient:
    """Illustrative management client (what AutoRest calls e.g. ContainerServiceAIManagerClient)."""

    def __init__(self, credential, subscription_id, base_url, credential_scopes=None, **kwargs):
        self._subscription_id = subscription_id
        policies = kwargs.pop("policies", None)
        if policies is None:
            policies = [ARMAutoResourceProviderRegistrationPolicy()]
        self._pipeline_client = ARMPipelineClient(
            base_url=base_url,
            credential=credential,
            credential_scopes=credential_scopes or [base_url.rstrip("/") + "/.default"],
            per_call_policies=policies,
            **kwargs,
        )
        client_models = {k: v for k, v in _models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._serialize.client_side_validation = False
        self._deserialize = Deserializer(client_models)
        self.ai_managers = AIManagersOperations(self, self._serialize, self._deserialize)
        self.ai_manager_namespaces = AIManagerNamespacesOperations(
            self, self._serialize, self._deserialize)

    # convenience shims so operations can use `self._client.<...>`
    @property
    def _pipeline(self):
        return self._pipeline_client._pipeline

    def format_url(self, template, **kwargs):
        return self._pipeline_client.format_url(template, **kwargs)
