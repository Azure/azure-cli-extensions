# pylint: disable=too-many-lines
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
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
    build_collaboration_analytics_datasets_document_id_get_request,
    build_collaboration_analytics_datasets_document_id_publish_post_request,
    build_collaboration_analytics_datasets_document_id_queries_get_request,
    build_collaboration_analytics_datasets_list_get_request,
    build_collaboration_analytics_get_request,
    build_collaboration_analytics_queries_document_id_get_request,
    build_collaboration_analytics_queries_document_id_publish_post_request,
    build_collaboration_analytics_queries_document_id_run_post_request,
    build_collaboration_analytics_queries_document_id_runs_get_request,
    build_collaboration_analytics_queries_document_id_vote_post_request,
    build_collaboration_analytics_queries_list_get_request,
    build_collaboration_analytics_runs_job_id_get_request,
    build_collaboration_analytics_secrets_secret_name_put_request,
    build_collaboration_consent_document_id_get_request,
    build_collaboration_consent_document_id_put_request,
    build_collaboration_id_get_request,
    build_collaboration_invitation_id_accept_post_request,
    build_collaboration_invitation_id_get_request,
    build_collaboration_invitations_get_request,
    build_collaboration_list_get_request,
    build_collaboration_oidc_issuer_info_get_request,
    build_collaboration_oidc_keys_get_request,
    build_collaboration_oidc_set_issuer_url_post_request,
    build_collaboration_report_get_request,
)
from .._configuration import AnalyticsFrontendAPIConfiguration

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, dict[str, Any]], Any]]


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
        self._client: AsyncPipelineClient = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config: AnalyticsFrontendAPIConfiguration = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize: Serializer = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize: Deserializer = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @distributed_trace_async
    async def list_get(self, *, active_only: bool = False, **kwargs: Any) -> list[JSON]:
        """List all collaborations.

        List all collaborations.

        :keyword active_only: When true, returns only active collaborations (email-only lookup). When
         false or omitted, returns all collaborations. Default value is False.
        :paramtype active_only: bool
        :return: list of JSON object
        :rtype: list[JSON]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    {
                        "collaborationId": "str",
                        "collaborationName": "str",
                        "userStatus": "str"
                    }
                ]
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[list[JSON]] = kwargs.pop("cls", None)

        _request = build_collaboration_list_get_request(
            active_only=active_only,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(list[JSON], deserialized), {})  # type: ignore

        return cast(list[JSON], deserialized)  # type: ignore

    @distributed_trace_async
    async def id_get(self, collaboration_id: str, *, active_only: bool = False, **kwargs: Any) -> JSON:
        """Get collaboration by id.

        Get collaboration by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :keyword active_only: When true, queries only the email-based table (active collaborations).
         When false or omitted, queries all tables. Default value is False.
        :paramtype active_only: bool
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "collaborationId": "str",
                    "collaborationName": "str",
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_id_get_request(
            collaboration_id=collaboration_id,
            active_only=active_only,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def report_get(self, collaboration_id: str, **kwargs: Any) -> JSON:
        """Get collaboration report.

        Get collaboration report.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "cgs": {
                        "cgsEndpoint": "str",
                        "recoveryAgentEndpoint": "str",
                        "report": {
                            "platform": "str",
                            "reportDataPayload": "str",
                            "report": {
                                "attestation": "str",
                                "platformCertificates": "str",
                                "serviceCert": "str",
                                "uvmEndorsements": "str"
                            }
                        }
                    },
                    "consortiumManager": {
                        "endpoint": "str",
                        "report": {
                            "platform": "str",
                            "serviceCert": "str",
                            "hostData": "str",
                            "report": {
                                "attestation": "str",
                                "platformCertificates": "str",
                                "serviceCert": "str",
                                "uvmEndorsements": "str"
                            }
                        }
                    }
                }
                # response body for status code(s): 400
                response == {
                    "error": "str",
                    "message": "str"
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_report_get_request(
            collaboration_id=collaboration_id,
            api_version=self._config.api_version,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 400, 422]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_get(self, collaboration_id: str, **kwargs: Any) -> JSON:
        """Get collaboration analytics workload.

        Get collaboration analytics workload.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "data": "str",
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_analytics_get_request(
            collaboration_id=collaboration_id,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_cleanroompolicy_get(self, collaboration_id: str, **kwargs: Any) -> JSON:
        """Get collaboration analytics cleanroompolicy.

        Get collaboration analytics cleanroompolicy.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "claims": {
                        "claims": {
                            "str": {}
                        }
                    },
                    "proposalIds": [
                        "str"
                    ]
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_analytics_cleanroompolicy_get_request(
            collaboration_id=collaboration_id,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def oidc_issuer_info_get(self, collaboration_id: str, **kwargs: Any) -> JSON:
        """Get collaboration OIDC issuer info.

        Get collaboration OIDC issuer info.

        :param collaboration_id: Required.
        :type collaboration_id: str
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_oidc_issuer_info_get_request(
            collaboration_id=collaboration_id,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @overload
    async def oidc_set_issuer_url_post(
        self,
        collaboration_id: str,
        body: Optional[JSON] = None,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> JSON:
        """Set collaboration oidc issuer url.

        Set collaboration oidc issuer url.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
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
                    "url": "str"
                }

                # response body for status code(s): 200
                response == {
                    "message": "str",
                    "url": "str"
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
    async def oidc_set_issuer_url_post(
        self,
        collaboration_id: str,
        body: Optional[IO[bytes]] = None,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> JSON:
        """Set collaboration oidc issuer url.

        Set collaboration oidc issuer url.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Default value is None.
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
                    "message": "str",
                    "url": "str"
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
    async def oidc_set_issuer_url_post(
        self, collaboration_id: str, body: Optional[Union[JSON, IO[bytes]]] = None, **kwargs: Any
    ) -> JSON:
        """Set collaboration oidc issuer url.

        Set collaboration oidc issuer url.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Default value is None.
        :type body: JSON or IO[bytes]
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "url": "str"
                }

                # response body for status code(s): 200
                response == {
                    "message": "str",
                    "url": "str"
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

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

        _request = build_collaboration_oidc_set_issuer_url_post_request(
            collaboration_id=collaboration_id,
            content_type=content_type,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def oidc_keys_get(self, collaboration_id: str, **kwargs: Any) -> JSON:
        """Get collaboration oidc signing keys (JWKS).

        Get collaboration oidc signing keys (JWKS).

        :param collaboration_id: Required.
        :type collaboration_id: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "keys": [
                        {
                            "kty": "str",
                            "alg": "str",
                            "e": "str",
                            "kid": "str",
                            "n": "str",
                            "use": "str",
                            "x5c": [
                                "str"
                            ],
                            "x5t": "str",
                            "x5t  #S256": "str"
                        }
                    ]
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_oidc_keys_get_request(
            collaboration_id=collaboration_id,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def invitations_get(self, collaboration_id: str, *, pending_only: bool = False, **kwargs: Any) -> JSON:
        """List all invitations.

        List all invitations.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :keyword pending_only: When true, returns only invitations where the user's status is not
         Active. When false or omitted, returns all matching invitations. Default value is False.
        :paramtype pending_only: bool
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "accountType": "str",
                    "invitationId": "str",
                    "status": "str"
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_invitations_get_request(
            collaboration_id=collaboration_id,
            pending_only=pending_only,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def invitation_id_get(self, collaboration_id: str, invitation_id: str, **kwargs: Any) -> JSON:
        """Get invitation by id.

        Get invitation by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param invitation_id: Required.
        :type invitation_id: str
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_invitation_id_get_request(
            collaboration_id=collaboration_id,
            invitation_id=invitation_id,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def invitation_id_accept_post(
        self, collaboration_id: str, invitation_id: str, **kwargs: Any
    ) -> Optional[JSON]:
        """Accept invitation by id.

        Accept invitation by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param invitation_id: Required.
        :type invitation_id: str
        :return: JSON object or None
        :rtype: JSON or None
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[Optional[JSON]] = kwargs.pop("cls", None)

        _request = build_collaboration_invitation_id_accept_post_request(
            collaboration_id=collaboration_id,
            invitation_id=invitation_id,
            api_version=self._config.api_version,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [204, 422]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        deserialized = None
        if response.status_code == 422:
            if response.content:
                deserialized = response.json()
            else:
                deserialized = None

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @distributed_trace_async
    async def analytics_datasets_list_get(self, collaboration_id: str, **kwargs: Any) -> JSON:
        """List all datasets.

        List all datasets.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "value": [
                        {
                            "id": "str",
                            "labels": {
                                "str": "str"
                            }
                        }
                    ]
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_analytics_datasets_list_get_request(
            collaboration_id=collaboration_id,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_datasets_document_id_get(self, collaboration_id: str, document_id: str, **kwargs: Any) -> JSON:
        """Get dataset by id.

        Get dataset by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "data": {
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
                        "name": "str",
                        "store": {
                            "containerName": "str",
                            "encryptionMode": "str",
                            "storageAccountType": "str",
                            "storageAccountUrl": "str",
                            "awsCgsSecretId": "str"
                        },
                        "dek": {
                            "keyVaultUrl": "str",
                            "secretId": "str",
                            "maaUrl": "str"
                        },
                        "identity": {
                            "clientId": "str",
                            "issuerUrl": "str",
                            "name": "str",
                            "tenantId": "str"
                        },
                        "kek": {
                            "keyVaultUrl": "str",
                            "secretId": "str",
                            "maaUrl": "str"
                        }
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_analytics_datasets_document_id_get_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @overload
    async def analytics_datasets_document_id_publish_post(  # pylint: disable=name-too-long
        self,
        collaboration_id: str,
        document_id: str,
        body: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Optional[JSON]:
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
        :return: JSON object or None
        :rtype: JSON or None
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
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
                    "name": "str",
                    "store": {
                        "containerName": "str",
                        "encryptionMode": "str",
                        "storageAccountType": "str",
                        "storageAccountUrl": "str",
                        "awsCgsSecretId": "str"
                    },
                    "dek": {
                        "keyVaultUrl": "str",
                        "secretId": "str",
                        "maaUrl": "str"
                    },
                    "identity": {
                        "clientId": "str",
                        "issuerUrl": "str",
                        "name": "str",
                        "tenantId": "str"
                    },
                    "kek": {
                        "keyVaultUrl": "str",
                        "secretId": "str",
                        "maaUrl": "str"
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
    async def analytics_datasets_document_id_publish_post(  # pylint: disable=name-too-long
        self,
        collaboration_id: str,
        document_id: str,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Optional[JSON]:
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
        :return: JSON object or None
        :rtype: JSON or None
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
    async def analytics_datasets_document_id_publish_post(  # pylint: disable=name-too-long
        self, collaboration_id: str, document_id: str, body: Union[JSON, IO[bytes]], **kwargs: Any
    ) -> Optional[JSON]:
        """Publish dataset by id.

        Publish dataset by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :return: JSON object or None
        :rtype: JSON or None
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
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
                    "name": "str",
                    "store": {
                        "containerName": "str",
                        "encryptionMode": "str",
                        "storageAccountType": "str",
                        "storageAccountUrl": "str",
                        "awsCgsSecretId": "str"
                    },
                    "dek": {
                        "keyVaultUrl": "str",
                        "secretId": "str",
                        "maaUrl": "str"
                    },
                    "identity": {
                        "clientId": "str",
                        "issuerUrl": "str",
                        "name": "str",
                        "tenantId": "str"
                    },
                    "kek": {
                        "keyVaultUrl": "str",
                        "secretId": "str",
                        "maaUrl": "str"
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[Optional[JSON]] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _json = None
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _json = body

        _request = build_collaboration_analytics_datasets_document_id_publish_post_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            content_type=content_type,
            api_version=self._config.api_version,
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

        if response.status_code not in [204, 422]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        deserialized = None
        if response.status_code == 422:
            if response.content:
                deserialized = response.json()
            else:
                deserialized = None

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @distributed_trace_async
    async def consent_document_id_get(self, collaboration_id: str, document_id: str, **kwargs: Any) -> JSON:
        """Check execution consent by ID of the Query or the Dataset.

        Check execution consent by ID of the Query or the Dataset.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_consent_document_id_get_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @overload
    async def consent_document_id_put(
        self,
        collaboration_id: str,
        document_id: str,
        body: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Optional[JSON]:
        """Set execution consent (enable / disable) by ID of the Query or the Dataset.

        Set execution consent (enable / disable) by ID of the Query or the Dataset.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: JSON object or None
        :rtype: JSON or None
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "consentAction": "str"
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
    async def consent_document_id_put(
        self,
        collaboration_id: str,
        document_id: str,
        body: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Optional[JSON]:
        """Set execution consent (enable / disable) by ID of the Query or the Dataset.

        Set execution consent (enable / disable) by ID of the Query or the Dataset.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: JSON object or None
        :rtype: JSON or None
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
    async def consent_document_id_put(
        self, collaboration_id: str, document_id: str, body: Union[JSON, IO[bytes]], **kwargs: Any
    ) -> Optional[JSON]:
        """Set execution consent (enable / disable) by ID of the Query or the Dataset.

        Set execution consent (enable / disable) by ID of the Query or the Dataset.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :return: JSON object or None
        :rtype: JSON or None
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "consentAction": "str"
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[Optional[JSON]] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _json = None
        _content = None
        if isinstance(body, (IOBase, bytes)):
            _content = body
        else:
            _json = body

        _request = build_collaboration_consent_document_id_put_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            content_type=content_type,
            api_version=self._config.api_version,
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

        if response.status_code not in [204, 422]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        deserialized = None
        if response.status_code == 422:
            if response.content:
                deserialized = response.json()
            else:
                deserialized = None

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @overload
    async def analytics_queries_document_id_publish_post(  # pylint: disable=name-too-long
        self,
        collaboration_id: str,
        document_id: str,
        body: JSON,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Optional[JSON]:
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
        :return: JSON object or None
        :rtype: JSON or None
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "inputDatasets": "str",
                    "outputDataset": "str",
                    "queryData": [
                        {
                            "data": "str",
                            "executionSequence": 0,
                            "postFilters": "str",
                            "preConditions": "str"
                        }
                    ]
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
    ) -> Optional[JSON]:
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
        :return: JSON object or None
        :rtype: JSON or None
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
    ) -> Optional[JSON]:
        """Publish query by id.

        Publish query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :return: JSON object or None
        :rtype: JSON or None
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "inputDatasets": "str",
                    "outputDataset": "str",
                    "queryData": [
                        {
                            "data": "str",
                            "executionSequence": 0,
                            "postFilters": "str",
                            "preConditions": "str"
                        }
                    ]
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[Optional[JSON]] = kwargs.pop("cls", None)

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
            api_version=self._config.api_version,
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

        if response.status_code not in [204, 422]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        deserialized = None
        if response.status_code == 422:
            if response.content:
                deserialized = response.json()
            else:
                deserialized = None

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

    @distributed_trace_async
    async def analytics_queries_list_get(self, collaboration_id: str, **kwargs: Any) -> JSON:
        """List all queries.

        List all queries.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "value": [
                        {
                            "id": "str",
                            "labels": {
                                "str": "str"
                            }
                        }
                    ]
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_analytics_queries_list_get_request(
            collaboration_id=collaboration_id,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_queries_document_id_get(self, collaboration_id: str, document_id: str, **kwargs: Any) -> JSON:
        """Get query by id.

        Get query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
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
                        "inputDatasets": "str",
                        "outputDataset": "str",
                        "queryData": [
                            {
                                "data": "str",
                                "executionSequence": 0,
                                "postFilters": "str",
                                "preConditions": "str"
                            }
                        ]
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_analytics_queries_document_id_get_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @overload
    async def analytics_queries_document_id_vote_post(
        self,
        collaboration_id: str,
        document_id: str,
        body: Optional[JSON] = None,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Optional[JSON]:
        """Vote on query by id.

        Vote on query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Default value is None.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: JSON object or None
        :rtype: JSON or None
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "proposalId": "str",
                    "voteAction": "str"
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
    async def analytics_queries_document_id_vote_post(
        self,
        collaboration_id: str,
        document_id: str,
        body: Optional[IO[bytes]] = None,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> Optional[JSON]:
        """Vote on query by id.

        Vote on query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Default value is None.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: JSON object or None
        :rtype: JSON or None
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
    async def analytics_queries_document_id_vote_post(
        self, collaboration_id: str, document_id: str, body: Optional[Union[JSON, IO[bytes]]] = None, **kwargs: Any
    ) -> Optional[JSON]:
        """Vote on query by id.

        Vote on query by id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :param body: Is either a JSON type or a IO[bytes] type. Default value is None.
        :type body: JSON or IO[bytes]
        :return: JSON object or None
        :rtype: JSON or None
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "proposalId": "str",
                    "voteAction": "str"
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        content_type = content_type if body else None
        cls: ClsType[Optional[JSON]] = kwargs.pop("cls", None)

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

        _request = build_collaboration_analytics_queries_document_id_vote_post_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            content_type=content_type,
            api_version=self._config.api_version,
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

        if response.status_code not in [204, 422]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        deserialized = None
        if response.status_code == 422:
            if response.content:
                deserialized = response.json()
            else:
                deserialized = None

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore

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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
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
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_runs_job_id_get(self, collaboration_id: str, job_id: str, **kwargs: Any) -> JSON:
        """Get query run result by job id.

        Get query run result by job id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param job_id: Required.
        :type job_id: str
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_analytics_runs_job_id_get_request(
            collaboration_id=collaboration_id,
            job_id=job_id,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_queries_document_id_runs_get(
        self, collaboration_id: str, document_id: str, **kwargs: Any
    ) -> Union[list[JSON], JSON]:
        """Get query run history by query id.

        Get query run history by query id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
        :return: list of JSON object or JSON object
        :rtype: list[JSON] or JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == [
                    {
                        "queryId": "str",
                        "runs": [
                            {
                                "isSuccessful": bool,
                                "runId": "str",
                                "durationSeconds": 0.0,
                                "endTime": "2020-02-20 00:00:00",
                                "error": {
                                    "code": "str",
                                    "message": "str"
                                },
                                "startTime": "2020-02-20 00:00:00",
                                "stats": {
                                    "rowsRead": 0,
                                    "rowsWritten": 0
                                }
                            }
                        ],
                        "latestRun": {
                            "isSuccessful": bool,
                            "runId": "str",
                            "durationSeconds": 0.0,
                            "endTime": "2020-02-20 00:00:00",
                            "error": {
                                "code": "str",
                                "message": "str"
                            },
                            "startTime": "2020-02-20 00:00:00",
                            "stats": {
                                "rowsRead": 0,
                                "rowsWritten": 0
                            }
                        },
                        "summary": {
                            "avgDurationSeconds": 0.0,
                            "failedRuns": 0,
                            "successfulRuns": 0,
                            "totalRowsRead": 0,
                            "totalRowsWritten": 0,
                            "totalRuns": 0,
                            "totalRuntimeSeconds": 0.0
                        }
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[Union[list[JSON], JSON]] = kwargs.pop("cls", None)

        _request = build_collaboration_analytics_queries_document_id_runs_get_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(Union[list[JSON], JSON], deserialized), {})  # type: ignore

        return cast(Union[list[JSON], JSON], deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_datasets_document_id_queries_get(  # pylint: disable=name-too-long
        self, collaboration_id: str, document_id: str, **kwargs: Any
    ) -> Union[list[str], JSON]:
        """Get queries by dataset id.

        Get queries by dataset id.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param document_id: Required.
        :type document_id: str
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[Union[list[str], JSON]] = kwargs.pop("cls", None)

        _request = build_collaboration_analytics_datasets_document_id_queries_get_request(
            collaboration_id=collaboration_id,
            document_id=document_id,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(Union[list[str], JSON], deserialized), {})  # type: ignore

        return cast(Union[list[str], JSON], deserialized)  # type: ignore

    @overload
    async def analytics_secrets_secret_name_put(
        self,
        collaboration_id: str,
        secret_name: str,
        body: Optional[JSON] = None,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> JSON:
        """Set secret for analytics workload.

        Set secret for analytics workload.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param secret_name: Required.
        :type secret_name: str
        :param body: Default value is None.
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
                    "secretValue": "str"
                }

                # response body for status code(s): 200
                response == {
                    "secretId": "str"
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
    async def analytics_secrets_secret_name_put(
        self,
        collaboration_id: str,
        secret_name: str,
        body: Optional[IO[bytes]] = None,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> JSON:
        """Set secret for analytics workload.

        Set secret for analytics workload.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param secret_name: Required.
        :type secret_name: str
        :param body: Default value is None.
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
                    "secretId": "str"
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
    async def analytics_secrets_secret_name_put(
        self, collaboration_id: str, secret_name: str, body: Optional[Union[JSON, IO[bytes]]] = None, **kwargs: Any
    ) -> JSON:
        """Set secret for analytics workload.

        Set secret for analytics workload.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :param secret_name: Required.
        :type secret_name: str
        :param body: Is either a JSON type or a IO[bytes] type. Default value is None.
        :type body: JSON or IO[bytes]
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "secretValue": "str"
                }

                # response body for status code(s): 200
                response == {
                    "secretId": "str"
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

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        content_type = content_type if body else None
        cls: ClsType[JSON] = kwargs.pop("cls", None)

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

        _request = build_collaboration_analytics_secrets_secret_name_put_request(
            collaboration_id=collaboration_id,
            secret_name=secret_name,
            content_type=content_type,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore

    @distributed_trace_async
    async def analytics_auditevents_get(
        self,
        collaboration_id: str,
        *,
        scope: Optional[str] = None,
        from_seqno: Optional[str] = None,
        to_seqno: Optional[str] = None,
        **kwargs: Any
    ) -> JSON:
        """Get audit events for analytics workload.

        Get audit events for analytics workload.

        :param collaboration_id: Required.
        :type collaboration_id: str
        :keyword scope: The event scope to query. Default value is None.
        :paramtype scope: str
        :keyword from_seqno: Start of the ledger sequence number range. Default value is None.
        :paramtype from_seqno: str
        :keyword to_seqno: End of the ledger sequence number range. Default value is None.
        :paramtype to_seqno: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "nextLink": "str",
                    "value": [
                        {
                            "data": {
                                "message": "str",
                                "source": "str"
                            },
                            "id": "str",
                            "scope": "str",
                            "timestamp": "str",
                            "timestampIso": "str"
                        }
                    ]
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

        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[JSON] = kwargs.pop("cls", None)

        _request = build_collaboration_analytics_auditevents_get_request(
            collaboration_id=collaboration_id,
            scope=scope,
            from_seqno=from_seqno,
            to_seqno=to_seqno,
            api_version=self._config.api_version,
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
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if response.content:
            deserialized = response.json()
        else:
            deserialized = None

        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})  # type: ignore

        return cast(JSON, deserialized)  # type: ignore
