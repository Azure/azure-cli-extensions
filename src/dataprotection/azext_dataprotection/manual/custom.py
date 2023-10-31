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
import uuid
import re
import time
from azure.cli.core.azclierror import (
    RequiredArgumentMissingError,
    InvalidArgumentValueError,
    CLIInternalError,
    ForbiddenError,
    MutuallyExclusiveArgumentError,
    UnauthorizedError
)
from knack.log import get_logger
from azext_dataprotection.vendored_sdks.resourcegraph.models import \
    QueryRequest, QueryRequestOptions
from azext_dataprotection.manual import backupcenter_helper, helpers as helper

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
    datasource_info = helper.get_datasource_info(datasource_type, datasource_id, datasource_location)
    datasourceset_info = None
    manifest = helper.load_manifest(datasource_type)
    if manifest["isProxyResource"]:
        datasourceset_info = helper.get_datasourceset_info(datasource_type, datasource_id, datasource_location)

    policy_parameters = None
    # Azure Disk and AKS specific code for adding datastoreparameter list in the json
    if manifest["addDataStoreParametersList"]:
        policy_parameters = {
            "data_store_parameters_list": [
                {
                    "object_type": "AzureOperationalStoreParameters",
                    "data_store_type": "OperationalStore",
                    "resource_group_id": helper.get_rg_id_from_arm_id(datasource_id)
                }
            ]
        }

        if snapshot_resource_group_name:
            disk_sub_id = helper.get_sub_id_from_arm_id(datasource_id)
            policy_parameters["data_store_parameters_list"][0]["resource_group_id"] = (disk_sub_id + "/resourceGroups/"
                                                                                       + snapshot_resource_group_name)

    datasource_auth_credentials_info = None
    if manifest["supportSecretStoreAuthentication"]:
        if secret_store_uri and secret_store_type:
            datasource_auth_credentials_info = {
                "secret_store_resource": {
                    "uri": secret_store_uri,
                    "value": None,
                    "secret_store_type": secret_store_type
                },
                "object_type": "SecretStoreBasedAuthCredentials"
            }
        elif secret_store_uri or secret_store_type:
            raise RequiredArgumentMissingError("Either secret store uri or secret store type not provided.")

    policy_info = {
        "policy_id": policy_id,
        "policy_parameters": policy_parameters
    }

    # Fetching or setting Friendly name, as appropriate
    # Following earlier patterns, not raising any concern if friendly name is provided where it isn't required
    # However, boilerplate code has been added here as Powershell raises an error here. We might want to flag to the user
    # that their provided friendly name will not be used.
    if not manifest["friendlyNameRequired"] and friendly_name is not None:
        logger.warning("--friendly-name is not a required parameter for the given DatasourceType, and the user input will be overridden")

    # If friendly name is required, we use the user input/validate accordingly if it wasn't provided. If it isn't, we override user input if any
    if manifest["friendlyNameRequired"]:
        if friendly_name is None:
            raise RequiredArgumentMissingError("friendly-name parameter is required for the given DatasourceType")
        friendly_name = datasourceset_info["resource_name"] + "/" + friendly_name
    elif manifest["isProxyResource"]:
        friendly_name = datasourceset_info["resource_name"] + "/" + datasource_info["resource_name"]
    else:
        friendly_name = datasource_info["resource_name"]

    guid = uuid.uuid1()
    backup_instance_name = ""
    if manifest["isProxyResource"]:
        backup_instance_name = datasourceset_info["resource_name"] + "-" + datasource_info["resource_name"] + "-" + str(guid)
    else:
        backup_instance_name = datasource_info["resource_name"] + "-" + datasource_info["resource_name"] + "-" + str(guid)

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


def dataprotection_backup_instance_list_from_resourcegraph(client, datasource_type, resource_groups=None, vaults=None, subscriptions=None, protection_status=None, datasource_id=None):
    if subscriptions is None:
        subscriptions = [backupcenter_helper.get_selected_subscription()]
    query = backupcenter_helper.get_backup_instance_query(datasource_type, resource_groups, vaults, protection_status, datasource_id)
    request_options = QueryRequestOptions(
        top=1000,
        skip=0
    )
    request = QueryRequest(query=query, subscriptions=subscriptions, options=request_options)
    response = client.resources(request)
    return response.data


