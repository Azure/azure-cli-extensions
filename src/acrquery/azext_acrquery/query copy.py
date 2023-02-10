# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import time
import json
from azure.core.rest import HttpRequest
from knack.log import get_logger
from azure.cli.core.azclierror import ResourceNotFoundError, RequiredArgumentMissingError, ClientRequestError, AzureConnectionError, AzureResponseError, AzureInternalError
from azure.core.utils import case_insensitive_dict
from azure.cli.core._profile import Profile
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id
from knack.util import CLIError
    
from azure.cli.command_modules.acr._docker_utils import get_access_credentials, RepoAccessTokenPermission, request_data_from_registry

logger = get_logger(__name__)

ACR_IMAGE_SUFFIX = "/acr/v1/"
DEFAULT_PAGINATION = 100

# EMPTY_GUID = '00000000-0000-0000-0000-000000000000'
# AAD_TOKEN_BASE_ERROR_MESSAGE = "Unable to get AAD authorization tokens with message"
# ALLOWS_BASIC_AUTH = "allows_basic_auth"


# class RepoAccessTokenPermission(Enum):
#     METADATA_READ = 'metadata_read'
#     METADATA_WRITE = 'metadata_write'
#     DELETE = 'delete'
#     DELETED_READ = 'deleted_read'
#     DELETED_RESTORE = 'deleted_restore'
#     PULL = 'pull'
#     META_WRITE_META_READ = '{},{}'.format(METADATA_WRITE, METADATA_READ)
#     DELETE_META_READ = '{},{}'.format(DELETE, METADATA_READ)
#     PULL_META_READ = '{},{}'.format(PULL, METADATA_READ)
#     DELETED_READ_RESTORE = '{},{}'.format(DELETED_READ, DELETED_RESTORE)

# class RegistryAccessTokenPermission(Enum):
#     CATALOG = 'catalog'
#     DELETED_CATALOG = 'deleted_catalog'


# class HelmAccessTokenPermission(Enum):
#     PULL = 'pull'
#     PUSH = 'push'
#     DELETE = 'delete'
#     PUSH_PULL = 'push,pull'
#     DELETE_PULL = 'delete,pull'

#az acr query -n MyRegistry --repository ubuntu -q "Manifests | where annotations['org.cncf.notary.signature.subject'] == 'wabbit-networks.io' | project createdAt, digest, subject"

#POST https://myregistry.azurecr.io/acr/v1/ubuntu/_metadata/_query?api-version=2021-08-01-preview
         #canarycabarker.azurecr.io/acr/v1/_metadata/_query?api-version=2021-08-01-preview
# {
# "query": "Manifests | where annotations['org.cncf.notary.signature.subject'] == 'wabbit-networks.io' | project createdAt, digest, subject"
# }

def create_query(cmd, registry_name, kql_query, repository_name=None, skip_token=None, username=None, password=None):
    '''Create a query.'''

    #get_credentials(cmd, username, password)
    #from azure.cli.core._profile import Profile
    #client = Profile(cli_ctx=cmd.cli_ctx)
    #creds, _, _  = profile.get_raw_token()
    #login_server, username, password = get_access_credentials(
    login_server, username, password = get_access_credentials(
        cmd=cmd,
        registry_name=registry_name,
        tenant_suffix=None,
        username=username,
        password=password)
        
   #########################
    # #/myregistry.azurecr.io/acr/v1/
    # queryURL = "https://" + registry_name + ACR_IMAGE_SUFFIX 

    # if repoistory_name != None:
    #     queryURL = queryURL + repoistory_name + "/"

    # queryURL = queryURL + "_metadata/_query"
    
    # headers = {
    #     'Authorization': 'Bearer ' + token
    # }

    # payload = {
    #     'query': kql_query
    # }
    # #print("query", queryURL, "headers, ", headers, "paydload ", payload)

    # result = requests.post(queryURL, headers=headers, json=payload)
    
    # json_results = json.loads(result.text)
    # #return json_results
    ##################### 
    # "/acr/v1/"
    queryPath = ACR_IMAGE_SUFFIX
    if repository_name != None:
        # "/acr/v1/ubuntu/"
        queryPath = queryPath + repository_name + "/" 

    queryPath = queryPath + "_metadata/_query?api-version=2021-08-01-preview"

    json_payload = {
        'query': kql_query
    }

    print("query", queryPath, " user, ", username," pass, ", password, " payload ", json_payload)
    print( _obtain_metadata_from_registry(
        login_server=login_server,
        path=queryPath,
        username=username,
        password=password, 
        json_payload=json_payload))
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

