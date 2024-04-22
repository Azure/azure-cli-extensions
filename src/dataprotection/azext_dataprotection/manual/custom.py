# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=line-too-long
# pylint: disable=too-many-branches
# pylint: disable=protected-access
# pylint: disable=unused-argument
# pylint: disable=too-many-nested-blocks
# pylint: disable=no-else-continue
# pylint: disable=no-else-raise
import time
from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    InvalidArgumentValueError,
    CLIInternalError,
    ForbiddenError,
    UnauthorizedError
)
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.command_modules.role.custom import list_role_assignments, create_role_assignment
from knack.log import get_logger
from knack.prompting import prompt_y_n
from msrestazure.tools import is_valid_resource_id, parse_resource_id
from azext_dataprotection.vendored_sdks.resourcegraph.models import \
    QueryRequest, QueryRequestOptions
from azext_dataprotection.manual import backupcenter_helper, helpers as helper
from azext_dataprotection.aaz.latest.dataprotection.backup_vault import Show as BackupVaultGet

logger = get_logger(__name__)


def dataprotection_resource_guard_list_protected_operations(cmd, resource_group_name, resource_guard_name, resource_type):
    from azext_dataprotection.aaz.latest.dataprotection.resource_guard import Show as ResourceGuardShow
    resource_guard_object = ResourceGuardShow(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": resource_group_name,
        "resource_guard_name": resource_guard_name,
    })
    protected_operations = resource_guard_object.get('properties').get('resourceGuardOperations')
    resource_type_protected_operation = []
    for protected_operation in protected_operations:
        if resource_type in protected_operation.get('vaultCriticalOperation'):
            resource_type_protected_operation.append(protected_operation)
    return resource_type_protected_operation


def dataprotection_backup_instance_validate_for_backup(cmd, vault_name, resource_group_name, backup_instance,
                                                       no_wait=False):

    from azext_dataprotection.aaz.latest.dataprotection.backup_instance import ValidateForBackup as _ValidateForBackup

    class Validate(_ValidateForBackup):

        @classmethod
        def _build_arguments_schema(cls, *args, **kwargs):
            args_schema = super()._build_arguments_schema(*args, **kwargs)

            args_schema.backup_instance.data_source_set_info.resource_id._required = False
            args_schema.backup_instance.datasource_auth_credentials.\
                secret_store_based_auth_credentials.secret_store_resource.secret_store_type._required = False

            return args_schema

        class BackupInstancesValidateForBackup(_ValidateForBackup.BackupInstancesValidateForBackup):

            @property
            def content(self):
                body = helper.convert_dict_keys_snake_to_camel(backup_instance['properties'])

                return {
                    "backupInstance": body
                }

    return Validate(cli_ctx=cmd.cli_ctx)(command_args={
        "vault_name": vault_name,
        "resource_group": resource_group_name,
        "backup_instance": backup_instance['properties'],
        "no_wait": no_wait,
    })


def dataprotection_backup_instance_initialize_backupconfig(datasource_type, excluded_resource_types=None,
                                                           included_resource_types=None, excluded_namespaces=None,
                                                           included_namespaces=None, label_selectors=None,
                                                           snapshot_volumes=None, include_cluster_scope_resources=None,
                                                           backup_hook_references=None):
    if snapshot_volumes is None:
        snapshot_volumes = True
    if include_cluster_scope_resources is None:
        include_cluster_scope_resources = True

    return {
        "excluded_resource_types": excluded_resource_types,
        "included_resource_types": included_resource_types,
        "excluded_namespaces": excluded_namespaces,
        "included_namespaces": included_namespaces,
        "label_selectors": label_selectors,
        "snapshot_volumes": snapshot_volumes,
        "include_cluster_scope_resources": include_cluster_scope_resources,
        "backup_hook_references": backup_hook_references
    }


def dataprotection_backup_instance_initialize(datasource_type, datasource_id, datasource_location, policy_id,
                                              friendly_name=None, backup_configuration=None,
                                              secret_store_type=None, secret_store_uri=None,
                                              snapshot_resource_group_name=None, tags=None):
    manifest = helper.load_manifest(datasource_type)

    datasource_info = helper.get_datasource_info(datasource_type, datasource_id, datasource_location)

    datasourceset_info = None
    if manifest["isProxyResource"]:
        datasourceset_info = helper.get_datasourceset_info(datasource_type, datasource_id, datasource_location)

    policy_parameters = None
    if manifest["addDataStoreParametersList"]:
        policy_parameters = helper.get_policy_parameters(datasource_id, snapshot_resource_group_name)

    datasource_auth_credentials_info = None
    if manifest["supportSecretStoreAuthentication"]:
        datasource_auth_credentials_info = helper.get_datasource_auth_credentials_info(secret_store_type, secret_store_uri)

    policy_info = {
        "policy_id": policy_id,
        "policy_parameters": policy_parameters
    }

    friendly_name = helper.get_friendly_name(datasource_type, friendly_name, datasourceset_info, datasource_info)

    backup_instance_name = helper.get_backup_instance_name(datasource_type, datasourceset_info, datasource_info)

    if manifest["addBackupDatasourceParametersList"]:
        if backup_configuration is None:
            raise RequiredArgumentMissingError("Please input parameter backup-configuration for AKS cluster backup. \
                           Use command az dataprotection backup-instance initialize-backupconfig \
                           for creating the backup-configuration")
        backup_configuration["object_type"] = "KubernetesClusterBackupDatasourceParameters"
        policy_info["policy_parameters"]["backup_datasource_parameters_list"] = []
        policy_info["policy_parameters"]["backup_datasource_parameters_list"].append(backup_configuration)
    else:
        if backup_configuration is not None:
            logger.warning("--backup-configuration is not required for the given DatasourceType, and will not be used")

    return {
        "backup_instance_name": backup_instance_name,
        "properties": {
            "data_source_info": datasource_info,
            "data_source_set_info": datasourceset_info,
            "policy_info": policy_info,
            "datasource_auth_credentials": datasource_auth_credentials_info,
            "friendly_name": friendly_name,
            "object_type": "BackupInstance"
        },
        "tags": tags
    }


