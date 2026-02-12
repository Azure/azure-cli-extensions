# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines

from collections.abc import MutableMapping
from io import IOBase
from typing import Any, Callable, IO, Optional, TypeVar, Union, cast, overload

from azure.core import AsyncPipelineClient
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.pipeline import PipelineResponse
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ..._utils.serialization import Deserializer, Serializer
from ...operations._operations import (
    build_collaboration_analytics_auditevents_get_request,
    build_collaboration_analytics_cleanroompolicy_get_request,
    build_collaboration_analytics_dataset_document_id_get_request,
    build_collaboration_analytics_dataset_document_id_publish_post_request,
    build_collaboration_analytics_datasets_list_get_request,
    build_collaboration_analytics_deployment_info_get_request,
    build_collaboration_analytics_get_request,
    build_collaboration_analytics_queries_document_id_get_request,
    build_collaboration_analytics_queries_document_id_publish_post_request,
    build_collaboration_analytics_queries_document_id_run_post_request,
    build_collaboration_analytics_queries_document_id_runhistory_get_request,
    build_collaboration_analytics_queries_document_id_vote_accept_post_request,
    build_collaboration_analytics_queries_document_id_vote_reject_post_request,
    build_collaboration_analytics_queries_jobid_get_request,
    build_collaboration_analytics_queries_list_get_request,
    build_collaboration_attestationreport_cgs_get_request,
    build_collaboration_attestationreport_cleanroom_get_request,
    build_collaboration_check_consent_document_id_get_request,
    build_collaboration_id_get_request,
    build_collaboration_invitation_id_accept_post_request,
    build_collaboration_invitation_id_get_request,
    build_collaboration_invitations_get_request,
    build_collaboration_list_request,
    build_collaboration_oidc_issuer_info_get_request,
    build_collaboration_set_consent_document_id_consent_action_post_request,
    build_collaboration_workloads_get_request,
)
from .._configuration import AnalyticsFrontendAPIConfiguration

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest,
                                              AsyncHttpResponse], T, dict[str, Any]], Any]]
List = list


