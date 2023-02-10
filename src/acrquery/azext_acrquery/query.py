# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.log import get_logger
    
from ._docker_utils import get_access_credentials, request_data_from_registry

logger = get_logger(__name__)

ACR_IMAGE_SUFFIX = "/acr/v1/"
DEFAULT_PAGINATION = 100

#az acr query -n MyRegistry --repository ubuntu -q "Manifests | where annotations['org.cncf.notary.signature.subject'] == 'wabbit-networks.io' | project createdAt, digest, subject"

#POST https://myregistry.azurecr.io/acr/v1/ubuntu/_metadata/_query?api-version=2021-08-01-preview
         #canarycabarker.azurecr.io/acr/v1/_metadata/_query?api-version=2021-08-01-preview
# {
# "query": "Manifests | where annotations['org.cncf.notary.signature.subject'] == 'wabbit-networks.io' | project createdAt, digest, subject"
# }

def create_query(cmd, registry_name, kql_query, repository_name=None, skip_token=None, username=None, password=None):
    '''Create a query.'''

    login_server, username, password = get_access_credentials(
        cmd=cmd,
        registry_name=registry_name,
        tenant_suffix=None,
        username=username,
        password=password)

    # "/acr/v1/"
    # queryPath = ACR_IMAGE_SUFFIX
    # if repository_name != None:
    #     # "/acr/v1/ubuntu/"
    #     queryPath = queryPath + repository_name + "/" 

    # queryPath = queryPath + "_metadata/_query?api-version=2021-08-01-preview"

    # json_payload = {
    #     'query': kql_query
    # }

    # print("query", queryPath, " user, ", username," pass, ", password, " payload ", json_payload)
    # print( _obtain_metadata_from_registry(
    #     login_server=login_server,
    #     path=queryPath,
    #     username=username,
    #     password=password, 
    #     json_payload=json_payload))
    return 

def _obtain_metadata_from_registry(login_server,
                               path,
                               username,
                               password,
                               json_payload=None):
    result_list = []
    execute_next_http_call = True

    while execute_next_http_call:
        execute_next_http_call = False

        result, next_link = request_data_from_registry(
            http_method='post',
            login_server=login_server,
            path=path,
            username=username,
            password=password,
            json_payload=json_payload)

        if result:
            result_list += result

        # if top is not None and top <= 0:
        #     break

        # if next_link:
        #     # The registry is telling us there's more items in the list,
        #     # and another call is needed. The link header looks something
        #     # like `Link: </v2/_catalog?last=hello-world&n=1>; rel="next"`
        #     # we should follow the next path indicated in the link header
        #     next_link_path = next_link[(next_link.index('<') + 1):next_link.index('>')]

        #     tokens = next_link_path.split('?', 1)

        #     params = {y[0]: unquote(y[1]) for y in (x.split('=', 1) for x in tokens[1].split('&'))}
        #     execute_next_http_call = True

    return result_list
