# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
import uuid
from abc import ABCMeta

from azure.common import (
    AzureHttpError,
    AzureMissingResourceHttpError,
)

from ..common._auth import (
    _StorageSASAuthentication,
    _StorageSharedKeyAuthentication,
    _StorageNoAuthentication,
)
from ..common._common_conversion import (
    _int_to_str,
    _to_str,
    _datetime_to_utc_string,
)
from ..common._connection import _ServiceParameters
from ..common._constants import (
    SERVICE_HOST_BASE,
    DEFAULT_PROTOCOL,
)
from ..common._deserialization import (
    _convert_xml_to_service_properties,
    _parse_metadata,
    _parse_properties,
    _convert_xml_to_service_stats,
    _parse_length_from_content_range,
)
from ..common._error import (
    _dont_fail_not_exist,
    _dont_fail_on_exist,
    _validate_not_none,
    _validate_decryption_required,
    _validate_access_policies,
    _ERROR_PARALLEL_NOT_SEEKABLE,
    _validate_user_delegation_key,
)
from ..common._http import HTTPRequest
from ..common._serialization import (
    _get_request_body,
    _convert_signed_identifiers_to_xml,
    _convert_service_properties_to_xml,
    _add_metadata_headers,
    _update_request, _add_date_header)
from ..common.models import (
    Services,
    ListGenerator,
    _OperationContext,
    LocationMode,
)
from .sharedaccesssignature import (
    BlobSharedAccessSignature,
)
from ..common.storageclient import StorageClient
from ._deserialization import (
    _convert_xml_to_containers,
    _parse_blob,
    _convert_xml_to_blob_list,
    _convert_xml_to_blob_name_list,
    _parse_container,
    _parse_snapshot_blob,
    _parse_lease,
    _convert_xml_to_signed_identifiers_and_access,
    _parse_base_properties,
    _parse_account_information,
    _convert_xml_to_user_delegation_key,
    _ingest_batch_response,
    _parse_continuation_token,
    _parse_path_permission_and_acl,
)
from ._download_chunking import _download_blob_chunks
from ._error import (
    _ERROR_INVALID_LEASE_DURATION,
    _ERROR_INVALID_LEASE_BREAK_PERIOD,
)
from ._serialization import (
    _get_path,
    _validate_and_format_range_headers,
    _convert_delegation_key_info_to_xml,
    _get_batch_request_delimiter,
    _serialize_batch_body,
    _validate_and_add_cpk_headers,
    _add_file_or_directory_properties_header,
)
from .models import (
    BlobProperties,
    _LeaseActions,
    ContainerPermissions,
    BlobPermissions,
)

from ._constants import (
    X_MS_VERSION,
    __version__ as package_version,
    _BLOB_SERVICE_PUBLIC_CLOUD_HOST,
    _DFS_SERVICE_PUBLIC_CLOUD_HOST,
)

_CONTAINER_ALREADY_EXISTS_ERROR_CODE = 'ContainerAlreadyExists'
_BLOB_NOT_FOUND_ERROR_CODE = 'BlobNotFound'
_CONTAINER_NOT_FOUND_ERROR_CODE = 'ContainerNotFound'
_PATH_NOT_FOUND_ERROR_CODE = 'PathNotFound'

if sys.version_info >= (3,):
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO


