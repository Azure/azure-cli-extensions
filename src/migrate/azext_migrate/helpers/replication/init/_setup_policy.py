# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
from knack.util import CLIError
from knack.log import get_logger
from azext_migrate.helpers._utils import (
    send_get_request,
    get_resource_by_id,
    delete_resource,
    create_or_update_resource,
    generate_hash_for_artifact,
    APIVersion,
    ProvisioningState,
    AzLocalInstanceTypes,
    FabricInstanceTypes,
    ReplicationPolicyDetails,
    StorageAccountProvisioningState
)


def determine_instance_types(source_site_id, target_site_id,
                             source_appliance_name,
                             target_appliance_name):
    """Determine instance types based on site IDs."""
    hyperv_site_pattern = "/Microsoft.OffAzure/HyperVSites/"
    vmware_site_pattern = "/Microsoft.OffAzure/VMwareSites/"

    if (hyperv_site_pattern in source_site_id and
            hyperv_site_pattern in target_site_id):
        instance_type = AzLocalInstanceTypes.HyperVToAzLocal.value
        fabric_instance_type = FabricInstanceTypes.HyperVInstance.value
    elif (vmware_site_pattern in source_site_id and
          hyperv_site_pattern in target_site_id):
        instance_type = AzLocalInstanceTypes.VMwareToAzLocal.value
        fabric_instance_type = FabricInstanceTypes.VMwareInstance.value
    else:
        src_type = (
            'VMware' if vmware_site_pattern in source_site_id
            else 'HyperV' if hyperv_site_pattern in source_site_id
            else 'Unknown'
        )
        tgt_type = (
            'VMware' if vmware_site_pattern in target_site_id
            else 'HyperV' if hyperv_site_pattern in target_site_id
            else 'Unknown'
        )
        raise CLIError(
            f"Error matching source '{source_appliance_name}' and target "
            f"'{target_appliance_name}' appliances. Source is {src_type}, "
            f"Target is {tgt_type}"
        )

    return instance_type, fabric_instance_type


def find_fabric(all_fabrics, appliance_name, fabric_instance_type,
                amh_solution, is_source=True):
    """Find and validate a fabric for the given appliance."""
    logger = get_logger(__name__)
    fabric = None
    fabric_candidates = []

    for candidate in all_fabrics:
        props = candidate.get('properties', {})
        custom_props = props.get('customProperties', {})
        fabric_name = candidate.get('name', '')

        # Check if this fabric matches our criteria
        is_succeeded = (props.get('provisioningState') ==
                        ProvisioningState.Succeeded.value)

        # Check solution ID match - handle case differences and trailing
        # slashes
        fabric_solution_id = (custom_props.get('migrationSolutionId', '')
                              .rstrip('/'))
        expected_solution_id = amh_solution.get('id', '').rstrip('/')
        is_correct_solution = (fabric_solution_id.lower() ==
                               expected_solution_id.lower())

        is_correct_instance = (custom_props.get('instanceType') ==
                               fabric_instance_type)

        # Check if fabric name contains appliance name or vice versa
        name_matches = (
            fabric_name.lower().startswith(appliance_name.lower()) or
            appliance_name.lower() in fabric_name.lower() or
            fabric_name.lower() in appliance_name.lower() or
            f"{appliance_name.lower()}-" in fabric_name.lower()
        )

        # Collect potential candidates even if they don't fully match
        if custom_props.get('instanceType') == fabric_instance_type:
            fabric_candidates.append({
                'name': fabric_name,
                'state': props.get('provisioningState'),
                'solution_match': is_correct_solution,
                'name_match': name_matches
            })

        if is_succeeded and is_correct_instance and name_matches:
            # If solution doesn't match, log warning but still consider it
            if not is_correct_solution:
                logger.warning(
                    "Fabric '%s' matches name and type but has "
                    "different solution ID", fabric_name)
            fabric = candidate
            break

    if not fabric:
        appliance_type_label = "source" if is_source else "target"
        error_msg = (
            f"Couldn't find connected {appliance_type_label} appliance "
            f"'{appliance_name}'.\n")

        if fabric_candidates:
            error_msg += (
                f"Found {len(fabric_candidates)} fabric(s) with "
                f"matching type '{fabric_instance_type}': \n")
            for candidate in fabric_candidates:
                error_msg += (
                    f" - {candidate['name']} "
                    f"(state: {candidate['state']}, "
                    f"solution_match: {candidate['solution_match']}, "
                    f"name_match: {candidate['name_match']})\n")
            error_msg += "\nPlease verify:\n"
            error_msg += "1. The appliance name matches exactly\n"
            error_msg += "2. The fabric is in 'Succeeded' state\n"
            error_msg += (
                "3. The fabric belongs to the correct migration solution")
        else:
            error_msg += (
                f"No fabrics found with instance type "
                f"'{fabric_instance_type}'.\n")
            error_msg += "\nThis usually means:\n"
            error_msg += (
                f"1. The {appliance_type_label} appliance "
                f"'{appliance_name}' is not properly configured\n")
            if (fabric_instance_type ==
                    FabricInstanceTypes.VMwareInstance.value):
                appliance_type = 'VMware'
            elif (fabric_instance_type ==
                    FabricInstanceTypes.HyperVInstance.value):
                appliance_type = 'HyperV'
            else:
                appliance_type = 'Azure Local'
            error_msg += (
                f"2. The appliance type doesn't match "
                f"(expecting {appliance_type})\n")
            error_msg += (
                "3. The fabric creation is still in progress - "
                "wait a few minutes and retry")

            if all_fabrics:
                error_msg += "\n\nAvailable fabrics in resource group:\n"
                for fab in all_fabrics:
                    props = fab.get('properties', {})
                    custom_props = props.get('customProperties', {})
                    error_msg += (
                        f" - {fab.get('name')} "
                        f"(type: {custom_props.get('instanceType')})\n")

        raise CLIError(error_msg)

    return fabric


