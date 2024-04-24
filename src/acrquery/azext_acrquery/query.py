# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.log import get_logger
from azure.cli.command_modules.acr._docker_utils import get_access_credentials, request_data_from_registry, RegistryAccessTokenPermission, RepoAccessTokenPermission

logger = get_logger(__name__)

ACR_IMAGE_SUFFIX = "/acr/v1/"
ACR_METADATA_PATH = "_metadata/_query"


def create_query(cmd, registry_name, kql_query, repository=None, skip_token=None, username=None, password=None):
    '''Create a query.'''

    if repository:
        login_server, username, password = get_access_credentials(
            cmd=cmd,
            registry_name=registry_name,
            username=username,
            password=password,
            repository=repository,
            permission=RepoAccessTokenPermission.METADATA_READ.value)
    else:
        login_server, username, password = get_access_credentials(
            cmd=cmd,
            registry_name=registry_name,
            username=username,
            password=password,
            repository=repository,
            permission=RegistryAccessTokenPermission.CATALOG.value)

    queryPath = ACR_IMAGE_SUFFIX

    if repository is not None:
        queryPath = queryPath + repository + "/"

    queryPath = queryPath + ACR_METADATA_PATH

    if skip_token:
        json_payload = {
            'query': kql_query,
            'options': {
                '$skipToken': skip_token
            }
        }
    else:
        json_payload = {
            'query': kql_query
        }

    return _obtain_metadata_from_registry(
        login_server=login_server,
        path=queryPath,
        username=username,
        password=password,
        json_payload=json_payload)[0]


def _obtain_metadata_from_registry(login_server,
                                   path,
                                   username,
                                   password,
                                   json_payload):

    result = request_data_from_registry(
        http_method='post',
        login_server=login_server,
        path=path,
        username=username,
        password=password,
        json_payload=json_payload)

    return result
