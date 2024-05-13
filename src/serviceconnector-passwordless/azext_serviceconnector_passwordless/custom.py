# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def connection_create_ext(cmd, client,  # pylint: disable=too-many-locals,too-many-statements
                          connection_name=None, client_type=None,
                          source_resource_group=None, source_id=None,
                          target_resource_group=None, target_id=None,
                          secret_auth_info=None, secret_auth_info_auto=None,
                          user_identity_auth_info=None, system_identity_auth_info=None,
                          service_principal_auth_info_secret=None,
                          key_vault_id=None,
                          app_config_id=None,
                          service_endpoint=None,
                          private_endpoint=None,
                          store_in_connection_string=False,
                          new_addon=False, no_wait=False,
                          yes=False,
                          # Resource.KubernetesCluster
                          cluster=None, scope=None, enable_csi=False,
                          customized_keys=None,
                          opt_out_list=None,
                          site=None, slot=None,                                  # Resource.WebApp
                          spring=None, app=None, deployment='default',           # Resource.SpringCloud
                          # Resource.*Postgres, Resource.*Sql*
                          server=None, database=None,
                          **kwargs,
                          ):
    from azure.cli.command_modules.serviceconnector.custom import connection_create_func
    from ._credential_free import get_enable_mi_for_db_linker_func
    return connection_create_func(cmd, client, connection_name, client_type,
                                  source_resource_group, source_id,
                                  target_resource_group, target_id,
                                  secret_auth_info, secret_auth_info_auto,
                                  user_identity_auth_info, system_identity_auth_info,
                                  service_principal_auth_info_secret,
                                  key_vault_id,
                                  service_endpoint,
                                  private_endpoint,
                                  store_in_connection_string,
                                  new_addon, no_wait,
                                  # Resource.KubernetesCluster
                                  cluster, scope, enable_csi,
                                  site, slot,
                                  spring, app, deployment,
                                  server, database,
                                  enable_mi_for_db_linker=get_enable_mi_for_db_linker_func(yes),
                                  customized_keys=customized_keys,
                                  opt_out_list=opt_out_list,
                                  app_config_id=app_config_id,
                                  **kwargs)


def local_connection_create_ext(cmd, client,  # pylint: disable=too-many-locals,too-many-statements
                                resource_group_name,
                                connection_name=None,
                                location=None,
                                client_type=None,
                                target_resource_group=None, target_id=None,
                                secret_auth_info=None, secret_auth_info_auto=None,
                                user_account_auth_info=None,                      # new auth info
                                service_principal_auth_info_secret=None,
                                no_wait=False,
                                customized_keys=None,
                                yes=False,
                                # Resource.*Postgres, Resource.*Sql*
                                server=None, database=None,
                                **kwargs
                                ):
    from azure.cli.command_modules.serviceconnector.custom import local_connection_create_func
    from ._credential_free import get_enable_mi_for_db_linker_func
    return local_connection_create_func(cmd, client,
                                        resource_group_name,
                                        connection_name,
                                        location,
                                        client_type,
                                        target_resource_group, target_id,
                                        secret_auth_info, secret_auth_info_auto,
                                        user_account_auth_info,                      # new auth info
                                        service_principal_auth_info_secret,
                                        no_wait,
                                        # Resource.*Postgres, Resource.*Sql*
                                        server, database,
                                        enable_mi_for_db_linker=get_enable_mi_for_db_linker_func(yes),
                                        customized_keys=customized_keys,
                                        **kwargs)