def dataprotection_backup_instance_update_policy(cmd, resource_group_name, vault_name, backup_instance_name, policy_id, no_wait=False):
    from azext_dataprotection.aaz.latest.dataprotection.backup_instance import Show as BackupInstanceShow
    backup_instance = BackupInstanceShow(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": resource_group_name,
        "vault_name": vault_name,
        "backup_instance_name": backup_instance_name
    })
    policy_info = backup_instance['properties']['policyInfo']
    policy_info['policyId'] = policy_id

    from azext_dataprotection.aaz.latest.dataprotection.backup_instance import Update
    return Update(cli_ctx=cmd.cli_ctx)(command_args={
        "no_wait": no_wait,
        "backup_instance_name": backup_instance_name,
        "resource_group": resource_group_name,
        "vault_name": vault_name,
        "policy_info": policy_info
    })


def dataprotection_backup_instance_list_from_resourcegraph(client, datasource_type=None, resource_groups=None, vaults=None,
                                                           subscriptions=None, protection_status=None, datasource_id=None,
                                                           backup_instance_id=None, backup_instance_name=None):
    if subscriptions is None:
        subscriptions = [backupcenter_helper.get_selected_subscription()]
    query = backupcenter_helper.get_backup_instance_query(datasource_type, resource_groups, vaults, protection_status,
                                                          datasource_id, backup_instance_id, backup_instance_name)
    request_options = QueryRequestOptions(
        top=1000,
        skip=0
    )
    request = QueryRequest(query=query, subscriptions=subscriptions, options=request_options)
    response = client.resources(request)
    return response.data


def dataprotection_backup_vault_list_from_resourcegraph(client, resource_groups=None, vaults=None,
                                                        subscriptions=None, vault_id=None):
    if subscriptions is None:
        subscriptions = [backupcenter_helper.get_selected_subscription()]
    query = backupcenter_helper.get_backup_vault_query(resource_groups, vaults, vault_id)

    request_options = QueryRequestOptions(
        top=1000,
        skip=0
    )
    request = QueryRequest(query=query, subscriptions=subscriptions, options=request_options)
    response = client.resources(request)
    return response.data