def get_fabric_agent(cmd, replication_fabrics_uri, fabric, appliance_name,
                     fabric_instance_type):
    """Get and validate fabric agent (DRA) for the given fabric."""
    fabric_name = fabric.get('name')
    dras_uri = (
        f"{replication_fabrics_uri}/{fabric_name}"
        f"/fabricAgents?api-version="
        f"{APIVersion.Microsoft_DataReplication.value}"
    )
    dras_response = send_get_request(cmd, dras_uri)
    dras = dras_response.json().get('value', [])

    dra = None
    for candidate in dras:
        props = candidate.get('properties', {})
        custom_props = props.get('customProperties', {})
        if (props.get('machineName') == appliance_name and
                custom_props.get('instanceType') == fabric_instance_type and
                bool(props.get('isResponsive'))):
            dra = candidate
            break

    if not dra:
        raise CLIError(
            f"The appliance '{appliance_name}' is in a disconnected state."
        )

    return dra


def setup_replication_policy(cmd,
                             rg_uri,
                             replication_vault_name,
                             instance_type):
    """Setup or validate replication policy."""
    policy_name = f"{replication_vault_name}{instance_type}policy"
    policy_uri = (
        f"{rg_uri}/providers/Microsoft.DataReplication/replicationVaults"
        f"/{replication_vault_name}/replicationPolicies/{policy_name}"
    )

    # Try to get existing policy, handle not found gracefully
    try:
        policy = get_resource_by_id(
            cmd, policy_uri, APIVersion.Microsoft_DataReplication.value
        )
    except CLIError as e:
        error_str = str(e)
        if ("ResourceNotFound" in error_str or "404" in error_str or
                "Not Found" in error_str):
            # Policy doesn't exist, this is expected for new setups
            print(f"Policy '{policy_name}' does not exist, will create it.")
            policy = None
        else:
            # Some other error occurred, re-raise it
            raise

    # Handle existing policy states
    if policy:
        provisioning_state = (
            policy
            .get('properties', {})
            .get('provisioningState')
        )

        # Wait for creating/updating to complete
        if provisioning_state in [ProvisioningState.Creating.value,
                                  ProvisioningState.Updating.value]:
            print(
                f"Policy '{policy_name}' found in Provisioning State "
                f"'{provisioning_state}'."
            )
            for i in range(20):
                time.sleep(30)
                policy = get_resource_by_id(
                    cmd, policy_uri,
                    APIVersion.Microsoft_DataReplication.value
                )
                if policy:
                    provisioning_state = (
                        policy.get('properties', {}).get('provisioningState')
                    )
                    if provisioning_state not in [
                            ProvisioningState.Creating.value,
                            ProvisioningState.Updating.value]:
                        break

        # Remove policy if in bad state
        if provisioning_state in [ProvisioningState.Canceled.value,
                                  ProvisioningState.Failed.value]:
            print(
                f"Policy '{policy_name}' found in unusable state "
                f"'{provisioning_state}'. Removing..."
            )
            delete_resource(
                cmd, policy_uri, APIVersion.Microsoft_DataReplication.value
            )
            time.sleep(30)
            policy = None

    # Create policy if needed
    if not policy or (
            policy and
            policy.get('properties', {}).get('provisioningState') ==
            ProvisioningState.Deleted.value):
        print(f"Creating Policy '{policy_name}'...")

        recoveryPoint = (
            ReplicationPolicyDetails.RecoveryPointHistoryInMinutes
        )
        crashConsistentFreq = (
            ReplicationPolicyDetails.CrashConsistentFrequencyInMinutes
        )
        appConsistentFreq = (
            ReplicationPolicyDetails.AppConsistentFrequencyInMinutes
        )

        policy_body = {
            "properties": {
                "customProperties": {
                    "instanceType": instance_type,
                    "recoveryPointHistoryInMinutes": recoveryPoint,
                    "crashConsistentFrequencyInMinutes": crashConsistentFreq,
                    "appConsistentFrequencyInMinutes": appConsistentFreq
                }
            }
        }

        create_or_update_resource(
            cmd,
            policy_uri,
            APIVersion.Microsoft_DataReplication.value,
            policy_body,
        )

        # Wait for policy creation
        for i in range(20):
            time.sleep(30)
            try:
                policy = get_resource_by_id(
                    cmd, policy_uri,
                    APIVersion.Microsoft_DataReplication.value
                )
            except Exception as poll_error:
                # During creation, it might still return 404 initially
                if ("ResourceNotFound" in str(poll_error) or
                        "404" in str(poll_error)):
                    print(f"Policy creation in progress... ({i + 1}/20)")
                    continue
                raise

            if policy:
                provisioning_state = (
                    policy.get('properties', {}).get('provisioningState')
                )
                print(f"Policy state: {provisioning_state}")
                if provisioning_state in [
                        ProvisioningState.Succeeded.value,
                        ProvisioningState.Failed.value,
                        ProvisioningState.Canceled.value,
                        ProvisioningState.Deleted.value]:
                    break

    if not policy or (
            policy.get('properties', {}).get('provisioningState') !=
            ProvisioningState.Succeeded.value):
        raise CLIError(f"Policy '{policy_name}' is not in Succeeded state.")

    return policy


