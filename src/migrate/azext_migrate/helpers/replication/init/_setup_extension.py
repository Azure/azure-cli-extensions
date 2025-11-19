# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
from knack.util import CLIError
from azext_migrate.helpers._utils import (
    send_get_request,
    get_resource_by_id,
    delete_resource,
    create_or_update_resource,
    APIVersion,
    ProvisioningState,
    AzLocalInstanceTypes,
    StorageAccountProvisioningState
)
import json


def get_or_check_existing_extension(cmd, extension_uri,
                                    replication_extension_name,
                                    storage_account_id):
    """Get existing extension and check if it's in a good state."""
    # Try to get existing extension, handle not found gracefully
    try:
        replication_extension = get_resource_by_id(
            cmd, extension_uri, APIVersion.Microsoft_DataReplication.value
        )
    except CLIError as e:
        error_str = str(e)
        if ("ResourceNotFound" in error_str or "404" in error_str or
                "Not Found" in error_str):
            # Extension doesn't exist, this is expected for new setups
            print(
                f"Extension '{replication_extension_name}' does not exist, "
                f"will create it."
            )
            return None, False
        # Some other error occurred, re-raise it
        raise

    # Check if extension exists and is in good state
    if replication_extension:
        existing_state = (
            replication_extension.get('properties', {})
            .get('provisioningState')
        )
        existing_storage_id = (replication_extension
                               .get('properties', {})
                               .get('customProperties', {})
                               .get('storageAccountId'))

        print(
            f"Found existing extension '{replication_extension_name}' in "
            f"state: {existing_state}"
        )

        # If it's succeeded with the correct storage account, we're done
        if (existing_state == ProvisioningState.Succeeded.value and
                existing_storage_id == storage_account_id):
            print(
                "Replication Extension already exists with correct "
                "configuration."
            )
            print("Successfully initialized replication infrastructure")
            return None, True  # Signal that we're done

        # If it's in a bad state or has wrong storage account, delete it
        if (existing_state in [ProvisioningState.Failed.value,
                               ProvisioningState.Canceled.value] or
                existing_storage_id != storage_account_id):
            print(f"Removing existing extension (state: {existing_state})")
            delete_resource(
                cmd, extension_uri, APIVersion.Microsoft_DataReplication.value
            )
            time.sleep(120)
            return None, False

    return replication_extension, False


def verify_extension_prerequisites(cmd, rg_uri, replication_vault_name,
                                   instance_type, storage_account_id,
                                   amh_solution_uri, source_fabric_id,
                                   target_fabric_id):
    """Verify all prerequisites before creating extension."""
    print("\nVerifying prerequisites before creating extension...")

    # 1. Verify policy is succeeded
    policy_name = f"{replication_vault_name}{instance_type}policy"
    policy_uri = (
        f"{rg_uri}/providers/Microsoft.DataReplication/replicationVaults"
        f"/{replication_vault_name}/replicationPolicies/{policy_name}"
    )
    policy_check = get_resource_by_id(
        cmd, policy_uri, APIVersion.Microsoft_DataReplication.value)
    if (policy_check.get('properties', {}).get('provisioningState') !=
            ProvisioningState.Succeeded.value):
        raise CLIError(
            "Policy is not in Succeeded state: {}".format(
                policy_check.get('properties', {}).get('provisioningState')))

    # 2. Verify storage account is succeeded
    storage_account_name = storage_account_id.split("/")[-1]
    storage_uri = (
        f"{rg_uri}/providers/Microsoft.Storage/storageAccounts/"
        f"{storage_account_name}")
    storage_check = get_resource_by_id(
        cmd, storage_uri, APIVersion.Microsoft_Storage.value)
    if (storage_check
            .get('properties', {})
            .get('provisioningState') !=
            StorageAccountProvisioningState.Succeeded.value):
        raise CLIError(
            "Storage account is not in Succeeded state: {}".format(
                storage_check.get('properties', {}).get(
                    'provisioningState')))

    # 3. Verify AMH solution has storage account
    solution_check = get_resource_by_id(
        cmd, amh_solution_uri, APIVersion.Microsoft_Migrate.value)
    if (solution_check
            .get('properties', {})
            .get('details', {})
            .get('extendedDetails', {})
            .get('replicationStorageAccountId') != storage_account_id):
        raise CLIError(
            "AMH solution doesn't have the correct storage account ID")

    # 4. Verify fabrics are responsive
    source_fabric_check = get_resource_by_id(
        cmd, source_fabric_id, APIVersion.Microsoft_DataReplication.value)
    if (source_fabric_check.get('properties', {}).get('provisioningState') !=
            ProvisioningState.Succeeded.value):
        raise CLIError("Source fabric is not in Succeeded state")

    target_fabric_check = get_resource_by_id(
        cmd, target_fabric_id, APIVersion.Microsoft_DataReplication.value)
    if (target_fabric_check.get('properties', {}).get('provisioningState') !=
            ProvisioningState.Succeeded.value):
        raise CLIError("Target fabric is not in Succeeded state")

    print("All prerequisites verified successfully!")
    time.sleep(30)