def dataprotection_backup_instance_update_msi_permissions(cmd, resource_group_name, datasource_type, vault_name, operation,
                                                          permissions_scope, backup_instance=None, restore_request_object=None,
                                                          keyvault_id=None, snapshot_resource_group_id=None,
                                                          target_storage_account_id=None, yes=False):
    if operation == 'Backup' and backup_instance is None:
        raise RequiredArgumentMissingError("--backup-instance needs to be given when --operation is given as Backup")

    if operation == "Restore" and restore_request_object is None:
        raise RequiredArgumentMissingError("--restore-request-object needs to be given when --operation is given as Restore")

    if datasource_type == 'AzureDatabaseForPostgreSQL':
        if not keyvault_id:
            raise RequiredArgumentMissingError("--keyvault-id needs to be given when --datasource-type is AzureDatabaseForPostgreSQL")
        if not is_valid_resource_id(keyvault_id):
            raise InvalidArgumentValueError("Please provide a valid keyvault ID")

    manifest = helper.load_manifest(datasource_type)

    warning_message = helper.get_help_text_on_grant_permissions_templatized(datasource_type, operation)
    if not yes and not prompt_y_n(warning_message):
        return None

    backup_vault = BackupVaultGet(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": resource_group_name,
        "vault_name": vault_name
    })
    vault_principal_id = backup_vault['identity']['principalId']

    role_assignments_arr = []

    if operation == "Backup":
        if helper.datasource_map[datasource_type] != backup_instance["properties"]["data_source_info"]["datasource_type"]:
            raise InvalidArgumentValueError("--backup-instance provided is not compatible with the --datasource-type.")

        if backup_instance['properties']['data_source_info']['resource_location'] != backup_vault['location']:
            raise InvalidArgumentValueError("Location of data source needs to be the same as backup vault.\nMake sure the datasource "
                                            "and vault are chosen properly")

        keyvault_client = None
        keyvault = None
        keyvault_subscription = None
        keyvault_name = None
        keyvault_rg = None
        if manifest['supportSecretStoreAuthentication']:
            cmd.command_kwargs['operation_group'] = 'vaults'
            keyvault_update = False

            from azure.cli.core.profiles import ResourceType
            from azure.cli.command_modules.keyvault._client_factory import Clients, data_plane_azure_keyvault_secret_client

            keyvault_params = parse_resource_id(keyvault_id)
            keyvault_subscription = keyvault_params['subscription']
            keyvault_name = keyvault_params['name']
            keyvault_rg = keyvault_params['resource_group']

            keyvault_client = getattr(get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_KEYVAULT, subscription_id=keyvault_subscription), Clients.vaults)

            keyvault = keyvault_client.get(resource_group_name=keyvault_rg, vault_name=keyvault_name)

            # Check if keyvault is not publicly accessible
            if keyvault.properties.public_network_access == 'Disabled':
                raise UnauthorizedError("Keyvault has public access disabled. Please enable public access, or grant access to your client IP")

            # Check if the secret URI provided in backup instance is a valid secret
            cmd.command_kwargs['vault_base_url'] = keyvault.properties.vault_uri
            data_secrets_client = data_plane_azure_keyvault_secret_client(cmd.cli_ctx, cmd.command_kwargs)
            secrets_list = data_secrets_client.list_properties_of_secrets()
            given_secret_uri = backup_instance['properties']['datasource_auth_credentials']['secret_store_resource']['uri']
            given_secret_id = helper.get_secret_params_from_uri(given_secret_uri)['secret_id']
            valid_secret = False
            for secret in secrets_list:
                if given_secret_id == secret.id:
                    valid_secret = True
                    break

            if not valid_secret:
                raise InvalidArgumentValueError("The secret URI provided in the --backup-instance is not associated with the "
                                                "--keyvault-id provided. Please input a valid combination of secret URI and "
                                                "--keyvault-id.")

            keyvault_permission_models = manifest['secretStorePermissions']
            if keyvault.properties.enable_rbac_authorization:
                role = keyvault_permission_models['rbacModel']['roleDefinitionName']

                keyvault_assignment_scope = helper.truncate_id_using_scope(keyvault_id, permissions_scope)

                role_assignment = list_role_assignments(cmd, assignee=vault_principal_id, role=role, scope=keyvault_id, include_inherited=True)
                if not role_assignment:
                    assignment = create_role_assignment(cmd, assignee=vault_principal_id, role=role, scope=keyvault_assignment_scope)
                    role_assignments_arr.append(helper.get_permission_object_from_role_object(assignment))

            else:
                from azure.cli.command_modules.keyvault.custom import set_policy
                vault_secret_permissions = (keyvault_permission_models['vaultAccessPolicyModel']
                                            ['accessPolicies']
                                            ['permissions']
                                            ['secrets'])

                secrets_array = []
                for policy in keyvault.properties.access_policies:
                    if policy.object_id == vault_principal_id:
                        secrets_array = policy.permissions.secrets
                        break

                permissions_set = True
                for permission in vault_secret_permissions:
                    if permission not in secrets_array:
                        permissions_set = False
                        secrets_array.append(permission)

                if not permissions_set:
                    keyvault_update = True
                    keyvault = set_policy(cmd, keyvault_client, keyvault_rg, keyvault_name, object_id=vault_principal_id, secret_permissions=secrets_array)
                    keyvault = keyvault.result()

            from azure.cli.command_modules.keyvault.custom import update_vault_setter

            if keyvault.properties.network_acls:
                if keyvault.properties.network_acls.bypass == 'None':
                    keyvault_update = True
                    keyvault.properties.network_acls.bypass = 'AzureServices'
                    update_vault_setter(cmd, keyvault_client, keyvault, resource_group_name=keyvault_rg, vault_name=keyvault_name)

            if keyvault_update:
                role_assignments_arr.append(helper.get_permission_object_from_keyvault(keyvault))

        if 'backupVaultPermissions' in manifest:
            for role_object in manifest['backupVaultPermissions']:
                role_assignments_arr = helper.check_and_assign_roles(cmd, permissions_scope=permissions_scope, role_object=role_object,
                                                                     backup_instance=backup_instance, principal_id=vault_principal_id,
                                                                     role_assignments_arr=role_assignments_arr)

        if 'dataSourcePermissions' in manifest:
            datasource_principal_id = helper.get_datasource_principal_id_from_object(cmd, datasource_type,
                                                                                     backup_instance=backup_instance)
            for role_object in manifest['dataSourcePermissions']:
                role_assignments_arr = helper.check_and_assign_roles(cmd, permissions_scope=permissions_scope, role_object=role_object,
                                                                     backup_instance=backup_instance, principal_id=datasource_principal_id,
                                                                     role_assignments_arr=role_assignments_arr)

        # Network line of sight access on server, if that is the datasource type
        if datasource_type == 'AzureDatabaseForPostgreSQL':
            server_params = parse_resource_id(backup_instance['properties']['data_source_info']['resource_id'])
            server_sub = server_params['subscription']
            server_name = server_params['name']
            server_rg = server_params['resource_group']

            from azure.mgmt.rdbms.postgresql import PostgreSQLManagementClient
            postgres_firewall_client = getattr(get_mgmt_service_client(cmd.cli_ctx, PostgreSQLManagementClient, subscription_id=server_sub), 'firewall_rules')

            firewall_rule_list = postgres_firewall_client.list_by_server(resource_group_name=server_rg, server_name=server_name)

            allow_access_to_azure_ips = False
            for rule in firewall_rule_list:
                if rule.start_ip_address == rule.end_ip_address and rule.start_ip_address == '0.0.0.0':
                    allow_access_to_azure_ips = True
                    break

            if not allow_access_to_azure_ips:
                firewall_rule_name = 'AllowAllWindowsAzureIps'
                parameters = {'name': firewall_rule_name, 'start_ip_address': '0.0.0.0', 'end_ip_address': '0.0.0.0'}

                rule = postgres_firewall_client.begin_create_or_update(server_rg, server_name, firewall_rule_name, parameters)
                role_assignments_arr.append(helper.get_permission_object_from_server_firewall_rule(rule.result()))
    elif operation == "Restore":
        if datasource_type not in ("AzureKubernetesService", "AzureDatabaseForMySQL",
                                   "AzureDatabaseForPostgreSQLFlexibleServer"):
            raise InvalidArgumentValueError("Set permissions for restore is currently not supported for given DataSourceType")

        for role_object in manifest['backupVaultRestorePermissions']:
            role_assignments_arr = helper.check_and_assign_roles(cmd, permissions_scope=permissions_scope, role_object=role_object,
                                                                 restore_request_object=restore_request_object, principal_id=vault_principal_id,
                                                                 role_assignments_arr=role_assignments_arr,
                                                                 target_storage_account_id=target_storage_account_id,
                                                                 snapshot_resource_group_id=snapshot_resource_group_id)

        if 'dataSourcePermissions' in manifest:
            datasource_principal_id = helper.get_datasource_principal_id_from_object(cmd, datasource_type,
                                                                                     restore_request_object=restore_request_object)
            for role_object in manifest['dataSourceRestorePermissions']:
                role_assignments_arr = helper.check_and_assign_roles(cmd, permissions_scope=permissions_scope, role_object=role_object,
                                                                     restore_request_object=restore_request_object, principal_id=datasource_principal_id,
                                                                     role_assignments_arr=role_assignments_arr,
                                                                     target_storage_account_id=target_storage_account_id,
                                                                     snapshot_resource_group_id=snapshot_resource_group_id)

    if not role_assignments_arr:
        logger.warning("The required permissions are already assigned!")
    else:
        # Wait for 60 seconds to let the role assignments propagate
        logger.warning("Waiting for 60 seconds for permissions to propagate")
        time.sleep(60)

    return role_assignments_arr