# def get_credentials(cmd, username, password):
#     # cli_ctx = cmd.cli_ctx
#     # subscription = get_subscription_id(cli_ctx)
#     # client = Profile(cli_ctx=cmd.cli_ctx)

#     # creds, _, _ = client.get_raw_token(subscription=subscription)
#     # print(client.get_raw_token(subscription=subscription))

#     if not username and not password:
#         raise CLIError('Please also specify username if password is specified.')

    
# def _get_credentials(cmd,  # pylint: disable=too-many-statements
#                      registry_name,
#                      tenant_suffix,
#                      username,
#                      password,
#                      only_refresh_token,
#                      repository=None,
#                      artifact_repository=None,
#                      permission=None,
#                      is_login_context=False):
#     """Try to get AAD authorization tokens or admin user credentials.
#     :param str registry_name: The name of container registry
#     :param str tenant_suffix: The registry login server tenant suffix
#     :param str username: The username used to log into the container registry
#     :param str password: The password used to log into the container registry
#     :param bool only_refresh_token: Whether to ask for only refresh token, or for both refresh and access tokens
#     :param str repository: Repository for which the access token is requested
#     :param str artifact_repository: Artifact repository for which the access token is requested
#     :param str permission: The requested permission on the repository, '*' or 'pull'
#     """
#     # Raise an error if password is specified but username isn't
#     if not username and password:
#         raise CLIError('Please also specify username if password is specified.')

#     cli_ctx = cmd.cli_ctx
#     resource_not_found, registry = None, None
#     try:
#         registry, resource_group_name = get_registry_by_name(cli_ctx, registry_name)
#         login_server = registry.login_server
#         if tenant_suffix:
#             logger.warning(
#                 "Obtained registry login server '%s' from service. The specified suffix '%s' is ignored.",
#                 login_server, tenant_suffix)
#     except (ResourceNotFound, CLIError) as e:
#         resource_not_found = str(e)
#         logger.debug("Could not get registry from service. Exception: %s", resource_not_found)
#         if not isinstance(e, ResourceNotFound) and _AZ_LOGIN_MESSAGE not in resource_not_found:
#             raise
#         # Try to use the pre-defined login server suffix to construct login server from registry name.
#         login_server_suffix = get_login_server_suffix(cli_ctx)
#         if not login_server_suffix:
#             raise
#         login_server = '{}{}{}'.format(
#             registry_name, '-{}'.format(tenant_suffix) if tenant_suffix else '', login_server_suffix).lower()

#     # Validate the login server is reachable
#     url = 'https://' + login_server + '/v2/'
#     try:
#         logger.debug(add_timestamp("Sending a HTTP Get request to {}".format(url)))
#         challenge = requests.get(url, verify=(not should_disable_connection_verify()))
#         if challenge.status_code == 403:
#             raise CLIError("Looks like you don't have access to registry '{}'. "
#                            "To see configured firewall rules, run 'az acr show --query networkRuleSet --name {}'. "
#                            "To see if public network access is enabled, run 'az acr show --query publicNetworkAccess'."
#                            "Please refer to https://aka.ms/acr/errors#connectivity_forbidden_error for more information."  # pylint: disable=line-too-long
#                            .format(login_server, registry_name))
#     except RequestException as e:
#         logger.debug("Could not connect to registry login server. Exception: %s", str(e))
#         if resource_not_found:
#             logger.warning("%s\nUsing '%s' as the default registry login server.", resource_not_found, login_server)

#         from azure.cli.command_modules.acr.check_health import ACR_CHECK_HEALTH_MSG
#         check_health_msg = ACR_CHECK_HEALTH_MSG.format(registry_name)
#         raise CLIError("Could not connect to the registry login server '{}'. "
#                        "Please verify that the registry exists and the URL '{}' is reachable from your environment.\n{}"
#                        .format(login_server, url, check_health_msg))