def list_existing_extensions(cmd, rg_uri, replication_vault_name):
    """List existing extensions for informational purposes."""
    existing_extensions_uri = (
        f"{rg_uri}/providers/Microsoft.DataReplication"
        f"/replicationVaults/{replication_vault_name}"
        f"/replicationExtensions"
        f"?api-version={APIVersion.Microsoft_DataReplication.value}"
    )
    try:
        existing_extensions_response = send_get_request(
            cmd, existing_extensions_uri)
        existing_extensions = (
            existing_extensions_response.json().get('value', []))
        if existing_extensions:
            print(f"Found {len(existing_extensions)} existing "
                  f"extension(s): ")
            for ext in existing_extensions:
                ext_name = ext.get('name')
                ext_state = (
                    ext.get('properties', {}).get('provisioningState'))
                ext_type = (ext.get('properties', {})
                            .get('customProperties', {})
                            .get('instanceType'))
                print(f" - {ext_name}: state={ext_state}, "
                      f"type={ext_type}")
        else:
            print("No existing extensions found")
    except CLIError as list_error:
        # If listing fails, it might mean no extensions exist at all
        print(f"Could not list extensions (this is normal for new "
              f"projects): {str(list_error)}")


def build_extension_body(instance_type, source_fabric_id,
                         target_fabric_id, storage_account_id):
    """Build the extension body based on instance type."""
    print("\n=== Creating extension for replication infrastructure ===")
    print(f"Instance Type: {instance_type}")
    print(f"Source Fabric ID: {source_fabric_id}")
    print(f"Target Fabric ID: {target_fabric_id}")
    print(f"Storage Account ID: {storage_account_id}")

    # Build the extension body with properties in the exact order from
    # the working API call
    if instance_type == AzLocalInstanceTypes.VMwareToAzLocal.value:
        # Match exact property order from working call for VMware
        extension_body = {
            "properties": {
                "customProperties": {
                    "azStackHciFabricArmId": target_fabric_id,
                    "storageAccountId": storage_account_id,
                    "storageAccountSasSecretName": None,
                    "instanceType": instance_type,
                    "vmwareFabricArmId": source_fabric_id
                }
            }
        }
    elif instance_type == AzLocalInstanceTypes.HyperVToAzLocal.value:
        # For HyperV, use similar order but with hyperVFabricArmId
        extension_body = {
            "properties": {
                "customProperties": {
                    "azStackHciFabricArmId": target_fabric_id,
                    "storageAccountId": storage_account_id,
                    "storageAccountSasSecretName": None,
                    "instanceType": instance_type,
                    "hyperVFabricArmId": source_fabric_id
                }
            }
        }
    else:
        raise CLIError(f"Unsupported instance type: {instance_type}")

    # Debug: Print the exact body being sent
    body_str = json.dumps(extension_body, indent=2)
    print(f"Extension body being sent: \n{body_str}")

    return extension_body


