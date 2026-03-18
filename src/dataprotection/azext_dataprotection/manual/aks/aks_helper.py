import json
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.mgmt.core.tools import parse_resource_id


# Tag used to identify storage accounts created for AKS backup
# Format: AKSAzureBackup: <location>
AKS_BACKUP_TAG_KEY = "AKSAzureBackup"


def _check_and_assign_role(cmd, role, assignee, scope, identity_name="identity", max_retries=3, retry_delay=10):
    """
    Check if a role assignment already exists, and create it if not.

    Args:
        cmd: CLI command context
        role: Role name (e.g., 'Contributor', 'Reader')
        assignee: Principal ID of the identity to assign the role to
        scope: Resource ID scope for the role assignment
        identity_name: Friendly name for log messages
        max_retries: Max retries for transient failures
        retry_delay: Delay in seconds between retries

    Returns:
        True if role was assigned (new or existing), raises on failure
    """
    import time
    from azure.cli.command_modules.role.custom import list_role_assignments, create_role_assignment

    # Check if role assignment already exists
    try:
        if list_role_assignments(cmd, assignee=assignee, role=role, scope=scope, include_inherited=True):
            print(f"\tRole '{role}' already assigned to {identity_name}")
            return True
    except Exception as e:
        print(f"\tWarning: Could not list role assignments for {identity_name}: {str(e)[:100]}")
        # Continue to try creating the assignment

    # Try to create with retries for identity propagation delay
    for attempt in range(max_retries):
        try:
            create_role_assignment(cmd, role=role, assignee=assignee, scope=scope)
            print(f"\tRole '{role}' assigned to {identity_name}")
            return True
        except Exception as e:
            error_str = str(e).lower()

            # Already exists — treat as success
            if "conflict" in error_str or "already exists" in error_str:
                print(f"\tRole '{role}' already assigned to {identity_name}")
                return True

            # Principal not found — retryable (identity propagation)
            is_propagation_error = "principal" in error_str or "does not exist" in error_str or "cannot find" in error_str
            if is_propagation_error and attempt < max_retries - 1:
                print(f"\tWaiting for identity to propagate... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                continue

            # Permission denied — actionable error
            if "authorization" in error_str or "forbidden" in error_str:
                raise InvalidArgumentValueError(
                    f"Insufficient permissions to assign '{role}' role to {identity_name}.\n"
                    f"Run manually:\n\n"
                    f"  az role assignment create --role \"{role}\" --assignee \"{assignee}\" --scope \"{scope}\"\n"
                )

            # Non-retryable error — break and raise
            break

    raise InvalidArgumentValueError(
        f"Failed to assign '{role}' role to {identity_name}.\n"
        f"Run manually:\n\n"
        f"  az role assignment create --role \"{role}\" --assignee \"{assignee}\" --scope \"{scope}\"\n"
    )


def _validate_request(datasource_id, backup_strategy, configuration_params):
    """
    Validate the request parameters. Raises InvalidArgumentValueError on validation failure.

    Args:
        datasource_id: Full ARM resource ID of the AKS cluster
        backup_strategy: Backup strategy (Week, Month, Immutable, DisasterRecovery, Custom)
        configuration_params: Dict with configuration settings (camelCase keys)
            - storageAccountResourceId: Storage account resource ID
            - blobContainerName: Blob container name
            - backupResourceGroupId: Resource group for backup resources
            - backupVaultId: Backup vault resource ID (required for Custom)
            - backupPolicyId: Backup policy resource ID (required for Custom)
            - tags: Resource tags dict
    """
    # Ensure configuration_params is a dict
    if configuration_params is None:
        configuration_params = {}

    # Parse if string
    if isinstance(configuration_params, str):
        try:
            json.loads(configuration_params)
        except json.JSONDecodeError:
            raise InvalidArgumentValueError("Invalid JSON in backup-configuration-file")

    # Validate Custom strategy requirements
    if backup_strategy == 'Custom':
        if not configuration_params.get("backupVaultId"):
            raise InvalidArgumentValueError(
                "backupVaultId is required in --backup-configuration-file when using Custom strategy"
            )
        if not configuration_params.get("backupPolicyId"):
            raise InvalidArgumentValueError(
                "backupPolicyId is required in --backup-configuration-file when using Custom strategy"
            )

    # Parse cluster subscription for validation
    cluster_id_parts = parse_resource_id(datasource_id)
    cluster_subscription_id = cluster_id_parts['subscription']

    # Validate provided resource IDs are in the same subscription as cluster
    backup_resource_group_id = configuration_params.get("backupResourceGroupId")
    if backup_resource_group_id:
        rg_parts = parse_resource_id(backup_resource_group_id)
        if rg_parts['subscription'].lower() != cluster_subscription_id.lower():
            raise InvalidArgumentValueError(
                f"backupResourceGroupId must be in the same subscription as the cluster. "
                f"Cluster subscription: {cluster_subscription_id}, Resource group subscription: {rg_parts['subscription']}"
            )

    storage_account_id = configuration_params.get("storageAccountResourceId")
    if storage_account_id:
        sa_parts = parse_resource_id(storage_account_id)
        if sa_parts['subscription'].lower() != cluster_subscription_id.lower():
            raise InvalidArgumentValueError(
                f"storageAccountResourceId must be in the same subscription as the cluster. "
                f"Cluster subscription: {cluster_subscription_id}, Storage account subscription: {sa_parts['subscription']}"
            )

    backup_vault_id = configuration_params.get("backupVaultId")
    if backup_vault_id:
        vault_parts = parse_resource_id(backup_vault_id)
        if vault_parts['subscription'].lower() != cluster_subscription_id.lower():
            raise InvalidArgumentValueError(
                f"backupVaultId must be in the same subscription as the cluster. "
                f"Cluster subscription: {cluster_subscription_id}, Backup vault subscription: {vault_parts['subscription']}"
            )


def _check_existing_backup_instance(resource_client, datasource_id, cluster_name):
    """
    Check if a backup instance already exists for this cluster using extension routing.

    Calls: GET {datasource_id}/providers/Microsoft.DataProtection/backupInstances

    Returns:
        None if no backup instance exists, raises error with details if one exists
    """
    print("\tChecking for existing backup configuration...")

    try:
        # Use extension routing to query backup instances on the cluster
        extension_resource_id = f"{datasource_id}/providers/Microsoft.DataProtection/backupInstances"
        response = resource_client.resources.get_by_id(
            extension_resource_id,
            api_version="2024-04-01"
        )

        # Parse the response to get backup instances list
        bi_list = []
        if hasattr(response, 'value'):
            bi_list = response.value if response.value else []
        elif hasattr(response, 'additional_properties'):
            props = response.additional_properties
            if isinstance(props, dict) and 'value' in props:
                bi_list = props['value'] if props['value'] else []

        # If list is empty, no backup instance exists
        if not bi_list:
            print("\tNo existing backup instance found")
            return None

        # Get details of the first backup instance
        bi = bi_list[0] if isinstance(bi_list, list) else bi_list
        bi_id = bi.get('id', 'Unknown') if isinstance(bi, dict) else getattr(bi, 'id', 'Unknown')
        bi_name = bi.get('name', 'Unknown') if isinstance(bi, dict) else getattr(bi, 'name', 'Unknown')

        # Get protection status from properties
        bi_properties = bi.get('properties', {}) if isinstance(bi, dict) else getattr(bi, 'properties', {})
        if isinstance(bi_properties, dict):
            protection_status = bi_properties.get('currentProtectionState', 'Unknown')
            protection_error = bi_properties.get('protectionErrorDetails', None)
        else:
            protection_status = getattr(bi_properties, 'current_protection_state', 'Unknown')
            protection_error = getattr(bi_properties, 'protection_error_details', None)

        # Parse vault info from the BI resource ID
        # Format: /subscriptions/.../resourceGroups/.../providers/Microsoft.DataProtection/backupVaults/{vault}/backupInstances/{bi}
        vault_name = "Unknown"
        vault_rg = "Unknown"
        if bi_id and '/backupvaults/' in str(bi_id).lower():
            bi_parts = parse_resource_id(bi_id)
            vault_name = bi_parts.get('name', 'Unknown')
            vault_rg = bi_parts.get('resource_group', 'Unknown')

        print("\tFound existing backup instance!")
        print(f"\t\t- Backup Instance: {bi_name}")
        print(f"\t\t- Backup Vault:    {vault_name}")
        print(f"\t\t- Resource Group:  {vault_rg}")
        print(f"\t\t- Protection State: {protection_status}")

        error_info = ""
        if protection_error:
            error_msg = protection_error.get('message', str(protection_error)) if isinstance(protection_error, dict) else str(protection_error)
            print(f"\t\t- Error Details:   {error_msg[:100]}..." if len(str(error_msg)) > 100 else f"        - Error Details:   {error_msg}")
            error_info = f"\n  Protection Error: {error_msg}\n"

        raise InvalidArgumentValueError(
            f"Cluster '{cluster_name}' is already protected by a backup instance.\n\n"
            f"Existing Backup Configuration:\n"
            f"  Backup Instance: {bi_name}\n"
            f"  Backup Vault:    {vault_name}\n"
            f"  Resource Group:  {vault_rg}\n"
            f"  Protection State: {protection_status}{error_info}\n"
            f"To reconfigure backup, first delete the existing backup instance:\n\n"
            f"  az dataprotection backup-instance delete \\\n"
            f"    --name \"{bi_name}\" \\\n"
            f"    --vault-name \"{vault_name}\" \\\n"
            f"    --resource-group \"{vault_rg}\" \\\n"
            f"    --yes\n\n"
            f"Then re-run this command."
        )

    except InvalidArgumentValueError:
        # Re-raise our own error
        raise
    except Exception as e:
        # 404 or other errors mean no backup instance exists - that's fine
        error_str = str(e).lower()
        if "not found" in error_str or "404" in error_str or "does not exist" in error_str:
            print("\tNo existing backup instance found")
            return None
        # For other errors, log and continue (don't block on extension routing failures)
        print(f"\tCould not check for existing backup (will proceed): {str(e)[:100]}")
        return None

    print("\tNo existing backup instance found")
    return None


def _get_cluster_msi_principal_id(cluster_resource, cluster_name):
    """
    Extract the managed identity principal ID from an AKS cluster resource.

    Supports both:
    - System-Assigned Managed Identity (SAMI): identity.principal_id
    - User-Assigned Managed Identity (UAMI): identity.user_assigned_identities[*].principal_id

    Returns:
        str: principal ID of the cluster's managed identity
    Raises:
        InvalidArgumentValueError if no managed identity is found
    """
    identity = cluster_resource.identity
    if not identity:
        raise InvalidArgumentValueError(
            f"Cluster '{cluster_name}' does not have a managed identity configured.\n"
            f"AKS backup requires a cluster with managed identity enabled."
        )

    identity_type = getattr(identity, 'type', '') or ''

    # System-assigned identity
    if identity.principal_id:
        print(f"\tIdentity type: {identity_type} (system-assigned)")
        return identity.principal_id

    # User-assigned identity — get the first UAMI's principal ID
    user_assigned = getattr(identity, 'user_assigned_identities', None)
    if user_assigned:
        # user_assigned_identities is a dict: {resource_id: {principal_id, client_id}}
        if isinstance(user_assigned, dict):
            for uami_id, uami_info in user_assigned.items():
                principal_id = None
                if isinstance(uami_info, dict):
                    principal_id = uami_info.get('principal_id') or uami_info.get('principalId')
                else:
                    principal_id = getattr(uami_info, 'principal_id', None) or getattr(uami_info, 'principalId', None)

                if principal_id:
                    uami_name = uami_id.split('/')[-1] if '/' in uami_id else uami_id
                    print(f"\tIdentity type: {identity_type} (user-assigned: {uami_name})")
                    return principal_id

    raise InvalidArgumentValueError(
        f"Could not extract managed identity principal ID from cluster '{cluster_name}'.\n"
        f"Identity type: {identity_type}\n"
        f"AKS backup requires a cluster with a system-assigned or user-assigned managed identity."
    )


def _validate_cluster(resource_client, datasource_id, cluster_name):
    """Validate the AKS cluster exists and get its details."""
    cluster_resource = resource_client.resources.get_by_id(datasource_id, api_version="2024-08-01")
    cluster_location = cluster_resource.location
    print(f"\tCluster: {cluster_name}")
    print(f"\tLocation: {cluster_location}")
    cluster_identity_principal_id = _get_cluster_msi_principal_id(cluster_resource, cluster_name)
    print("\t[OK] Cluster validated")
    return cluster_resource, cluster_location, cluster_identity_principal_id


def _find_existing_backup_resource_group(resource_client, cluster_location):
    """
    Search for an existing AKS backup resource group in the subscription by tag.

    Looks for resource groups with tag: AKSAzureBackup = <location>

    Returns:
        resource_group if found, None otherwise
    """
    try:
        # List all resource groups in the subscription
        for rg in resource_client.resource_groups.list():
            if rg.tags:
                # Check if this RG has the AKS backup tag matching the location
                tag_value = rg.tags.get(AKS_BACKUP_TAG_KEY)
                if tag_value and tag_value.lower() == cluster_location.lower():
                    return rg
    except Exception:
        # If we can't list resource groups, we'll create a new one
        pass
    return None


def _setup_resource_group(cmd, resource_client, backup_resource_group_id, cluster_location, cluster_name, cluster_identity_principal_id, resource_tags):
    """Create or use backup resource group."""
    if backup_resource_group_id:
        backup_resource_group_name = parse_resource_id(backup_resource_group_id)['resource_group']
        print(f"\tUsing provided resource group: {backup_resource_group_name}")
        try:
            backup_resource_group = resource_client.resource_groups.get(backup_resource_group_name)
        except Exception:
            raise InvalidArgumentValueError(
                f"Resource group '{backup_resource_group_name}' not found. "
                f"Please ensure the resource group exists or remove 'backupResourceGroupId' from configuration to create one automatically."
            )
    else:
        # Search for existing backup resource group with matching tag
        print(f"\tSearching for existing AKS backup resource group in region {cluster_location}...")
        backup_resource_group = _find_existing_backup_resource_group(resource_client, cluster_location)

        if backup_resource_group:
            # Found existing resource group - reuse it
            backup_resource_group_name = backup_resource_group.name
            print(f"\tFound existing backup resource group: {backup_resource_group_name}")
        else:
            # Create new resource group with AKS backup tag
            backup_resource_group_name = _generate_backup_resource_group_name(cluster_location)
            print(f"\tCreating resource group: {backup_resource_group_name}")

            # Build tags - include AKS backup tag plus any user-provided tags
            rg_tags = {AKS_BACKUP_TAG_KEY: cluster_location}
            if resource_tags:
                rg_tags.update(resource_tags)

            rg_params = {"location": cluster_location, "tags": rg_tags}
            backup_resource_group = resource_client.resource_groups.create_or_update(backup_resource_group_name, rg_params)

    print(f"\tResource Group: {backup_resource_group.id}")
    _check_and_assign_role(
        cmd,
        role="Contributor",
        assignee=cluster_identity_principal_id,
        scope=backup_resource_group.id,
        identity_name="cluster identity")
    print("\t[OK] Resource group ready")

    return backup_resource_group, backup_resource_group_name


def _find_existing_backup_storage_account(storage_client, cluster_location):
    """
    Search for an existing AKS backup storage account in the subscription by tag.

    Looks for storage accounts with tag: AKSAzureBackup = <location>

    Returns:
        tuple: (storage_account, resource_group_name) if found, (None, None) otherwise
    """
    try:
        # List all storage accounts in the subscription
        for sa in storage_client.storage_accounts.list():
            if sa.tags:
                # Check if this SA has the AKS backup tag matching the location
                tag_value = sa.tags.get(AKS_BACKUP_TAG_KEY)
                if tag_value and tag_value.lower() == cluster_location.lower():
                    # Parse resource group from the SA id
                    sa_parts = parse_resource_id(sa.id)
                    return sa, sa_parts['resource_group']
    except Exception:
        # If we can't list storage accounts, we'll create a new one
        pass
    return None, None


def _setup_storage_account(cmd, cluster_subscription_id, storage_account_id, blob_container_name, backup_resource_group_name, cluster_location, cluster_name, cluster_resource_group_name, resource_tags):
    """Create or use storage account."""
    from azure.mgmt.storage import StorageManagementClient

    storage_client = get_mgmt_service_client(cmd.cli_ctx, StorageManagementClient, subscription_id=cluster_subscription_id)
    storage_account_rg = backup_resource_group_name  # Default to backup RG

    if storage_account_id:
        # Use provided storage account
        sa_parts = parse_resource_id(storage_account_id)
        backup_storage_account_name = sa_parts['name']
        storage_account_rg = sa_parts['resource_group']
        print(f"\tUsing provided storage account: {backup_storage_account_name}")
        backup_storage_account = storage_client.storage_accounts.get_properties(storage_account_rg, backup_storage_account_name)
        backup_storage_account_container_name = blob_container_name if blob_container_name else _generate_backup_storage_account_container_name(cluster_name, cluster_resource_group_name)
    else:
        # Search for existing backup storage account with matching tag
        print(f"\tSearching for existing AKS backup storage account in region {cluster_location}...")
        backup_storage_account, existing_rg = _find_existing_backup_storage_account(storage_client, cluster_location)

        if backup_storage_account:
            # Found existing storage account - reuse it
            backup_storage_account_name = backup_storage_account.name
            storage_account_rg = existing_rg
            print(f"\tFound existing backup storage account: {backup_storage_account_name}")
        else:
            # Create new storage account with AKS backup tag
            backup_storage_account_name = _generate_backup_storage_account_name(cluster_location)
            print(f"\tCreating storage account: {backup_storage_account_name}")

            # Build tags - include AKS backup tag plus any user-provided tags
            sa_tags = {AKS_BACKUP_TAG_KEY: cluster_location}
            if resource_tags:
                sa_tags.update(resource_tags)

            storage_params = {
                "location": cluster_location,
                "kind": "StorageV2",
                "sku": {"name": "Standard_LRS"},
                "allow_blob_public_access": False,
                "allow_shared_key_access": False,
                "tags": sa_tags
            }
            backup_storage_account = storage_client.storage_accounts.begin_create(
                resource_group_name=backup_resource_group_name,
                account_name=backup_storage_account_name,
                parameters=storage_params).result()

        backup_storage_account_container_name = _generate_backup_storage_account_container_name(cluster_name, cluster_resource_group_name)

    print(f"\tStorage Account: {backup_storage_account.id}")
    print(f"\tCreating blob container: {backup_storage_account_container_name}")
    storage_client.blob_containers.create(storage_account_rg, backup_storage_account_name, backup_storage_account_container_name, {})
    print("\t[OK] Storage account ready")

    return backup_storage_account, backup_storage_account_name, backup_storage_account_container_name


def _install_backup_extension(cmd, cluster_subscription_id, cluster_resource_group_name, cluster_name, backup_storage_account_name, backup_storage_account_container_name, backup_resource_group_name, backup_storage_account):
    """Install backup extension on the cluster."""
    backup_extension = _create_backup_extension(
        cmd,
        cluster_subscription_id,
        cluster_resource_group_name,
        cluster_name,
        backup_storage_account_name,
        backup_storage_account_container_name,
        backup_resource_group_name,
        cluster_subscription_id)

    _check_and_assign_role(
        cmd,
        role="Storage Blob Data Contributor",
        assignee=backup_extension.aks_assigned_identity.principal_id,
        scope=backup_storage_account.id,
        identity_name="backup extension identity")
    print("\t[OK] Backup extension ready")

    return backup_extension


def _get_existing_backup_extension(cmd, cluster_subscription_id, cluster_resource_group_name, cluster_name):
    """
    Check if a backup extension already exists on the cluster.

    Returns:
        extension object if found and healthy, None if not found.
        Raises on Failed or transient states.
    """
    from azext_dataprotection.vendored_sdks.azure_mgmt_kubernetesconfiguration import SourceControlConfigurationClient
    k8s_configuration_client = get_mgmt_service_client(cmd.cli_ctx, SourceControlConfigurationClient, subscription_id=cluster_subscription_id)

    try:
        extensions = k8s_configuration_client.extensions.list(
            cluster_rp="Microsoft.ContainerService",
            cluster_resource_name="managedClusters",
            resource_group_name=cluster_resource_group_name,
            cluster_name=cluster_name)

        for page in extensions.by_page():
            for extension in page:
                if extension.extension_type and extension.extension_type.lower() == 'microsoft.dataprotection.kubernetes':
                    provisioning_state = extension.provisioning_state
                    if provisioning_state == "Succeeded":
                        return extension
                    elif provisioning_state == "Failed":
                        raise InvalidArgumentValueError(
                            f"Data protection extension '{extension.name}' exists on cluster '{cluster_name}' but is in Failed state.\n"
                            f"Please take corrective action before running this command again:\n"
                            f"  1. Check extension logs: az k8s-extension show --name {extension.name} --cluster-name {cluster_name} --resource-group {cluster_resource_group_name} --cluster-type managedClusters\n"
                            f"  2. Delete the failed extension: az k8s-extension delete --name {extension.name} --cluster-name {cluster_name} --resource-group {cluster_resource_group_name} --cluster-type managedClusters --yes\n"
                            f"  3. Re-run this command to install a fresh extension.\n"
                            f"For troubleshooting, visit: https://aka.ms/aksclusterbackup"
                        )
                    else:
                        raise InvalidArgumentValueError(
                            f"Data protection extension '{extension.name}' is in '{provisioning_state}' state.\n"
                            f"Please wait for the operation to complete and try again."
                        )
    except InvalidArgumentValueError:
        raise
    except Exception:
        pass

    return None


def _get_storage_account_from_extension(cmd, extension, cluster_subscription_id):
    """
    Extract the storage account details from an existing backup extension's configuration.

    The extension stores config in Velero-style keys:
      - configuration.backupStorageLocation.config.storageAccount
      - configuration.backupStorageLocation.bucket
      - configuration.backupStorageLocation.config.resourceGroup

    Returns:
        tuple: (storage_account_object, storage_account_name, container_name, resource_group)
    """
    from azure.mgmt.storage import StorageManagementClient

    config = extension.configuration_settings or {}
    sa_name = config.get("configuration.backupStorageLocation.config.storageAccount")
    container = config.get("configuration.backupStorageLocation.bucket")
    sa_rg = config.get("configuration.backupStorageLocation.config.resourceGroup")

    if not sa_name or not sa_rg:
        return None, None, None, None

    print(f"\tExtension is configured with storage account: {sa_name} (RG: {sa_rg}, container: {container})")

    storage_client = get_mgmt_service_client(cmd.cli_ctx, StorageManagementClient, subscription_id=cluster_subscription_id)
    try:
        sa = storage_client.storage_accounts.get_properties(sa_rg, sa_name)
        return sa, sa_name, container, sa_rg
    except Exception as e:
        print(f"\tWarning: Could not fetch storage account '{sa_name}' from extension config: {str(e)[:100]}")
        return None, None, None, None


def _find_existing_backup_vault(cmd, cluster_subscription_id, cluster_location):
    """
    Search for an existing AKS backup vault in the subscription by tag.

    Looks for backup vaults with tag: AKSAzureBackup = <location>

    Returns:
        backup_vault if found, None otherwise
    """
    from azext_dataprotection.aaz.latest.dataprotection.backup_vault import List as _BackupVaultList

    try:
        # List all backup vaults in the cluster's subscription
        vaults = _BackupVaultList(cli_ctx=cmd.cli_ctx)(command_args={
            "subscription": cluster_subscription_id
        })

        for vault in vaults:
            if vault.get('tags'):
                # Check if this vault has the AKS backup tag matching the location
                tag_value = vault['tags'].get(AKS_BACKUP_TAG_KEY)
                if tag_value and tag_value.lower() == cluster_location.lower():
                    return vault
    except Exception:
        # If we can't list vaults, we'll create a new one
        pass
    return None


def _try_create_vault_with_storage_type(cmd, vault_create_cls, backup_vault_name, backup_resource_group_name, cluster_location, vault_tags, storage_type, cluster_subscription_id=None):
    """
    Attempt to create a backup vault with the given storage type.

    Returns:
        backup_vault dict on success, None on failure
    """
    backup_vault_args = {
        "vault_name": backup_vault_name,
        "resource_group": backup_resource_group_name,
        "location": cluster_location,
        "type": "SystemAssigned",
        "storage_setting": [{'type': storage_type, 'datastore-type': 'VaultStore'}],
        "soft_delete_state": "On",
        "retention_duration_in_days": 14.0,
        "immutability_state": "Unlocked",
        "cross_subscription_restore_state": "Enabled",
        "tags": vault_tags
    }

    if cluster_subscription_id:
        backup_vault_args["subscription"] = cluster_subscription_id

    # Enable CRR only for GRS vaults (requires paired region)
    if storage_type == 'GeoRedundant':
        backup_vault_args["cross_region_restore_state"] = "Enabled"

    try:
        backup_vault = vault_create_cls(cli_ctx=cmd.cli_ctx)(command_args=backup_vault_args).result()
        return backup_vault
    except Exception as e:
        print(f"\tVault creation with {storage_type} failed: {str(e)[:120]}")
        return None


def _setup_backup_vault(cmd, backup_strategy, backup_vault_id, cluster_subscription_id, cluster_location, backup_resource_group_name, cluster_resource, backup_resource_group, resource_tags):
    """Create or use backup vault."""
    from azext_dataprotection.aaz.latest.dataprotection.backup_vault import Create as _BackupVaultCreate

    if backup_strategy == 'Custom' and backup_vault_id:
        # Use provided vault for Custom strategy
        vault_parts = parse_resource_id(backup_vault_id)
        backup_vault_name = vault_parts['name']
        vault_rg = vault_parts['resource_group']
        print(f"\tUsing provided backup vault: {backup_vault_name}")
        from azext_dataprotection.aaz.latest.dataprotection.backup_vault import Show as _BackupVaultShow
        backup_vault = _BackupVaultShow(cli_ctx=cmd.cli_ctx)(command_args={
            "vault_name": backup_vault_name,
            "resource_group": vault_rg,
            "subscription": cluster_subscription_id
        })
    else:
        # Search for existing backup vault with matching tag
        print(f"\tSearching for existing AKS backup vault in region {cluster_location}...")
        backup_vault = _find_existing_backup_vault(cmd, cluster_subscription_id, cluster_location)

        if backup_vault:
            # Found existing vault - reuse it
            backup_vault_name = backup_vault['name']
            print(f"\tFound existing backup vault: {backup_vault_name}")
        else:
            # Create new backup vault with AKS backup tag
            backup_vault_name = _generate_backup_vault_name(cluster_location)
            print(f"\tCreating backup vault: {backup_vault_name}")

            # Build tags - include AKS backup tag plus any user-provided tags
            vault_tags = {AKS_BACKUP_TAG_KEY: cluster_location}
            if resource_tags:
                vault_tags.update(resource_tags)

            # Try storage types in order of preference: GRS → ZRS → LRS
            # Not all regions support all types, so we fall back gracefully.
            backup_vault = None
            storage_type = None

            for try_type in ['GeoRedundant', 'ZoneRedundant', 'LocallyRedundant']:
                print(f"\tTrying storage type: {try_type}...")
                backup_vault = _try_create_vault_with_storage_type(
                    cmd, _BackupVaultCreate, backup_vault_name, backup_resource_group_name,
                    cluster_location, vault_tags, try_type, cluster_subscription_id)
                if backup_vault:
                    storage_type = try_type
                    print(f"\tVault created with storage type: {storage_type}")
                    break

            if not backup_vault:
                raise InvalidArgumentValueError(
                    f"Failed to create backup vault '{backup_vault_name}' in region '{cluster_location}' "
                    f"with any storage type (GeoRedundant, ZoneRedundant, LocallyRedundant).\n"
                    f"Please check region availability and try again."
                )

    print(f"\tBackup Vault: {backup_vault['id']}")
    _check_and_assign_role(
        cmd,
        role="Reader",
        assignee=backup_vault["identity"]["principalId"],
        scope=cluster_resource.id,
        identity_name="backup vault identity (on cluster)")

    _check_and_assign_role(
        cmd,
        role="Reader",
        assignee=backup_vault["identity"]["principalId"],
        scope=backup_resource_group.id,
        identity_name="backup vault identity (on resource group)")

    _check_and_assign_role(
        cmd,
        role="Disk Snapshot Contributor",
        assignee=backup_vault["identity"]["principalId"],
        scope=backup_resource_group.id,
        identity_name="backup vault identity (snapshot contributor on resource group)")
    print("\t[OK] Backup vault ready")

    return backup_vault, backup_vault_name


def _setup_backup_policy(cmd, backup_vault, backup_vault_name, backup_resource_group_name, backup_strategy, backup_vault_id, backup_policy_id, cluster_subscription_id):
    """Create or use backup policy."""
    from azext_dataprotection.manual.aaz_operations.backup_policy import Create as _BackupPolicyCreate
    from azext_dataprotection.aaz.latest.dataprotection.backup_policy import List as _BackupPolicyList

    # Create or use backup policy
    if backup_strategy == 'Custom' and backup_policy_id:
        # Use provided policy for Custom strategy
        backup_policy_name = parse_resource_id(backup_policy_id)['name']
        print(f"\tUsing provided backup policy: {backup_policy_name}")
        backup_policy = {"id": backup_policy_id}
    else:
        # Get vault RG - for custom with provided vault, use vault's RG
        vault_rg_for_policy = backup_resource_group_name
        if backup_strategy == 'Custom' and backup_vault_id:
            vault_rg_for_policy = parse_resource_id(backup_vault_id)['resource_group']

        # Check if policy already exists in this vault
        backup_policy_name = _generate_backup_policy_name(backup_strategy)
        existing_policy = None
        try:
            policies = _BackupPolicyList(cli_ctx=cmd.cli_ctx)(command_args={
                "resource_group": vault_rg_for_policy,
                "vault_name": backup_vault_name,
                "subscription": cluster_subscription_id
            })
            for policy in policies:
                if policy.get('name') == backup_policy_name:
                    existing_policy = policy
                    break
        except Exception:
            pass

        if existing_policy:
            print(f"\tFound existing backup policy: {backup_policy_name}")
            backup_policy = existing_policy
        else:
            # Create policy based on strategy
            policy_config = _get_policy_config_for_strategy(backup_strategy)
            print(f"\tCreating backup policy: {backup_policy_name}")

            backup_policy = _BackupPolicyCreate(cli_ctx=cmd.cli_ctx)(command_args={
                "backup_policy_name": backup_policy_name,
                "resource_group": vault_rg_for_policy,
                "vault_name": backup_vault_name,
                "policy": policy_config,
                "subscription": cluster_subscription_id
            })

    print(f"\tBackup Policy: {backup_policy.get('id', backup_policy_id if backup_policy_id else 'N/A')}")
    print("\t[OK] Backup policy ready")

    return backup_policy


def _setup_trusted_access(cmd, cluster_subscription_id, cluster_resource_group_name, cluster_name, backup_vault):
    """Setup trusted access role binding between backup vault and cluster."""
    from azext_dataprotection.vendored_sdks.azure_mgmt_containerservice import ContainerServiceClient
    from azext_dataprotection.vendored_sdks.azure_mgmt_containerservice.models import TrustedAccessRoleBinding

    cluster_client = get_mgmt_service_client(cmd.cli_ctx, ContainerServiceClient, subscription_id=cluster_subscription_id)
    vault_id = backup_vault["id"]
    vault_name = backup_vault["name"]

    print("\tConfiguring trusted access between:")
    print(f"\t\t- Backup Vault: {vault_name}")
    print(f"\t\t- AKS Cluster:  {cluster_name}")

    # Check if trusted access binding already exists for this vault-cluster pair
    print("\tChecking for existing trusted access binding...")
    try:
        existing_bindings = cluster_client.trusted_access_role_bindings.list(
            resource_group_name=cluster_resource_group_name,
            resource_name=cluster_name
        )
        for binding in existing_bindings:
            if binding.source_resource_id.lower() == vault_id.lower():
                print(f"\tFound existing binding: {binding.name}")
                print("\t[OK] Trusted access already configured")
                return
    except Exception:
        # If we can't list, we'll try to create
        pass

    # Create new trusted access role binding with GUID-based name
    binding_name = _generate_trusted_access_role_binding_name()
    print(f"\tCreating trusted access role binding: {binding_name}")
    print("\t\tRole: Microsoft.DataProtection/backupVaults/backup-operator")

    _trusted_access_role_binding = TrustedAccessRoleBinding(
        source_resource_id=vault_id,
        roles=["Microsoft.DataProtection/backupVaults/backup-operator"])

    cluster_client.trusted_access_role_bindings.begin_create_or_update(
        resource_group_name=cluster_resource_group_name,
        resource_name=cluster_name,
        trusted_access_role_binding_name=binding_name,
        trusted_access_role_binding=_trusted_access_role_binding).result()
    print("\t[OK] Trusted access configured - vault can now access cluster for backup operations")


def _create_backup_instance(cmd, cluster_name, cluster_resource_group_name, datasource_id, cluster_location, backup_vault_name, backup_resource_group_name, backup_strategy, backup_vault_id, backup_policy, backup_policy_id, backup_resource_group, cluster_subscription_id):
    """Create backup instance."""
    from azext_dataprotection.manual.aaz_operations.backup_instance import ValidateAndCreate as _BackupInstanceValidateAndCreate
    import uuid

    backup_instance_name = f"{cluster_name}-{str(uuid.uuid4())[:8]}"

    # Get vault RG for backup instance - use backup RG unless custom vault provided
    vault_rg_for_bi = backup_resource_group_name
    if backup_strategy == 'Custom' and backup_vault_id:
        vault_rg_for_bi = parse_resource_id(backup_vault_id)['resource_group']

    # Get policy ID
    policy_id_for_bi = backup_policy.get("id") if isinstance(backup_policy, dict) else backup_policy_id

    print(f"\tCreating backup instance: {backup_instance_name}")
    backup_instance_payload = _get_backup_instance_payload(
        backup_instance_name=backup_instance_name,
        cluster_name=cluster_name,
        datasource_id=datasource_id,
        cluster_location=cluster_location,
        policy_id=policy_id_for_bi,
        backup_resource_group_id=backup_resource_group.id
    )

    backup_instance = _BackupInstanceValidateAndCreate(cli_ctx=cmd.cli_ctx)(command_args={
        "backup_instance_name": backup_instance_name,
        "resource_group": vault_rg_for_bi,
        "vault_name": backup_vault_name,
        "backup_instance": backup_instance_payload,
        "subscription": cluster_subscription_id
    }).result()

    # Check and report the protection state
    protection_state = backup_instance.get('properties', {}).get('currentProtectionState', 'Unknown')
    print(f"\tProtection State: {protection_state}")

    if protection_state == "ProtectionConfigured":
        print("\t[OK] Backup instance created and protection configured")
    elif protection_state == "ConfiguringProtection":
        print("\t[OK] Backup instance created - protection configuration in progress")
    elif protection_state == "ProtectionError":
        error_details = backup_instance.get('properties', {}).get('protectionErrorDetails', {})
        error_msg = error_details.get('message', 'Unknown error') if isinstance(error_details, dict) else str(error_details)
        print(f"\t[WARNING] Backup instance created but protection has errors: {error_msg}")
    else:
        print("\t[OK] Backup instance created")

    return backup_instance, policy_id_for_bi


def dataprotection_enable_backup_helper(cmd, datasource_id: str, backup_strategy='Week', configuration_params=None):
    """
    Enable backup for an AKS cluster.

    Args:
        cmd: CLI command context
        datasource_id: Full ARM resource ID of the AKS cluster
        backup_strategy: Backup strategy (Week, Month, Immutable, DisasterRecovery, Custom)
        configuration_params: Dict with configuration settings
    """
    print("=" * 60)
    print("Enabling backup for AKS cluster")
    print("=" * 60)
    print(f"Datasource ID: {datasource_id}")
    print(f"Backup Strategy: {backup_strategy}")

    # Parse configuration_params
    if configuration_params is None:
        configuration_params = {}
    if isinstance(configuration_params, str):
        configuration_params = json.loads(configuration_params)

    # Validate request (raises on failure)
    _validate_request(datasource_id, backup_strategy, configuration_params)

    # Extract configuration values (camelCase keys)
    resource_tags = configuration_params.get("tags")
    storage_account_id = configuration_params.get("storageAccountResourceId")
    blob_container_name = configuration_params.get("blobContainerName")
    backup_resource_group_id = configuration_params.get("backupResourceGroupId")
    backup_vault_id = configuration_params.get("backupVaultId")
    backup_policy_id = configuration_params.get("backupPolicyId")

    # Parse cluster details from resource ID
    cluster_id_parts = parse_resource_id(datasource_id)
    cluster_subscription_id = cluster_id_parts['subscription']
    cluster_resource_group_name = cluster_id_parts['resource_group']
    cluster_name = cluster_id_parts['name']

    if resource_tags:
        print(f"Resource Tags: {json.dumps(resource_tags)}")

    # Show execution plan and get user confirmation
    print("\nThis command will perform the following steps:")
    print("  [1] Validate the AKS cluster")
    print("  [2] Create or reuse a backup resource group (AKSAzureBackup_<region>)")
    print("  [3] Create or reuse a storage account for backup data")
    print("  [4] Install the data protection extension on the cluster")
    print("  [5] Create or reuse a backup vault")
    print("  [6] Create or reuse a backup policy")
    print("  [7] Configure trusted access between vault and cluster")
    print("  [8] Create a backup instance to start protection")
    print("")
    print("The following RBAC role assignments will be created:")
    print("  - Cluster MSI   → Contributor on Backup Resource Group")
    print("  - Extension MSI → Storage Blob Data Contributor on Storage Account")
    print("  - Vault MSI     → Reader on AKS Cluster")
    print("  - Vault MSI     → Reader on Backup Resource Group")
    print("  - Vault MSI     → Disk Snapshot Contributor on Backup Resource Group")
    print("  - Vault MSI     → Storage Blob Data Reader on Storage Account")
    print("")
    print(f"  Subscription: {cluster_subscription_id}")
    print(f"  Cluster:      {cluster_name}")
    print("  Region:       (will be determined from cluster)")
    print(f"  Strategy:     {backup_strategy}")
    print("")
    print("NOTE: This command requires elevated privileges (Owner or")
    print("  User Access Administrator) on the subscription to create")
    print("  RBAC role assignments listed above.")
    print("")

    from knack.prompting import prompt_y_n
    if not prompt_y_n("Do you want to proceed?", default='y'):
        print("Operation cancelled by user.")
        return

    from azure.mgmt.resource import ResourceManagementClient
    resource_client = get_mgmt_service_client(cmd.cli_ctx, ResourceManagementClient, subscription_id=cluster_subscription_id)

    # Pre-check: Verify no existing backup instance for this cluster
    print("\n[Pre-check] Checking for existing backup...")
    _check_existing_backup_instance(resource_client, datasource_id, cluster_name)

    # Step 1: Validate cluster
    print("\n[1/8] Validating cluster...")
    cluster_resource, cluster_location, cluster_identity_principal_id = _validate_cluster(resource_client, datasource_id, cluster_name)

    # Step 2: Setup resource group
    print("\n[2/8] Setting up backup resource group...")
    backup_resource_group, backup_resource_group_name = _setup_resource_group(
        cmd, resource_client, backup_resource_group_id, cluster_location, cluster_name,
        cluster_identity_principal_id, resource_tags)

    # Step 3 & 4: Check extension first, then handle storage account accordingly
    # If the extension is already installed, use its configured storage account
    # instead of creating/finding a new one (which may be different).
    print("\n[3/8] Checking for existing backup extension...")
    existing_extension = _get_existing_backup_extension(
        cmd, cluster_subscription_id, cluster_resource_group_name, cluster_name)

    if existing_extension:
        print(f"\tBackup extension already installed: {existing_extension.name}")

        # Extract the storage account the extension is actually configured with
        ext_sa, ext_sa_name, ext_container, ext_sa_rg = _get_storage_account_from_extension(
            cmd, existing_extension, cluster_subscription_id)

        if ext_sa:
            # Use the extension's configured storage account for all subsequent operations
            backup_storage_account = ext_sa
            backup_storage_account_name = ext_sa_name
            backup_storage_account_container_name = ext_container
            print(f"\tUsing extension's storage account: {ext_sa_name}")
        else:
            # Fallback: extension exists but we can't read its config — setup storage account normally
            print("\tWarning: Could not read extension storage config, setting up storage account...")
            backup_storage_account, backup_storage_account_name, backup_storage_account_container_name = _setup_storage_account(
                cmd, cluster_subscription_id, storage_account_id, blob_container_name,
                backup_resource_group_name, cluster_location, cluster_name, cluster_resource_group_name, resource_tags)

        # Ensure extension identity has correct role on its storage account
        _check_and_assign_role(
            cmd,
            role="Storage Blob Data Contributor",
            assignee=existing_extension.aks_assigned_identity.principal_id,
            scope=backup_storage_account.id,
            identity_name="backup extension identity")
        print("\t[OK] Storage account ready")

        print("\n[4/8] Backup extension already installed...")
        print("\t[OK] Backup extension ready")
    else:
        # No extension — setup storage account first, then install extension
        print("\tNo existing extension found, setting up storage account...")
        backup_storage_account, backup_storage_account_name, backup_storage_account_container_name = _setup_storage_account(
            cmd, cluster_subscription_id, storage_account_id, blob_container_name,
            backup_resource_group_name, cluster_location, cluster_name, cluster_resource_group_name, resource_tags)

        print("\n[4/8] Installing backup extension...")
        _install_backup_extension(
            cmd, cluster_subscription_id, cluster_resource_group_name, cluster_name,
            backup_storage_account_name, backup_storage_account_container_name,
            backup_resource_group_name, backup_storage_account)

    # Step 5: Setup backup vault
    print("\n[5/8] Setting up backup vault...")
    backup_vault, backup_vault_name = _setup_backup_vault(
        cmd, backup_strategy, backup_vault_id, cluster_subscription_id, cluster_location, backup_resource_group_name,
        cluster_resource, backup_resource_group, resource_tags)

    # Grant vault identity read access to the backup storage account
    _check_and_assign_role(
        cmd,
        role="Storage Blob Data Reader",
        assignee=backup_vault["identity"]["principalId"],
        scope=backup_storage_account.id,
        identity_name="backup vault identity (on storage account)")

    # Step 6: Setup backup policy
    print("\n[6/8] Setting up backup policy...")
    backup_policy = _setup_backup_policy(
        cmd, backup_vault, backup_vault_name, backup_resource_group_name,
        backup_strategy, backup_vault_id, backup_policy_id, cluster_subscription_id)

    # Step 7: Setup trusted access
    print("\n[7/8] Setting up trusted access...")
    _setup_trusted_access(
        cmd, cluster_subscription_id, cluster_resource_group_name, cluster_name, backup_vault)

    # Wait for role assignment propagation before creating backup instance
    import time
    wait_seconds = 120
    print(f"\n\tWaiting {wait_seconds} seconds for permission propagation across Azure AD...")
    for remaining in range(wait_seconds, 0, -10):
        print(f"\t  {remaining} seconds remaining...", end='\r')
        time.sleep(min(10, remaining))
    print("\t  Permission propagation wait complete.      ")

    # Step 8: Create backup instance
    print("\n[8/8] Configuring backup instance...")
    backup_instance, policy_id_for_bi = _create_backup_instance(
        cmd, cluster_name, cluster_resource_group_name, datasource_id, cluster_location,
        backup_vault_name, backup_resource_group_name, backup_strategy, backup_vault_id, backup_policy, backup_policy_id, backup_resource_group, cluster_subscription_id)

    # Print summary
    print("\n" + "=" * 60)
    print("Backup enabled successfully!")
    print("=" * 60)
    print("\nBackup Configuration:")
    print(f"  * Resource Group:   {backup_resource_group.id}")
    print(f"  * Storage Account:  {backup_storage_account.id}")
    print(f"  * Backup Vault:     {backup_vault['id']}")
    print(f"  * Backup Policy:    {policy_id_for_bi}")
    print(f"  * Backup Instance:  {backup_instance.get('id', 'N/A')}")
    print("=" * 60)


def _get_policy_config_for_strategy(backup_strategy):
    """Get backup policy configuration based on strategy.

    Strategies:
    - Week: 7 days operational tier only, daily incremental
    - Month: 30 days operational tier only, daily incremental
    - DisasterRecovery: 7 days operational tier + 90 days vault tier, daily incremental with FirstOfDay vault copy
    """
    if backup_strategy == 'Week':
        op_retention = "P7D"
        vault_retention = None
    elif backup_strategy == 'Month':
        op_retention = "P30D"
        vault_retention = None
    elif backup_strategy == 'DisasterRecovery':
        op_retention = "P7D"
        vault_retention = "P90D"
    else:
        raise InvalidArgumentValueError(
            f"Unknown backup strategy '{backup_strategy}'. Supported strategies: Week, Month, DisasterRecovery, Custom."
        )

    # Operational Store retention rule (all strategies)
    policy_rules = [
        {
            "isDefault": True,
            "lifecycles": [
                {
                    "deleteAfter": {
                        "duration": op_retention,
                        "objectType": "AbsoluteDeleteOption"
                    },
                    "sourceDataStore": {
                        "dataStoreType": "OperationalStore",
                        "objectType": "DataStoreInfoBase"
                    },
                    "targetDataStoreCopySettings": []
                }
            ],
            "name": "Default",
            "objectType": "AzureRetentionRule"
        }
    ]

    # Vault Store retention rule (only when vault_retention is set)
    if vault_retention:
        policy_rules.append({
            "isDefault": False,
            "lifecycles": [
                {
                    "deleteAfter": {
                        "duration": vault_retention,
                        "objectType": "AbsoluteDeleteOption"
                    },
                    "sourceDataStore": {
                        "dataStoreType": "VaultStore",
                        "objectType": "DataStoreInfoBase"
                    },
                    "targetDataStoreCopySettings": []
                }
            ],
            "name": "Vault",
            "objectType": "AzureRetentionRule"
        })

    # Tagging criteria — Default for all, Vault (FirstOfDay) when vault tier is enabled
    tagging_criteria = [
        {
            "isDefault": True,
            "tagInfo": {"id": "Default_", "tagName": "Default"},
            "taggingPriority": 99
        }
    ]
    if vault_retention:
        tagging_criteria.append({
            "isDefault": False,
            "tagInfo": {"id": "Vault_", "tagName": "Vault"},
            "taggingPriority": 50,
            "criteria": [
                {
                    "objectType": "ScheduleBasedBackupCriteria",
                    "absoluteCriteria": ["FirstOfDay"]
                }
            ]
        })

    # Backup rule — daily incremental
    policy_rules.append({
        "backupParameters": {
            "backupType": "Incremental",
            "objectType": "AzureBackupParams"
        },
        "dataStore": {
            "dataStoreType": "OperationalStore",
            "objectType": "DataStoreInfoBase"
        },
        "name": "BackupDaily",
        "objectType": "AzureBackupRule",
        "trigger": {
            "objectType": "ScheduleBasedTriggerContext",
            "schedule": {
                "repeatingTimeIntervals": ["R/2024-01-01T00:00:00+00:00/P1D"],
                "timeZone": "Coordinated Universal Time"
            },
            "taggingCriteria": tagging_criteria
        }
    })

    return {
        "objectType": "BackupPolicy",
        "datasourceTypes": ["Microsoft.ContainerService/managedClusters"],
        "policyRules": policy_rules
    }


def _get_backup_instance_payload(backup_instance_name, cluster_name, datasource_id, cluster_location, policy_id, backup_resource_group_id):
    """Get backup instance payload for AKS cluster."""
    return {
        "backup_instance_name": backup_instance_name,
        "properties": {
            "friendly_name": f"{cluster_name}\\fullbackup",
            "object_type": "BackupInstance",
            "data_source_info": {
                "datasource_type": "Microsoft.ContainerService/managedClusters",
                "object_type": "Datasource",
                "resource_id": datasource_id,
                "resource_location": cluster_location,
                "resource_name": cluster_name,
                "resource_type": "Microsoft.ContainerService/managedclusters",
                "resource_uri": datasource_id
            },
            "data_source_set_info": {
                "datasource_type": "Microsoft.ContainerService/managedClusters",
                "object_type": "DatasourceSet",
                "resource_id": datasource_id,
                "resource_location": cluster_location,
                "resource_name": cluster_name,
                "resource_type": "Microsoft.ContainerService/managedclusters",
                "resource_uri": datasource_id
            },
            "policy_info": {
                "policy_id": policy_id,
                "policy_parameters": {
                    "backup_datasource_parameters_list": [
                        {
                            "objectType": "KubernetesClusterBackupDatasourceParameters",
                            "include_cluster_scope_resources": True,
                            "snapshot_volumes": True
                        }
                    ],
                    "data_store_parameters_list": [
                        {
                            "object_type": "AzureOperationalStoreParameters",
                            "data_store_type": "OperationalStore",
                            "resource_group_id": backup_resource_group_id
                        }
                    ]
                }
            }
        }
    }


def _generate_arm_id(subscription_id, resource_group_name, resource_type, resource_name):
    return f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/{resource_type}/{resource_name}"


def _generate_backup_resource_group_name(cluster_location):
    """
    Generate backup resource group name (one per region, shared across clusters).

    Naming constraints:
    - Length: 1-90 characters
    - Allowed characters: alphanumerics, underscores, parentheses, hyphens, periods
    - Cannot end with a period

    Format: AKSAzureBackup_<location> (one resource group per region)
    Example: AKSAzureBackup_eastasia
    """
    return f"AKSAzureBackup_{cluster_location}"


def _generate_backup_storage_account_name(cluster_location):
    """
    Generate backup storage account name (one per region, shared across clusters).

    Naming constraints:
    - Length: 3-24 characters
    - Allowed characters: lowercase letters and numbers only
    - Must be globally unique

    Format: aksbkp<location><guid_suffix> (one storage account per region)
    Example: aksbkpeastasia1a2b3c
    """
    import uuid
    # Remove any non-alphanumeric chars from location and make lowercase
    sanitized_location = ''.join(c for c in cluster_location.lower() if c.isalnum())
    # Generate a short GUID suffix for uniqueness
    guid_suffix = str(uuid.uuid4()).replace('-', '')[:6]
    # Truncate location to fit: 24 chars max - 6 (aksbkp) - 6 (guid) = 12 chars for location
    sanitized_location = sanitized_location[:12]
    return f"aksbkp{sanitized_location}{guid_suffix}"


def _generate_backup_storage_account_container_name(cluster_name, cluster_resource_group_name):
    """
    Generate backup blob container name (unique per cluster).

    Naming constraints:
    - Length: 3-63 characters
    - Allowed characters: lowercase letters, numbers, and hyphens
    - Must start with a letter or number
    - Cannot contain consecutive hyphens

    Format: <sanitized_cluster_name>-<sanitized_cluster_rg_name>
    Example: contoso-aks-hack-contoso-aks-rg
    """
    import re

    def sanitize(name):
        # Lowercase, replace invalid chars with hyphens
        sanitized = re.sub(r'[^a-z0-9-]', '-', name.lower())
        # Remove consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remove leading/trailing hyphens
        return sanitized.strip('-')

    sanitized_cluster = sanitize(cluster_name)
    sanitized_rg = sanitize(cluster_resource_group_name)

    # Combine and truncate to 63 chars max
    container_name = f"{sanitized_cluster}-{sanitized_rg}"
    return container_name[:63].rstrip('-')


def _generate_backup_vault_name(cluster_location):
    """
    Generate backup vault name (one per region, shared across clusters).

    Naming constraints:
    - Length: 2-50 characters
    - Allowed characters: alphanumerics and hyphens
    - Must start with a letter
    - Cannot end with a hyphen

    Format: AKSAzureBackup-<location> (one vault per region)
    Example: AKSAzureBackup-eastasia
    """
    return f"AKSAzureBackup-{cluster_location}"


def _generate_backup_policy_name(backup_strategy):
    """
    Generate backup policy name (shared per strategy).

    Naming constraints:
    - Length: 3-150 characters
    - Allowed characters: alphanumerics and hyphens

    Format: AKSBackupPolicy-<strategy>
    """
    return f"AKSBackupPolicy-{backup_strategy}"


def _generate_trusted_access_role_binding_name():
    """
    Generate trusted access role binding name using GUID.

    Naming constraints:
    - Length: 1-24 characters
    - Allowed characters: alphanumerics, underscores, hyphens

    Format: tarb-<guid_first_16_chars>
    Example: tarb-a1b2c3d4e5f6g7h8
    """
    import uuid
    # Generate GUID and take first 16 chars (without hyphens)
    guid_suffix = str(uuid.uuid4()).replace('-', '')[:16]
    # "tarb-" (5 chars) + guid (16 chars) = 21 chars
    return f"tarb-{guid_suffix}"


def _create_backup_extension(cmd, subscription_id, resource_group_name, cluster_name, storage_account_name, storage_account_container_name, storage_account_resource_group, storage_account_subscription_id):
    from azext_dataprotection.vendored_sdks.azure_mgmt_kubernetesconfiguration import SourceControlConfigurationClient
    k8s_configuration_client = get_mgmt_service_client(cmd.cli_ctx, SourceControlConfigurationClient, subscription_id=subscription_id)

    extensions = k8s_configuration_client.extensions.list(
        cluster_rp="Microsoft.ContainerService",
        cluster_resource_name="managedClusters",
        resource_group_name=resource_group_name,
        cluster_name=cluster_name)

    for page in extensions.by_page():
        for extension in page:
            if extension.extension_type.lower() == 'microsoft.dataprotection.kubernetes':
                # Check extension provisioning state
                provisioning_state = extension.provisioning_state
                if provisioning_state == "Succeeded":
                    print(f"\tData protection extension ({extension.name}) is already installed and healthy.")
                    return extension
                elif provisioning_state == "Failed":
                    raise InvalidArgumentValueError(
                        f"Data protection extension '{extension.name}' exists on cluster '{cluster_name}' but is in Failed state.\n"
                        f"Please take corrective action before running this command again:\n"
                        f"  1. Check extension logs: az k8s-extension show --name {extension.name} --cluster-name {cluster_name} --resource-group {resource_group_name} --cluster-type managedClusters\n"
                        f"  2. Delete the failed extension: az k8s-extension delete --name {extension.name} --cluster-name {cluster_name} --resource-group {resource_group_name} --cluster-type managedClusters --yes\n"
                        f"  3. Re-run this command to install a fresh extension.\n"
                        f"For troubleshooting, visit: https://aka.ms/aksclusterbackup"
                    )
                else:
                    # Extension is in a transient state (Creating, Updating, Deleting, etc.)
                    raise InvalidArgumentValueError(
                        f"Data protection extension '{extension.name}' is in '{provisioning_state}' state.\n"
                        f"Please wait for the operation to complete and try again."
                    )

    print("\tInstalling data protection extension (azure-aks-backup)...")

    from azure.cli.core.extension.operations import add_extension_to_path
    from importlib import import_module
    add_extension_to_path("k8s-extension")
    K8s_extension_client_factory = import_module("azext_k8s_extension._client_factory")
    k8s_extension_module = import_module("azext_k8s_extension.custom")

    extension = k8s_extension_module.create_k8s_extension(
        cmd=cmd,
        client=K8s_extension_client_factory.cf_k8s_extension_operation(cmd.cli_ctx),
        resource_group_name=resource_group_name,
        cluster_name=cluster_name,
        name="azure-aks-backup",
        cluster_type="managedClusters",
        extension_type="microsoft.dataprotection.kubernetes",
        cluster_resource_provider="Microsoft.ContainerService",
        scope="cluster",
        auto_upgrade_minor_version=True,
        release_train="stable",
        configuration_settings=[{
            "blobContainer": storage_account_container_name,
            "storageAccount": storage_account_name,
            "storageAccountResourceGroup": storage_account_resource_group,
            "storageAccountSubscriptionId": storage_account_subscription_id
        }]
    ).result()

    # Verify extension is in healthy state after installation
    if extension.provisioning_state == "Succeeded":
        print("\tExtension installed and healthy (Provisioning State: Succeeded)")
    else:
        print(f"\tWarning: Extension provisioning state is '{extension.provisioning_state}'")

    return extension