def dataprotection_job_list_from_resourcegraph(client, datasource_type=None, resource_groups=None, vaults=None,
                                               subscriptions=None, start_time=None, end_time=None,
                                               status=None, operation=None, datasource_id=None):
    if subscriptions is None:
        subscriptions = [backupcenter_helper.get_selected_subscription()]

    query = backupcenter_helper.get_backup_job_query(datasource_type, resource_groups, vaults, start_time, end_time, status, operation, datasource_id)
    request_options = QueryRequestOptions(
        top=1000,
        skip=0
    )
    request = QueryRequest(query=query, subscriptions=subscriptions, options=request_options)
    response = client.resources(request)
    return response.data


def dataprotection_job_list(cmd, resource_group_name, vault_name, use_secondary_region=None,
                            max_items=None, next_token=None):
    from azext_dataprotection.aaz.latest.dataprotection.job import List as ListJobs
    from azext_dataprotection.aaz.latest.dataprotection.cross_region_restore import FetchJobs as ListJobsCRR

    if use_secondary_region:
        source_backup_vault = helper.get_backup_vault_from_resourcegraph(cmd, resource_group_name, vault_name)
        source_backup_vault_id = source_backup_vault['id']
        source_location, target_location = helper.get_source_and_replicated_region_from_backup_vault(source_backup_vault)

        return ListJobsCRR(cli_ctx=cmd.cli_ctx)(command_args={
            "resource_group": resource_group_name,
            "location": target_location,
            "source_backup_vault_id": source_backup_vault_id,
            "source_region": source_location,
            "pagination_limit": max_items,
            "pagination_token": next_token
        })

    return ListJobs(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": resource_group_name,
        "vault_name": vault_name,
        "pagination_limit": max_items,
        "pagination_token": next_token
    })


def dataprotection_job_show(cmd, resource_group_name, vault_name, job_id, use_secondary_region=None):
    from azext_dataprotection.aaz.latest.dataprotection.job import Show as ShowJob
    from azext_dataprotection.aaz.latest.dataprotection.cross_region_restore._fetch_job import FetchJob as ShowJobCRR

    if use_secondary_region:
        source_backup_vault = helper.get_backup_vault_from_resourcegraph(cmd, resource_group_name, vault_name)
        source_backup_vault_id = source_backup_vault['id']
        source_location, target_location = helper.get_source_and_replicated_region_from_backup_vault(source_backup_vault)

        return ShowJobCRR(cli_ctx=cmd.cli_ctx)(command_args={
            "resource_group": resource_group_name,
            "source_backup_vault_id": source_backup_vault_id,
            "job_id": job_id,
            "source_region": source_location,
            "location": target_location
        })

    return ShowJob(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": resource_group_name,
        "vault_name": vault_name,
        "job_id": job_id
    })