def setup_cache_storage_account(cmd, rg_uri, amh_solution,
                                cache_storage_account_id,
                                source_site_id, source_appliance_name,
                                migrate_project, project_name):
    """Setup or validate cache storage account."""
    logger = get_logger(__name__)

    amh_stored_storage_account_id = (
        amh_solution.get('properties', {})
        .get('details', {})
        .get('extendedDetails', {})
        .get('replicationStorageAccountId')
    )
    cache_storage_account = None

    if amh_stored_storage_account_id:
        # Check existing storage account
        storage_account_name = amh_stored_storage_account_id.split("/")[8]
        storage_uri = (
            f"{rg_uri}/providers/Microsoft.Storage/storageAccounts"
            f"/{storage_account_name}"
        )
        storage_account = get_resource_by_id(
            cmd, storage_uri, APIVersion.Microsoft_Storage.value
        )

        if storage_account and (
            storage_account
            .get('properties', {})
            .get('provisioningState') ==
                StorageAccountProvisioningState.Succeeded.value
        ):
            cache_storage_account = storage_account
            if (cache_storage_account_id and
                    cache_storage_account['id'] !=
                    cache_storage_account_id):
                warning_msg = (
                    f"A Cache Storage Account '{storage_account_name}' is "
                    f"already linked. "
                )
                warning_msg += "Ignoring provided -cache_storage_account_id."
                logger.warning(warning_msg)

    # Use user-provided storage account if no existing one
    if not cache_storage_account and cache_storage_account_id:
        storage_account_name = cache_storage_account_id.split("/")[8].lower()
        storage_uri = (
            f"{rg_uri}/providers/Microsoft.Storage/storageAccounts/"
            f"{storage_account_name}"
        )
        user_storage_account = get_resource_by_id(
            cmd, storage_uri, APIVersion.Microsoft_Storage.value
        )

        if user_storage_account and (
            user_storage_account
            .get('properties', {})
            .get('provisioningState') ==
                StorageAccountProvisioningState.Succeeded.value
        ):
            cache_storage_account = user_storage_account
        else:
            error_msg = (
                f"Cache Storage Account with Id "
                f"'{cache_storage_account_id}' not found "
            )
            error_msg += "or not in valid state."
            raise CLIError(error_msg)

    # Create new storage account if needed
    if not cache_storage_account:
        artifact = f"{source_site_id}/{source_appliance_name}"
        suffix_hash = generate_hash_for_artifact(artifact)
        if len(suffix_hash) > 14:
            suffix_hash = suffix_hash[:14]
        storage_account_name = f"migratersa{suffix_hash}"

        print(f"Creating Cache Storage Account '{storage_account_name}'...")

        storage_body = {
            "location": migrate_project.get('location'),
            "tags": {"Migrate Project": project_name},
            "sku": {"name": "Standard_LRS"},
            "kind": "StorageV2",
            "properties": {
                "allowBlobPublicAccess": False,
                "allowCrossTenantReplication": True,
                "minimumTlsVersion": "TLS1_2",
                "networkAcls": {
                    "defaultAction": "Allow"
                },
                "encryption": {
                    "services": {
                        "blob": {"enabled": True},
                        "file": {"enabled": True}
                    },
                    "keySource": "Microsoft.Storage"
                },
                "accessTier": "Hot"
            }
        }

        storage_uri = (
            f"{rg_uri}/providers/Microsoft.Storage/storageAccounts"
            f"/{storage_account_name}"
        )
        cache_storage_account = create_or_update_resource(
            cmd,
            storage_uri,
            APIVersion.Microsoft_Storage.value,
            storage_body
        )

        for _ in range(20):
            time.sleep(30)
            cache_storage_account = get_resource_by_id(
                cmd,
                storage_uri,
                APIVersion.Microsoft_Storage.value
            )
            if cache_storage_account and (
                cache_storage_account
                .get('properties', {})
                .get('provisioningState') ==
                    StorageAccountProvisioningState.Succeeded.value
            ):
                break

    if not cache_storage_account or (
        cache_storage_account
        .get('properties', {})
        .get('provisioningState') !=
            StorageAccountProvisioningState.Succeeded.value
    ):
        raise CLIError("Failed to setup Cache Storage Account.")

    return cache_storage_account


