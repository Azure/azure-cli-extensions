# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azure.cli.core.profiles import ResourceType, get_sdk
from azext_connectedk8s._client_factory import _graph_client_factory
from azext_connectedk8s._client_factory import _resource_client_factory
from azext_connectedk8s._client_factory import _auth_client_factory
import datetime
from msrest.serialization import TZ_UTC
from dateutil.relativedelta import relativedelta
import uuid
from azure.graphrbac.models import (PasswordCredential, ApplicationCreateParameters, ServicePrincipalCreateParameters)
from knack.log import get_logger
from azext_connectedk8s._multi_api_adaptor import MultiAPIAdaptor

logger = get_logger(__name__)

def create_connectedk8s(cmd, client, subscription_name, resource_group_name, cluster_name, onboarding_spn_id=None, onboarding_spn_secret=None, location=None, tags=None):
    resource_group_params = {'location': location}
    rg_client = _resource_client_factory(cmd.cli_ctx)
    rg_client.resource_groups.create_or_update(resource_group_name, resource_group_params)
    if(onboarding_spn_id is None):
        graph_client = _graph_client_factory(cmd.cli_ctx)
        role_client = _auth_client_factory(cmd.cli_ctx).role_assignments
        scopes = ['/subscriptions/' + role_client.config.subscription_id]
        print(scopes)
        years = 1
        import time
        app_start_date = datetime.datetime.now(TZ_UTC)
        app_end_date = app_start_date + relativedelta(years=years)
        app_display_name = ('azure-cli-' + app_start_date.strftime('%Y-%m-%d-%H-%M-%S'))
        name = 'http://' + app_display_name
        password = str(uuid.uuid4())
        aad_application = create_application(cmd,
                                         display_name=app_display_name,
                                         homepage='https://' + app_display_name,
                                         identifier_uris=[name],
                                         available_to_other_tenants=False,
                                         password=password,
                                         key_value=None,
                                         start_date=app_start_date,
                                         end_date=app_end_date,
                                         credential_description='rbac')
        _RETRY_TIMES = 36
        app_id = aad_application.app_id
        aad_sp = None
        for l in range(0, _RETRY_TIMES):
            try:
                aad_sp = _create_service_principal(cmd.cli_ctx, app_id, resolve_app=False)
                break
            except Exception as ex:  # pylint: disable=broad-except
                if l < _RETRY_TIMES and (
                        ' does not reference ' in str(ex) or ' does not exist ' in str(ex)):
                    time.sleep(5)
                    logger.warning('Retrying service principal creation: %s/%s', l + 1, _RETRY_TIMES)
                else:
                    logger.warning(
                        "Creating service principal failed for appid '%s'. Trace followed:\n%s",
                        name, ex.response.headers if hasattr(ex,
                                                             'response') else ex)  # pylint: disable=no-member
                    raise
        role = 'Contributor'
        sp_oid = aad_sp.object_id
        for scope in scopes:
            logger.warning('Creating a role assignment under the scope of "%s"', scope)
            for l in range(0, _RETRY_TIMES):
                try:
                    _create_role_assignment(cmd.cli_ctx, role, sp_oid, None, scope, resolve_assignee=False)
                    print("created rass")
                    break
                except Exception as ex:
                    if l < _RETRY_TIMES and ' does not exist in the directory ' in str(ex):
                        time.sleep(5)
                        logger.warning('  Retrying role assignment creation: %s/%s', l + 1,
                                       _RETRY_TIMES)
                        continue
                    elif _error_caused_by_role_assignment_exists(ex):
                        logger.warning('  Role assignment already exits.\n')
                        break
                    else:
                        # dump out history for diagnoses
                        logger.warning('  Role assignment creation failed.\n')
                        if getattr(ex, 'response', None) is not None:
                            logger.warning('  role assignment response headers: %s\n',
                                           ex.response.headers)  # pylint: disable=no-member
                    raise
        print(app_id)
        print(password)
        print(name)
        print(app_display_name)
        print(graph_client.config.tenant_id)
    return client.create(subscription_name, resource_group_name, cluster_name, onboarding_spn_id, onboarding_spn_secret, "connected_cluster")


def list_connectedk8s(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `connectedk8s list`')


def update_connectedk8s(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance

def create_application(cmd, display_name, homepage=None, identifier_uris=None,  # pylint: disable=too-many-locals
                       available_to_other_tenants=False, password=None, reply_urls=None,
                       key_value=None, key_type=None, key_usage=None, start_date=None, end_date=None,
                       oauth2_allow_implicit_flow=None, required_resource_accesses=None, native_app=None,
                       credential_description=None, app_roles=None):
    print(identifier_uris)
    graph_client = _graph_client_factory(cmd.cli_ctx)
    password_creds = [PasswordCredential(start_date=start_date, end_date=end_date, key_id=str(uuid.uuid4()), value=password, custom_key_identifier=None)]
    app_create_param = ApplicationCreateParameters(available_to_other_tenants=False,
                                                   display_name=display_name,
                                                   identifier_uris=identifier_uris,
                                                   homepage='https://' + display_name,
                                                   reply_urls=None,
                                                   key_credentials=None,
                                                   password_credentials=password_creds,
                                                   oauth2_allow_implicit_flow=None,
                                                   required_resource_access=None,
                                                   app_roles=None)
    try:
        result = graph_client.applications.create(app_create_param)
    except GraphErrorException as ex:
        if 'insufficient privileges' in str(ex).lower():
            link = 'https://docs.microsoft.com/azure/azure-resource-manager/resource-group-create-service-principal-portal'  # pylint: disable=line-too-long
            raise CLIError("Directory permission is needed for the current user to register the application. "
                           "For how to configure, please refer '{}'. Original error: {}".format(link, ex))
        raise
    return result

def _create_service_principal(cli_ctx, identifier, resolve_app=True):
    client = _graph_client_factory(cli_ctx)
    app_id = identifier
    if resolve_app:
        if _is_guid(identifier):
            result = list(client.applications.list(filter="appId eq '{}'".format(identifier)))
        else:
            result = list(client.applications.list(
                filter="identifierUris/any(s:s eq '{}')".format(identifier)))

        try:
            if not result:  # assume we get an object id
                result = [client.applications.get(identifier)]
            app_id = result[0].app_id
        except GraphErrorException:
            pass  # fallback to appid (maybe from an external tenant?)

    return client.service_principals.create(ServicePrincipalCreateParameters(app_id=app_id, account_enabled=True))

def _error_caused_by_role_assignment_exists(ex):
    return getattr(ex, 'status_code', None) == 409 and 'role assignment already exists' in ex.message

def _create_role_assignment(cli_ctx, role, assignee, resource_group_name=None, scope=None,
                            resolve_assignee=True, assignee_principal_type=None):
    factory = _auth_client_factory(cli_ctx, scope)
    assignments_client = factory.role_assignments
    definitions_client = factory.role_definitions
    role = 'b24988ac-6180-42a0-ab88-20f7382dd24c'
    role_id = '/subscriptions/{}/providers/Microsoft.Authorization/roleDefinitions/{}'.format(definitions_client.config.subscription_id, role)
    object_id = assignee
    worker = MultiAPIAdaptor(cli_ctx)
    return worker.create_role_assignment(assignments_client, uuid.uuid4(), role_id, object_id, scope,
                                         assignee_principal_type)