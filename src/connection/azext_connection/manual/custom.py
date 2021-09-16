# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.cli.core.util import sdk_no_wait
from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    ValidationError
)
from ._resource_config import SUPPORTED_AUTH_TYPE, TARGET_RESOURCES
from ._validators import (
    get_source_resource_name,
    get_target_resource_name
)
from ._addon_factory import AddonFactory


err_msg = 'Required argument missing, please provide the prompt info or the arguments: {}'


def connection_list(client,
                    source_resource_group=None,
                    source_id=None,
                    webapp=None,
                    spring_service=None,
                    app_name=None,
                    deployment_name=None):
    if not source_id:
        raise RequiredArgumentMissingError(err_msg.format('--source-id'))
    return client.list(resource_uri=source_id)


def connection_list_support_types(cmd, client,
                                  target_resource_type=None):
    results = []
    source = get_source_resource_name(cmd)

    targets = SUPPORTED_AUTH_TYPE.get(source).keys()
    if target_resource_type is not None:
        targets = []
        for resource in TARGET_RESOURCES:
            if target_resource_type == resource.value:
                targets.append(resource)
                break

    for target in targets:
        for auth_type in SUPPORTED_AUTH_TYPE.get(source).get(target):
            results.append({
                'source': source.value,
                'target': target.value,
                'auth_type': auth_type.value
            })

    return results


def connection_show(client,
                    connection_name=None,
                    source_resource_group=None,
                    source_id=None,
                    id=None,
                    webapp=None,
                    spring_service=None,
                    app_name=None,
                    deployment_name=None):
    if not source_id or not connection_name:
        raise RequiredArgumentMissingError(err_msg.format('--source-id, --connection-name'))
    return client.get(resource_uri=source_id,
                      linker_name=connection_name)


def connection_delete(client,
                      connection_name=None,
                      source_resource_group=None,
                      source_id=None,
                      id=None,
                      webapp=None,
                      spring_service=None,
                      app_name=None,
                      deployment_name=None):
    if not source_id or not connection_name:
        raise RequiredArgumentMissingError(err_msg.format('--source-id, --connection-name'))
    return client.delete(resource_uri=source_id,
                         linker_name=connection_name)


def connection_list_configuration(client,
                                  connection_name=None,
                                  source_resource_group=None,
                                  source_id=None,
                                  id=None,
                                  webapp=None,
                                  spring_service=None,
                                  app_name=None,
                                  deployment_name=None):
    if not source_id or not connection_name:
        raise RequiredArgumentMissingError(err_msg.format('--source-id, --connection-name'))
    return client.list_configurations(resource_uri=source_id,
                                      linker_name=connection_name)


def connection_validate(client,
                        connection_name=None,
                        source_resource_group=None,
                        source_id=None,
                        id=None,
                        webapp=None,
                        spring_service=None,
                        app_name=None,
                        deployment_name=None,
                        no_wait=False):
    if not source_id or not connection_name:
        raise RequiredArgumentMissingError(err_msg.format('--source-id, --connection-name'))
    return sdk_no_wait(no_wait,
                       client.validate_linker,
                       resource_uri=source_id,
                       linker_name=connection_name)


def connection_create(client,
                      connection_name=None, client_type=None,
                      source_resource_group=None, source_id=None,
                      target_resource_group=None, target_id=None,
                      secret_auth_info=None, user_identity_auth_info=None, system_identity_auth_info=None, service_principal_auth_info=None,
                      no_wait=False,
                      webapp=None,                                                                               # Resource.WebApp
                      spring_service=None, app_name=None, deployment_name=None,                                  # Resource.SpringCloud
                      postgres=None, database=None,                                                              # Resource.Postgres
                      vault_name=None,                                                                           # Resource.KeyVault
                      cosmos_account_name=None, key_space=None, db_name=None, graph_name=None, table_name=None,  # Resource.CosmosCassandra, CosmosGremlin, CosmosMongo, CosmosSql, CosmosTable
                      server_name=None,                                                                          # Resource.FlexibleCosmosSql, MysqlFlexible, Mysql
                      storage_account_name=None):                                                                # Resource.StorageBlob, StorageQueue, StorageFile, StorageTable

    if not source_id or not connection_name or not target_id:
        raise RequiredArgumentMissingError(err_msg.format('--source-id, --connection-name', '--target-id'))

    all_auth_info = []
    if secret_auth_info is not None:
        all_auth_info.append(secret_auth_info)
    if user_identity_auth_info is not None:
        all_auth_info.append(user_identity_auth_info)
    if system_identity_auth_info is not None:
        all_auth_info.append(system_identity_auth_info)
    if service_principal_auth_info is not None:
        all_auth_info.append(service_principal_auth_info)
    if len(all_auth_info) > 1:
        raise ValidationError('at most one of secret_auth_info, user_identity_auth_info, '
                              'system_identity_auth_info, service_principal_auth_info is needed for auth_info!')
    auth_info = all_auth_info[0] if len(all_auth_info) == 1 else None
    parameters = dict()
    parameters['target_id'] = target_id
    parameters['auth_info'] = auth_info
    parameters['client_type'] = client_type

    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       resource_uri=source_id,
                       linker_name=connection_name,
                       parameters=parameters)


def connection_addons(cmd, client,
                      connection_name=None,
                      source_resource_group=None,
                      source_id=None,
                      client_type=None,
                      target_resource_group=None,
                      secret_auth_info=None,
                      user_identity_auth_info=None,
                      system_identity_auth_info=None,
                      service_principal_auth_info=None,
                      no_wait=False,
                      webapp=None,
                      spring_cloud=None):

    target_type = get_target_resource_name(cmd)
    addon_factory = AddonFactory(target_type, source_id)
    target_id, auth_info = addon_factory.create()

    parameters = dict()
    parameters['target_id'] = target_id
    parameters['auth_info'] = auth_info
    parameters['client_type'] = client_type
    return sdk_no_wait(no_wait,
                       client.begin_create_or_update,
                       resource_uri=source_id,
                       linker_name=connection_name,
                       parameters=parameters)