#     # 1. if username was specified, verify that password was also specified
#     if username:
#         if not password:
#             try:
#                 password = prompt_pass(msg='Password: ')
#             except NoTTYException:
#                 raise CLIError('Please specify both username and password in non-interactive mode.')

#         username, password = _get_token_with_username_and_password(
#             login_server, username, password, repository, artifact_repository, permission, is_login_context
#         )
#         return login_server, username, password

#     # 2. if we don't yet have credentials, attempt to get a refresh token
#     if not registry or registry.sku.name in get_managed_sku(cmd):
#         logger.info("Attempting to retrieve AAD refresh token...")
#         try:
#             use_acr_audience = False

#             if registry:
#                 aad_auth_policy = acr_config_authentication_as_arm_show(cmd, registry_name, resource_group_name)
#                 use_acr_audience = (aad_auth_policy and aad_auth_policy.status == 'disabled')

#             return login_server, EMPTY_GUID, _get_aad_token(cli_ctx,
#                                                             login_server,
#                                                             only_refresh_token,
#                                                             repository,
#                                                             artifact_repository,
#                                                             permission,
#                                                             use_acr_audience=use_acr_audience)
#         except CLIError as e:
#             logger.warning("%s: %s", AAD_TOKEN_BASE_ERROR_MESSAGE, str(e))

#     # # 3. if we still don't have credentials, attempt to get the admin credentials (if enabled)
#     # if registry:
#     #     if registry.admin_user_enabled:
#     #         logger.info("Attempting with admin credentials...")
#     #         try:
#     #             cred = cf_acr_registries(cli_ctx).list_credentials(resource_group_name, registry_name)
#     #             return login_server, cred.username, cred.passwords[0].value
#     #         except CLIError as e:
#     #             logger.warning("%s: %s", ADMIN_USER_BASE_ERROR_MESSAGE, str(e))
#     #     else:
#     #         logger.warning("%s: %s", ADMIN_USER_BASE_ERROR_MESSAGE, "Admin user is disabled.")
#     # else:
#     #     logger.warning("%s: %s", ADMIN_USER_BASE_ERROR_MESSAGE, resource_not_found)

#     # 4. if we still don't have credentials, prompt the user
#     try:
#         username = prompt('Username: ')
#         password = prompt_pass(msg='Password: ')
#         username, password = _get_token_with_username_and_password(
#             login_server, username, password, repository, artifact_repository, permission, is_login_context
#         )
#         return login_server, username, password
#     except NoTTYException:
#         raise CLIError(
#             'Unable to authenticate using AAD ' +
#             'Please specify both username and password in non-interactive mode.')

#     return login_server, None, None


# def get_login_server_suffix(cli_ctx):
#     """Get the Azure Container Registry login server suffix in the current cloud."""
#     try:
#         return cli_ctx.cloud.suffixes.acr_login_server_endpoint
#     except CloudSuffixNotSetException as e:
#         logger.debug("Could not get login server endpoint suffix. Exception: %s", str(e))
#         # Ignore the error if the suffix is not set, the caller should then try to get login server from server.
#         return None

# def _get_token_with_username_and_password(login_server,
#                                           username,
#                                           password,
#                                           repository=None,
#                                           artifact_repository=None,
#                                           permission=None,
#                                           is_login_context=False,
#                                           is_diagnostics_context=False):
#     """Decides and obtains credentials for a registry using username and password.
#        To be used for scoped access credentials.
#     :param str login_server: The registry login server URL to log in to
#     :param bool only_refresh_token: Whether to ask for only refresh token, or for both refresh and access tokens
#     :param str repository: Repository for which the access token is requested
#     :param str artifact_repository: Artifact repository for which the access token is requested
#     :param str permission: The requested permission on the repository, '*' or 'pull'
#     """

#     if is_login_context:
#         return username, password

#     token_params = _handle_challenge_phase(
#         login_server, repository, artifact_repository, permission, False, is_diagnostics_context
#     )

#     from azure.cli.command_modules.acr._errors import ErrorClass
#     if isinstance(token_params, ErrorClass):
#         if is_diagnostics_context:
#             return token_params
#         raise CLIError(token_params.get_error_message())

#     if ALLOWS_BASIC_AUTH in token_params:
#         return username, password