def _wait_for_extension_creation(cmd, extension_uri):
    """Wait for extension creation to complete."""
    for i in range(20):
        time.sleep(30)
        try:
            api_version = APIVersion.Microsoft_DataReplication.value
            replication_extension = get_resource_by_id(
                cmd, extension_uri, api_version)
            if replication_extension:
                ext_state = replication_extension.get(
                    'properties', {}).get('provisioningState')
                print(f"Extension state: {ext_state}")
                if ext_state in [ProvisioningState.Succeeded.value,
                                 ProvisioningState.Failed.value,
                                 ProvisioningState.Canceled.value]:
                    break
        except CLIError:
            print(f"Waiting for extension... ({i + 1}/20)")


def _handle_extension_creation_error(cmd, extension_uri, create_error):
    """Handle errors during extension creation."""
    error_str = str(create_error)
    print(f"Error during extension creation: {error_str}")

    # Check if extension was created despite the error
    time.sleep(30)
    try:
        api_version = APIVersion.Microsoft_DataReplication.value
        replication_extension = get_resource_by_id(
            cmd, extension_uri, api_version)
        if replication_extension:
            print(
                f"Extension exists despite error, "
                f"state: {replication_extension.get('properties', {}).get('provisioningState')}"
            )
    except CLIError:
        replication_extension = None

    if not replication_extension:
        raise CLIError(
            f"Failed to create replication extension: "
            f"{str(create_error)}") from create_error


def create_replication_extension(cmd, extension_uri, extension_body):
    """Create the replication extension and wait for it to complete."""
    try:
        result = create_or_update_resource(
            cmd, extension_uri,
            APIVersion.Microsoft_DataReplication.value,
            extension_body)
        if result:
            print("Extension creation initiated successfully")
            # Wait for the extension to be created
            print("Waiting for extension creation to complete...")
            _wait_for_extension_creation(cmd, extension_uri)
    except CLIError as create_error:
        _handle_extension_creation_error(cmd, extension_uri, create_error)


def setup_replication_extension(cmd, rg_uri, replication_vault_name,
                                source_fabric, target_fabric,
                                instance_type, storage_account_id,
                                amh_solution_uri, pass_thru):
    """Setup replication extension - main orchestration function."""
    # Setup Replication Extension
    source_fabric_id = source_fabric['id']
    target_fabric_id = target_fabric['id']
    source_fabric_short_name = source_fabric_id.split('/')[-1]
    target_fabric_short_name = target_fabric_id.split('/')[-1]
    replication_extension_name = (
        f"{source_fabric_short_name}-{target_fabric_short_name}-"
        f"MigReplicationExtn")

    extension_uri = (
        f"{rg_uri}/providers/Microsoft.DataReplication/"
        f"replicationVaults/{replication_vault_name}/"
        f"replicationExtensions/{replication_extension_name}"
    )

    # Get or check existing extension
    replication_extension, is_complete = get_or_check_existing_extension(
        cmd, extension_uri, replication_extension_name,
        storage_account_id
    )

    if is_complete:
        return True if pass_thru else None

    # Verify prerequisites
    verify_extension_prerequisites(
        cmd, rg_uri, replication_vault_name, instance_type,
        storage_account_id, amh_solution_uri, source_fabric_id,
        target_fabric_id
    )

    # Create extension if needed
    if not replication_extension:
        print(
            f"Creating Replication Extension "
            f"'{replication_extension_name}'...")

        # List existing extensions for context
        list_existing_extensions(cmd, rg_uri, replication_vault_name)

        # Build extension body
        extension_body = build_extension_body(
            instance_type, source_fabric_id, target_fabric_id,
            storage_account_id
        )

        # Create the extension
        create_replication_extension(cmd, extension_uri, extension_body)

    print("Successfully initialized replication infrastructure")
    return True if pass_thru else None