def dataprotection_backup_instance_update_msi_permissions(cmd, resource_group_name, datasource_type, vault_name, operation,
                                                          permissions_scope, backup_instance=None, restore_request_object=None,
                                                          keyvault_id=None, snapshot_resource_group_id=None, yes=False):
    from msrestazure.tools import is_valid_resource_id, parse_resource_id

    if operation == 'Backup' and backup_instance is None:
        raise RequiredArgumentMissingError("--backup-instance needs to be given when --operation is given as Backup")
    elif operation == "Restore" and restore_request_object is None:
        raise RequiredArgumentMissingError("--restore-request-object needs to be given when --operation is given as Restore")

    if datasource_type == 'AzureDatabaseForPostgreSQL':
        if not keyvault_id:
            raise RequiredArgumentMissingError("--keyvault-id needs to be given when --datasource-type is AzureDatabaseForPostgreSQL")

        if not is_valid_resource_id(keyvault_id):
            raise InvalidArgumentValueError("Please provide a valid keyvault ID")

    datasource_map = {
        "AzureDisk": "Microsoft.Compute/disks",
        "AzureBlob": "Microsoft.Storage/storageAccounts/blobServices",
        "AzureDatabaseForPostgreSQL": "Microsoft.DBforPostgreSQL/servers/databases",
        "AzureKubernetesService": "Microsoft.ContainerService/managedClusters"
    }

    manifest = helper.load_manifest(datasource_type)

    from knack.prompting import prompt_y_n
    msg = helper.get_help_text_on_grant_permissions_templatized(datasource_type)
    if not yes and not prompt_y_n(msg):
        return None

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.cli.command_modules.role.custom import list_role_assignments, create_role_assignment
    from azext_dataprotection.aaz.latest.dataprotection.backup_vault import Show as BackupVaultGet

    backup_vault = BackupVaultGet(cli_ctx=cmd.cli_ctx)(command_args={
        "resource_group": resource_group_name,
        "vault_name": vault_name
    })
    principal_id = backup_vault['identity']['principalId']

    role_assignments_arr = []

    if operation == "Backup":
        if datasource_map[datasource_type] != backup_instance["properties"]["data_source_info"]["datasource_type"]:
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
            from azure.cli.command_modules.keyvault._client_factory import Clients, get_client

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
            data_entity = get_client(cmd.cli_ctx, ResourceType.DATA_KEYVAULT)
            data_client = data_entity.client_factory(cmd.cli_ctx, None)
            secrets_list = data_client.get_secrets(vault_base_url=keyvault.properties.vault_uri)
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

                role_assignment = list_role_assignments(cmd, assignee=principal_id, role=role, scope=keyvault_id, include_inherited=True)
                if not role_assignment:
                    assignment = create_role_assignment(cmd, assignee=principal_id, role=role, scope=keyvault_assignment_scope)
                    role_assignments_arr.append(helper.get_permission_object_from_role_object(assignment))

            else:
                from azure.cli.command_modules.keyvault.custom import set_policy
                vault_secret_permissions = (keyvault_permission_models['vaultAccessPolicyModel']
                                            ['accessPolicies']
                                            ['permissions']
                                            ['secrets'])

                secrets_array = []
                for policy in keyvault.properties.access_policies:
                    if policy.object_id == principal_id:
                        secrets_array = policy.permissions.secrets
                        break

                permissions_set = True
                for permission in vault_secret_permissions:
                    if permission not in secrets_array:
                        permissions_set = False
                        secrets_array.append(permission)

                if not permissions_set:
                    keyvault_update = True
                    keyvault = set_policy(cmd, keyvault_client, keyvault_rg, keyvault_name, object_id=principal_id, secret_permissions=secrets_array)
                    keyvault = keyvault.result()

            from azure.cli.command_modules.keyvault.custom import update_vault_setter

            if keyvault.properties.network_acls:
                if keyvault.properties.network_acls.bypass == 'None':
                    keyvault_update = True
                    keyvault.properties.network_acls.bypass = 'AzureServices'
                    update_vault_setter(cmd, keyvault_client, keyvault, resource_group_name=keyvault_rg, vault_name=keyvault_name)

            if keyvault_update:
                role_assignments_arr.append(helper.get_permission_object_from_keyvault(keyvault))

        for role_object in manifest['backupVaultPermissions']:
            resource_id = helper.get_resource_id_from_backup_instance(backup_instance, role_object['type'])
            resource_id = helper.truncate_id_using_scope(resource_id, "Resource")

            assignment_scope = helper.truncate_id_using_scope(resource_id, permissions_scope)

            role_assignments = list_role_assignments(cmd, assignee=principal_id, role=role_object['roleDefinitionName'],
                                                     scope=resource_id, include_inherited=True)
            if not role_assignments:
                assignment = create_role_assignment(cmd, assignee=principal_id, role=role_object['roleDefinitionName'],
                                                    scope=assignment_scope)
                role_assignments_arr.append(helper.get_permission_object_from_role_object(assignment))

        if 'dataSourcePermissions' in manifest:
            for role_object in manifest['dataSourcePermissions']:
                datasource_principal_id = None

                if datasource_type == "AzureKubernetesService":
                    datasource_arm_id = helper.get_resource_id_from_backup_instance(backup_instance, 'DataSource')
                    subscription_arm_id = helper.get_sub_id_from_arm_id(datasource_arm_id)
                    subscription_id = subscription_arm_id.split("/")[-1]

                    from azext_dataprotection.vendored_sdks.azure_mgmt_preview_aks import ContainerServiceClient
                    aks_client = get_mgmt_service_client(cmd.cli_ctx, ContainerServiceClient, subscription_id=subscription_id)
                    aks_client = getattr(aks_client, 'managed_clusters')
                    aks_name = helper.get_resource_name_from_backup_instance(backup_instance, 'DataSource')
                    aks_rg_id = helper.get_rg_id_from_arm_id(datasource_arm_id)
                    aks_rg = aks_rg_id.split('/')[-1]
                    aks_cluster = aks_client.get(aks_rg, aks_name)

                    if "UserAssigned" in aks_cluster.identity.type:
                        uami_key = list(aks_cluster.identity.user_assigned_identities.keys())[0]
                        if uami_key == "" or uami_key is None:
                            raise CLIInternalError("User assigned identity not found for AKS Cluster")
                        datasource_principal_id = aks_cluster.identity.user_assigned_identities[uami_key].principal_id
                    else:
                        datasource_principal_id = aks_cluster.identity.principal_id
                else:
                    raise InvalidArgumentValueError("Datasource-over-X permissions can currently only be set for Datasource type AzureKubernetesService")

                resource_id = helper.get_resource_id_from_backup_instance(backup_instance, role_object['type'])
                resource_id = helper.truncate_id_using_scope(resource_id, "Resource")
                assignment_scope = helper.truncate_id_using_scope(resource_id, permissions_scope)

                role_assignments = list_role_assignments(cmd, assignee=datasource_principal_id,
                                                         role=role_object['roleDefinitionName'], scope=resource_id,
                                                         include_inherited=True)
                if not role_assignments:
                    assignment = create_role_assignment(cmd, assignee=datasource_principal_id,
                                                        role=role_object['roleDefinitionName'], scope=assignment_scope)
                    role_assignments_arr.append(helper.get_permission_object_from_role_object(assignment))

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
        if datasource_type != "AzureKubernetesService":
            raise InvalidArgumentValueError("Set permissions for restore is currently not supported for given DataSourceType")

        for role_object in manifest['backupVaultPermissions']:
            resource_id = helper.get_resource_id_from_restore_request_object(restore_request_object, role_object['type'])

            if role_object['type'] == 'SnapshotRG':
                if snapshot_resource_group_id is None:
                    logger.warning("snapshot-resource-group-id parameter is required to assign permissions over snapshot resource group, skipping")
                    continue
                else:
                    resource_id = snapshot_resource_group_id

            resource_id = helper.truncate_id_using_scope(resource_id, "Resource")

            assignment_scope = helper.truncate_id_using_scope(resource_id, permissions_scope)

            role_assignments = list_role_assignments(cmd, assignee=principal_id, role=role_object['roleDefinitionName'],
                                                     scope=resource_id, include_inherited=True)
            if not role_assignments:
                assignment = create_role_assignment(cmd, assignee=principal_id, role=role_object['roleDefinitionName'],
                                                    scope=assignment_scope)
                role_assignments_arr.append(helper.get_permission_object_from_role_object(assignment))

        if 'dataSourcePermissions' in manifest:
            for role_object in manifest['dataSourcePermissions']:
                resource_id = helper.get_resource_id_from_restore_request_object(restore_request_object, role_object['type'])

                if role_object['type'] == 'SnapshotRG':
                    if snapshot_resource_group_id is None:
                        logger.warning("snapshot-resource-group-id parameter is required to assign permissions over snapshot resource group, skipping")
                        continue
                    else:
                        resource_id = snapshot_resource_group_id

                resource_id = helper.truncate_id_using_scope(resource_id, "Resource")
                assignment_scope = helper.truncate_id_using_scope(resource_id, permissions_scope)

                datasource_principal_id = None

                if datasource_type == "AzureKubernetesService":
                    datasource_arm_id = helper.get_resource_id_from_restore_request_object(restore_request_object, 'DataSource')
                    subscription_arm_id = helper.get_sub_id_from_arm_id(datasource_arm_id)
                    subscription_id = subscription_arm_id.split("/")[-1]

                    from azext_dataprotection.vendored_sdks.azure_mgmt_preview_aks import ContainerServiceClient
                    aks_client = get_mgmt_service_client(cmd.cli_ctx, ContainerServiceClient, subscription_id=subscription_id)
                    aks_client = getattr(aks_client, 'managed_clusters')
                    aks_name = helper.get_resource_name_from_restore_request_object(restore_request_object, 'DataSource')
                    aks_rg_id = helper.get_rg_id_from_arm_id(datasource_arm_id)
                    aks_rg = aks_rg_id.split('/')[-1]
                    aks_cluster = aks_client.get(aks_rg, aks_name)

                    if "UserAssigned" in aks_cluster.identity.type:
                        uami_key = list(aks_cluster.identity.user_assigned_identities.keys())[0]
                        if uami_key == "" or uami_key is None:
                            raise CLIInternalError("User assigned identity not found for AKS Cluster")
                        datasource_principal_id = aks_cluster.identity.user_assigned_identities[uami_key].principal_id
                    else:
                        datasource_principal_id = aks_cluster.identity.principal_id
                else:
                    raise InvalidArgumentValueError("Datasource-over-X permissions can currently only be set for Datasource type AzureKubernetesService")

                role_assignments = list_role_assignments(cmd, assignee=datasource_principal_id,
                                                         role=role_object['roleDefinitionName'], scope=resource_id,
                                                         include_inherited=True)
                if not role_assignments:
                    assignment = create_role_assignment(cmd, assignee=datasource_principal_id,
                                                        role=role_object['roleDefinitionName'], scope=assignment_scope)
                    role_assignments_arr.append(helper.get_permission_object_from_role_object(assignment))

    if not role_assignments_arr:
        logger.warning("The required permissions are already assigned!")
    else:
        # Wait for 60 seconds to let the role assignments propagate
        logger.warning("Waiting for 60 seconds for permissions to propagate")
        time.sleep(60)

    return role_assignments_arr