#     if repository:
#         scope = 'repository:{}:{}'.format(repository, permission)
#     elif artifact_repository:
#         scope = 'artifact-repository:{}:{}'.format(artifact_repository, permission)
#     else:
#         # Registry level permissions only have * as permission, even for a read operation
#         scope = 'registry:{}:*'.format(permission)

#     authurl = urlparse(token_params['realm'])
#     authhost = urlunparse((authurl[0], authurl[1], '/oauth2/token', '', '', ''))
#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#     content = {
#         'service': token_params['service'],
#         'grant_type': 'password',
#         'username': username,
#         'password': password,
#         'scope': scope
#     }

#     logger.debug(add_timestamp("Sending a HTTP Post request to {}".format(authhost)))
#     response = requests.post(authhost, urlencode(content), headers=headers,
#                              verify=(not should_disable_connection_verify()))

#     if response.status_code != 200:
#         from azure.cli.command_modules.acr._errors import CONNECTIVITY_ACCESS_TOKEN_ERROR
#         if is_diagnostics_context:
#             return CONNECTIVITY_ACCESS_TOKEN_ERROR.format_error_message(login_server, response.status_code)
#         raise CLIError(CONNECTIVITY_ACCESS_TOKEN_ERROR.format_error_message(login_server, response.status_code)
#                        .get_error_message())

#     access_token = loads(response.content.decode("utf-8"))["access_token"]

#     return EMPTY_GUID, access_token

# def _get_aad_token(cli_ctx,
#                    login_server,
#                    only_refresh_token,
#                    repository=None,
#                    artifact_repository=None,
#                    permission=None,
#                    is_diagnostics_context=False,
#                    use_acr_audience=False):
#     """Obtains refresh and access tokens for an AAD-enabled registry.
#     :param str login_server: The registry login server URL to log in to
#     :param bool only_refresh_token: Whether to ask for only refresh token, or for both refresh and access tokens
#     :param str repository: Repository for which the access token is requested
#     :param str artifact_repository: Artifact repository for which the access token is requested
#     :param str permission: The requested permission on the repository, '*' or 'pull'
#     """
#     token_params = _handle_challenge_phase(
#         login_server, repository, artifact_repository, permission, True, is_diagnostics_context
#     )
#     from azure.cli.command_modules.acr._errors import ErrorClass
#     if isinstance(token_params, ErrorClass):
#         if is_diagnostics_context:
#             return token_params
#         raise CLIError(token_params.get_error_message())

#     return _get_aad_token_after_challenge(cli_ctx,
#                                           token_params,
#                                           login_server,
#                                           only_refresh_token,
#                                           repository,
#                                           artifact_repository,
#                                           permission,
#                                           is_diagnostics_context,
#                                           use_acr_audience)

# def _handle_challenge_phase(login_server,
#                             repository,
#                             artifact_repository,
#                             permission,
#                             is_aad_token=True,
#                             is_diagnostics_context=False):

#     if repository and artifact_repository:
#         raise ValueError("Only one of repository and artifact_repository can be provided.")

#     repo_permissions = {permission.value for permission in RepoAccessTokenPermission}
#     if repository and permission not in repo_permissions:
#         raise ValueError(
#             "Permission is required for a repository. Allowed access token permission: {}"
#             .format(repo_permissions))

#     helm_permissions = {permission.value for permission in HelmAccessTokenPermission}
#     if artifact_repository and permission not in helm_permissions:
#         raise ValueError(
#             "Permission is required for an artifact_repository. Allowed access token permission: {}"
#             .format(helm_permissions))

#     login_server = login_server.rstrip('/')

#     request_url = 'https://' + login_server + '/v2/'
#     logger.debug(add_timestamp("Sending a HTTP Get request to {}".format(request_url)))
#     challenge = requests.get(request_url, verify=(not should_disable_connection_verify()))

#     if challenge.status_code != 401 or 'WWW-Authenticate' not in challenge.headers:
#         from azure.cli.command_modules.acr._errors import CONNECTIVITY_CHALLENGE_ERROR
#         if is_diagnostics_context:
#             return CONNECTIVITY_CHALLENGE_ERROR.format_error_message(login_server)
#         raise CLIError(CONNECTIVITY_CHALLENGE_ERROR.format_error_message(login_server).get_error_message())

#     authenticate = challenge.headers['WWW-Authenticate']

#     tokens = authenticate.split(' ', 2)