def dataprotection_backup_policy_get_default_policy_template(datasource_type):
    manifest = helper.load_manifest(datasource_type)
    if manifest is not None and manifest["policySettings"] is not None and manifest["policySettings"]["defaultPolicy"] is not None:
        return manifest["policySettings"]["defaultPolicy"]
    raise CLIInternalError("Unable to get default policy template.")


def dataprotection_backup_policy_trigger_create_schedule(interval_type, interval_count, schedule_days):
    # Do validations on interval_type and interval_count
    if interval_type.lower() in ["daily", "weekly"] and interval_count != 1:
        raise InvalidArgumentValueError("Interval Count for Daily or Weekly Backup must be 1.")

    if interval_type.lower() == "hourly" and interval_count not in [4, 6, 8, 12]:
        raise InvalidArgumentValueError("Interval Count for Hourly Backup must be one of 4, 6, 8, 12.")

    if interval_count <= 0:
        raise InvalidArgumentValueError("Interval count must be greater than zero.")

    repeating_time_intervals = []
    for day in schedule_days:
        backup_frequency = helper.get_backup_frequency_string(interval_type, interval_count)
        time_interval = "R/" + day + "+00:00/" + backup_frequency
        repeating_time_intervals.append(time_interval)

    return repeating_time_intervals


def dataprotection_backup_policy_create_lifecycle(source_datastore, retention_duration_type, retention_duration_count, target_datastore=None, copy_option=None):
    delete_after = {
        "objectType": "AbsoluteDeleteOption",
        "duration": "P" + str(retention_duration_count) + retention_duration_type[0]
    }

    source_data_store = {
        "objectType": "DataStoreInfoBase",
        "dataStoreType": source_datastore
    }

    copy_settings = None
    if target_datastore is not None and copy_option is not None:
        copy_settings = {
            "dataStore": {
                "objectType": "DataStoreInfoBase",
                "dataStoreType": target_datastore
            },
            "copyAfter": {
                "objectType": copy_option
            }
        }

    return {
        "deleteAfter": delete_after,
        "sourceDataStore": source_data_store,
        "targetDataStoreCopySettings": copy_settings
    }


def dataprotection_backup_policy_retention_set_in_policy(policy, name, lifecycles):
    retention_policy_index = -1
    for index in range(0, len(policy["policyRules"])):
        if policy["policyRules"][index]["objectType"] == "AzureRetentionRule" and policy["policyRules"][index]["name"] == name:
            retention_policy_index = index
            break

    if retention_policy_index == -1:
        datasource_type = helper.get_client_datasource_type(policy["datasourceTypes"][0])
        manifest = helper.load_manifest(datasource_type)
        if manifest["policySettings"]["disableAddRetentionRule"]:
            raise InvalidArgumentValueError("Adding New Retention Rule is not supported for " + datasource_type + " datasource type")

        if name not in manifest["policySettings"]["supportedRetentionTags"]:
            raise InvalidArgumentValueError("Selected Retention Rule " + name + " is not applicable for Datasource Type " + datasource_type)

        new_retention_rule = {
            "objectType": "AzureRetentionRule",
            "isDefault": name == "Default",
            "name": name,
            "lifecycles": lifecycles
        }

        policy["policyRules"].append(new_retention_rule)
        return policy

    policy["policyRules"][retention_policy_index]["lifecycles"] = lifecycles
    return policy


def dataprotection_backup_policy_retention_remove_in_policy(name, policy):
    if name == "Default":
        raise ForbiddenError("Removing Default Retention Rule is not allowed. Please try again with different rule name.")

    for index in range(0, len(policy["policyRules"])):
        if policy["policyRules"][index]["objectType"] == "AzureRetentionRule" and policy["policyRules"][index]["name"] == name:
            policy["policyRules"].pop(index)
            break

    return policy


def dataprotection_backup_policy_trigger_set_in_policy(policy, schedule):
    datasource_type = helper.get_client_datasource_type(policy["datasourceTypes"][0])
    helper.validate_backup_schedule(datasource_type, schedule)

    backup_rule_index = -1
    for index in range(0, len(policy["policyRules"])):
        if policy["policyRules"][index]["objectType"] == "AzureBackupRule":
            backup_rule_index = index
            break

    if index != -1:
        policy["policyRules"][backup_rule_index]["trigger"]["schedule"]["repeatingTimeIntervals"] = schedule
        policy["policyRules"][backup_rule_index]["name"] = helper.get_backup_frequency_from_time_interval(schedule)

    return policy


def dataprotection_backup_policy_create_absolute_criteria(absolute_criteria):
    return {
        "objectType": "ScheduleBasedBackupCriteria",
        "absoluteCriteria": [absolute_criteria]
    }