def verify_storage_account_network_settings(cmd,
                                            rg_uri,
                                            cache_storage_account):
    """Verify and update storage account network settings if needed."""
    storage_account_id = cache_storage_account['id']

    # Verify storage account network settings
    print("Verifying storage account network configuration...")
    network_acls = (
        cache_storage_account.get('properties', {}).get('networkAcls', {})
    )
    default_action = network_acls.get('defaultAction', 'Allow')

    if default_action != 'Allow':
        print(
            f"WARNING: Storage account network defaultAction is "
            f"'{default_action}'. "
            "This may cause permission issues."
        )
        print(
            "Updating storage account to allow public network access..."
        )

        # Update storage account to allow public access
        storage_account_name = storage_account_id.split("/")[-1]
        storage_uri = (
            f"{rg_uri}/providers/Microsoft.Storage/storageAccounts/"
            f"{storage_account_name}"
        )

        update_body = {
            "properties": {
                "networkAcls": {
                    "defaultAction": "Allow"
                }
            }
        }

        create_or_update_resource(
            cmd, storage_uri, APIVersion.Microsoft_Storage.value,
            update_body
        )

        # Wait for network update to propagate
        time.sleep(30)


def get_all_fabrics(cmd, rg_uri, resource_group_name,
                    source_appliance_name,
                    target_appliance_name, project_name):
    """Get all replication fabrics in the resource group."""
    replication_fabrics_uri = (
        f"{rg_uri}/providers/Microsoft.DataReplication/replicationFabrics"
    )
    fabrics_uri = (
        f"{replication_fabrics_uri}?api-version="
        f"{APIVersion.Microsoft_DataReplication.value}"
    )
    fabrics_response = send_get_request(cmd, fabrics_uri)
    all_fabrics = fabrics_response.json().get('value', [])

    # If no fabrics exist at all, provide helpful message
    if not all_fabrics:
        raise CLIError(
            f"No replication fabrics found in resource group "
            f"'{resource_group_name}'. "
            f"Please ensure that: \n"
            f"1. The source appliance '{source_appliance_name}' is deployed "
            f"and connected\n"
            f"2. The target appliance '{target_appliance_name}' is deployed "
            f"and connected\n"
            f"3. Both appliances are registered with the Azure Migrate "
            f"project '{project_name}'"
        )

    return all_fabrics, replication_fabrics_uri