#     if not is_aad_token and tokens[0].lower() == 'basic':
#         return {ALLOWS_BASIC_AUTH: True}

#     token_params = {y[0]: y[1].strip('"') for y in (x.strip().split('=', 2) for x in tokens[1].split(','))} \
#         if len(tokens) >= 2 and tokens[0].lower() == 'bearer' else None

#     if not token_params or 'realm' not in token_params or 'service' not in token_params:
#         from azure.cli.command_modules.acr._errors import CONNECTIVITY_AAD_LOGIN_ERROR, CONNECTIVITY_WWW_AUTHENTICATE_ERROR
#         error = CONNECTIVITY_AAD_LOGIN_ERROR if is_aad_token else CONNECTIVITY_WWW_AUTHENTICATE_ERROR

#         if is_diagnostics_context:
#             return error.format_error_message(login_server)
#         raise CLIError(error.format_error_message(login_server).get_error_message())

#     return token_params

# def _get_aad_token_after_challenge(cli_ctx,
#                                    token_params,
#                                    login_server,
#                                    only_refresh_token,
#                                    repository,
#                                    artifact_repository,
#                                    permission,
#                                    is_diagnostics_context,
#                                    use_acr_audience):
#     authurl = urlparse(token_params['realm'])
#     authhost = urlunparse((authurl[0], authurl[1], '/oauth2/exchange', '', '', ''))

#     from azure.cli.core._profile import Profile
#     profile = Profile(cli_ctx=cli_ctx)

#     scope = None
#     if use_acr_audience:
#         logger.debug("Using ACR audience token for authentication")
#         scope = "https://{}.azure.net".format(ACR_AUDIENCE_RESOURCE_NAME)

#     # this might be a cross tenant scenario, so pass subscription to get_raw_token
#     subscription = get_subscription_id(cli_ctx)
#     creds, _, tenant = profile.get_raw_token(subscription=subscription,
#                                              resource=scope)

#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#     content = {
#         'grant_type': 'access_token',
#         'service': token_params['service'],
#         'tenant': tenant,
#         'access_token': creds[1]
#     }

#     logger.debug(add_timestamp("Sending a HTTP Post request to {}".format(authhost)))
#     response = requests.post(authhost, urlencode(content), headers=headers,
#                              verify=(not should_disable_connection_verify()))

#     if response.status_code not in [200]:
#         from azure.cli.command_modules.acr._errors import CONNECTIVITY_REFRESH_TOKEN_ERROR
#         if is_diagnostics_context:
#             return CONNECTIVITY_REFRESH_TOKEN_ERROR.format_error_message(login_server, response.status_code)
#         raise CLIError(CONNECTIVITY_REFRESH_TOKEN_ERROR.format_error_message(login_server, response.status_code)
#                        .get_error_message())

#     refresh_token = loads(response.content.decode("utf-8"))["refresh_token"]
#     if only_refresh_token:
#         return refresh_token

#     authhost = urlunparse((authurl[0], authurl[1], '/oauth2/token', '', '', ''))

#     if repository:
#         scope = 'repository:{}:{}'.format(repository, permission)
#     elif artifact_repository:
#         scope = 'artifact-repository:{}:{}'.format(artifact_repository, permission)
#     else:
#         # Registry level permissions only have * as permission, even for a read operation
#         scope = 'registry:{}:*'.format(permission)
#     content = {
#         'grant_type': 'refresh_token',
#         'service': login_server,
#         'scope': scope,
#         'refresh_token': refresh_token
#     }

#     logger.debug(add_timestamp("Sending a HTTP Post request to {}".format(authhost)))
#     response = requests.post(authhost, urlencode(content), headers=headers,
#                              verify=(not should_disable_connection_verify()))

#     if response.status_code not in [200]:
#         from azure.cli.command_modules.acr._errors import CONNECTIVITY_ACCESS_TOKEN_ERROR
#         if is_diagnostics_context:
#             return CONNECTIVITY_ACCESS_TOKEN_ERROR.format_error_message(login_server, response.status_code)
#         raise CLIError(CONNECTIVITY_ACCESS_TOKEN_ERROR.format_error_message(login_server, response.status_code)
#                        .get_error_message())

#     return loads(response.content.decode("utf-8"))["access_token"]