def dataprotection_job_list_from_resourcegraph(client, datasource_type, resource_groups=None, vaults=None,
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

    # Input Validation and variable-assignment from params for recovery via RP or point-in-time
    if recovery_point_id is not None and point_in_time is not None:
        raise RequiredArgumentMissingError("Please provide either recovery point id or point in time parameter, not both.")

    if recovery_point_id is not None:
        restore_request["object_type"] = "AzureBackupRecoveryPointBasedRestoreRequest"
        restore_request["recovery_point_id"] = recovery_point_id
        restore_mode = "RecoveryPointBased"

    if point_in_time is not None:
        restore_request["object_type"] = "AzureBackupRecoveryTimeBasedRestoreRequest"
        restore_request["recovery_point_time"] = point_in_time
        restore_mode = "PointInTimeBased"

    if recovery_point_id is None and point_in_time is None:
        raise RequiredArgumentMissingError("Please provide either recovery point id or point in time parameter.")

    manifest = helper.load_manifest(datasource_type)

    # Restore mode (assigned during RP/point-in-time validation earlier) should be supported for the workload
    if manifest is not None and manifest["allowedRestoreModes"] is not None and restore_mode not in manifest["allowedRestoreModes"]:
        raise InvalidArgumentValueError(restore_mode + " restore mode is not supported for datasource type " + datasource_type +
                                        ". Supported restore modes are " + ','.join(manifest["allowedRestoreModes"]))

    # If the source datastore (type) is allowed for the workload, we start creating the restore request object.
    # We also check for rehydration priority/duration in here for some reason? It could be shifted out.
    if source_datastore in manifest["policySettings"]["supportedDatastoreTypes"]:
        restore_request["source_data_store_type"] = source_datastore
        if rehydration_priority:
            if rehydration_duration < 10 or rehydration_duration > 30:
                raise InvalidArgumentValueError("The allowed range of rehydration duration is 10 to 30 days.")
            restore_request["object_type"] = "AzureBackupRestoreWithRehydrationRequest"
            restore_request["rehydration_priority"] = rehydration_priority
            restore_request["rehydration_retention_duration"] = "P" + str(rehydration_duration) + "D"
    else:
        raise InvalidArgumentValueError(source_datastore + " datastore type is not supported for datasource type " + datasource_type +
                                        ". Supported datastore types are " + ','.join(manifest["policySettings"]["supportedDatastoreTypes"]))

    restore_request["restore_target_info"] = {}
    restore_request["restore_target_info"]["restore_location"] = restore_location
    restore_request["restore_target_info"]["recovery_option"] = "FailIfExists"

    datasource_id = None
    # Alternate/Original Location - setting the Target's datasource info accordingly
    if target_resource_id is not None and backup_instance_id is not None:
        raise MutuallyExclusiveArgumentError("Please provide either target-resource-id or backup-instance-id not both.")

    if target_resource_id is not None:
        # No validation for alternate/original location restore, as target_resource_id can be used for both
        datasource_id = target_resource_id

    if backup_instance_id is not None:
        # No validation for alternate/original location restore, to be added if understood to be required
        vault_resource_group = helper.get_vault_rg_from_bi_id(backup_instance_id)
        vault_name = helper.get_vault_name_from_bi_id((backup_instance_id))
        backup_instance_name = helper.get_bi_name_from_bi_id(backup_instance_id)

        from azext_dataprotection.aaz.latest.dataprotection.backup_instance import Show as _Show
        backup_instance = _Show(cli_ctx=cmd.cli_ctx)(command_args={
            "vault_name": vault_name,
            "resource_group": vault_resource_group,
            "backup_instance_name": backup_instance_name
        })
        datasource_id = backup_instance['properties']['dataSourceInfo']['resourceID']

    if backup_instance_id is None and target_resource_id is None:
        raise MutuallyExclusiveArgumentError("Please provide either target-resource-id (for alternate location restore) or backup-instance-id (for original location restore).")

    restore_request["restore_target_info"]["datasource_info"] = helper.get_datasource_info(datasource_type, datasource_id, restore_location)

    # AKS Data-level and Item-level are identical in their configuration, for our purpose
    if datasource_type != 'AzureKubernetesService':
        restore_request["restore_target_info"]["object_type"] = "RestoreTargetInfo"
    else:
        restore_request["restore_target_info"]["object_type"] = "ItemLevelRestoreTargetInfo"

        restore_criteria_list = []
        if restore_configuration is not None:
            restore_criteria = restore_configuration
        else:
            raise RequiredArgumentMissingError("Please input parameter restore_configuration for AKS cluster restore.\n\
                                                Use command initialize-restoreconfig for creating the RestoreConfiguration")
        restore_criteria_list.append(restore_criteria)
        restore_request["restore_target_info"]["restore_criteria"] = restore_criteria_list

    if manifest["isProxyResource"]:
        restore_request["restore_target_info"]["datasource_set_info"] = helper.get_datasourceset_info(datasource_type, datasource_id, restore_location)

    if manifest["supportSecretStoreAuthentication"]:
        if secret_store_uri and secret_store_type:
            restore_request["restore_target_info"]["datasource_auth_credentials"] = {
                "secret_store_resource": {
                    "uri": secret_store_uri,
                    "value": None,
                    "secret_store_type": secret_store_type
                },
                "object_type": "SecretStoreBasedAuthCredentials"
            }
        elif secret_store_uri or secret_store_type:
            raise RequiredArgumentMissingError("Either secret store uri or secret store type not provided.")

    return restore_request


def restore_initialize_for_data_recovery_as_files(target_blob_container_url, target_file_name, datasource_type, source_datastore,
                                                  restore_location, target_resource_id=None,
                                                  recovery_point_id=None, point_in_time=None,
                                                  rehydration_priority=None, rehydration_duration=15):

    restore_request = {}
    restore_mode = None

    # Input Validation and variable-assignment from params for recovery via RP or point-in-time
    if recovery_point_id is not None and point_in_time is not None:
        raise MutuallyExclusiveArgumentError("Please provide either recovery point id or point in time parameter, not both.")

    if recovery_point_id is not None:
        restore_request["object_type"] = "AzureBackupRecoveryPointBasedRestoreRequest"
        restore_request["recovery_point_id"] = recovery_point_id
        restore_mode = "RecoveryPointBased"

    if point_in_time is not None:
        restore_request["object_type"] = "AzureBackupRecoveryTimeBasedRestoreRequest"
        restore_request["recovery_point_time"] = point_in_time
        restore_mode = "PointInTimeBased"

    if recovery_point_id is None and point_in_time is None:
        raise RequiredArgumentMissingError("Please provide either recovery point id or point in time parameter.")

    manifest = helper.load_manifest(datasource_type)

    # Restore mode (assigned during RP/point-in-time validation earlier) should be supported for the workload
    if manifest is not None and manifest["allowedRestoreModes"] is not None and restore_mode not in manifest["allowedRestoreModes"]:
        raise InvalidArgumentValueError(restore_mode + " restore mode is not supported for datasource type " + datasource_type +
                                        ". Supported restore modes are " + ','.join(manifest["allowedRestoreModes"]))

    # If the source datastore (type) is allowed for the workload, we start creating the restore request object.
    # We also check for rehydration priority/duration in here for some reason? It could be shifted out.
    if source_datastore in manifest["policySettings"]["supportedDatastoreTypes"]:
        restore_request["source_data_store_type"] = source_datastore
        if rehydration_priority:
            if rehydration_duration < 10 or rehydration_duration > 30:
                raise InvalidArgumentValueError("The allowed range of rehydration duration is 10 to 30 days.")
            restore_request["object_type"] = "AzureBackupRestoreWithRehydrationRequest"
            restore_request["rehydration_priority"] = rehydration_priority
            restore_request["rehydration_retention_duration"] = "P" + str(rehydration_duration) + "D"
    else:
        raise InvalidArgumentValueError(source_datastore + " datastore type is not supported for datasource type " + datasource_type +
                                        ". Supported datastore types are " + ','.join(manifest["policySettings"]["supportedDatastoreTypes"]))

    # Constructing the rest of the restore request object. No further validation is being done.
    # Currently, restore_target_info.target_details.restore_target_location_type is fixed to AzureBlobs
    # There is no check currently for ensuring that the manifest's allowedRestoreTargetTypes contains RestoreAsFiles
    restore_request["restore_target_info"] = {}
    restore_request["restore_target_info"]["object_type"] = "RestoreFilesTargetInfo"
    restore_request["restore_target_info"]["restore_location"] = restore_location
    restore_request["restore_target_info"]["recovery_option"] = "FailIfExists"
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

    # Input Validation and variable-assignment from params for recovery via RP or point-in-time
    if recovery_point_id is not None and point_in_time is not None:
        raise MutuallyExclusiveArgumentError("Please provide either recovery point id or point in time parameter, not both.")

    if recovery_point_id is not None:
        restore_request["object_type"] = "AzureBackupRecoveryPointBasedRestoreRequest"
        restore_request["recovery_point_id"] = recovery_point_id
        restore_mode = "RecoveryPointBased"

    if point_in_time is not None:
        restore_request["object_type"] = "AzureBackupRecoveryTimeBasedRestoreRequest"
        restore_request["recovery_point_time"] = point_in_time
        restore_mode = "PointInTimeBased"

    if recovery_point_id is None and point_in_time is None:
        raise RequiredArgumentMissingError("Please provide either recovery point id or point in time parameter.")

    manifest = helper.load_manifest(datasource_type)

    # Restore mode (assigned during RP/point-in-time validation earlier) should be supported for the workload
    if manifest is not None and manifest["allowedRestoreModes"] is not None and restore_mode not in manifest["allowedRestoreModes"]:
        raise InvalidArgumentValueError(restore_mode + " restore mode is not supported for datasource type " + datasource_type +
                                        ". Supported restore modes are " + ','.join(manifest["allowedRestoreModes"]))

    # Workload should allow for item level recovery
    if manifest is not None and not manifest["itemLevelRecoveyEnabled"]:
        raise InvalidArgumentValueError("Specified DatasourceType " + datasource_type + " doesn't support Item Level Recovery")

    # Constructing the rest of the restore request object. No further validation is being done.
    restore_request["source_data_store_type"] = source_datastore
    restore_request["restore_target_info"] = {}
    restore_request["restore_target_info"]["object_type"] = "ItemLevelRestoreTargetInfo"
    restore_request["restore_target_info"]["restore_location"] = restore_location
    restore_request["restore_target_info"]["recovery_option"] = "FailIfExists"

    # We set the restore criteria depending on the datasource type and on the prefix pattern/container list as provided
    # AKS directly uses the restore configuration. Currently, the "else" just covers Blobs.
    restore_criteria_list = []
    if datasource_type == "AzureKubernetesService":
        if restore_configuration is not None:
            restore_criteria = restore_configuration
        else:
            raise RequiredArgumentMissingError("Please input parameter restore_configuration for AKS cluster restore.\n\
                                               Use command initialize-restoreconfig for creating the RestoreConfiguration")
        restore_criteria_list.append(restore_criteria)
    else:
        # For non-AKS workloads, we need either a prefix-pattern or a container-list. Accordingly, the restore
        # criteria's min_matching_value and max_matching_value are set. We need to provide one, but can't provide both
        if container_list is not None and (from_prefix_pattern is not None or to_prefix_pattern is not None):
            raise MutuallyExclusiveArgumentError("Please specify either container list or prefix pattern.")

        if container_list is not None:
            if len(container_list) > 10:
                raise InvalidArgumentValueError("A maximum of 10 containers can be restored. Please choose up to 10 containers.")
            for container in container_list:
                if container[0] == '$':
                    raise InvalidArgumentValueError("container name can not start with '$'. Please retry with different sets of containers.")
                restore_criteria = {}
                restore_criteria["object_type"] = "RangeBasedItemLevelRestoreCriteria"
                restore_criteria["min_matching_value"] = container
                restore_criteria["max_matching_value"] = container + "-0"

                restore_criteria_list.append(restore_criteria)

        if from_prefix_pattern is not None or to_prefix_pattern is not None:
            if from_prefix_pattern is None or to_prefix_pattern is None or \
               len(from_prefix_pattern) != len(to_prefix_pattern) or len(from_prefix_pattern) > 10:
                raise InvalidArgumentValueError(
                    "from-prefix-pattern and to-prefix-pattern should not be null, both of them should have "
                    "equal length and can have a maximum of 10 patterns."
                )

            for index, _ in enumerate(from_prefix_pattern):
                if from_prefix_pattern[index][0] == '$' or to_prefix_pattern[index][0] == '$':
                    raise InvalidArgumentValueError(
                        "Prefix patterns should not start with '$'. Please provide valid prefix patterns and try again."
                    )

                if not 3 <= len(from_prefix_pattern[index]) <= 63 or not 3 <= len(to_prefix_pattern[index]) <= 63:
                    raise InvalidArgumentValueError(
                        "Prefix patterns needs to be between 3 to 63 characters."
                    )

                if from_prefix_pattern[index] >= to_prefix_pattern[index]:
                    raise InvalidArgumentValueError(
                        "From prefix pattern must be less than to prefix pattern."
                    )

                regex_pattern = r"^[a-z0-9](?!.*--)[a-z0-9-]{1,61}[a-z0-9](\/.{1,60})*$"
                if re.match(regex_pattern, from_prefix_pattern[index]) is None:
                    raise InvalidArgumentValueError(
                        "prefix patterns must start or end with a letter or number,"
                        "and can contain only lowercase letters, numbers, and the dash (-) character. "
                        "consecutive dashes are not permitted."
                        "Given pattern " + from_prefix_pattern[index] + " violates the above rule."
                    )

                if re.match(regex_pattern, to_prefix_pattern[index]) is None:
                    raise InvalidArgumentValueError(
                        "prefix patterns must start or end with a letter or number,"
                        "and can contain only lowercase letters, numbers, and the dash (-) character. "
                        "consecutive dashes are not permitted."
                        "Given pattern " + to_prefix_pattern[index] + " violates the above rule."
                    )

                for compareindex in range(index + 1, len(from_prefix_pattern)):
                    if (from_prefix_pattern[index] <= from_prefix_pattern[compareindex] and to_prefix_pattern[index] >= from_prefix_pattern[compareindex]) or \
                       (from_prefix_pattern[index] >= from_prefix_pattern[compareindex] and from_prefix_pattern[index] <= to_prefix_pattern[compareindex]):
                        raise InvalidArgumentValueError(
                            "overlapping ranges are not allowed."
                        )

            for index, _ in enumerate(from_prefix_pattern):
                restore_criteria = {}
                restore_criteria["object_type"] = "RangeBasedItemLevelRestoreCriteria"
                restore_criteria["min_matching_value"] = from_prefix_pattern[index]
                restore_criteria["max_matching_value"] = to_prefix_pattern[index]

                restore_criteria_list.append(restore_criteria)

        if container_list is None and from_prefix_pattern is None and to_prefix_pattern is None:
            raise RequiredArgumentMissingError("Provide ContainersList or Prefixes for Item Level Recovery")

    restore_request["restore_target_info"]["restore_criteria"] = restore_criteria_list

    datasource_id = None
    # Alternate/Original Location - setting the Target's datasource info accordingly
    if target_resource_id is not None and backup_instance_id is not None:
        raise MutuallyExclusiveArgumentError("Please provide either target-resource-id or backup-instance-id not both.")

    if target_resource_id is not None:
        # No validation for alternate/original location restore, as target_resource_id can be used for both
        datasource_id = target_resource_id

    if backup_instance_id is not None:
        # No validation for alternate/original location restore, to be added if understood to be required
        vault_resource_group = helper.get_vault_rg_from_bi_id(backup_instance_id)
        vault_name = helper.get_vault_name_from_bi_id((backup_instance_id))
        backup_instance_name = helper.get_bi_name_from_bi_id(backup_instance_id)

        from azext_dataprotection.aaz.latest.dataprotection.backup_instance import Show as _Show
        backup_instance = _Show(cli_ctx=cmd.cli_ctx)(command_args={
            "vault_name": vault_name,
            "resource_group": vault_resource_group,
            "backup_instance_name": backup_instance_name
        })
        datasource_id = backup_instance['properties']['dataSourceInfo']['resourceID']

    if backup_instance_id is None and target_resource_id is None:
        raise RequiredArgumentMissingError("Please provide either target-resource-id (for alternate location restore) of backup-instance-id (for original location restore).")

    restore_request["restore_target_info"]["datasource_info"] = helper.get_datasource_info(datasource_type, datasource_id, restore_location)

    if manifest["isProxyResource"]:
        restore_request["restore_target_info"]["datasource_set_info"] = helper.get_datasourceset_info(datasource_type, datasource_id, restore_location)

    return restore_request