def dataprotection_backup_policy_create_generic_criteria(days_of_week=None, weeks_of_month=None, months_of_year=None, days_of_month=None):
    days_of_month_criteria = None
    if days_of_month is not None:
        days_of_month_criteria = []
        for day_of_month in days_of_month:
            if day_of_month.isdigit():
                day_of_month = int(day_of_month)
                if day_of_month > 28 or day_of_month < 1:
                    raise InvalidArgumentValueError("Day of month should be between 1 and 28.")
                days_of_month_criteria.append({
                    "date": day_of_month,
                    "is_last": False
                })
            else:
                if day_of_month.lower() != "last":
                    raise InvalidArgumentValueError("Day of month should either be between 1 and 28 or it should be last")
                days_of_month_criteria.append({"is_last": True})

    return {
        "object_type": "ScheduleBasedBackupCriteria",
        "days_of_month": days_of_month_criteria,
        "days_of_the_week": days_of_week,
        "months_of_year": months_of_year,
        "weeks_of_the_month": weeks_of_month
    }


def dataprotection_backup_policy_tag_set_in_policy(name, policy, criteria):
    datasource_type = helper.get_client_datasource_type(policy["datasourceTypes"][0])
    manifest = helper.load_manifest(datasource_type)

    if name not in manifest["policySettings"]["supportedRetentionTags"]:
        raise InvalidArgumentValueError("Selected Retention Tag " + name + " is not applicable for Datasource Type " + datasource_type)

    if manifest["policySettings"]["disableCustomRetentionTag"]:
        for criterion in criteria:
            if "absoluteCriteria" not in criterion:
                raise InvalidArgumentValueError("Only Absolute Criteria is supported for this policy")

    backup_rule_index = -1
    for index in range(0, len(policy["policyRules"])):
        if policy["policyRules"][index]["objectType"] == "AzureBackupRule":
            backup_rule_index = index
            break

    if backup_rule_index != -1:
        tagindex = -1
        for index in range(0, len(policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"])):
            if policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"][index]["tagInfo"]["tagName"] == name:
                tagindex = index
                break

        if tagindex != -1:
            policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"][tagindex]["Criteria"] = criteria
            return policy

        tagcriteria = {
            "criteria": criteria,
            "isDefault": False,
            "taggingPriority": helper.get_tagging_priority(name),
            "tagInfo": {
                "tagName": name
            }
        }

        policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"].append(tagcriteria)
        return policy

    return policy


def dataprotection_backup_policy_tag_remove_in_policy(name, policy):
    backup_rule_index = -1
    for index in range(0, len(policy["policyRules"])):
        if policy["policyRules"][index]["objectType"] == "AzureBackupRule":
            backup_rule_index = index
            break

    for index in range(0, len(policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"])):
        if policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"][index]["tagInfo"]["tagName"] == name:
            policy["policyRules"][backup_rule_index]["trigger"]["taggingCriteria"].pop(index)
            break

    return policy


def dataprotection_recovery_point_list(cmd, backup_instance_name, resource_group_name, vault_name,
                                       start_time=None, end_time=None, use_secondary_region=None,
                                       max_items=None, next_token=None):
    from .aaz_operations.recovery_point import List as RecoveryPointList
    from azext_dataprotection.aaz.latest.dataprotection.cross_region_restore import FetchSecondaryRecoveryPoints

    if use_secondary_region:
        source_backup_instance = helper.get_backup_instance_from_resourcegraph(cmd, resource_group_name, vault_name,
                                                                               backup_instance_name)
        source_backup_instance_id = source_backup_instance['id']
        source_location = source_backup_instance['properties']['backupInstanceExtendedProperties']['protectedPrimaryRegion']
        target_location = source_backup_instance['properties']['backupInstanceExtendedProperties']['protectedSecondaryRegion']

        if start_time or end_time:
            logger.warning("start-time and end-time filters will not work with use-secondary-region option")

        return FetchSecondaryRecoveryPoints(cli_ctx=cmd.cli_ctx)(command_args={
            "resource_group": resource_group_name,
            "location": target_location,
            "source_backup_instance_id": source_backup_instance_id,
            "source_region": source_location,
            "pagination_limit": max_items,
            "pagination_token": next_token
        })

    return RecoveryPointList(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": resource_group_name,
        "vault_name": vault_name,
        "backup_instance_name": backup_instance_name,
        "start_time": start_time,
        "end_time": end_time,
        "pagination_limit": max_items,
        "pagination_token": next_token
    })


def dataprotection_backup_instance_restore_trigger(cmd, vault_name, resource_group_name, backup_instance_name,
                                                   restore_request_object, use_secondary_region=None, no_wait=False):
    from .aaz_operations.backup_instance import (
        RestoreTrigger,
        TriggerCRR
    )

    if use_secondary_region:
        source_backup_instance = helper.get_backup_instance_from_resourcegraph(cmd, resource_group_name, vault_name,
                                                                               backup_instance_name)
        source_backup_instance_id = source_backup_instance['id']
        source_location = source_backup_instance['properties']['backupInstanceExtendedProperties']['protectedPrimaryRegion']
        target_location = source_backup_instance['properties']['backupInstanceExtendedProperties']['protectedSecondaryRegion']

        return TriggerCRR(cli_ctx=cmd.cli_ctx)(command_args={
            "resource_group": resource_group_name,
            "location": target_location,
            "source_backup_instance_id": source_backup_instance_id,
            "source_region": source_location,
            "restore_request_object": restore_request_object,
            "no_wait": no_wait
        })

    return RestoreTrigger(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": resource_group_name,
        "vault_name": vault_name,
        "backup_instance_name": backup_instance_name,
        "restore_request_object": restore_request_object,
        "no_wait": no_wait
    })


def dataprotection_backup_instance_validate_for_restore(cmd, vault_name, resource_group_name, backup_instance_name,
                                                        restore_request_object, use_secondary_region=None, no_wait=False):
    from .aaz_operations.backup_instance import (
        ValidateForCRR as CRRValidateRestore,
        ValidateForRestore as BackupInstanceValidateRestore,
    )

    if use_secondary_region:
        source_backup_instance = helper.get_backup_instance_from_resourcegraph(cmd, resource_group_name, vault_name,
                                                                               backup_instance_name)
        source_backup_instance_id = source_backup_instance['id']
        source_location = source_backup_instance['properties']['backupInstanceExtendedProperties']['protectedPrimaryRegion']
        target_location = source_backup_instance['properties']['backupInstanceExtendedProperties']['protectedSecondaryRegion']

        return CRRValidateRestore(cli_ctx=cmd.cli_ctx)(command_args={
            "resource_group": resource_group_name,
            "location": target_location,
            "source_backup_instance_id": source_backup_instance_id,
            "source_region": source_location,
            "restore_request_object": restore_request_object,
            "no_wait": no_wait
        })

    return BackupInstanceValidateRestore(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": resource_group_name,
        "vault_name": vault_name,
        "backup_instance_name": backup_instance_name,
        "restore_request_object": restore_request_object,
        "no_wait": no_wait
    })


def dataprotection_backup_instance_initialize_restoreconfig(datasource_type, excluded_resource_types=None,
                                                            included_resource_types=None, excluded_namespaces=None,
                                                            included_namespaces=None, label_selectors=None,
                                                            persistent_volume_restore_mode=None,
                                                            include_cluster_scope_resources=None,
                                                            namespace_mappings=None, conflict_policy=None,
                                                            restore_hook_references=None):
    if datasource_type != "AzureKubernetesService":
        raise InvalidArgumentValueError("This command is currently not supported for datasource types other than AzureKubernetesService")

    object_type = "KubernetesClusterRestoreCriteria"

    if persistent_volume_restore_mode is None:
        persistent_volume_restore_mode = "RestoreWithVolumeData"
    if conflict_policy is None:
        conflict_policy = "Skip"
    if include_cluster_scope_resources is None:
        include_cluster_scope_resources = True

    return {
        "object_type": object_type,
        "excluded_resource_types": excluded_resource_types,
        "included_resource_types": included_resource_types,
        "excluded_namespaces": excluded_namespaces,
        "included_namespaces": included_namespaces,
        "label_selectors": label_selectors,
        "persistent_volume_restore_mode": persistent_volume_restore_mode,
        "include_cluster_scope_resources": include_cluster_scope_resources,
        "conflict_policy": conflict_policy,
        "namespace_mappings": namespace_mappings,
        "restore_hook_references": restore_hook_references
    }


def restore_initialize_for_data_recovery(cmd, datasource_type, source_datastore, restore_location, target_resource_id=None,
                                         recovery_point_id=None, point_in_time=None, secret_store_type=None,
                                         secret_store_uri=None, rehydration_priority=None, rehydration_duration=15,
                                         restore_configuration=None, backup_instance_id=None):
    restore_request = {}
    restore_mode = None
    manifest = helper.load_manifest(datasource_type)

    # Setting up restore request according to Recovery-Point/Point-in-time style of restore
    restore_request, restore_mode = helper.validate_and_set_restore_mode_in_restore_request(recovery_point_id, point_in_time, restore_request)
    # We also check for rehydration priority/duration, in which case restore style changes
    if rehydration_priority:
        restore_request = helper.validate_and_set_rehydration_priority_in_restore_request(rehydration_priority, rehydration_duration, restore_request)

    # Restore mode (assigned during RP/point-in-time validation earlier) should be supported for the workload
    helper.validate_restore_mode_for_workload(restore_mode, datasource_type, manifest)

    # If the source datastore (type) is allowed for the workload, we start creating the restore request object.
    restore_request = helper.validate_and_set_source_datastore_type_in_restore_request(source_datastore, datasource_type,
                                                                                       restore_request, manifest)

    restore_request["restore_target_info"] = helper.get_restore_target_info_basics("RestoreTargetInfo", restore_location)

    # The datasource ID is set either from Backup instance ID or Target Resource Id, depending on restore type
    datasource_id = helper.validate_and_set_datasource_id_in_restore_request(cmd, target_resource_id, backup_instance_id)
    restore_request["restore_target_info"]["datasource_info"] = helper.get_datasource_info(datasource_type, datasource_id, restore_location)

    if manifest["isProxyResource"]:
        restore_request["restore_target_info"]["datasource_set_info"] = helper.get_datasourceset_info(datasource_type, datasource_id, restore_location)

    if manifest["supportSecretStoreAuthentication"]:
        restore_request["restore_target_info"]["datasource_auth_credentials"] = helper.get_datasource_auth_credentials_info(secret_store_type, secret_store_uri)

    # AKS Data-level and Item-level are identical in their configuration, for our purpose, and restore criteria is required for item level
    if datasource_type == 'AzureKubernetesService':
        restore_request["restore_target_info"]["object_type"] = "ItemLevelRestoreTargetInfo"
        restore_request["restore_target_info"]["restore_criteria"] = helper.get_resource_criteria_list(datasource_type, restore_configuration,
                                                                                                       None, None, None)

    return restore_request


def restore_initialize_for_data_recovery_as_files(target_blob_container_url, target_file_name, datasource_type, source_datastore,
                                                  restore_location, target_resource_id=None,
                                                  recovery_point_id=None, point_in_time=None,
                                                  rehydration_priority=None, rehydration_duration=15):
    restore_request = {}
    restore_mode = None
    manifest = helper.load_manifest(datasource_type)

    # Workload should allow for Recover as files
    if manifest is not None and "RestoreAsFiles" not in manifest["allowedRestoreTargetTypes"]:
        raise InvalidArgumentValueError("Specified DatasourceType " + datasource_type + " doesn't support Recovery as Files")

    # Setting up restore request according to Recovery-Point/Point-in-time style of restore
    restore_request, restore_mode = helper.validate_and_set_restore_mode_in_restore_request(recovery_point_id, point_in_time, restore_request)
    # We also check for rehydration priority/duration, in which case restore style changes
    if rehydration_priority:
        restore_request = helper.validate_and_set_rehydration_priority_in_restore_request(rehydration_priority, rehydration_duration, restore_request)

    # Restore mode (assigned during RP/point-in-time validation earlier) should be supported for the workload
    helper.validate_restore_mode_for_workload(restore_mode, datasource_type, manifest)

    # If the source datastore (type) is allowed for the workload, we start creating the restore request object.
    restore_request = helper.validate_and_set_source_datastore_type_in_restore_request(source_datastore, datasource_type,
                                                                                       restore_request, manifest)

    # Constructing the rest of the restore request object. No further validation is being done.
    restore_request["restore_target_info"] = helper.get_restore_target_info_basics("RestoreFilesTargetInfo", restore_location)

    # Currently, restore_target_info.target_details.restore_target_location_type is fixed to AzureBlobs
    restore_request["restore_target_info"]["target_details"] = {}
    restore_request["restore_target_info"]["target_details"]["url"] = target_blob_container_url
    restore_request["restore_target_info"]["target_details"]["file_prefix"] = target_file_name
    restore_request["restore_target_info"]["target_details"]["restore_target_location_type"] = "AzureBlobs"

    # Mandatory for Cross-subscription restore scenario for OSS
    if target_resource_id is not None:
        restore_request["restore_target_info"]["target_details"]["target_resource_arm_id"] = target_resource_id

    return restore_request


def restore_initialize_for_item_recovery(cmd, datasource_type, source_datastore, restore_location, backup_instance_id=None,
                                         target_resource_id=None, recovery_point_id=None, point_in_time=None, container_list=None,
                                         from_prefix_pattern=None, to_prefix_pattern=None, restore_configuration=None):
    restore_request = {}
    restore_mode = None
    manifest = helper.load_manifest(datasource_type)

    # Workload should allow for item level recovery
    if manifest is not None and not manifest["itemLevelRecoveyEnabled"]:
        raise InvalidArgumentValueError("Specified DatasourceType " + datasource_type + " doesn't support Item Level Recovery")

    # Setting up restore request according to Recovery-Point/Point-in-time style of restore
    restore_request, restore_mode = helper.validate_and_set_restore_mode_in_restore_request(recovery_point_id, point_in_time, restore_request)

    # Restore mode (assigned during RP/point-in-time validation earlier) should be supported for the workload
    helper.validate_restore_mode_for_workload(restore_mode, datasource_type, manifest)

    # If the source datastore (type) is allowed for the workload, we start creating the restore request object.
    restore_request = helper.validate_and_set_source_datastore_type_in_restore_request(source_datastore, datasource_type,
                                                                                       restore_request, manifest)

    # Constructing the rest of the restore request object. No further validation is being done.
    restore_request["restore_target_info"] = helper.get_restore_target_info_basics("ItemLevelRestoreTargetInfo", restore_location)

    # The datasource ID is set either from Backup instance ID or Target Resource Id, depending on restore type
    datasource_id = helper.validate_and_set_datasource_id_in_restore_request(cmd, target_resource_id, backup_instance_id)
    restore_request["restore_target_info"]["datasource_info"] = helper.get_datasource_info(datasource_type, datasource_id, restore_location)

    if manifest["isProxyResource"]:
        restore_request["restore_target_info"]["datasource_set_info"] = helper.get_datasourceset_info(datasource_type, datasource_id, restore_location)

    restore_request["restore_target_info"]["restore_criteria"] = helper.get_resource_criteria_list(datasource_type, restore_configuration,
                                                                                                   container_list, from_prefix_pattern,
                                                                                                   to_prefix_pattern)

    return restore_request