class BaseBlobService(StorageClient):
    '''
    This is the main class managing Blob resources.

    The Blob service stores text and binary data as blobs in the cloud.
    The Blob service offers the following three resources: the storage account,
    containers, and blobs. Within your storage account, containers provide a
    way to organize sets of blobs. For more information please see:
    https://msdn.microsoft.com/en-us/library/azure/ee691964.aspx

    :ivar int MAX_SINGLE_GET_SIZE:
        The size of the first range get performed by get_blob_to_* methods if
        max_connections is greater than 1. Less data will be returned if the
        blob is smaller than this.
    :ivar int MAX_CHUNK_GET_SIZE:
        The size of subsequent range gets performed by get_blob_to_* methods if
        max_connections is greater than 1 and the blob is larger than MAX_SINGLE_GET_SIZE.
        Less data will be returned if the remainder of the blob is smaller than
        this. If this is set to larger than 4MB, content_validation will throw an
        error if enabled. However, if content_validation is not desired a size
        greater than 4MB may be optimal. Setting this below 4MB is not recommended.
    :ivar object key_encryption_key:
        The key-encryption-key optionally provided by the user. If provided, will be used to
        encrypt/decrypt in supported methods.
        For methods requiring decryption, either the key_encryption_key OR the resolver must be provided.
        If both are provided, the resolver will take precedence.
        Must implement the following methods for APIs requiring encryption:
        wrap_key(key)--wraps the specified key (bytes) using an algorithm of the user's choice. Returns the encrypted key as bytes.
        get_key_wrap_algorithm()--returns the algorithm used to wrap the specified symmetric key.
        get_kid()--returns a string key id for this key-encryption-key.
        Must implement the following methods for APIs requiring decryption:
        unwrap_key(key, algorithm)--returns the unwrapped form of the specified symmetric key using the string-specified algorithm.
        get_kid()--returns a string key id for this key-encryption-key.
    :ivar function key_resolver_function(kid):
        A function to resolve keys optionally provided by the user. If provided, will be used to decrypt in supported methods.
        For methods requiring decryption, either the key_encryption_key OR
        the resolver must be provided. If both are provided, the resolver will take precedence.
        It uses the kid string to return a key-encryption-key implementing the interface defined above.
    :ivar bool require_encryption:
        A flag that may be set to ensure that all messages successfully uploaded to the queue and all those downloaded and
        successfully read from the queue are/were encrypted while on the server. If this flag is set, all required
        parameters for encryption/decryption must be provided. See the above comments on the key_encryption_key and resolver.
    '''

    __metaclass__ = ABCMeta
    MAX_SINGLE_GET_SIZE = 32 * 1024 * 1024
    MAX_CHUNK_GET_SIZE = 4 * 1024 * 1024

    def __init__(self, account_name=None, account_key=None, sas_token=None, is_emulated=False,
                 protocol=DEFAULT_PROTOCOL, endpoint_suffix=SERVICE_HOST_BASE, custom_domain=None, request_session=None,
                 connection_string=None, socket_timeout=None, token_credential=None):
        '''
        :param str account_name:
            The storage account name. This is used to authenticate requests 
            signed with an account key and to construct the storage endpoint. It 
            is required unless a connection string is given, or if a custom 
            domain is used with anonymous authentication.
        :param str account_key:
            The storage account key. This is used for shared key authentication. 
            If neither account key or sas token is specified, anonymous access 
            will be used.
        :param str sas_token:
             A shared access signature token to use to authenticate requests 
             instead of the account key. If account key and sas token are both 
             specified, account key will be used to sign. If neither are 
             specified, anonymous access will be used.
        :param bool is_emulated:
            Whether to use the emulator. Defaults to False. If specified, will 
            override all other parameters besides connection string and request 
            session.
        :param str protocol:
            The protocol to use for requests. Defaults to https.
        :param str endpoint_suffix:
            The host base component of the url, minus the account name. Defaults 
            to Azure (core.windows.net). Override this to use the China cloud 
            (core.chinacloudapi.cn).
        :param str custom_domain:
            The custom domain to use. This can be set in the Azure Portal. For 
            example, 'www.mydomain.com'.
        :param requests.Session request_session:
            The session object to use for http requests.
        :param str connection_string:
            If specified, this will override all other parameters besides 
            request session. See
            http://azure.microsoft.com/en-us/documentation/articles/storage-configure-connection-string/
            for the connection string format
        :param int socket_timeout:
            If specified, this will override the default socket timeout. The timeout specified is in seconds.
            See DEFAULT_SOCKET_TIMEOUT in _constants.py for the default value.
        :param token_credential:
            A token credential used to authenticate HTTPS requests. The token value
            should be updated before its expiration.
        :type `~..common.TokenCredential`
        '''
        service_params = _ServiceParameters.get_service_parameters(
            'blob',
            account_name=account_name,
            account_key=account_key,
            sas_token=sas_token,
            token_credential=token_credential,
            is_emulated=is_emulated,
            protocol=protocol,
            endpoint_suffix=endpoint_suffix,
            custom_domain=custom_domain,
            request_session=request_session,
            connection_string=connection_string,
            socket_timeout=socket_timeout)

        super(BaseBlobService, self).__init__(service_params)

        if self.account_key:
            self.authentication = _StorageSharedKeyAuthentication(
                self.account_name,
                self.account_key,
                self.is_emulated
            )
        elif self.sas_token:
            self.authentication = _StorageSASAuthentication(self.sas_token)
        elif self.token_credential:
            self.authentication = self.token_credential
        else:
            self.authentication = _StorageNoAuthentication()

        self.require_encryption = False
        self.key_encryption_key = None
        self.key_resolver_function = None
        self._X_MS_VERSION = X_MS_VERSION
        self._update_user_agent_string(package_version)

    def make_blob_url(self, container_name, blob_name, protocol=None, sas_token=None, snapshot=None):
        '''
        Creates the url to access a blob.

        :param str container_name:
            Name of container.
        :param str blob_name:
            Name of blob.
        :param str protocol:
            Protocol to use: 'http' or 'https'. If not specified, uses the
            protocol specified when BaseBlobService was initialized.
        :param str sas_token:
            Shared access signature token created with
            generate_shared_access_signature.
        :param str snapshot:
            An string value that uniquely identifies the snapshot. The value of
            this query parameter indicates the snapshot version.
        :return: blob access URL.
        :rtype: str
        '''

        url = '{}://{}/{}/{}'.format(
            protocol or self.protocol,
            self.primary_endpoint,
            container_name,
            blob_name,
        )

        if snapshot and sas_token:
            url = '{}?snapshot={}&{}'.format(url, snapshot, sas_token)
        elif snapshot:
            url = '{}?snapshot={}'.format(url, snapshot)
        elif sas_token:
            url = '{}?{}'.format(url, sas_token)

        return url

    def make_container_url(self, container_name, protocol=None, sas_token=None):
        '''
        Creates the url to access a container.

        :param str container_name:
            Name of container.
        :param str protocol:
            Protocol to use: 'http' or 'https'. If not specified, uses the
            protocol specified when BaseBlobService was initialized.
        :param str sas_token:
            Shared access signature token created with
            generate_shared_access_signature.
        :return: container access URL.
        :rtype: str
        '''

        url = '{}://{}/{}?restype=container'.format(
            protocol or self.protocol,
            self.primary_endpoint,
            container_name,
        )

        if sas_token:
            url = '{}&{}'.format(url, sas_token)

        return url

    def generate_account_shared_access_signature(self, resource_types, permission,
                                                 expiry, start=None, ip=None, protocol=None):
        '''
        Generates a shared access signature for the blob service.
        Use the returned signature with the sas_token parameter of any BlobService.

        :param ResourceTypes resource_types:
            Specifies the resource types that are accessible with the account SAS.
        :param AccountPermissions permission:
            The permissions associated with the shared access signature. The 
            user is restricted to operations allowed by the permissions. 
            Required unless an id is given referencing a stored access policy 
            which contains this field. This field must be omitted if it has been 
            specified in an associated stored access policy.
        :param expiry:
            The time at which the shared access signature becomes invalid. 
            Required unless an id is given referencing a stored access policy 
            which contains this field. This field must be omitted if it has 
            been specified in an associated stored access policy. Azure will always 
            convert values to UTC. If a date is passed in without timezone info, it 
            is assumed to be UTC.
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If 
            omitted, start time for this call is assumed to be the time when the 
            storage service receives the request. Azure will always convert values 
            to UTC. If a date is passed in without timezone info, it is assumed to 
            be UTC.
        :type start: datetime or str
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~..common.models.Protocol` for possible values.
        :return: A Shared Access Signature (sas) token.
        :rtype: str
        '''
        _validate_not_none('self.account_name', self.account_name)
        _validate_not_none('self.account_key', self.account_key)

        sas = BlobSharedAccessSignature(self.account_name, self.account_key)
        return sas.generate_account(Services.BLOB, resource_types, permission,
                                    expiry, start=start, ip=ip, protocol=protocol)

    def generate_container_shared_access_signature(self, container_name,
                                                   permission=None, expiry=None,
                                                   start=None, id=None, ip=None, protocol=None,
                                                   cache_control=None, content_disposition=None,
                                                   content_encoding=None, content_language=None,
                                                   content_type=None, user_delegation_key=None):
        '''
        Generates a shared access signature for the container.
        Use the returned signature with the sas_token parameter of any BlobService.

        :param str container_name:
            Name of container.
        :param ContainerPermissions permission:
            The permissions associated with the shared access signature. The 
            user is restricted to operations allowed by the permissions.
            Permissions must be ordered read, write, delete, list.
            Required unless an id is given referencing a stored access policy 
            which contains this field. This field must be omitted if it has been 
            specified in an associated stored access policy.
        :param expiry:
            The time at which the shared access signature becomes invalid. 
            Required unless an id is given referencing a stored access policy 
            which contains this field. This field must be omitted if it has 
            been specified in an associated stored access policy. Azure will always 
            convert values to UTC. If a date is passed in without timezone info, it 
            is assumed to be UTC.
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If 
            omitted, start time for this call is assumed to be the time when the 
            storage service receives the request. Azure will always convert values 
            to UTC. If a date is passed in without timezone info, it is assumed to 
            be UTC.
        :type start: datetime or str
        :param str id:
            A unique value up to 64 characters in length that correlates to a 
            stored access policy. To create a stored access policy, use 
            set_blob_service_properties.
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~..common.models.Protocol` for possible values.
        :param str cache_control:
            Response header value for Cache-Control when resource is accessed
            using this shared access signature.
        :param str content_disposition:
            Response header value for Content-Disposition when resource is accessed
            using this shared access signature.
        :param str content_encoding:
            Response header value for Content-Encoding when resource is accessed
            using this shared access signature.
        :param str content_language:
            Response header value for Content-Language when resource is accessed
            using this shared access signature.
        :param str content_type:
            Response header value for Content-Type when resource is accessed
            using this shared access signature.
        :param ~azure.storage.blob.models.UserDelegationKey user_delegation_key:
            Instead of an account key, the user could pass in a user delegation key.
            A user delegation key can be obtained from the service by authenticating with an AAD identity;
            this can be accomplished by calling get_user_delegation_key.
            When present, the SAS is signed with the user delegation key instead.
        :return: A Shared Access Signature (sas) token.
        :rtype: str
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('self.account_name', self.account_name)

        if user_delegation_key is not None:
            _validate_user_delegation_key(user_delegation_key)
            sas = BlobSharedAccessSignature(self.account_name, user_delegation_key=user_delegation_key)
        else:
            _validate_not_none('self.account_key', self.account_key)
            sas = BlobSharedAccessSignature(self.account_name, account_key=self.account_key)

        return sas.generate_container(
            container_name,
            permission,
            expiry,
            start=start,
            id=id,
            ip=ip,
            protocol=protocol,
            cache_control=cache_control,
            content_disposition=content_disposition,
            content_encoding=content_encoding,
            content_language=content_language,
            content_type=content_type,
        )

    def generate_blob_shared_access_signature(
            self, container_name, blob_name, snapshot=None, permission=None,
            expiry=None, start=None, id=None, ip=None, protocol=None,
            cache_control=None, content_disposition=None,
            content_encoding=None, content_language=None,
            content_type=None, user_delegation_key=None):
        '''
        Generates a shared access signature for the blob or one of its snapshots.
        Use the returned signature with the sas_token parameter of any BlobService.

        :param str container_name:
            Name of container.
        :param str blob_name:
            Name of blob.
        :param str snapshot:
            The snapshot parameter is an opaque DateTime value that,
            when present, specifies the blob snapshot to grant permission.
        :param BlobPermissions permission:
            The permissions associated with the shared access signature. The 
            user is restricted to operations allowed by the permissions.
            Permissions must be ordered read, write, delete, list.
            Required unless an id is given referencing a stored access policy 
            which contains this field. This field must be omitted if it has been 
            specified in an associated stored access policy.
        :param expiry:
            The time at which the shared access signature becomes invalid. 
            Required unless an id is given referencing a stored access policy 
            which contains this field. This field must be omitted if it has 
            been specified in an associated stored access policy. Azure will always 
            convert values to UTC. If a date is passed in without timezone info, it 
            is assumed to be UTC.
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If 
            omitted, start time for this call is assumed to be the time when the 
            storage service receives the request. Azure will always convert values 
            to UTC. If a date is passed in without timezone info, it is assumed to 
            be UTC.
        :type start: datetime or str
        :param str id:
            A unique value up to 64 characters in length that correlates to a 
            stored access policy. To create a stored access policy, use :func:`~set_container_acl`.
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~..common.models.Protocol` for possible values.
        :param str cache_control:
            Response header value for Cache-Control when resource is accessed
            using this shared access signature.
        :param str content_disposition:
            Response header value for Content-Disposition when resource is accessed
            using this shared access signature.
        :param str content_encoding:
            Response header value for Content-Encoding when resource is accessed
            using this shared access signature.
        :param str content_language:
            Response header value for Content-Language when resource is accessed
            using this shared access signature.
        :param str content_type:
            Response header value for Content-Type when resource is accessed
            using this shared access signature.
        :param ~azure.storage.blob.models.UserDelegationKey user_delegation_key:
            Instead of an account key, the user could pass in a user delegation key.
            A user delegation key can be obtained from the service by authenticating with an AAD identity;
            this can be accomplished by calling get_user_delegation_key.
            When present, the SAS is signed with the user delegation key instead.
        :return: A Shared Access Signature (sas) token.
        :rtype: str
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('self.account_name', self.account_name)

        if user_delegation_key is not None:
            _validate_user_delegation_key(user_delegation_key)
            sas = BlobSharedAccessSignature(self.account_name, user_delegation_key=user_delegation_key)
        else:
            _validate_not_none('self.account_key', self.account_key)
            sas = BlobSharedAccessSignature(self.account_name, account_key=self.account_key)

        return sas.generate_blob(
            container_name=container_name,
            blob_name=blob_name,
            snapshot=snapshot,
            permission=permission,
            expiry=expiry,
            start=start,
            id=id,
            ip=ip,
            protocol=protocol,
            cache_control=cache_control,
            content_disposition=content_disposition,
            content_encoding=content_encoding,
            content_language=content_language,
            content_type=content_type,
        )

    def get_user_delegation_key(self, key_start_time, key_expiry_time, timeout=None):
        """
        Obtain a user delegation key for the purpose of signing SAS tokens.
        A token credential must be present on the service object for this request to succeed.

        :param datetime key_start_time:
            A DateTime value. Indicates when the key becomes valid.
        :param datetime key_expiry_time:
            A DateTime value. Indicates when the key stops being valid.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: The user delegation key.
        :rtype: ~azure.storage.blob.models.UserDelegationKey
        """
        _validate_not_none('key_start_time', key_start_time)
        _validate_not_none('key_end_time', key_expiry_time)

        request = HTTPRequest()
        request.method = 'POST'
        request.host_locations = self._get_host_locations(secondary=True)
        request.query = {
            'restype': 'service',
            'comp': 'userdelegationkey',
            'timeout': _int_to_str(timeout),
        }
        request.body = _get_request_body(_convert_delegation_key_info_to_xml(key_start_time, key_expiry_time))
        return self._perform_request(request, _convert_xml_to_user_delegation_key)

    def list_containers(self, prefix=None, num_results=None, include_metadata=False,
                        marker=None, timeout=None):
        '''
        Returns a generator to list the containers under the specified account.
        The generator will lazily follow the continuation tokens returned by
        the service and stop when all containers have been returned or num_results is reached.

        If num_results is specified and the account has more than that number of 
        containers, the generator will have a populated next_marker field once it 
        finishes. This marker can be used to create a new generator if more 
        results are desired.

        :param str prefix:
            Filters the results to return only containers whose names
            begin with the specified prefix.
        :param int num_results:
            Specifies the maximum number of containers to return. A single list
            request may return up to 1000 contianers and potentially a continuation
            token which should be followed to get additional resutls.
        :param bool include_metadata:
            Specifies that container metadata be returned in the response.
        :param str marker:
            An opaque continuation token. This value can be retrieved from the 
            next_marker field of a previous generator object if num_results was 
            specified and that generator has finished enumerating results. If 
            specified, this generator will begin returning results from the point 
            where the previous generator stopped.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        '''
        include = 'metadata' if include_metadata else None
        operation_context = _OperationContext(location_lock=True)
        kwargs = {'prefix': prefix, 'marker': marker, 'max_results': num_results,
                  'include': include, 'timeout': timeout, '_context': operation_context}
        resp = self._list_containers(**kwargs)

        return ListGenerator(resp, self._list_containers, (), kwargs)

    def _list_containers(self, prefix=None, marker=None, max_results=None,
                         include=None, timeout=None, _context=None):
        '''
        Returns a list of the containers under the specified account.

        :param str prefix:
            Filters the results to return only containers whose names
            begin with the specified prefix.
        :param str marker:
            A string value that identifies the portion of the list
            to be returned with the next list operation. The operation returns
            a next_marker value within the response body if the list returned was
            not complete. The marker value may then be used in a subsequent
            call to request the next set of list items. The marker value is
            opaque to the client.
        :param int max_results:
            Specifies the maximum number of containers to return. A single list
            request may return up to 1000 contianers and potentially a continuation
            token which should be followed to get additional resutls.
        :param str include:
            Include this parameter to specify that the container's
            metadata be returned as part of the response body. set this
            parameter to string 'metadata' to get container's metadata.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        '''
        request = HTTPRequest()
        request.method = 'GET'
        request.host_locations = self._get_host_locations(secondary=True)
        request.path = _get_path()
        request.query = {
            'comp': 'list',
            'prefix': _to_str(prefix),
            'marker': _to_str(marker),
            'maxresults': _int_to_str(max_results),
            'include': _to_str(include),
            'timeout': _int_to_str(timeout)
        }

        return self._perform_request(request, _convert_xml_to_containers, operation_context=_context)

    def create_container(self, container_name, metadata=None,
                         public_access=None, fail_on_exist=False, timeout=None):
        '''
        Creates a new container under the specified account. If the container
        with the same name already exists, the operation fails if
        fail_on_exist is True.

        :param str container_name:
            Name of container to create.
            The container name may only contain lowercase letters, numbers, and hyphens, and must begin with a letter or
            a number. Each hyphen must be preceded and followed by a non-hyphen character. The name must also be
            between 3 and 63 characters long.
        :param metadata:
            A dict with name_value pairs to associate with the
            container as metadata. Example:{'Category':'test'}
        :type metadata: dict(str, str)
        :param ~azure.storage.blob.models.PublicAccess public_access:
            Possible values include: container, blob.
        :param bool fail_on_exist:
            Specify whether to throw an exception when the container exists.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: True if container is created, False if container already exists.
        :rtype: bool
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name)
        request.query = {
            'restype': 'container',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-blob-public-access': _to_str(public_access)
        }
        _add_metadata_headers(metadata, request)

        if not fail_on_exist:
            try:
                self._perform_request(request, expected_errors=[_CONTAINER_ALREADY_EXISTS_ERROR_CODE])
                return True
            except AzureHttpError as ex:
                _dont_fail_on_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def get_container_properties(self, container_name, lease_id=None, timeout=None):
        '''
        Returns all user-defined metadata and system properties for the specified
        container. The data returned does not include the container's list of blobs.

        :param str container_name:
            Name of existing container.
        :param str lease_id:
            If specified, get_container_properties only succeeds if the
            container's lease is active and matches this ID.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: properties for the specified container within a container object.
        :rtype: :class:`~azure.storage.blob.models.Container`
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host_locations = self._get_host_locations(secondary=True)
        request.path = _get_path(container_name)
        request.query = {
            'restype': 'container',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {'x-ms-lease-id': _to_str(lease_id)}

        return self._perform_request(request, _parse_container, [container_name])

    def get_container_metadata(self, container_name, lease_id=None, timeout=None):
        '''
        Returns all user-defined metadata for the specified container.

        :param str container_name:
            Name of existing container.
        :param str lease_id:
            If specified, get_container_metadata only succeeds if the
            container's lease is active and matches this ID.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return:
            A dictionary representing the container metadata name, value pairs.
        :rtype: dict(str, str)
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host_locations = self._get_host_locations(secondary=True)
        request.path = _get_path(container_name)
        request.query = {
            'restype': 'container',
            'comp': 'metadata',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {'x-ms-lease-id': _to_str(lease_id)}

        return self._perform_request(request, _parse_metadata)

    def set_container_metadata(self, container_name, metadata=None,
                               lease_id=None, if_modified_since=None, timeout=None):
        '''
        Sets one or more user-defined name-value pairs for the specified
        container. Each call to this operation replaces all existing metadata
        attached to the container. To remove all metadata from the container,
        call this operation with no metadata dict.

        :param str container_name:
            Name of existing container.
        :param metadata:
            A dict containing name-value pairs to associate with the container as 
            metadata. Example: {'category':'test'}
        :type metadata: dict(str, str)
        :param str lease_id:
            If specified, set_container_metadata only succeeds if the
            container's lease is active and matches this ID.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: ETag and last modified properties for the updated Container
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name)
        request.query = {
            'restype': 'container',
            'comp': 'metadata',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'x-ms-lease-id': _to_str(lease_id),
        }
        _add_metadata_headers(metadata, request)

        return self._perform_request(request, _parse_base_properties)

    def get_container_acl(self, container_name, lease_id=None, timeout=None):
        '''
        Gets the permissions for the specified container.
        The permissions indicate whether container data may be accessed publicly.

        :param str container_name:
            Name of existing container.
        :param lease_id:
            If specified, get_container_acl only succeeds if the
            container's lease is active and matches this ID.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: A dictionary of access policies associated with the container. dict of str to
            :class:`..common.models.AccessPolicy` and a public_access property
            if public access is turned on
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host_locations = self._get_host_locations(secondary=True)
        request.path = _get_path(container_name)
        request.query = {
            'restype': 'container',
            'comp': 'acl',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {'x-ms-lease-id': _to_str(lease_id)}

        return self._perform_request(request, _convert_xml_to_signed_identifiers_and_access)

    def set_container_acl(self, container_name, signed_identifiers=None,
                          public_access=None, lease_id=None,
                          if_modified_since=None, if_unmodified_since=None, timeout=None):
        '''
        Sets the permissions for the specified container or stored access 
        policies that may be used with Shared Access Signatures. The permissions
        indicate whether blobs in a container may be accessed publicly.

        :param str container_name:
            Name of existing container.
        :param signed_identifiers:
            A dictionary of access policies to associate with the container. The 
            dictionary may contain up to 5 elements. An empty dictionary 
            will clear the access policies set on the service. 
        :type signed_identifiers: dict(str, :class:`~..common.models.AccessPolicy`)
        :param ~azure.storage.blob.models.PublicAccess public_access:
            Possible values include: container, blob.
        :param str lease_id:
            If specified, set_container_acl only succeeds if the
            container's lease is active and matches this ID.
        :param datetime if_modified_since:
            A datetime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified date/time.
        :param datetime if_unmodified_since:
            A datetime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: ETag and last modified properties for the updated Container
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_access_policies(signed_identifiers)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name)
        request.query = {
            'restype': 'container',
            'comp': 'acl',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-blob-public-access': _to_str(public_access),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'x-ms-lease-id': _to_str(lease_id),
        }
        request.body = _get_request_body(
            _convert_signed_identifiers_to_xml(signed_identifiers))

        return self._perform_request(request, _parse_base_properties)

    def delete_container(self, container_name, fail_not_exist=False,
                         lease_id=None, if_modified_since=None,
                         if_unmodified_since=None, timeout=None):
        '''
        Marks the specified container for deletion. The container and any blobs
        contained within it are later deleted during garbage collection.

        :param str container_name:
            Name of container to delete.
        :param bool fail_not_exist:
            Specify whether to throw an exception when the container doesn't
            exist.
        :param str lease_id:
            If specified, delete_container only succeeds if the
            container's lease is active and matches this ID.
            Required if the container has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: True if container is deleted, False container doesn't exist.
        :rtype: bool
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name)
        request.query = {
            'restype': 'container',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
        }

        if not fail_not_exist:
            try:
                self._perform_request(request, expected_errors=[_CONTAINER_NOT_FOUND_ERROR_CODE])
                return True
            except AzureHttpError as ex:
                _dont_fail_not_exist(ex)
                return False
        else:
            self._perform_request(request)
            return True

    def _lease_container_impl(
            self, container_name, lease_action, lease_id, lease_duration,
            lease_break_period, proposed_lease_id, if_modified_since,
            if_unmodified_since, timeout):
        '''
        Establishes and manages a lease on a container.
        The Lease Container operation can be called in one of five modes
            Acquire, to request a new lease
            Renew, to renew an existing lease
            Change, to change the ID of an existing lease
            Release, to free the lease if it is no longer needed so that another
                client may immediately acquire a lease against the container
            Break, to end the lease but ensure that another client cannot acquire
                a new lease until the current lease period has expired

        :param str container_name:
            Name of existing container.
        :param str lease_action:
            Possible _LeaseActions values: acquire|renew|release|break|change
        :param str lease_id:
            Required if the container has an active lease.
        :param int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change. For backwards compatibility, the default is
            60, and the value is only used on an acquire operation.
        :param int lease_break_period:
            For a break operation, this is the proposed duration of
            seconds that the lease should continue before it is broken, between
            0 and 60 seconds. This break period is only used if it is shorter
            than the time remaining on the lease. If longer, the time remaining
            on the lease is used. A new lease will not be available before the
            break period has expired, but the lease may be held for longer than
            the break period. If this header does not appear with a break
            operation, a fixed-duration lease breaks after the remaining lease
            period elapses, and an infinite lease breaks immediately.
        :param str proposed_lease_id:
            Optional for Acquire, required for Change. Proposed lease ID, in a
            GUID string format. The Blob service returns 400 (Invalid request)
            if the proposed lease ID is not in the correct format.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return:
            Response headers returned from the service call.
        :rtype: dict(str, str)
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('lease_action', lease_action)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name)
        request.query = {
            'restype': 'container',
            'comp': 'lease',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'x-ms-lease-action': _to_str(lease_action),
            'x-ms-lease-duration': _to_str(lease_duration),
            'x-ms-lease-break-period': _to_str(lease_break_period),
            'x-ms-proposed-lease-id': _to_str(proposed_lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
        }

        return self._perform_request(request, _parse_lease)

    def acquire_container_lease(
            self, container_name, lease_duration=-1, proposed_lease_id=None,
            if_modified_since=None, if_unmodified_since=None, timeout=None):
        '''
        Requests a new lease. If the container does not have an active lease,
        the Blob service creates a lease on the container and returns a new
        lease ID.

        :param str container_name:
            Name of existing container.
        :param int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change. Default is -1 (infinite lease).
        :param str proposed_lease_id:
            Proposed lease ID, in a GUID string format. The Blob service returns
            400 (Invalid request) if the proposed lease ID is not in the correct format.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: the lease ID of the newly created lease.
        :return: str
        '''
        _validate_not_none('lease_duration', lease_duration)
        if lease_duration is not -1 and \
                (lease_duration < 15 or lease_duration > 60):
            raise ValueError(_ERROR_INVALID_LEASE_DURATION)

        lease = self._lease_container_impl(container_name,
                                           _LeaseActions.Acquire,
                                           None,  # lease_id
                                           lease_duration,
                                           None,  # lease_break_period
                                           proposed_lease_id,
                                           if_modified_since,
                                           if_unmodified_since,
                                           timeout)
        return lease['id']

    def renew_container_lease(
            self, container_name, lease_id, if_modified_since=None,
            if_unmodified_since=None, timeout=None):
        '''
        Renews the lease. The lease can be renewed if the lease ID specified
        matches that associated with the container. Note that
        the lease may be renewed even if it has expired as long as the container
        has not been leased again since the expiration of that lease. When you
        renew a lease, the lease duration clock resets.
        
        :param str container_name:
            Name of existing container.
        :param str lease_id:
            Lease ID for active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: the lease ID of the renewed lease.
        :return: str
        '''
        _validate_not_none('lease_id', lease_id)

        lease = self._lease_container_impl(container_name,
                                           _LeaseActions.Renew,
                                           lease_id,
                                           None,  # lease_duration
                                           None,  # lease_break_period
                                           None,  # proposed_lease_id
                                           if_modified_since,
                                           if_unmodified_since,
                                           timeout)
        return lease['id']

    def release_container_lease(
            self, container_name, lease_id, if_modified_since=None,
            if_unmodified_since=None, timeout=None):
        '''
        Release the lease. The lease may be released if the lease_id specified matches
        that associated with the container. Releasing the lease allows another client
        to immediately acquire the lease for the container as soon as the release is complete. 

        :param str container_name:
            Name of existing container.
        :param str lease_id:
            Lease ID for active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        '''
        _validate_not_none('lease_id', lease_id)

        self._lease_container_impl(container_name,
                                   _LeaseActions.Release,
                                   lease_id,
                                   None,  # lease_duration
                                   None,  # lease_break_period
                                   None,  # proposed_lease_id
                                   if_modified_since,
                                   if_unmodified_since,
                                   timeout)

    def break_container_lease(
            self, container_name, lease_break_period=None,
            if_modified_since=None, if_unmodified_since=None, timeout=None):
        '''
        Break the lease, if the container has an active lease. Once a lease is
        broken, it cannot be renewed. Any authorized request can break the lease;
        the request is not required to specify a matching lease ID. When a lease
        is broken, the lease break period is allowed to elapse, during which time
        no lease operation except break and release can be performed on the container.
        When a lease is successfully broken, the response indicates the interval
        in seconds until a new lease can be acquired. 

        :param str container_name:
            Name of existing container.
        :param int lease_break_period:
            This is the proposed duration of seconds that the lease
            should continue before it is broken, between 0 and 60 seconds. This
            break period is only used if it is shorter than the time remaining
            on the lease. If longer, the time remaining on the lease is used.
            A new lease will not be available before the break period has
            expired, but the lease may be held for longer than the break
            period. If this header does not appear with a break
            operation, a fixed-duration lease breaks after the remaining lease
            period elapses, and an infinite lease breaks immediately.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: Approximate time remaining in the lease period, in seconds.
        :return: int
        '''
        if (lease_break_period is not None) and (lease_break_period < 0 or lease_break_period > 60):
            raise ValueError(_ERROR_INVALID_LEASE_BREAK_PERIOD)

        lease = self._lease_container_impl(container_name,
                                           _LeaseActions.Break,
                                           None,  # lease_id
                                           None,  # lease_duration
                                           lease_break_period,
                                           None,  # proposed_lease_id
                                           if_modified_since,
                                           if_unmodified_since,
                                           timeout)
        return lease['time']

    def change_container_lease(
            self, container_name, lease_id, proposed_lease_id,
            if_modified_since=None, if_unmodified_since=None, timeout=None):
        '''
        Change the lease ID of an active lease. A change must include the current
        lease ID and a new lease ID.

        :param str container_name:
            Name of existing container.
        :param str lease_id:
            Lease ID for active lease.
        :param str proposed_lease_id:
            Proposed lease ID, in a GUID string format. The Blob service returns 400
            (Invalid request) if the proposed lease ID is not in the correct format.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        '''
        _validate_not_none('lease_id', lease_id)

        self._lease_container_impl(container_name,
                                   _LeaseActions.Change,
                                   lease_id,
                                   None,  # lease_duration
                                   None,  # lease_break_period
                                   proposed_lease_id,
                                   if_modified_since,
                                   if_unmodified_since,
                                   timeout)

    def list_blobs(self, container_name, prefix=None, num_results=None, include=None,
                   delimiter=None, marker=None, timeout=None):
        '''
        Returns a generator to list the blobs under the specified container.
        The generator will lazily follow the continuation tokens returned by
        the service and stop when all blobs have been returned or num_results is reached.

        If num_results is specified and the account has more than that number of 
        blobs, the generator will have a populated next_marker field once it 
        finishes. This marker can be used to create a new generator if more 
        results are desired.

        :param str container_name:
            Name of existing container.
        :param str prefix:
            Filters the results to return only blobs whose names
            begin with the specified prefix.
        :param int num_results:
            Specifies the maximum number of blobs to return,
            including all :class:`BlobPrefix` elements. If the request does not specify
            num_results or specifies a value greater than 5,000, the server will
            return up to 5,000 items. Setting num_results to a value less than
            or equal to zero results in error response code 400 (Bad Request).
        :param ~azure.storage.blob.models.Include include:
            Specifies one or more additional datasets to include in the response.
        :param str delimiter:
            When the request includes this parameter, the operation
            returns a :class:`~azure.storage.blob.models.BlobPrefix` element in the
            result list that acts as a placeholder for all blobs whose names begin
            with the same substring up to the appearance of the delimiter character.
            The delimiter may be a single character or a string.
        :param str marker:
            An opaque continuation token. This value can be retrieved from the 
            next_marker field of a previous generator object if num_results was 
            specified and that generator has finished enumerating results. If 
            specified, this generator will begin returning results from the point 
            where the previous generator stopped.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        '''
        operation_context = _OperationContext(location_lock=True)
        args = (container_name,)
        kwargs = {'prefix': prefix, 'marker': marker, 'max_results': num_results,
                  'include': include, 'delimiter': delimiter, 'timeout': timeout,
                  '_context': operation_context,
                  '_converter': _convert_xml_to_blob_list}
        resp = self._list_blobs(*args, **kwargs)

        return ListGenerator(resp, self._list_blobs, args, kwargs)

    def list_blob_names(self, container_name, prefix=None, num_results=None,
                        include=None, delimiter=None, marker=None,
                        timeout=None):
        '''
        Returns a generator to list the blob names under the specified container.
        The generator will lazily follow the continuation tokens returned by
        the service and stop when all blobs have been returned or num_results is reached.

        If num_results is specified and the account has more than that number of 
        blobs, the generator will have a populated next_marker field once it 
        finishes. This marker can be used to create a new generator if more 
        results are desired.

        :param str container_name:
            Name of existing container.
        :param str prefix:
            Filters the results to return only blobs whose names
            begin with the specified prefix.
        :param int num_results:
            Specifies the maximum number of blobs to return,
            including all :class:`BlobPrefix` elements. If the request does not specify
            num_results or specifies a value greater than 5,000, the server will
            return up to 5,000 items. Setting num_results to a value less than
            or equal to zero results in error response code 400 (Bad Request).
        :param ~azure.storage.blob.models.Include include:
            Specifies one or more additional datasets to include in the response.
        :param str delimiter:
            When the request includes this parameter, the operation
            returns a :class:`~azure.storage.blob.models.BlobPrefix` element in the
            result list that acts as a placeholder for all blobs whose names begin
            with the same substring up to the appearance of the delimiter character.
            The delimiter may be a single character or a string.
        :param str marker:
            An opaque continuation token. This value can be retrieved from the 
            next_marker field of a previous generator object if num_results was 
            specified and that generator has finished enumerating results. If 
            specified, this generator will begin returning results from the point 
            where the previous generator stopped.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        '''
        operation_context = _OperationContext(location_lock=True)
        args = (container_name,)
        kwargs = {'prefix': prefix, 'marker': marker, 'max_results': num_results,
                  'include': include, 'delimiter': delimiter, 'timeout': timeout,
                  '_context': operation_context,
                  '_converter': _convert_xml_to_blob_name_list}
        resp = self._list_blobs(*args, **kwargs)

        return ListGenerator(resp, self._list_blobs, args, kwargs)

    def _list_blobs(self, container_name, prefix=None, marker=None,
                    max_results=None, include=None, delimiter=None, timeout=None,
                    _context=None, _converter=None):
        '''
        Returns the list of blobs under the specified container.

        :param str container_name:
            Name of existing container.
        :parm str prefix:
            Filters the results to return only blobs whose names
            begin with the specified prefix.
        :param str marker:
            A string value that identifies the portion of the list
            to be returned with the next list operation. The operation returns
            a next_marker value within the response body if the list returned was
            not complete. The marker value may then be used in a subsequent
            call to request the next set of list items. The marker value is
            opaque to the client.
        :param int max_results:
            Specifies the maximum number of blobs to return,
            including all :class:`~azure.storage.blob.models.BlobPrefix` elements. If the request does not specify
            max_results or specifies a value greater than 5,000, the server will
            return up to 5,000 items. Setting max_results to a value less than
            or equal to zero results in error response code 400 (Bad Request).
        :param str include:
            Specifies one or more datasets to include in the
            response. To specify more than one of these options on the URI,
            you must separate each option with a comma. Valid values are:
                snapshots:
                    Specifies that snapshots should be included in the
                    enumeration. Snapshots are listed from oldest to newest in
                    the response.
                metadata:
                    Specifies that blob metadata be returned in the response.
                uncommittedblobs:
                    Specifies that blobs for which blocks have been uploaded,
                    but which have not been committed using Put Block List
                    (REST API), be included in the response.
                copy:
                    Version 2012-02-12 and newer. Specifies that metadata
                    related to any current or previous Copy Blob operation
                    should be included in the response.
                deleted:
                    Version 2017-07-29 and newer. Specifies that soft deleted blobs
                    which are retained by the service should be included
                    in the response.
        :param str delimiter:
            When the request includes this parameter, the operation
            returns a :class:`~azure.storage.blob.models.BlobPrefix` element in the response body that acts as a
            placeholder for all blobs whose names begin with the same
            substring up to the appearance of the delimiter character. The
            delimiter may be a single character or a string.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        '''
        _validate_not_none('container_name', container_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host_locations = self._get_host_locations(secondary=True)
        request.path = _get_path(container_name)
        request.query = {
            'restype': 'container',
            'comp': 'list',
            'prefix': _to_str(prefix),
            'delimiter': _to_str(delimiter),
            'marker': _to_str(marker),
            'maxresults': _int_to_str(max_results),
            'include': _to_str(include),
            'timeout': _int_to_str(timeout),
        }

        return self._perform_request(request, _converter, operation_context=_context)

    def get_blob_account_information(self, container_name=None, blob_name=None, timeout=None):
        """
        Gets information related to the storage account.
        The information can also be retrieved if the user has a SAS to a container or blob.

        :param str container_name:
            Name of existing container.
            Optional, unless using a SAS token to a specific container or blob, in which case it's required.
        :param str blob_name:
            Name of existing blob.
            Optional, unless using a SAS token to a specific blob, in which case it's required.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: The :class:`~azure.storage.blob.models.AccountInformation`.
        """
        request = HTTPRequest()
        request.method = 'HEAD'
        request.host_locations = self._get_host_locations(secondary=True)
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'restype': 'account',
            'comp': 'properties',
            'timeout': _int_to_str(timeout),
        }

        return self._perform_request(request, _parse_account_information)

    def get_blob_service_stats(self, timeout=None):
        '''
        Retrieves statistics related to replication for the Blob service. It is 
        only available when read-access geo-redundant replication is enabled for 
        the storage account.

        With geo-redundant replication, Azure Storage maintains your data durable 
        in two locations. In both locations, Azure Storage constantly maintains 
        multiple healthy replicas of your data. The location where you read, 
        create, update, or delete data is the primary storage account location. 
        The primary location exists in the region you choose at the time you 
        create an account via the Azure Management Azure classic portal, for 
        example, North Central US. The location to which your data is replicated 
        is the secondary location. The secondary location is automatically 
        determined based on the location of the primary; it is in a second data 
        center that resides in the same region as the primary location. Read-only 
        access is available from the secondary location, if read-access geo-redundant 
        replication is enabled for your storage account.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: The blob service stats.
        :rtype: :class:`~..common.models.ServiceStats`
        '''
        request = HTTPRequest()
        request.method = 'GET'
        request.host_locations = self._get_host_locations(primary=False, secondary=True)
        request.path = _get_path()
        request.query = {
            'restype': 'service',
            'comp': 'stats',
            'timeout': _int_to_str(timeout),
        }

        return self._perform_request(request, _convert_xml_to_service_stats)

    def set_blob_service_properties(
            self, logging=None, hour_metrics=None, minute_metrics=None,
            cors=None, target_version=None, timeout=None, delete_retention_policy=None, static_website=None):
        '''
        Sets the properties of a storage account's Blob service, including
        Azure Storage Analytics. If an element (ex Logging) is left as None, the 
        existing settings on the service for that functionality are preserved.

        :param logging:
            Groups the Azure Analytics Logging settings.
        :type logging:
            :class:`~..common.models.Logging`
        :param hour_metrics:
            The hour metrics settings provide a summary of request 
            statistics grouped by API in hourly aggregates for blobs.
        :type hour_metrics:
            :class:`~..common.models.Metrics`
        :param minute_metrics:
            The minute metrics settings provide request statistics 
            for each minute for blobs.
        :type minute_metrics:
            :class:`~..common.models.Metrics`
        :param cors:
            You can include up to five CorsRule elements in the 
            list. If an empty list is specified, all CORS rules will be deleted, 
            and CORS will be disabled for the service.
        :type cors: list(:class:`~..common.models.CorsRule`)
        :param str target_version:
            Indicates the default version to use for requests if an incoming 
            request's version is not specified. 
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :param delete_retention_policy:
            The delete retention policy specifies whether to retain deleted blobs.
            It also specifies the number of days and versions of blob to keep.
        :type delete_retention_policy:
            :class:`~..common.models.DeleteRetentionPolicy`
        :param static_website:
            Specifies whether the static website feature is enabled,
            and if yes, indicates the index document and 404 error document to use.
        :type static_website:
            :class:`~..common.models.StaticWebsite`
        '''
        if all(parameter is None for parameter in [logging, hour_metrics, minute_metrics, cors, target_version,
                                                   delete_retention_policy, static_website]):
            raise ValueError("set_blob_service_properties should be called with at least one parameter")

        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path()
        request.query = {
            'restype': 'service',
            'comp': 'properties',
            'timeout': _int_to_str(timeout),
        }
        request.body = _get_request_body(
            _convert_service_properties_to_xml(logging, hour_metrics, minute_metrics,
                                               cors, target_version, delete_retention_policy, static_website))

        self._perform_request(request)

    def get_blob_service_properties(self, timeout=None):
        '''
        Gets the properties of a storage account's Blob service, including
        Azure Storage Analytics.

        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: The blob :class:`~..common.models.ServiceProperties` with an attached
            target_version property.
        '''
        request = HTTPRequest()
        request.method = 'GET'
        request.host_locations = self._get_host_locations(secondary=True)
        request.path = _get_path()
        request.query = {
            'restype': 'service',
            'comp': 'properties',
            'timeout': _int_to_str(timeout),
        }

        return self._perform_request(request, _convert_xml_to_service_properties)

    def get_blob_properties(
            self, container_name, blob_name, snapshot=None, lease_id=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None, timeout=None, cpk=None):
        '''
        Returns all user-defined metadata, standard HTTP properties, and
        system prdoperties for the blob. It does not return the content of the blob.
        Returns :class:`~azure.storage.blob.moels.Blob`
        with :class:`~azure.storage.blob.models.BlobProperties` and a metadata dict.
        
        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str snapshot:
            The snapshot parameter is an opaque DateTime value that,
            when present, specifies the blob snapshot to retrieve.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param ~azure.storage.blob.models.CustomerProvidedEncryptionKey cpk:
            Decrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: a blob object including properties and metadata.
        :rtype: :class:`~azure.storage.blob.models.Blob`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'HEAD'
        request.host_locations = self._get_host_locations(secondary=True)
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'snapshot': _to_str(snapshot),
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
        }
        _validate_and_add_cpk_headers(request, encryption_key=cpk, protocol=self.protocol)
        return self._perform_request(request, _parse_blob, [blob_name, snapshot])

    def set_blob_properties(
            self, container_name, blob_name, content_settings=None, lease_id=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None, timeout=None, cpk=None):
        '''
        Sets system properties on the blob. If one property is set for the
        content_settings, all properties will be overriden.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param ~azure.storage.blob.models.ContentSettings content_settings:
            ContentSettings object used to set blob properties.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param ~azure.storage.blob.models.CustomerProvidedEncryptionKey cpk:
            Encrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: ETag and last modified properties for the updated Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'properties',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
            'x-ms-lease-id': _to_str(lease_id)
        }
        _validate_and_add_cpk_headers(request, encryption_key=cpk, protocol=self.protocol)
        if content_settings is not None:
            request.headers.update(content_settings._to_headers())

        return self._perform_request(request, _parse_base_properties)

    def exists(self, container_name, blob_name=None, snapshot=None, timeout=None):
        '''
        Returns a boolean indicating whether the container exists (if blob_name 
        is None), or otherwise a boolean indicating whether the blob exists.

        :param str container_name:
            Name of a container.
        :param str blob_name:
            Name of a blob. If None, the container will be checked for existence.
        :param str snapshot:
            The snapshot parameter is an opaque DateTime value that,
            when present, specifies the snapshot.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: A boolean indicating whether the resource exists.
        :rtype: bool
        '''
        _validate_not_none('container_name', container_name)
        try:
            # make head request to see if container/blob/snapshot exists
            request = HTTPRequest()
            request.method = 'GET' if blob_name is None else 'HEAD'
            request.host_locations = self._get_host_locations(secondary=True)
            request.path = _get_path(container_name, blob_name)
            request.query = {
                'snapshot': _to_str(snapshot),
                'timeout': _int_to_str(timeout),
                'restype': 'container' if blob_name is None else None,
            }

            expected_errors = [_CONTAINER_NOT_FOUND_ERROR_CODE] if blob_name is None \
                else [_CONTAINER_NOT_FOUND_ERROR_CODE, _BLOB_NOT_FOUND_ERROR_CODE]
            self._perform_request(request, expected_errors=expected_errors)

            return True
        except AzureHttpError as ex:
            _dont_fail_not_exist(ex)
            return False

    def _get_blob(
            self, container_name, blob_name, snapshot=None, start_range=None,
            end_range=None, validate_content=False, lease_id=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None, cpk=None,
            _context=None):
        '''
        Downloads a blob's content, metadata, and properties. You can also
        call this API to read a snapshot. You can specify a range if you don't
        need to download the blob in its entirety. If no range is specified,
        the full blob will be downloaded.

        See get_blob_to_* for high level functions that handle the download
        of large blobs with automatic chunking and progress notifications.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str snapshot:
            The snapshot parameter is an opaque DateTime value that,
            when present, specifies the blob snapshot to retrieve.
        :param int start_range:
            Start of byte range to use for downloading a section of the blob.
            If no end_range is given, all bytes after the start_range will be downloaded.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of blob.
        :param int end_range:
            End of byte range to use for downloading a section of the blob.
            If end_range is given, start_range must be provided.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of blob.
        :param bool validate_content:
            When this is set to True and specified together with the Range header, 
            the service returns the MD5 hash for the range, as long as the range 
            is less than or equal to 4 MB in size.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param ~azure.storage.blob.models.CustomerProvidedEncryptionKey cpk:
            Decrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: A Blob with content, properties, and metadata.
        :rtype: :class:`~azure.storage.blob.models.Blob`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_decryption_required(self.require_encryption,
                                      self.key_encryption_key,
                                      self.key_resolver_function)

        start_offset, end_offset = 0, 0
        if self.key_encryption_key is not None or self.key_resolver_function is not None:
            if start_range is not None:
                # Align the start of the range along a 16 byte block
                start_offset = start_range % 16
                start_range -= start_offset

                # Include an extra 16 bytes for the IV if necessary
                # Because of the previous offsetting, start_range will always
                # be a multiple of 16.
                if start_range > 0:
                    start_offset += 16
                    start_range -= 16

            if end_range is not None:
                # Align the end of the range along a 16 byte block
                end_offset = 15 - (end_range % 16)
                end_range += end_offset

        request = HTTPRequest()
        request.method = 'GET'
        request.host_locations = self._get_host_locations(secondary=True)
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'snapshot': _to_str(snapshot),
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
        }
        _validate_and_add_cpk_headers(request, encryption_key=cpk, protocol=self.protocol)
        _validate_and_format_range_headers(
            request,
            start_range,
            end_range,
            start_range_required=False,
            end_range_required=False,
            check_content_md5=validate_content)

        return self._perform_request(request, _parse_blob,
                                     [blob_name, snapshot, validate_content, self.require_encryption,
                                      self.key_encryption_key, self.key_resolver_function,
                                      start_offset, end_offset],
                                     operation_context=_context)

    def get_blob_to_path(
            self, container_name, blob_name, file_path, open_mode='wb',
            snapshot=None, start_range=None, end_range=None,
            validate_content=False, progress_callback=None,
            max_connections=2, lease_id=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None, cpk=None):
        '''
        Downloads a blob to a file path, with automatic chunking and progress
        notifications. Returns an instance of :class:`~azure.storage.blob.models.Blob` with
        properties and metadata.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str file_path:
            Path of file to write out to.
        :param str open_mode:
            Mode to use when opening the file. Note that specifying append only 
            open_mode prevents parallel download. So, max_connections must be set 
            to 1 if this open_mode is used.
        :param str snapshot:
            The snapshot parameter is an opaque DateTime value that,
            when present, specifies the blob snapshot to retrieve.
        :param int start_range:
            Start of byte range to use for downloading a section of the blob.
            If no end_range is given, all bytes after the start_range will be downloaded.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of blob.
        :param int end_range:
            End of byte range to use for downloading a section of the blob.
            If end_range is given, start_range must be provided.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of blob.
        :param bool validate_content:
            If set to true, validates an MD5 hash for each retrieved portion of 
            the blob. This is primarily valuable for detecting bitflips on the wire 
            if using http instead of https as https (the default) will already 
            validate. Note that the service will only return transactional MD5s 
            for chunks 4MB or less so the first get request will be of size 
            self.MAX_CHUNK_GET_SIZE instead of self.MAX_SINGLE_GET_SIZE. If 
            self.MAX_CHUNK_GET_SIZE was set to greater than 4MB an error will be 
            thrown. As computing the MD5 takes processing time and more requests 
            will need to be done due to the reduced chunk size there may be some 
            increase in latency.
        :param progress_callback:
            Callback for progress with signature function(current, total) 
            where current is the number of bytes transfered so far, and total is 
            the size of the blob if known.
        :type progress_callback: func(current, total)
        :param int max_connections:
            If set to 2 or greater, an initial get will be done for the first 
            self.MAX_SINGLE_GET_SIZE bytes of the blob. If this is the entire blob, 
            the method returns at this point. If it is not, it will download the 
            remaining data parallel using the number of threads equal to 
            max_connections. Each chunk will be of size self.MAX_CHUNK_GET_SIZE.
            If set to 1, a single large get request will be done. This is not 
            generally recommended but available if very few threads should be 
            used, network requests are very expensive, or a non-seekable stream 
            prevents parallel download. This may also be useful if many blobs are 
            expected to be empty as an extra request is required for empty blobs 
            if max_connections is greater than 1.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param ~azure.storage.blob.models.CustomerProvidedEncryptionKey cpk:
            Decrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make 
            multiple calls to the Azure service and the timeout will apply to 
            each call individually.
        :return: A Blob with properties and metadata. If max_connections is greater 
            than 1, the content_md5 (if set on the blob) will not be returned. If you 
            require this value, either use get_blob_properties or set max_connections 
            to 1.
        :rtype: :class:`~azure.storage.blob.models.Blob`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('file_path', file_path)
        _validate_not_none('open_mode', open_mode)

        if max_connections > 1 and 'a' in open_mode:
            raise ValueError(_ERROR_PARALLEL_NOT_SEEKABLE)

        with open(file_path, open_mode) as stream:
            blob = self.get_blob_to_stream(
                container_name,
                blob_name,
                stream,
                snapshot,
                start_range,
                end_range,
                validate_content,
                progress_callback,
                max_connections,
                lease_id,
                if_modified_since,
                if_unmodified_since,
                if_match,
                if_none_match,
                timeout=timeout,
                cpk=cpk)

        return blob

    def get_blob_to_stream(
            self, container_name, blob_name, stream, snapshot=None,
            start_range=None, end_range=None, validate_content=False,
            progress_callback=None, max_connections=2, lease_id=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None, timeout=None, cpk=None):

        '''
        Downloads a blob to a stream, with automatic chunking and progress
        notifications. Returns an instance of :class:`~azure.storage.blob.models.Blob` with
        properties and metadata.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param io.IOBase stream:
            Opened stream to write to.
        :param str snapshot:
            The snapshot parameter is an opaque DateTime value that,
            when present, specifies the blob snapshot to retrieve.
        :param int start_range:
            Start of byte range to use for downloading a section of the blob.
            If no end_range is given, all bytes after the start_range will be downloaded.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of blob.
        :param int end_range:
            End of byte range to use for downloading a section of the blob.
            If end_range is given, start_range must be provided.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of blob.
        :param bool validate_content:
            If set to true, validates an MD5 hash for each retrieved portion of 
            the blob. This is primarily valuable for detecting bitflips on the wire 
            if using http instead of https as https (the default) will already 
            validate. Note that the service will only return transactional MD5s 
            for chunks 4MB or less so the first get request will be of size 
            self.MAX_CHUNK_GET_SIZE instead of self.MAX_SINGLE_GET_SIZE. If 
            self.MAX_CHUNK_GET_SIZE was set to greater than 4MB an error will be 
            thrown. As computing the MD5 takes processing time and more requests 
            will need to be done due to the reduced chunk size there may be some 
            increase in latency.
        :param progress_callback:
            Callback for progress with signature function(current, total) 
            where current is the number of bytes transfered so far, and total is 
            the size of the blob if known.
        :type progress_callback: func(current, total)
        :param int max_connections:
            If set to 2 or greater, an initial get will be done for the first 
            self.MAX_SINGLE_GET_SIZE bytes of the blob. If this is the entire blob, 
            the method returns at this point. If it is not, it will download the 
            remaining data parallel using the number of threads equal to 
            max_connections. Each chunk will be of size self.MAX_CHUNK_GET_SIZE.
            If set to 1, a single large get request will be done. This is not 
            generally recommended but available if very few threads should be 
            used, network requests are very expensive, or a non-seekable stream 
            prevents parallel download. This may also be useful if many blobs are 
            expected to be empty as an extra request is required for empty blobs 
            if max_connections is greater than 1.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param ~azure.storage.blob.models.CustomerProvidedEncryptionKey cpk:
            Decrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make 
            multiple calls to the Azure service and the timeout will apply to 
            each call individually.
        :return: A Blob with properties and metadata. If max_connections is greater 
            than 1, the content_md5 (if set on the blob) will not be returned. If you 
            require this value, either use get_blob_properties or set max_connections 
            to 1.
        :rtype: :class:`~azure.storage.blob.models.Blob`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('stream', stream)

        if end_range is not None:
            _validate_not_none("start_range", start_range)

        # the stream must be seekable if parallel download is required
        if max_connections > 1:
            if sys.version_info >= (3,) and not stream.seekable():
                raise ValueError(_ERROR_PARALLEL_NOT_SEEKABLE)

            try:
                stream.seek(stream.tell())
            except (NotImplementedError, AttributeError):
                raise ValueError(_ERROR_PARALLEL_NOT_SEEKABLE)

        # The service only provides transactional MD5s for chunks under 4MB.
        # If validate_content is on, get only self.MAX_CHUNK_GET_SIZE for the first
        # chunk so a transactional MD5 can be retrieved.
        first_get_size = self.MAX_SINGLE_GET_SIZE if not validate_content else self.MAX_CHUNK_GET_SIZE

        initial_request_start = start_range if start_range is not None else 0

        if end_range is not None and end_range - start_range < first_get_size:
            initial_request_end = end_range
        else:
            initial_request_end = initial_request_start + first_get_size - 1

        # Send a context object to make sure we always retry to the initial location
        operation_context = _OperationContext(location_lock=True)
        try:
            blob = self._get_blob(container_name,
                                  blob_name,
                                  snapshot,
                                  start_range=initial_request_start,
                                  end_range=initial_request_end,
                                  validate_content=validate_content,
                                  lease_id=lease_id,
                                  if_modified_since=if_modified_since,
                                  if_unmodified_since=if_unmodified_since,
                                  if_match=if_match,
                                  if_none_match=if_none_match,
                                  timeout=timeout,
                                  _context=operation_context,
                                  cpk=cpk)

            # Parse the total blob size and adjust the download size if ranges
            # were specified
            blob_size = _parse_length_from_content_range(blob.properties.content_range)
            if end_range is not None:
                # Use the end_range unless it is over the end of the blob
                download_size = min(blob_size, end_range - start_range + 1)
            elif start_range is not None:
                download_size = blob_size - start_range
            else:
                download_size = blob_size
        except AzureHttpError as ex:
            if start_range is None and ex.status_code == 416:
                # Get range will fail on an empty blob. If the user did not
                # request a range, do a regular get request in order to get
                # any properties.
                blob = self._get_blob(container_name,
                                      blob_name,
                                      snapshot,
                                      validate_content=validate_content,
                                      lease_id=lease_id,
                                      if_modified_since=if_modified_since,
                                      if_unmodified_since=if_unmodified_since,
                                      if_match=if_match,
                                      if_none_match=if_none_match,
                                      timeout=timeout,
                                      _context=operation_context,
                                      cpk=cpk)

                # Set the download size to empty
                download_size = 0
            else:
                raise ex

        # Mark the first progress chunk. If the blob is small or this is a single
        # shot download, this is the only call
        if progress_callback:
            progress_callback(blob.properties.content_length, download_size)

        # Write the content to the user stream
        # Clear blob content since output has been written to user stream
        if blob.content is not None:
            stream.write(blob.content)
            blob.content = None

        # If the blob is small, the download is complete at this point.
        # If blob size is large, download the rest of the blob in chunks.
        if blob.properties.content_length != download_size:
            # Lock on the etag. This can be overriden by the user by specifying '*'
            if_match = if_match if if_match is not None else blob.properties.etag

            end_blob = blob_size
            if end_range is not None:
                # Use the end_range unless it is over the end of the blob
                end_blob = min(blob_size, end_range + 1)

            _download_blob_chunks(
                self,
                container_name,
                blob_name,
                snapshot,
                download_size,
                self.MAX_CHUNK_GET_SIZE,
                first_get_size,
                initial_request_end + 1,  # start where the first download ended
                end_blob,
                stream,
                max_connections,
                progress_callback,
                validate_content,
                lease_id,
                if_modified_since,
                if_unmodified_since,
                if_match,
                if_none_match,
                timeout,
                operation_context,
                cpk,
            )

            # Set the content length to the download size instead of the size of
            # the last range
            blob.properties.content_length = download_size

            # Overwrite the content range to the user requested range
            blob.properties.content_range = 'bytes {0}-{1}/{2}'.format(start_range, end_range, blob_size)

            # Overwrite the content MD5 as it is the MD5 for the last range instead
            # of the stored MD5
            # TODO: Set to the stored MD5 when the service returns this
            blob.properties.content_md5 = None

        return blob

    def get_blob_to_bytes(
            self, container_name, blob_name, snapshot=None,
            start_range=None, end_range=None, validate_content=False,
            progress_callback=None, max_connections=2, lease_id=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None, timeout=None, cpk=None):
        '''
        Downloads a blob as an array of bytes, with automatic chunking and
        progress notifications. Returns an instance of :class:`~azure.storage.blob.models.Blob` with
        properties, metadata, and content.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str snapshot:
            The snapshot parameter is an opaque DateTime value that,
            when present, specifies the blob snapshot to retrieve.
        :param int start_range:
            Start of byte range to use for downloading a section of the blob.
            If no end_range is given, all bytes after the start_range will be downloaded.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of blob.
        :param int end_range:
            End of byte range to use for downloading a section of the blob.
            If end_range is given, start_range must be provided.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of blob.
        :param bool validate_content:
            If set to true, validates an MD5 hash for each retrieved portion of 
            the blob. This is primarily valuable for detecting bitflips on the wire 
            if using http instead of https as https (the default) will already 
            validate. Note that the service will only return transactional MD5s 
            for chunks 4MB or less so the first get request will be of size 
            self.MAX_CHUNK_GET_SIZE instead of self.MAX_SINGLE_GET_SIZE. If 
            self.MAX_CHUNK_GET_SIZE was set to greater than 4MB an error will be 
            thrown. As computing the MD5 takes processing time and more requests 
            will need to be done due to the reduced chunk size there may be some 
            increase in latency.
        :param progress_callback:
            Callback for progress with signature function(current, total) 
            where current is the number of bytes transfered so far, and total is 
            the size of the blob if known.
        :type progress_callback: func(current, total)
        :param int max_connections:
            If set to 2 or greater, an initial get will be done for the first 
            self.MAX_SINGLE_GET_SIZE bytes of the blob. If this is the entire blob, 
            the method returns at this point. If it is not, it will download the 
            remaining data parallel using the number of threads equal to 
            max_connections. Each chunk will be of size self.MAX_CHUNK_GET_SIZE.
            If set to 1, a single large get request will be done. This is not 
            generally recommended but available if very few threads should be 
            used, network requests are very expensive, or a non-seekable stream 
            prevents parallel download. This may also be useful if many blobs are 
            expected to be empty as an extra request is required for empty blobs 
            if max_connections is greater than 1.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param ~azure.storage.blob.models.CustomerProvidedEncryptionKey cpk:
            Decrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make 
            multiple calls to the Azure service and the timeout will apply to 
            each call individually.
        :return: A Blob with properties and metadata. If max_connections is greater 
            than 1, the content_md5 (if set on the blob) will not be returned. If you 
            require this value, either use get_blob_properties or set max_connections 
            to 1.
        :rtype: :class:`~azure.storage.blob.models.Blob`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)

        stream = BytesIO()
        blob = self.get_blob_to_stream(
            container_name,
            blob_name,
            stream,
            snapshot,
            start_range,
            end_range,
            validate_content,
            progress_callback,
            max_connections,
            lease_id,
            if_modified_since,
            if_unmodified_since,
            if_match,
            if_none_match,
            timeout=timeout,
            cpk=cpk)

        blob.content = stream.getvalue()
        return blob

    def get_blob_to_text(
            self, container_name, blob_name, encoding='utf-8', snapshot=None,
            start_range=None, end_range=None, validate_content=False,
            progress_callback=None, max_connections=2, lease_id=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None, timeout=None, cpk=None):
        '''
        Downloads a blob as unicode text, with automatic chunking and progress
        notifications. Returns an instance of :class:`~azure.storage.blob.models.Blob` with
        properties, metadata, and content.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str encoding:
            Python encoding to use when decoding the blob data.
        :param str snapshot:
            The snapshot parameter is an opaque DateTime value that,
            when present, specifies the blob snapshot to retrieve.
        :param int start_range:
            Start of byte range to use for downloading a section of the blob.
            If no end_range is given, all bytes after the start_range will be downloaded.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of blob.
        :param int end_range:
            End of byte range to use for downloading a section of the blob.
            If end_range is given, start_range must be provided.
            The start_range and end_range params are inclusive.
            Ex: start_range=0, end_range=511 will download first 512 bytes of blob.
        :param bool validate_content:
            If set to true, validates an MD5 hash for each retrieved portion of 
            the blob. This is primarily valuable for detecting bitflips on the wire 
            if using http instead of https as https (the default) will already 
            validate. Note that the service will only return transactional MD5s 
            for chunks 4MB or less so the first get request will be of size 
            self.MAX_CHUNK_GET_SIZE instead of self.MAX_SINGLE_GET_SIZE. If 
            self.MAX_CHUNK_GET_SIZE was set to greater than 4MB an error will be 
            thrown. As computing the MD5 takes processing time and more requests 
            will need to be done due to the reduced chunk size there may be some 
            increase in latency.
        :param progress_callback:
            Callback for progress with signature function(current, total) 
            where current is the number of bytes transfered so far, and total is 
            the size of the blob if known.
        :type progress_callback: func(current, total)
        :param int max_connections:
            If set to 2 or greater, an initial get will be done for the first 
            self.MAX_SINGLE_GET_SIZE bytes of the blob. If this is the entire blob, 
            the method returns at this point. If it is not, it will download the 
            remaining data parallel using the number of threads equal to 
            max_connections. Each chunk will be of size self.MAX_CHUNK_GET_SIZE.
            If set to 1, a single large get request will be done. This is not 
            generally recommended but available if very few threads should be 
            used, network requests are very expensive, or a non-seekable stream 
            prevents parallel download. This may also be useful if many blobs are 
            expected to be empty as an extra request is required for empty blobs 
            if max_connections is greater than 1.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param ~azure.storage.blob.models.CustomerProvidedEncryptionKey cpk:
            Decrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :param int timeout:
            The timeout parameter is expressed in seconds. This method may make 
            multiple calls to the Azure service and the timeout will apply to 
            each call individually.
        :return: A Blob with properties and metadata. If max_connections is greater 
            than 1, the content_md5 (if set on the blob) will not be returned. If you 
            require this value, either use get_blob_properties or set max_connections 
            to 1.
        :rtype: :class:`~azure.storage.blob.models.Blob`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('encoding', encoding)

        blob = self.get_blob_to_bytes(container_name,
                                      blob_name,
                                      snapshot,
                                      start_range,
                                      end_range,
                                      validate_content,
                                      progress_callback,
                                      max_connections,
                                      lease_id,
                                      if_modified_since,
                                      if_unmodified_since,
                                      if_match,
                                      if_none_match,
                                      timeout=timeout,
                                      cpk=cpk)
        blob.content = blob.content.decode(encoding)
        return blob

    def get_blob_metadata(
            self, container_name, blob_name, snapshot=None, lease_id=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None, timeout=None, cpk=None):
        '''
        Returns all user-defined metadata for the specified blob or snapshot.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str snapshot:
            The snapshot parameter is an opaque value that,
            when present, specifies the blob snapshot to retrieve.
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param ~azure.storage.blob.models.CustomerProvidedEncryptionKey cpk:
            Decrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return:
            A dictionary representing the blob metadata name, value pairs.
        :rtype: dict(str, str)
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'GET'
        request.host_locations = self._get_host_locations(secondary=True)
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'snapshot': _to_str(snapshot),
            'comp': 'metadata',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
        }
        _validate_and_add_cpk_headers(request, encryption_key=cpk, protocol=self.protocol)
        return self._perform_request(request, _parse_metadata)

    def set_blob_metadata(self, container_name, blob_name,
                          metadata=None, lease_id=None,
                          if_modified_since=None, if_unmodified_since=None,
                          if_match=None, if_none_match=None, timeout=None, cpk=None):
        '''
        Sets user-defined metadata for the specified blob as one or more
        name-value pairs.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param metadata:
            Dict containing name and value pairs. Each call to this operation
            replaces all existing metadata attached to the blob. To remove all
            metadata from the blob, call this operation with no metadata headers.
        :type metadata: dict(str, str)
        :param str lease_id:
            Required if the blob has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param ~azure.storage.blob.models.CustomerProvidedEncryptionKey cpk:
            Encrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: ETag and last modified properties for the updated Blob
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'metadata',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
            'x-ms-lease-id': _to_str(lease_id),
        }
        _add_metadata_headers(metadata, request)
        _validate_and_add_cpk_headers(request, encryption_key=cpk, protocol=self.protocol)
        return self._perform_request(request, _parse_base_properties)

    def _lease_blob_impl(self, container_name, blob_name,
                         lease_action, lease_id,
                         lease_duration, lease_break_period,
                         proposed_lease_id, if_modified_since,
                         if_unmodified_since, if_match, if_none_match, timeout=None):
        '''
        Establishes and manages a lease on a blob for write and delete operations.
        The Lease Blob operation can be called in one of five modes:
            Acquire, to request a new lease.
            Renew, to renew an existing lease.
            Change, to change the ID of an existing lease.
            Release, to free the lease if it is no longer needed so that another
                client may immediately acquire a lease against the blob.
            Break, to end the lease but ensure that another client cannot acquire
                a new lease until the current lease period has expired.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str lease_action:
            Possible _LeaseActions acquire|renew|release|break|change
        :param str lease_id:
            Required if the blob has an active lease.
        :param int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change.
        :param int lease_break_period:
            For a break operation, this is the proposed duration of
            seconds that the lease should continue before it is broken, between
            0 and 60 seconds. This break period is only used if it is shorter
            than the time remaining on the lease. If longer, the time remaining
            on the lease is used. A new lease will not be available before the
            break period has expired, but the lease may be held for longer than
            the break period. If this header does not appear with a break
            operation, a fixed-duration lease breaks after the remaining lease
            period elapses, and an infinite lease breaks immediately.
        :param str proposed_lease_id:
            Optional for acquire, required for change. Proposed lease ID, in a
            GUID string format. The Blob service returns 400 (Invalid request)
            if the proposed lease ID is not in the correct format. 
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return:
            Response headers returned from the service call.
        :rtype: dict(str, str)
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('lease_action', lease_action)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'lease',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'x-ms-lease-action': _to_str(lease_action),
            'x-ms-lease-duration': _to_str(lease_duration),
            'x-ms-lease-break-period': _to_str(lease_break_period),
            'x-ms-proposed-lease-id': _to_str(proposed_lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
        }

        return self._perform_request(request, _parse_lease)

    def acquire_blob_lease(self, container_name, blob_name,
                           lease_duration=-1,
                           proposed_lease_id=None,
                           if_modified_since=None,
                           if_unmodified_since=None,
                           if_match=None,
                           if_none_match=None, timeout=None):
        '''
        Requests a new lease. If the blob does not have an active lease, the Blob
        service creates a lease on the blob and returns a new lease ID.
        
        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change. Default is -1 (infinite lease).
        :param str proposed_lease_id:
            Proposed lease ID, in a GUID string format. The Blob service
            returns 400 (Invalid request) if the proposed lease ID is not
            in the correct format. 
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: the lease ID of the newly created lease.
        :return: str
        '''
        _validate_not_none('lease_duration', lease_duration)

        if lease_duration is not -1 and \
                (lease_duration < 15 or lease_duration > 60):
            raise ValueError(_ERROR_INVALID_LEASE_DURATION)
        lease = self._lease_blob_impl(container_name,
                                      blob_name,
                                      _LeaseActions.Acquire,
                                      None,  # lease_id
                                      lease_duration,
                                      None,  # lease_break_period
                                      proposed_lease_id,
                                      if_modified_since,
                                      if_unmodified_since,
                                      if_match,
                                      if_none_match,
                                      timeout)
        return lease['id']

    def renew_blob_lease(self, container_name, blob_name,
                         lease_id, if_modified_since=None,
                         if_unmodified_since=None, if_match=None,
                         if_none_match=None, timeout=None):
        '''
        Renews the lease. The lease can be renewed if the lease ID specified on
        the request matches that associated with the blob. Note that the lease may
        be renewed even if it has expired as long as the blob has not been modified
        or leased again since the expiration of that lease. When you renew a lease,
        the lease duration clock resets. 
        
        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str lease_id:
            Lease ID for active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: the lease ID of the renewed lease.
        :return: str
        '''
        _validate_not_none('lease_id', lease_id)

        lease = self._lease_blob_impl(container_name,
                                      blob_name,
                                      _LeaseActions.Renew,
                                      lease_id,
                                      None,  # lease_duration
                                      None,  # lease_break_period
                                      None,  # proposed_lease_id
                                      if_modified_since,
                                      if_unmodified_since,
                                      if_match,
                                      if_none_match,
                                      timeout)
        return lease['id']

    def release_blob_lease(self, container_name, blob_name,
                           lease_id, if_modified_since=None,
                           if_unmodified_since=None, if_match=None,
                           if_none_match=None, timeout=None):
        '''
        Releases the lease. The lease may be released if the lease ID specified on the
        request matches that associated with the blob. Releasing the lease allows another
        client to immediately acquire the lease for the blob as soon as the release is complete. 
        
        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str lease_id:
            Lease ID for active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        '''
        _validate_not_none('lease_id', lease_id)

        self._lease_blob_impl(container_name,
                              blob_name,
                              _LeaseActions.Release,
                              lease_id,
                              None,  # lease_duration
                              None,  # lease_break_period
                              None,  # proposed_lease_id
                              if_modified_since,
                              if_unmodified_since,
                              if_match,
                              if_none_match,
                              timeout)

    def break_blob_lease(self, container_name, blob_name,
                         lease_break_period=None,
                         if_modified_since=None,
                         if_unmodified_since=None,
                         if_match=None,
                         if_none_match=None, timeout=None):
        '''
        Breaks the lease, if the blob has an active lease. Once a lease is broken,
        it cannot be renewed. Any authorized request can break the lease; the request
        is not required to specify a matching lease ID. When a lease is broken,
        the lease break period is allowed to elapse, during which time no lease operation
        except break and release can be performed on the blob. When a lease is successfully
        broken, the response indicates the interval in seconds until a new lease can be acquired. 

        A lease that has been broken can also be released, in which case another client may
        immediately acquire the lease on the blob.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param int lease_break_period:
            For a break operation, this is the proposed duration of
            seconds that the lease should continue before it is broken, between
            0 and 60 seconds. This break period is only used if it is shorter
            than the time remaining on the lease. If longer, the time remaining
            on the lease is used. A new lease will not be available before the
            break period has expired, but the lease may be held for longer than
            the break period. If this header does not appear with a break
            operation, a fixed-duration lease breaks after the remaining lease
            period elapses, and an infinite lease breaks immediately.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: Approximate time remaining in the lease period, in seconds.
        :return: int
        '''
        if (lease_break_period is not None) and (lease_break_period < 0 or lease_break_period > 60):
            raise ValueError(_ERROR_INVALID_LEASE_BREAK_PERIOD)

        lease = self._lease_blob_impl(container_name,
                                      blob_name,
                                      _LeaseActions.Break,
                                      None,  # lease_id
                                      None,  # lease_duration
                                      lease_break_period,
                                      None,  # proposed_lease_id
                                      if_modified_since,
                                      if_unmodified_since,
                                      if_match,
                                      if_none_match,
                                      timeout)
        return lease['time']

    def change_blob_lease(self, container_name, blob_name,
                          lease_id,
                          proposed_lease_id,
                          if_modified_since=None,
                          if_unmodified_since=None,
                          if_match=None,
                          if_none_match=None, timeout=None):
        '''
        Changes the lease ID of an active lease. A change must include the current
        lease ID and a new lease ID.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str lease_id:
            Required if the blob has an active lease.
        :param str proposed_lease_id:
            Proposed lease ID, in a GUID string format. The Blob service returns
            400 (Invalid request) if the proposed lease ID is not in the correct format. 
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        '''
        self._lease_blob_impl(container_name,
                              blob_name,
                              _LeaseActions.Change,
                              lease_id,
                              None,  # lease_duration
                              None,  # lease_break_period
                              proposed_lease_id,
                              if_modified_since,
                              if_unmodified_since,
                              if_match,
                              if_none_match,
                              timeout)

    def snapshot_blob(self, container_name, blob_name,
                      metadata=None, if_modified_since=None,
                      if_unmodified_since=None, if_match=None,
                      if_none_match=None, lease_id=None, timeout=None, cpk=None):
        '''
        Creates a read-only snapshot of a blob.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param metadata:
            Specifies a user-defined name-value pair associated with the blob.
            If no name-value pairs are specified, the operation will copy the
            base blob metadata to the snapshot. If one or more name-value pairs
            are specified, the snapshot is created with the specified metadata,
            and metadata is not copied from the base blob.
        :type metadata: dict(str, str)
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param str lease_id:
            Required if the blob has an active lease.
        :param ~azure.storage.blob.models.CustomerProvidedEncryptionKey cpk:
            Encrypts the data on the service-side with the given key.
            Use of customer-provided keys must be done over HTTPS.
            As the encryption key itself is provided in the request,
            a secure connection must be established to transfer the key.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: snapshot properties
        :rtype: :class:`~azure.storage.blob.models.Blob`
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'snapshot',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
            'x-ms-lease-id': _to_str(lease_id)
        }
        _validate_and_add_cpk_headers(request, encryption_key=cpk, protocol=self.protocol)
        _add_metadata_headers(metadata, request)

        return self._perform_request(request, _parse_snapshot_blob, [blob_name])

    def copy_blob(self, container_name, blob_name, copy_source,
                  metadata=None,
                  source_if_modified_since=None,
                  source_if_unmodified_since=None,
                  source_if_match=None, source_if_none_match=None,
                  destination_if_modified_since=None,
                  destination_if_unmodified_since=None,
                  destination_if_match=None,
                  destination_if_none_match=None,
                  destination_lease_id=None,
                  source_lease_id=None, timeout=None):
        '''
        Copies a blob asynchronously. This operation returns a copy operation 
        properties object, including a copy ID you can use to check or abort the 
        copy operation. The Blob service copies blobs on a best-effort basis.

        The source blob for a copy operation may be a block blob, an append blob, 
        or a page blob. If the destination blob already exists, it must be of the 
        same blob type as the source blob. Any existing destination blob will be 
        overwritten. The destination blob cannot be modified while a copy operation 
        is in progress.

        When copying from a page blob, the Blob service creates a destination page 
        blob of the source blob's length, initially containing all zeroes. Then 
        the source page ranges are enumerated, and non-empty ranges are copied. 

        For a block blob or an append blob, the Blob service creates a committed 
        blob of zero length before returning from this operation. When copying 
        from a block blob, all committed blocks and their block IDs are copied. 
        Uncommitted blocks are not copied. At the end of the copy operation, the 
        destination blob will have the same committed block count as the source.

        When copying from an append blob, all committed blocks are copied. At the 
        end of the copy operation, the destination blob will have the same committed 
        block count as the source.

        For all blob types, you can call get_blob_properties on the destination 
        blob to check the status of the copy operation. The final blob will be 
        committed when the copy completes.

        :param str container_name:
            Name of the destination container. The container must exist.
        :param str blob_name:
            Name of the destination blob. If the destination blob exists, it will 
            be overwritten. Otherwise, it will be created.
        :param str copy_source:
            A URL of up to 2 KB in length that specifies an Azure file or blob. 
            The value should be URL-encoded as it would appear in a request URI. 
            If the source is in another account, the source must either be public 
            or must be authenticated via a shared access signature. If the source 
            is public, no authentication is required.
            Examples:
            https://myaccount.blob.core.windows.net/mycontainer/myblob
            https://myaccount.blob.core.windows.net/mycontainer/myblob?snapshot=<DateTime>
            https://otheraccount.blob.core.windows.net/mycontainer/myblob?sastoken
        :param metadata:
            Name-value pairs associated with the blob as metadata. If no name-value 
            pairs are specified, the operation will copy the metadata from the 
            source blob or file to the destination blob. If one or more name-value 
            pairs are specified, the destination blob is created with the specified 
            metadata, and metadata is not copied from the source blob or file. 
        :type metadata: dict(str, str)
        :param datetime source_if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.  
            Specify this conditional header to copy the blob only if the source
            blob has been modified since the specified date/time.
        :param datetime source_if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this conditional header to copy the blob only if the source blob
            has not been modified since the specified date/time.
        :param ETag source_if_match:
            An ETag value, or the wildcard character (*). Specify this conditional
            header to copy the source blob only if its ETag matches the value
            specified. If the ETag values do not match, the Blob service returns
            status code 412 (Precondition Failed). This header cannot be specified
            if the source is an Azure File.
        :param ETag source_if_none_match:
            An ETag value, or the wildcard character (*). Specify this conditional
            header to copy the blob only if its ETag does not match the value
            specified. If the values are identical, the Blob service returns status
            code 412 (Precondition Failed). This header cannot be specified if the
            source is an Azure File.
        :param datetime destination_if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this conditional header to copy the blob only
            if the destination blob has been modified since the specified date/time.
            If the destination blob has not been modified, the Blob service returns
            status code 412 (Precondition Failed).
        :param datetime destination_if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this conditional header to copy the blob only
            if the destination blob has not been modified since the specified
            date/time. If the destination blob has been modified, the Blob service
            returns status code 412 (Precondition Failed).
        :param ETag destination_if_match:
            An ETag value, or the wildcard character (*). Specify an ETag value for
            this conditional header to copy the blob only if the specified ETag value
            matches the ETag value for an existing destination blob. If the ETag for
            the destination blob does not match the ETag specified for If-Match, the
            Blob service returns status code 412 (Precondition Failed).
        :param ETag destination_if_none_match:
            An ETag value, or the wildcard character (*). Specify an ETag value for
            this conditional header to copy the blob only if the specified ETag value
            does not match the ETag value for the destination blob. Specify the wildcard
            character (*) to perform the operation only if the destination blob does not
            exist. If the specified condition isn't met, the Blob service returns status
            code 412 (Precondition Failed).
        :param str destination_lease_id:
            The lease ID specified for this header must match the lease ID of the
            destination blob. If the request does not include the lease ID or it is not
            valid, the operation fails with status code 412 (Precondition Failed).
        :param str source_lease_id:
            Specify this to perform the Copy Blob operation only if
            the lease ID given matches the active lease ID of the source blob.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: Copy operation properties such as status, source, and ID.
        :rtype: :class:`~azure.storage.blob.models.CopyProperties`
        '''
        return self._copy_blob(container_name, blob_name, copy_source,
                               metadata,
                               None,
                               source_if_modified_since, source_if_unmodified_since,
                               source_if_match, source_if_none_match,
                               destination_if_modified_since,
                               destination_if_unmodified_since,
                               destination_if_match,
                               destination_if_none_match,
                               destination_lease_id,
                               source_lease_id, timeout,
                               False, False)

    def _copy_blob(self, container_name, blob_name, copy_source,
                   metadata=None,
                   premium_page_blob_tier=None,
                   source_if_modified_since=None,
                   source_if_unmodified_since=None,
                   source_if_match=None, source_if_none_match=None,
                   destination_if_modified_since=None,
                   destination_if_unmodified_since=None,
                   destination_if_match=None,
                   destination_if_none_match=None,
                   destination_lease_id=None,
                   source_lease_id=None, timeout=None,
                   incremental_copy=False,
                   requires_sync=None,
                   standard_blob_tier=None,
                   rehydrate_priority=None):
        '''
        See copy_blob for more details. This helper method
        allows for standard copies as well as incremental copies which are only supported for page blobs and sync
        copies which are only supported for block blobs.
        :param bool incremental_copy:
            Performs an incremental copy operation on a page blob instead of a standard copy operation.
        :param bool requires_sync:
            Enforces that the service will not return a response until the copy is complete.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('copy_source', copy_source)

        if copy_source.startswith('/'):
            # Backwards compatibility for earlier versions of the SDK where
            # the copy source can be in the following formats:
            # - Blob in named container:
            #     /accountName/containerName/blobName
            # - Snapshot in named container:
            #     /accountName/containerName/blobName?snapshot=<DateTime>
            # - Blob in root container:
            #     /accountName/blobName
            # - Snapshot in root container:
            #     /accountName/blobName?snapshot=<DateTime>
            account, _, source = \
                copy_source.partition('/')[2].partition('/')
            copy_source = self.protocol + '://' + \
                          self.primary_endpoint + '/' + source

        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)

        if incremental_copy:
            request.query = {
                'comp': 'incrementalcopy',
                'timeout': _int_to_str(timeout),
            }
        else:
            request.query = {'timeout': _int_to_str(timeout)}

        request.headers = {
            'x-ms-copy-source': _to_str(copy_source),
            'x-ms-source-if-modified-since': _to_str(source_if_modified_since),
            'x-ms-source-if-unmodified-since': _to_str(source_if_unmodified_since),
            'x-ms-source-if-match': _to_str(source_if_match),
            'x-ms-source-if-none-match': _to_str(source_if_none_match),
            'If-Modified-Since': _datetime_to_utc_string(destination_if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(destination_if_unmodified_since),
            'If-Match': _to_str(destination_if_match),
            'If-None-Match': _to_str(destination_if_none_match),
            'x-ms-lease-id': _to_str(destination_lease_id),
            'x-ms-source-lease-id': _to_str(source_lease_id),
            'x-ms-access-tier': _to_str(premium_page_blob_tier) or _to_str(standard_blob_tier),
            'x-ms-requires-sync': _to_str(requires_sync),
            'x-ms-rehydrate-priority': _to_str(rehydrate_priority)
        }

        _add_metadata_headers(metadata, request)

        return self._perform_request(request, _parse_properties, [BlobProperties]).copy

    def abort_copy_blob(self, container_name, blob_name, copy_id,
                        lease_id=None, timeout=None):
        '''
         Aborts a pending copy_blob operation, and leaves a destination blob
         with zero length and full metadata.

         :param str container_name:
             Name of destination container.
         :param str blob_name:
             Name of destination blob.
         :param str copy_id:
             Copy identifier provided in the copy.id of the original
             copy_blob operation.
         :param str lease_id:
             Required if the destination blob has an active infinite lease.
         :param int timeout:
             The timeout parameter is expressed in seconds.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        _validate_not_none('copy_id', copy_id)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'copy',
            'copyid': _to_str(copy_id),
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'x-ms-copy-action': 'abort',
        }

        self._perform_request(request)

    def delete_blob(self, container_name, blob_name, snapshot=None,
                    lease_id=None, delete_snapshots=None,
                    if_modified_since=None, if_unmodified_since=None,
                    if_match=None, if_none_match=None, timeout=None):
        '''
        Marks the specified blob or snapshot for deletion.
        The blob is later deleted during garbage collection.

        Note that in order to delete a blob, you must delete all of its
        snapshots. You can delete both at the same time with the Delete
        Blob operation.

        If a delete retention policy is enabled for the service, then this operation soft deletes the blob or snapshot
        and retains the blob or snapshot for specified number of days.
        After specified number of days, blob's data is removed from the service during garbage collection.
        Soft deleted blob or snapshot is accessible through List Blobs API specifying include=Include.Deleted option.
        Soft-deleted blob or snapshot can be restored using Undelete API.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param str snapshot:
            The snapshot parameter is an opaque DateTime value that,
            when present, specifies the blob snapshot to delete.
        :param str lease_id:
            Required if the blob has an active lease.
        :param ~azure.storage.blob.models.DeleteSnapshot delete_snapshots:
            Required if the blob has associated snapshots.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC. 
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        '''
        request = self._get_basic_delete_blob_http_request(container_name,
                                                           blob_name,
                                                           snapshot=snapshot,
                                                           lease_id=lease_id,
                                                           delete_snapshots=delete_snapshots,
                                                           if_modified_since=if_modified_since,
                                                           if_unmodified_since=if_unmodified_since,
                                                           if_match=if_match,
                                                           if_none_match=if_none_match,
                                                           timeout=timeout)

        self._perform_request(request)

    def batch_delete_blobs(self, batch_delete_sub_requests, timeout=None):
        '''
        Sends a batch of multiple blob delete requests.

        The blob delete method deletes the specified blob or snapshot. Note that deleting a blob also deletes all its
        snapshots. For more information, see https://docs.microsoft.com/rest/api/storageservices/delete-blob

        :param list(BatchDeleteSubRequest) batch_delete_sub_requests:
            The blob delete requests to send as a batch.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: parsed batch delete HTTP response
        :rtype: list of :class:`~azure.storage.blob.models.BatchSubResponse`
        '''
        self._check_batch_request(batch_delete_sub_requests)

        request = HTTPRequest()
        request.method = 'POST'
        request.host_locations = self._get_host_locations()
        request.path = _get_path()
        batch_id = str(uuid.uuid1())
        request.headers = {
            'Content-Type': "multipart/mixed; boundary=" + _get_batch_request_delimiter(batch_id, False, False),
        }
        request.query = {
            'comp': 'batch',
            'timeout': _int_to_str(timeout)
        }

        batch_http_requests = []
        for batch_delete_sub_request in batch_delete_sub_requests:
            batch_delete_sub_http_request = self._construct_batch_delete_sub_http_request(len(batch_http_requests),
                                                                                          batch_delete_sub_request)
            batch_http_requests.append(batch_delete_sub_http_request)

        request.body = _serialize_batch_body(batch_http_requests, batch_id)

        return self._perform_request(request, parser=_ingest_batch_response, parser_args=[batch_delete_sub_requests])

    def _construct_batch_delete_sub_http_request(self, content_id, batch_delete_sub_request):
        """
        Construct an HTTPRequest instance from a batch delete sub-request.

        :param int content_id:
            the index of sub-request in the list of sub-requests
        :param ~azure.storage.blob.models.BatchDeleteSubRequest batch_delete_sub_request:
            one of the delete request to be sent in a batch
        :return: HTTPRequest parsed from batch delete sub-request
        :rtype: :class:`~..common._http.HTTPRequest`
        """
        request = self._get_basic_delete_blob_http_request(batch_delete_sub_request.container_name,
                                                           batch_delete_sub_request.blob_name,
                                                           snapshot=batch_delete_sub_request.snapshot,
                                                           lease_id=batch_delete_sub_request.lease_id,
                                                           delete_snapshots=batch_delete_sub_request.delete_snapshots,
                                                           if_modified_since=batch_delete_sub_request.if_modified_since,
                                                           if_unmodified_since=batch_delete_sub_request.if_unmodified_since,
                                                           if_match=batch_delete_sub_request.if_match,
                                                           if_none_match=batch_delete_sub_request.if_none_match)
        request.headers.update({
            'Content-ID': _int_to_str(content_id),
            'Content-Length': _int_to_str(0),
            'Content-Transfer-Encoding': 'binary',
        })

        _update_request(request, None, self._USER_AGENT_STRING)
        # sub-request will use the batch request id automatically, no need to generate a separate one
        request.headers.pop('x-ms-client-request-id', None)

        _add_date_header(request)
        self.authentication.sign_request(request)

        return request

    def _get_basic_delete_blob_http_request(self, container_name, blob_name, snapshot=None, lease_id=None,
                                            delete_snapshots=None, if_modified_since=None, if_unmodified_since=None,
                                            if_match=None, if_none_match=None, timeout=None):
        """
        Construct a basic HTTPRequest instance for delete blob

        For more information about the parameters please see delete_blob

        :return: an HTTPRequest for delete blob
        :rtype :class:`~..common._http.HTTPRequest`
        """
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'x-ms-delete-snapshots': _to_str(delete_snapshots),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
        }
        request.query = {
            'snapshot': _to_str(snapshot),
            'timeout': _int_to_str(timeout)
        }

        return request

    @staticmethod
    def _check_batch_request(request):
        if request is None or len(request) < 1 or len(request) > 256:
            raise ValueError("Batch request should take 1 to 256 sub-requests")

    def undelete_blob(self, container_name, blob_name, timeout=None):
        '''
        The undelete Blob operation restores the contents and metadata of soft deleted blob or snapshot.
        Attempting to undelete a blob or snapshot that is not soft deleted will succeed without any changes.

        :param str container_name:
            Name of existing container.
        :param str blob_name:
            Name of existing blob.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        '''
        _validate_not_none('container_name', container_name)
        _validate_not_none('blob_name', blob_name)
        request = HTTPRequest()
        request.method = 'PUT'
        request.host_locations = self._get_host_locations()
        request.path = _get_path(container_name, blob_name)
        request.query = {
            'comp': 'undelete',
            'timeout': _int_to_str(timeout)
        }

        self._perform_request(request)

    # ----------------------------Methods related to directory manipulations---------------------------- #

    def create_directory(self, container_name, directory_path, lease_id=None, metadata=None,
                         posix_permissions=None, posix_umask=None, timeout=None):
        """
        Create a directory which can contain other directories or blobs.

        :param str container_name:
            Name of existing container.
        :param str directory_path:
            Path of the directory to be created. Ex: 'dirfoo/dirbar'.
            The service will create parent directories if they do not exist yet.
        :param str lease_id:
            Required if the directory to be overwritten has an active lease.
        :param metadata:
            A dict with name_value pairs to associate with the
            container as metadata. Example:{'Category':'test'}
        :type metadata: dict(str, str)
        :param str posix_permissions:
            Optional and only valid if Hierarchical Namespace is enabled for the account.
            Sets POSIX access permissions for the file owner, the file owning group, and others.
            Each class may be granted read, write, or execute permission.
            The sticky bit is also supported.
            Both symbolic (rwxrw-rw-) and 4-digit octal notation (e.g. 0766) are supported.
        :param str posix_umask:
            Optional and only valid if Hierarchical Namespace is enabled for the account.
            This umask restricts permission settings for file and directory,
            and will only be applied when default Acl does not exist in parent directory.
            If the umask bit has set, it means that the corresponding permission will be disabled.
            Otherwise the corresponding permission will be determined by the permission.
            A 4-digit octal notation (e.g. 0022) is supported here.
            If no umask was specified, a default umask - 0027 will be used.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: ETag and last modified time of the new directory.
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        """

        _validate_not_none('container_name', container_name)
        _validate_not_none('directory_path', directory_path)

        request = HTTPRequest()
        # TODO remove endpoint swapping after service update
        request.host_locations = self._swap_blob_endpoints(self._get_host_locations())
        request.method = 'PUT'
        request.path = _get_path(container_name, directory_path)
        request.query = {
            'resource': 'directory',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'x-ms-permissions': _to_str(posix_permissions),
            'x-ms-umask': _to_str(posix_umask),
        }
        # TODO add test cases for lease
        _add_file_or_directory_properties_header(metadata, request)
        return self._perform_request(request, parser=_parse_base_properties)

    def delete_directory(self, container_name, directory_path, fail_not_exist=False, recursive=False, marker=None,
                         lease_id=None, if_modified_since=None, if_unmodified_since=None, if_match=None,
                         if_none_match=None, timeout=None):
        """
        Delete a directory. This operation's behavior is different depending on whether Hierarchical Namespace
        is enabled; if yes, then the delete operation can be atomic and instantaneous;
        if not, the operation is performed in batches and a continuation token could be returned.

        :param str container_name:
            Name of existing container.
        :param str directory_path:
            Path of the directory to be deleted. Ex: 'dirfoo/dirbar'.
        :param fail_not_exist:
            Specify whether to throw an exception when the directory doesn't exist.
        :param recursive:
            If "true", all paths beneath the directory will be deleted.
            If "false" and the directory is non-empty, an error occurs.
        :param marker:
            Optional. When deleting a directory without the Hierarchical Namespace,
            the number of paths that are deleted with each invocation is limited.
            If the number of paths to be deleted exceeds this limit,
            a continuation token is returned. When a continuation token is returned,
            it must be specified in a subsequent invocation of the delete operation to continue deleting the directory.
        :param str lease_id:
            Required if the directory has an active lease.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return:
            (True, marker) if the directory is successfully deleted. Otherwise return (False, None).
        :rtype: (bool, str)
        """
        _validate_not_none('container_name', container_name)
        _validate_not_none('directory_path', directory_path)

        request = HTTPRequest()
        # TODO remove endpoint swapping after service update
        request.host_locations = self._swap_blob_endpoints(self._get_host_locations())
        request.method = 'DELETE'
        request.path = _get_path(container_name, directory_path)
        request.query = {
            'recursive': _to_str(recursive),
            'continuation': _to_str(marker),
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
        }
        # TODO add test cases for lease
        if not fail_not_exist:
            try:
                return True, self._perform_request(request, expected_errors=[_PATH_NOT_FOUND_ERROR_CODE],
                                                   parser=_parse_continuation_token)
            except AzureMissingResourceHttpError as ex:
                _dont_fail_not_exist(ex)
                return False, None
        else:
            return True, self._perform_request(request, parser=_parse_continuation_token)

    def rename_path(self, container_name, new_path, source_path,
                    mode=None, marker=None, lease_id=None, source_lease_id=None,
                    source_if_modified_since=None, source_if_unmodified_since=None,
                    source_if_match=None, source_if_none_match=None, timeout=None):
        """
        Rename a blob or directory(which can contain other directories or blobs).

        :param str container_name:
            Name of existing container.
        :param str new_path:
            New path for source_path. Ex: 'topdir1/dirsubfoo'.
            Note that the path should be an absolute path under the container.
        :param str source_path:
            Path to be renamed. Ex: 'topdir1/dirbar'.
            Note that the path should be an absolute path under the container.
        :param mode:
            Optional. Valid only when namespace is enabled.
            This parameter determines the behavior of the rename operation.
            The value must be "legacy" or "posix", and the default value will be "posix".
            Legacy: if the destination of the move is an existing directory and that directory is empty,
            the source will overwrite the destination. If the directory is not empty, the move will fail.
            Posix: if the destination of the move is an existing empty directory,
            destination will be overwritten. Otherwise, the source will be moved into the destination directory.
            If the destination is an existing file, the file will be overwritten.
        :param marker:
            Optional. When renaming a directory, the number of paths that are renamed with each invocation is limited.
            If the number of paths to be renamed exceeds this limit,
            a continuation token is returned. When a continuation token is returned,
            it must be specified in a subsequent invocation of the rename operation to continue renaming the directory.
        :param str lease_id:
            Optional. A lease ID for the new_path.
            The new_path must have an active lease and the lease ID must match.
        :param str source_lease_id:
            Optional. A lease ID for the source_path.
            The source_path must have an active lease and the lease ID must match.
        :param datetime source_if_modified_since:
            Optional. A date and time value. Specify this header to perform the rename operation
            only if the source has been modified since the specified date and time.
        :param datetime source_if_unmodified_since:
            Optional. A date and time value. Specify this header to perform the rename operation
            only if the source has not been modified since the specified date and time.
        :param str source_if_match:
            Optional. An ETag value. Specify this header to perform the rename operation
            only if the source's ETag matches the value specified.
        :param str source_if_none_match:
            Optional. An ETag value or the special wildcard ("*") value.
            Specify this header to perform the rename operation
            only if the source's ETag does not match the value specified.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return:
            A continuation marker if applicable. Otherwise return None.
        :rtype: str
        """
        _validate_not_none('source_path', source_path)
        _validate_not_none('new_path', new_path)

        request = HTTPRequest()
        # TODO remove endpoint swapping after service update
        request.host_locations = self._swap_blob_endpoints(self._get_host_locations())
        request.method = 'PUT'
        request.path = _get_path(container_name, new_path)
        request.query = {
            'mode': mode,
            'continuation': _to_str(marker),
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-rename-source': _get_path(container_name, source_path),
            'x-ms-lease-id': _to_str(lease_id),
            'x-ms-source-lease-id': _to_str(source_lease_id),
            'x-ms-source-if-modified-since': _datetime_to_utc_string(source_if_modified_since),
            'x-ms-source-if-unmodified-since': _datetime_to_utc_string(source_if_unmodified_since),
            'x-ms-source-if-match': _to_str(source_if_match),
            'x-ms-source-if-none-match': _to_str(source_if_none_match),
        }
        return self._perform_request(request, parser=_parse_continuation_token)

    def get_path_access_control(self, container_name, path, user_principle_names=False,
                                lease_id=None, if_modified_since=None, if_unmodified_since=None,
                                if_match=None, if_none_match=None, timeout=None):
        """
        Retrieve the access control properties of a path(directory or blob).

        :param str container_name:
            Name of existing container.
        :param str path:
            Path of the directory/blob.
        :param user_principle_names:
            Valid only when Hierarchical Namespace is enabled for the account.
            If "true", the user identity values returned for owner, group, and acl will be transformed
            from Azure Active Directory Object IDs to User Principal Names.
            If "false", the values will be returned as Azure Active Directory Object IDs.
            The default value is false. Note that group and application Object IDs are not translated
            because they do not have unique friendly names.
        :param str lease_id:
            Required if the path has an active lease.
        :param datetime if_modified_since:
            A date and time value. Specify this header to perform the operation only if the resource
            has been modified since the specified date and time.
        :param datetime if_unmodified_since:
            A date and time value. Specify this header to perform the operation only if the resource
            has not been modified since the specified date and time.
        :param datetime if_match:
            An ETag value. Specify this header to perform the operation
            only if the resource's ETag matches the value specified. The ETag must be specified in quotes.
        :param datetime if_none_match:
            An ETag value or the special wildcard ("*") value.
            Specify this header to perform the operation only if the resource's ETag
            does not match the value specified. The ETag must be specified in quotes.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: ETag and last modified time of the new directory.
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        """
        _validate_not_none('path', path)

        request = HTTPRequest()
        # TODO remove endpoint swapping after service update
        request.host_locations = self._swap_blob_endpoints(self._get_host_locations())
        request.method = 'HEAD'
        request.path = _get_path(container_name, path)
        request.query = {
            'action': 'getAccessControl',
            'upn': _to_str(user_principle_names),
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
        }
        return self._perform_request(request, parser=_parse_path_permission_and_acl)

    def set_path_access_control(self, container_name, path, owner=None, group=None, permissions=None,
                                acl=None, lease_id=None, if_modified_since=None, if_unmodified_since=None,
                                if_match=None, if_none_match=None, timeout=None):
        """
        Set the access control properties of a path(directory or blob).

        :param str container_name:
            Name of existing container.
        :param str path:
            Path of the directory/blob.
        :param str owner:
            Sets the owner of the file or directory.
        :param str group:
            Sets the owning group of the file or directory.
        :param str permissions:
            Invalid in conjunction with acl.
            Sets POSIX access permissions for the file owner, the file owning group, and others.
            Each class may be granted read, write, or execute permission.
            The sticky bit is also supported. Both symbolic (rwxrw-rw-)
            and 4-digit octal notation (e.g. 0766) are supported.
        :param str acl:
            Invalid in conjunction with permissions.
            Sets POSIX access control rights on files and directories.
            The value is a comma-separated list of access control entries that fully replaces the existing
            access control list (ACL). Each access control entry (ACE) consists of a scope, a type,
            a user or group identifier, and permissions in the format "[scope:][type]:[id]:[permissions]".
            The scope must be "default" to indicate the ACE belongs to the default ACL for a directory;
            otherwise scope is implicit and the ACE belongs to the access ACL.
            There are four ACE types: "user" grants rights to the owner or a named user,
            "group" grants rights to the owning group or a named group,
            "mask" restricts rights granted to named users and the members of groups,
            and "other" grants rights to all users not found in any of the other entries.
            The user or group identifier is omitted for entries of type "mask" and "other".
            The user or group identifier is also omitted for the owner and owning group.
            The permission field is a 3-character sequence where the first character is 'r' to grant read access,
            the second character is 'w' to grant write access, and the third character is 'x'
            to grant execute permission. If access is not granted, the '-' character is used to denote
            that the permission is denied. For example, the following ACL grants read, write, and execute rights to
            the file owner and john.doe@contoso, the read right to the owning group,
            and nothing to everyone else: "user::rwx,user:john.doe@contoso:rwx,group::r--,other::---,mask=rwx".
        :param str lease_id:
            Required if the path has an active lease.
        :param datetime if_modified_since:
            A date and time value. Specify this header to perform the operation only if the resource
            has been modified since the specified date and time.
        :param datetime if_unmodified_since:
            A date and time value. Specify this header to perform the operation only if the resource
            has not been modified since the specified date and time.
        :param datetime if_match:
            An ETag value. Specify this header to perform the operation
            only if the resource's ETag matches the value specified. The ETag must be specified in quotes.
        :param datetime if_none_match:
            An ETag value or the special wildcard ("*") value.
            Specify this header to perform the operation only if the resource's ETag
            does not match the value specified. The ETag must be specified in quotes.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: ETag and last modified time of the new directory.
        :rtype: :class:`~azure.storage.blob.models.ResourceProperties`
        """
        _validate_not_none('path', path)

        request = HTTPRequest()
        # TODO remove endpoint swapping after service update
        request.host_locations = self._swap_blob_endpoints(self._get_host_locations())
        request.method = 'PATCH'
        request.path = _get_path(container_name, path)
        request.query = {
            'action': 'setAccessControl',
            'timeout': _int_to_str(timeout),
        }
        request.headers = {
            'x-ms-owner': _to_str(owner),
            'x-ms-group': _to_str(group),
            'x-ms-permissions': _to_str(permissions),
            'x-ms-acl': _to_str(acl),
            'x-ms-lease-id': _to_str(lease_id),
            'If-Modified-Since': _datetime_to_utc_string(if_modified_since),
            'If-Unmodified-Since': _datetime_to_utc_string(if_unmodified_since),
            'If-Match': _to_str(if_match),
            'If-None-Match': _to_str(if_none_match),
        }
        return self._perform_request(request, parser=_parse_base_properties)

    # ----------------------------Helpers for directory manipulations---------------------------- #
    @staticmethod
    def _swap_blob_endpoints(host_locations):
        # Note that only the primary endpoint is supported for the DFS endpoint
        return {LocationMode.PRIMARY: host_locations[LocationMode.PRIMARY].replace(_BLOB_SERVICE_PUBLIC_CLOUD_HOST,
                                                                                   _DFS_SERVICE_PUBLIC_CLOUD_HOST, 1)}