class CollaborationOperations:  # pylint: disable=too-many-public-methods
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~analytics_frontend_api.aio.AnalyticsFrontendAPI`'s
        :attr:`collaboration` attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        input_args = list(args)
        self._client: AsyncPipelineClient = input_args.pop(
            0) if input_args else kwargs.pop("client")
        self._config: AnalyticsFrontendAPIConfiguration = input_args.pop(
            0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(
            0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(
            0) if input_args else kwargs.pop("deserializer")

    @distributed_trace_async
    async def list(
            self,
            body: Optional[Any] = None,
            **kwargs: Any) -> List[str]:
        """List all collaborations.

        List all collaborations.

        :param body: Default value is None.
        :type body: any
        :return: list of str
        :rtype: list[str]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    "str"
                ]
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[List[str]] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_list_request(
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    List[str],
                    deserialized),
                {})  # type: ignore

        return cast(List[str], deserialized)  # type: ignore

    @distributed_trace_async
    async def id_get(
            self,
            collaboration_id: str,
            body: Optional[Any] = None,
            **kwargs: Any) -> JSON:
        """Get collaboration by id.

        Get collaboration by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
        :type body: any
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "collaborationId": "str",
                    "consortiumEndpoint": "str",
                    "consortiumServiceCertificatePem": "str",
                    "userEmail": "str",
                    "userStatus": "str"
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_id_get_request(
            collaboration_id=collaboration_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    JSON,
                    deserialized),
                {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def workloads_get(
        self, collaboration_id: str, body: Optional[Any] = None, **kwargs: Any
    ) -> Union[List[str], JSON]:
        """List all collaboration workloads.

        List all collaboration workloads.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
        :type body: any
        :return: list of str or JSON object
        :rtype: list[str] or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    "str"
                ]
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[Union[List[str], JSON]] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_workloads_get_request(
            collaboration_id=collaboration_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(
                Union[List[str], JSON], deserialized), {})  # type: ignore

        return cast(Union[List[str], JSON], deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_get(
            self,
            collaboration_id: str,
            body: Optional[Any] = None,
            **kwargs: Any) -> JSON:
        """Get collaboration analytics workload.

        Get collaboration analytics workload.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
        :type body: any
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "data": {},
                    "id": "str",
                    "state": "str",
                    "version": "str"
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_analytics_get_request(
            collaboration_id=collaboration_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    JSON,
                    deserialized),
                {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_deployment_info_get(
        self, collaboration_id: str, body: Optional[Any] = None, **kwargs: Any
    ) -> JSON:
        """Get collaboration analytics deploymentInfo.

        Get collaboration analytics deploymentInfo.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
        :type body: any
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "data": {}
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_analytics_deployment_info_get_request(
            collaboration_id=collaboration_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    JSON,
                    deserialized),
                {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_cleanroompolicy_get(
        self, collaboration_id: str, body: Optional[Any] = None, **kwargs: Any
    ) -> JSON:
        """Get collaboration analytics cleanroompolicy.

        Get collaboration analytics cleanroompolicy.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
        :type body: any
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "policy": {},
                    "proposalId": "str"
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_analytics_cleanroompolicy_get_request(
            collaboration_id=collaboration_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    JSON,
                    deserialized),
                {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def oidc_issuer_info_get(
            self,
            collaboration_id: str,
            body: Optional[Any] = None,
            **kwargs: Any) -> JSON:
        """Get collaboration oidcissuer.

        Get collaboration oidcissuer.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
        :type body: any
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "enabled": bool,
                    "issuerUrl": "str",
                    "tenantData": {
                        "issuerUrl": "str",
                        "tenantId": "str"
                    }
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_oidc_issuer_info_get_request(
            collaboration_id=collaboration_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    JSON,
                    deserialized),
                {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def invitations_get(
        self, collaboration_id: str, body: Optional[Any] = None, **kwargs: Any
    ) -> Union[List[str], JSON]:
        """List all invitations.

        List all invitations.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
        :type body: any
        :return: list of str or JSON object
        :rtype: list[str] or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    "str"
                ]
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[Union[List[str], JSON]] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_invitations_get_request(
            collaboration_id=collaboration_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(
                Union[List[str], JSON], deserialized), {})  # type: ignore

        return cast(Union[List[str], JSON], deserialized)  # type: ignore

    @distributed_trace_async
    async def invitation_id_get(
            self,
            collaboration_id: str,
            invitation_id: str,
            body: Optional[Any] = None,
            **kwargs: Any) -> JSON:
        """Get invitation by id.

        Get invitation by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param invitation_id: Required.
        :type invitation_id: str
        :param body: Default value is None.
        :type body: any
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "accountType": "str",
                    "invitationId": "str",
                    "status": "str",
                    "userInfo": {
                        "data": {
                            "tenantId": "str"
                        },
                        "userId": "str"
                    }
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_invitation_id_get_request(
            collaboration_id=collaboration_id,
            invitation_id=invitation_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    JSON,
                    deserialized),
                {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def invitation_id_accept_post(self,
                                        collaboration_id: str,
                                        invitation_id: str,
                                        body: Optional[Any] = None,
                                        **kwargs: Any) -> Union[Any,
                                                                JSON]:
        """Accept invitation by id.

        Accept invitation by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param invitation_id: Required.
        :type invitation_id: str
        :param body: Default value is None.
        :type body: any
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[Union[Any, JSON]] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_invitation_id_accept_post_request(
            collaboration_id=collaboration_id,
            invitation_id=invitation_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(
                Union[Any, JSON], deserialized), {})  # type: ignore

        return cast(Union[Any, JSON], deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_datasets_list_get(
        self, collaboration_id: str, body: Optional[Any] = None, **kwargs: Any
    ) -> Union[List[str], JSON]:
        """List all datasets.

        List all datasets.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
        :type body: any
        :return: list of str or JSON object
        :rtype: list[str] or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    "str"
                ]
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[Union[List[str], JSON]] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_analytics_datasets_list_get_request(
            collaboration_id=collaboration_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(
                Union[List[str], JSON], deserialized), {})  # type: ignore

        return cast(Union[List[str], JSON], deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_dataset_document_id_get(
            self,
            collaboration_id: str,
            document_id: str,
            body: Optional[Any] = None,
            **kwargs: Any) -> JSON:
        """Get dataset by id.

        Get dataset by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Default value is None.
        :type body: any
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "data": {
                        "datasetAccessPoint": {
                            "name": "str",
                            "path": "str",
                            "protection": {
                                "proxyMode": "str",
                                "proxyType": "str",
                                "configuration": "",
                                "encryptionSecretAccessIdentity": {
                                    "clientId": "str",
                                    "name": "str",
                                    "tenantId": "str",
                                    "tokenIssuer": {}
                                },
                                "encryptionSecrets": {
                                    "dek": {
                                        "name": "str",
                                        "secret": {
                                            "backingResource": {
                                                "id": "str",
                                                "name": "str",
                                                "provider": {
                                                    "protocol":
                                                      "str",
                                                    "url": "str",
                "configuration": ""
                                                },
                                                "type": "str"
                                            },
                                            "secretType": "str"
                                        }
                                    },
                                    "kek": {
                                        "name": "str",
                                        "secret": {
                                            "backingResource": {
                                                "id": "str",
                                                "name": "str",
                                                "provider": {
                                                    "protocol":
                                                      "str",
                                                    "url": "str",
                "configuration": ""
                                                },
                                                "type": "str"
                                            },
                                            "secretType": "str"
                                        }
                                    }
                                },
                                "privacyPolicy": {
                                    "policy": {}
                                }
                            },
                            "store": {
                                "id": "str",
                                "name": "str",
                                "provider": {
                                    "protocol": "str",
                                    "url": "str",
                                    "configuration": ""
                                },
                                "type": "str"
                            },
                            "type": "str",
                            "identity": {
                                "clientId": "str",
                                "name": "str",
                                "tenantId": "str",
                                "tokenIssuer": {}
                            }
                        },
                        "datasetAccessPolicy": {
                            "accessMode": "str",
                            "allowedFields": [
                                "str"
                            ]
                        },
                        "datasetSchema": {
                            "fields": [
                                {
                                    "fieldName": "str",
                                    "fieldType": "str"
                                }
                            ],
                            "format": "str"
                        },
                        "name": "str"
                    },
                    "id": "str",
                    "proposerId": "str",
                    "state": "str",
                    "version": "str"
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_analytics_dataset_document_id_get_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    JSON,
                    deserialized),
                {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @overload
    async def analytics_dataset_document_id_publish_post(  # pylint: disable=name-too-long
        self,
        collaboration_id: str,
        document_id: str,
        body: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Union[Any, JSON]:
        """Publish dataset by id.

        Publish dataset by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "data": {
                        "datasetAccessPoint": {
                            "name": "str",
                            "path": "str",
                            "protection": {
                                "proxyMode": "str",
                                "proxyType": "str",
                                "configuration": "",
                                "encryptionSecretAccessIdentity": {
                                    "clientId": "str",
                                    "name": "str",
                                    "tenantId": "str",
                                    "tokenIssuer": {}
                                },
                                "encryptionSecrets": {
                                    "dek": {
                                        "name": "str",
                                        "secret": {
                                            "backingResource": {
                                                "id": "str",
                                                "name": "str",
                                                "provider": {
                                                    "protocol":
                                                      "str",
                                                    "url": "str",
                "configuration": ""
                                                },
                                                "type": "str"
                                            },
                                            "secretType": "str"
                                        }
                                    },
                                    "kek": {
                                        "name": "str",
                                        "secret": {
                                            "backingResource": {
                                                "id": "str",
                                                "name": "str",
                                                "provider": {
                                                    "protocol":
                                                      "str",
                                                    "url": "str",
                "configuration": ""
                                                },
                                                "type": "str"
                                            },
                                            "secretType": "str"
                                        }
                                    }
                                },
                                "privacyPolicy": {
                                    "policy": {}
                                }
                            },
                            "store": {
                                "id": "str",
                                "name": "str",
                                "provider": {
                                    "protocol": "str",
                                    "url": "str",
                                    "configuration": ""
                                },
                                "type": "str"
                            },
                            "type": "str",
                            "identity": {
                                "clientId": "str",
                                "name": "str",
                                "tenantId": "str",
                                "tokenIssuer": {}
                            }
                        },
                        "datasetAccessPolicy": {
                            "accessMode": "str",
                            "allowedFields": [
                                "str"
                            ]
                        },
                        "datasetSchema": {
                            "fields": [
                                {
                                    "fieldName": "str",
                                    "fieldType": "str"
                                }
                            ],
                            "format": "str"
                        },
                        "name": "str"
                    },
                    "version": "str"
                }

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """

    @overload
    async def analytics_dataset_document_id_publish_post(  # pylint: disable=name-too-long
        self,
        collaboration_id: str,
        document_id: str,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Union[Any, JSON]:
        """Publish dataset by id.

        Publish dataset by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """

    @distributed_trace_async
    async def analytics_dataset_document_id_publish_post(  # pylint: disable=name-too-long
        self, collaboration_id: str, document_id: str, body: Union[JSON, IO[bytes]], **kwargs: Any
    ) -> Union[Any, JSON]:
        """Publish dataset by id.

        Publish dataset by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "data": {
                        "datasetAccessPoint": {
                            "name": "str",
                            "path": "str",
                            "protection": {
                                "proxyMode": "str",
                                "proxyType": "str",
                                "configuration": "",
                                "encryptionSecretAccessIdentity": {
                                    "clientId": "str",
                                    "name": "str",
                                    "tenantId": "str",
                                    "tokenIssuer": {}
                                },
                                "encryptionSecrets": {
                                    "dek": {
                                        "name": "str",
                                        "secret": {
                                            "backingResource": {
                                                "id": "str",
                                                "name": "str",
                                                "provider": {
                                                    "protocol":
                                                      "str",
                                                    "url": "str",
                "configuration": ""
                                                },
                                                "type": "str"
                                            },
                                            "secretType": "str"
                                        }
                                    },
                                    "kek": {
                                        "name": "str",
                                        "secret": {
                                            "backingResource": {
                                                "id": "str",
                                                "name": "str",
                                                "provider": {
                                                    "protocol":
                                                      "str",
                                                    "url": "str",
                "configuration": ""
                                                },
                                                "type": "str"
                                            },
                                            "secretType": "str"
                                        }
                                    }
                                },
                                "privacyPolicy": {
                                    "policy": {}
                                }
                            },
                            "store": {
                                "id": "str",
                                "name": "str",
                                "provider": {
                                    "protocol": "str",
                                    "url": "str",
                                    "configuration": ""
                                },
                                "type": "str"
                            },
                            "type": "str",
                            "identity": {
                                "clientId": "str",
                                "name": "str",
                                "tenantId": "str",
                                "tokenIssuer": {}
                            }
                        },
                        "datasetAccessPolicy": {
                            "accessMode": "str",
                            "allowedFields": [
                                "str"
                            ]
                        },
                        "datasetSchema": {
                            "fields": [
                                {
                                    "fieldName": "str",
                                    "fieldType": "str"
                                }
                            ],
                            "format": "str"
                        },
                        "name": "str"
                    },
                    "version": "str"
                }

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop("Content-Type", None))
        cls: ClsType[Union[Any, JSON]] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _json = None
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _json = body

        _request = build_collaboration_analytics_dataset_document_id_publish_post_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            content_type=content_type,
            json=_json,
            content=_content,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(
                Union[Any, JSON], deserialized), {})  # type: ignore

        return cast(Union[Any, JSON], deserialized)  # type: ignore

    @distributed_trace_async
    async def check_consent_document_id_get(
            self,
            collaboration_id: str,
            document_id: str,
            body: Optional[Any] = None,
            **kwargs: Any) -> JSON:
        """Check execution consent by ID of the Query or the Dataset.

        Check execution consent by ID of the Query or the Dataset.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Default value is None.
        :type body: any
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "status": "str",
                    "reason": {
                        "code": "str",
                        "message": "str"
                    }
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_check_consent_document_id_get_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    JSON,
                    deserialized),
                {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def set_consent_document_id_consent_action_post(  # pylint: disable=name-too-long
        self, collaboration_id: str, document_id: str, consent_action: str, body: Optional[Any] = None, **kwargs: Any
    ) -> Union[Any, JSON]:
        """Set execution consent (accept / reject) by ID of the Query or the Dataset.

        Set execution consent (accept / reject) by ID of the Query or the Dataset.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param consent_action: Known values are: "enable" and "disable". Required.
        :type consent_action: str
        :param body: Default value is None.
        :type body: any
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[Union[Any, JSON]] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_set_consent_document_id_consent_action_post_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            consent_action=consent_action,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(
                Union[Any, JSON], deserialized), {})  # type: ignore

        return cast(Union[Any, JSON], deserialized)  # type: ignore

    @overload
    async def analytics_queries_document_id_publish_post(  # pylint: disable=name-too-long
        self,
        collaboration_id: str,
        document_id: str,
        body: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Union[Any, JSON]:
        """Publish query by id.

        Publish query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "inputDatasets": [
                        {
                            "datasetDocumentId": "str",
                            "view": "str"
                        }
                    ],
                    "outputDataset": {
                        "datasetDocumentId": "str",
                        "view": "str"
                    },
                    "queryData": {
                        "segments": [
                            {
                                "data": "str",
                                "executionSequence": 0,
                                "postFilters": [
                                    {
                                        "columnName": "str",
                                        "value": 0
                                    }
                                ],
                                "preConditions": [
                                    {
                                        "minRowCount": 0,
                                        "viewName": "str"
                                    }
                                ]
                            }
                        ]
                    }
                }

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """

    @overload
    async def analytics_queries_document_id_publish_post(  # pylint: disable=name-too-long
        self,
        collaboration_id: str,
        document_id: str,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Union[Any, JSON]:
        """Publish query by id.

        Publish query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """

    @distributed_trace_async
    async def analytics_queries_document_id_publish_post(  # pylint: disable=name-too-long
        self, collaboration_id: str, document_id: str, body: Union[JSON, IO[bytes]], **kwargs: Any
    ) -> Union[Any, JSON]:
        """Publish query by id.

        Publish query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "inputDatasets": [
                        {
                            "datasetDocumentId": "str",
                            "view": "str"
                        }
                    ],
                    "outputDataset": {
                        "datasetDocumentId": "str",
                        "view": "str"
                    },
                    "queryData": {
                        "segments": [
                            {
                                "data": "str",
                                "executionSequence": 0,
                                "postFilters": [
                                    {
                                        "columnName": "str",
                                        "value": 0
                                    }
                                ],
                                "preConditions": [
                                    {
                                        "minRowCount": 0,
                                        "viewName": "str"
                                    }
                                ]
                            }
                        ]
                    }
                }

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop("Content-Type", None))
        cls: ClsType[Union[Any, JSON]] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _json = None
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _json = body

        _request = build_collaboration_analytics_queries_document_id_publish_post_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            content_type=content_type,
            json=_json,
            content=_content,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(
                Union[Any, JSON], deserialized), {})  # type: ignore

        return cast(Union[Any, JSON], deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_queries_list_get(
        self, collaboration_id: str, body: Optional[Any] = None, **kwargs: Any
    ) -> Union[List[str], JSON]:
        """List all queries.

        List all queries.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
        :type body: any
        :return: list of str or JSON object
        :rtype: list[str] or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    "str"
                ]
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[Union[List[str], JSON]] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_analytics_queries_list_get_request(
            collaboration_id=collaboration_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(
                Union[List[str], JSON], deserialized), {})  # type: ignore

        return cast(Union[List[str], JSON], deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_queries_document_id_get(
            self,
            collaboration_id: str,
            document_id: str,
            body: Optional[Any] = None,
            **kwargs: Any) -> JSON:
        """Get query by id.

        Get query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Default value is None.
        :type body: any
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "approvers": [
                        {
                            "approverId": "str",
                            "approverIdType": "str"
                        }
                    ],
                    "data": {
                        "applicationType": "str",
                        "inputDataset": [
                            {
                                "specification": "str",
                                "view": "str"
                            }
                        ],
                        "outputDataset": {
                            "specification": "str",
                            "view": "str"
                        },
                        "query": "str"
                    },
                    "id": "str",
                    "proposalId": "str",
                    "proposerId": "str",
                    "state": "str",
                    "version": "str"
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_analytics_queries_document_id_get_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    JSON,
                    deserialized),
                {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @overload
    async def analytics_queries_document_id_vote_accept_post(  # pylint: disable=name-too-long
        self,
        collaboration_id: str,
        document_id: str,
        body: Optional[JSON] = None,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Union[Any, JSON]:
        """Vote accept on query by id.

        Vote accept on query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Default value is None.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "proposalId": "str"
                }

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """

    @overload
    async def analytics_queries_document_id_vote_accept_post(  # pylint: disable=name-too-long
        self,
        collaboration_id: str,
        document_id: str,
        body: Optional[IO[bytes]] = None,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Union[Any, JSON]:
        """Vote accept on query by id.

        Vote accept on query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Default value is None.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """

    @distributed_trace_async
    async def analytics_queries_document_id_vote_accept_post(  # pylint: disable=name-too-long
        self, collaboration_id: str, document_id: str, body: Optional[Union[JSON, IO[bytes]]] = None, **kwargs: Any
    ) -> Union[Any, JSON]:
        """Vote accept on query by id.

        Vote accept on query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Default value is None.
        :type body: JSON or IO[bytes]
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "proposalId": "str"
                }

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop("Content-Type", None))
        content_type = content_type if body else None
        cls: ClsType[Union[Any, JSON]] = kwargs.pop("cls", None)

        content_type = content_type or "application/json" if body else None
        _json = None
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            if body is not None:
                _json = body
            else:
                _json = None

        _request = build_collaboration_analytics_queries_document_id_vote_accept_post_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            content_type=content_type,
            json=_json,
            content=_content,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(
                Union[Any, JSON], deserialized), {})  # type: ignore

        return cast(Union[Any, JSON], deserialized)  # type: ignore

    @overload
    async def analytics_queries_document_id_vote_reject_post(  # pylint: disable=name-too-long
        self,
        collaboration_id: str,
        document_id: str,
        body: Optional[JSON] = None,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Union[Any, JSON]:
        """Vote reject on query by id.

        Vote reject on query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Default value is None.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "proposalId": "str"
                }

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """

    @overload
    async def analytics_queries_document_id_vote_reject_post(  # pylint: disable=name-too-long
        self,
        collaboration_id: str,
        document_id: str,
        body: Optional[IO[bytes]] = None,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Union[Any, JSON]:
        """Vote reject on query by id.

        Vote reject on query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Default value is None.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """

    @distributed_trace_async
    async def analytics_queries_document_id_vote_reject_post(  # pylint: disable=name-too-long
        self, collaboration_id: str, document_id: str, body: Optional[Union[JSON, IO[bytes]]] = None, **kwargs: Any
    ) -> Union[Any, JSON]:
        """Vote reject on query by id.

        Vote reject on query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Default value is None.
        :type body: JSON or IO[bytes]
        :return: any or JSON object
        :rtype: any or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "proposalId": "str"
                }

                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop("Content-Type", None))
        content_type = content_type if body else None
        cls: ClsType[Union[Any, JSON]] = kwargs.pop("cls", None)

        content_type = content_type or "application/json" if body else None
        _json = None
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            if body is not None:
                _json = body
            else:
                _json = None

        _request = build_collaboration_analytics_queries_document_id_vote_reject_post_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            content_type=content_type,
            json=_json,
            content=_content,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(
                Union[Any, JSON], deserialized), {})  # type: ignore

        return cast(Union[Any, JSON], deserialized)  # type: ignore

    @overload
    async def analytics_queries_document_id_run_post(
        self,
        collaboration_id: str,
        document_id: str,
        body: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> JSON:
        """Run query by id.

        Run query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "runId": "str",
                    "dryRun": bool,
                    "endDate": "str",
                    "startDate": "str",
                    "useOptimizer": bool
                }

                # response body for status code(s): 200
                response == {
                    "jobId": "str",
                    "status": "str",
                    "dryRun": bool,
                    "jobIdField": "str",
                    "optimizationUsed": bool,
                    "reasoning": "str",
                    "skuSettings": {
                        "driver": {
                            "cores": 0,
                            "memory": "str",
                            "serviceAccount": "str"
                        },
                        "executor": {
                            "cores": 0,
                            "deleteOnTermination": bool,
                            "instances": {
                                "max": 0,
                                "min": 0
                            },
                            "memory": "str"
                        }
                    },
                    "x-ms-client-request-id": "str",
                    "x-ms-correlation-id": "str"
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """

    @overload
    async def analytics_queries_document_id_run_post(
        self,
        collaboration_id: str,
        document_id: str,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> JSON:
        """Run query by id.

        Run query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "jobId": "str",
                    "status": "str",
                    "dryRun": bool,
                    "jobIdField": "str",
                    "optimizationUsed": bool,
                    "reasoning": "str",
                    "skuSettings": {
                        "driver": {
                            "cores": 0,
                            "memory": "str",
                            "serviceAccount": "str"
                        },
                        "executor": {
                            "cores": 0,
                            "deleteOnTermination": bool,
                            "instances": {
                                "max": 0,
                                "min": 0
                            },
                            "memory": "str"
                        }
                    },
                    "x-ms-client-request-id": "str",
                    "x-ms-correlation-id": "str"
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """

    @distributed_trace_async
    async def analytics_queries_document_id_run_post(
        self, collaboration_id: str, document_id: str, body: Union[JSON, IO[bytes]], **kwargs: Any
    ) -> JSON:
        """Run query by id.

        Run query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "runId": "str",
                    "dryRun": bool,
                    "endDate": "str",
                    "startDate": "str",
                    "useOptimizer": bool
                }

                # response body for status code(s): 200
                response == {
                    "jobId": "str",
                    "status": "str",
                    "dryRun": bool,
                    "jobIdField": "str",
                    "optimizationUsed": bool,
                    "reasoning": "str",
                    "skuSettings": {
                        "driver": {
                            "cores": 0,
                            "memory": "str",
                            "serviceAccount": "str"
                        },
                        "executor": {
                            "cores": 0,
                            "deleteOnTermination": bool,
                            "instances": {
                                "max": 0,
                                "min": 0
                            },
                            "memory": "str"
                        }
                    },
                    "x-ms-client-request-id": "str",
                    "x-ms-correlation-id": "str"
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop("Content-Type", None))
        cls: ClsType[JSON] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _json = None
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _json = body

        _request = build_collaboration_analytics_queries_document_id_run_post_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            content_type=content_type,
            json=_json,
            content=_content,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    JSON,
                    deserialized),
                {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_queries_jobid_get(
            self,
            collaboration_id: str,
            jobid: str,
            body: Optional[Any] = None,
            **kwargs: Any) -> JSON:
        """Get query run result by run id.

        Get query run result by run id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param jobid: Required.
        :type jobid: str
        :param body: Default value is None.
        :type body: any
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "events": [
                        {
                            "message": "str",
                            "reason": "str",
                            "type": "str",
                            "count": 0,
                            "firstTimestamp": "2020-02-20 00:00:00",
                            "lastTimestamp": "2020-02-20 00:00:00",
                            "name": "str"
                        }
                    ],
                    "jobId": "str",
                    "status": {
                        "applicationState": {
                            "state": "str"
                        },
                        "terminationTime": "2020-02-20 00:00:00"
                    }
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_analytics_queries_jobid_get_request(
            collaboration_id=collaboration_id,
            jobid=jobid,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    JSON,
                    deserialized),
                {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_queries_document_id_runhistory_get(  # pylint: disable=name-too-long
        self, collaboration_id: str, document_id: str, body: Optional[Any] = None, **kwargs: Any
    ) -> Union[List[JSON], JSON]:
        """Get query run history by query id.

        Get query run history by query id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Default value is None.
        :type body: any
        :return: list of JSON object or JSON object
        :rtype: list[JSON] or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    {
                        "data": {},
                        "queryId": "str",
                        "runId": "str"
                    }
                ]
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[Union[List[JSON], JSON]] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_analytics_queries_document_id_runhistory_get_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(
                Union[List[JSON], JSON], deserialized), {})  # type: ignore

        return cast(Union[List[JSON], JSON], deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_auditevents_get(
        self, collaboration_id: str, body: Optional[Any] = None, **kwargs: Any
    ) -> Union[List[JSON], JSON]:
        """Get audit events for analytics workload.

        Get audit events for analytics workload.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
        :type body: any
        :return: list of JSON object or JSON object
        :rtype: list[JSON] or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    {
                        "data": {},
                        "id": "str",
                        "scope": "str",
                        "timestamp": "str",
                        "timestampIso": "str"
                    }
                ]
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[Union[List[JSON], JSON]] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_analytics_auditevents_get_request(
            collaboration_id=collaboration_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(
                Union[List[JSON], JSON], deserialized), {})  # type: ignore

        return cast(Union[List[JSON], JSON], deserialized)  # type: ignore

    @distributed_trace_async
    async def attestationreport_cgs_get(
            self,
            collaboration_id: str,
            body: Optional[Any] = None,
            **kwargs: Any) -> JSON:
        """Get attestation report from CGS.

        Get attestation report from CGS.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
        :type body: any
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "platform": "str",
                    "reportDataPayload": "str",
                    "report": {
                        "attestation": "str",
                        "platformCertificates": "str",
                        "uvmEndorsements": "str"
                    }
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_attestationreport_cgs_get_request(
            collaboration_id=collaboration_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    JSON,
                    deserialized),
                {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def attestationreport_cleanroom_get(
        self, collaboration_id: str, body: Optional[Any] = None, **kwargs: Any
    ) -> JSON:
        """Get attestation report from Cleanroom.

        Get attestation report from Cleanroom.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
        :type body: any
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "platform": "str",
                    "reportDataPayload": "str",
                    "report": {
                        "attestation": "str",
                        "platformCertificates": "str",
                        "uvmEndorsements": "str"
                    }
                }
                # response body for status code(s): 422
                response == {
                    "loc": [
                        {}
                    ],
                    "msg": "str",
                    "type": "str"
                }
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", _headers.pop(
                "Content-Type", "application/json"))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

        if body is not None:
            _json = body
        else:
            _json = None

        _request = build_collaboration_attestationreport_cleanroom_get_request(
            collaboration_id=collaboration_id,
            content_type=content_type,
            json=_json,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 422]:
            map_error(
                status_code=response.status_code,
                response=response,
                error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(
                pipeline_response,
                cast(
                    JSON,
                    deserialized),
                {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore
