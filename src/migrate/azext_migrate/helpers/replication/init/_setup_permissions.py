# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
from knack.util import CLIError
from azext_migrate.helpers._utils import (
    create_or_update_resource,
    APIVersion,
    RoleDefinitionIds
)


def _get_role_name(role_def_id):
    """Get role name from role definition ID."""
    return ("Contributor" if role_def_id == RoleDefinitionIds.ContributorId
            else "Storage Blob Data Contributor")


def _assign_role_to_principal(auth_client, storage_account_id,
                              subscription_id,
                              principal_id, role_def_id,
                              principal_type_name):
    """Assign a role to a principal if not already assigned."""
    from uuid import uuid4
    from azure.mgmt.authorization.models import (
        RoleAssignmentCreateParameters, PrincipalType
    )

    role_name = _get_role_name(role_def_id)

    # Check if assignment exists
    assignments = auth_client.role_assignments.list_for_scope(
        scope=storage_account_id,
        filter=f"principalId eq '{principal_id}'"
    )

    roles = [a.role_definition_id.endswith(role_def_id) for a in assignments]
    has_role = any(roles)

    if not has_role:
        role_assignment_params = RoleAssignmentCreateParameters(
            role_definition_id=(
                f"/subscriptions/{subscription_id}/providers"
                f"/Microsoft.Authorization/roleDefinitions/{role_def_id}"
            ),
            principal_id=principal_id,
            principal_type=PrincipalType.SERVICE_PRINCIPAL
        )
        auth_client.role_assignments.create(
            scope=storage_account_id,
            role_assignment_name=str(uuid4()),
            parameters=role_assignment_params
        )
        print(
            f"  ✓ Created {role_name} role for {principal_type_name} "
            f"{principal_id[:8]}..."
        )
        return f"{principal_id[:8]} - {role_name}", False
    print(
        f"  ✓ {role_name} role already exists for {principal_type_name} "
        f"{principal_id[:8]}"
    )
    return f"{principal_id[:8]} - {role_name} (existing)", True


def _verify_role_assignments(auth_client, storage_account_id,
                             expected_principal_ids):
    """Verify that role assignments were created successfully."""
    print("Verifying role assignments...")
    all_assignments = list(
        auth_client.role_assignments.list_for_scope(
            scope=storage_account_id
        )
    )
    verified_principals = set()

    for assignment in all_assignments:
        principal_id = assignment.principal_id
        if principal_id in expected_principal_ids:
            verified_principals.add(principal_id)
            role_id = assignment.role_definition_id.split('/')[-1]
            role_display = _get_role_name(role_id)
            print(
                f"  ✓ Verified {role_display} for principal "
                f"{principal_id[:8]}"
            )

    missing_principals = set(expected_principal_ids) - verified_principals
    if missing_principals:
        print(
            f"WARNING: {len(missing_principals)} principal(s) missing role "
            f"assignments: "
        )
        for principal in missing_principals:
            print(f" - {principal}")


def grant_storage_permissions(cmd, storage_account_id, source_dra,
                              target_dra, replication_vault, subscription_id):
    """Grant role assignments for DRAs and vault identity to storage acct."""
    from azure.mgmt.authorization import AuthorizationManagementClient

    # Get role assignment client
    from azure.cli.core.commands.client_factory import (
        get_mgmt_service_client
    )
    auth_client = get_mgmt_service_client(
        cmd.cli_ctx, AuthorizationManagementClient
    )

    source_dra_object_id = (
        source_dra.get('properties', {})
        .get('resourceAccessIdentity', {}).get('objectId')
    )
    target_dra_object_id = (
        target_dra.get('properties', {})
        .get('resourceAccessIdentity', {}).get('objectId')
    )

    # Get vault identity from either root level or properties level
    vault_identity = (
        replication_vault.get('identity') or
        replication_vault.get('properties', {}).get('identity')
    )
    vault_identity_id = (
        vault_identity.get('principalId') if vault_identity else None
    )

    print("Granting permissions to the storage account...")
    print(f"  Source DRA Principal ID: {source_dra_object_id}")
    print(f"  Target DRA Principal ID: {target_dra_object_id}")
    print(f"  Vault Identity Principal ID: {vault_identity_id}")

    successful_assignments = []
    failed_assignments = []

    # Create role assignments for source and target DRAs
    for object_id in [source_dra_object_id, target_dra_object_id]:
        if object_id:
            for role_def_id in [
                RoleDefinitionIds.ContributorId,
                RoleDefinitionIds.StorageBlobDataContributorId
            ]:
                try:
                    assignment_msg, _ = _assign_role_to_principal(
                        auth_client, storage_account_id, subscription_id,
                        object_id, role_def_id, "DRA"
                    )
                    successful_assignments.append(assignment_msg)
                except CLIError as e:
                    role_name = _get_role_name(role_def_id)
                    error_msg = f"{object_id[:8]} - {role_name}: {str(e)}"
                    failed_assignments.append(error_msg)

    # Grant vault identity permissions if exists
    if vault_identity_id:
        for role_def_id in [RoleDefinitionIds.ContributorId,
                            RoleDefinitionIds.StorageBlobDataContributorId]:
            try:
                assignment_msg, _ = _assign_role_to_principal(
                    auth_client, storage_account_id, subscription_id,
                    vault_identity_id, role_def_id, "vault"
                )
                successful_assignments.append(assignment_msg)
            except CLIError as e:
                role_name = _get_role_name(role_def_id)
                error_msg = f"{vault_identity_id[:8]} - {role_name}: {str(e)}"
                failed_assignments.append(error_msg)

    # Report role assignment status
    print("\nRole Assignment Summary:")
    print(f"  Successful: {len(successful_assignments)}")
    if failed_assignments:
        print(f"  Failed: {len(failed_assignments)}")
        for failure in failed_assignments:
            print(f" - {failure}")

    # If there are failures, raise an error
    if failed_assignments:
        raise CLIError(
            f"Failed to create {len(failed_assignments)} role "
            f"assignment(s). "
            "The storage account may not have proper permissions."
        )

    # Add a wait after role assignments to ensure propagation
    time.sleep(120)

    # Verify role assignments were successful
    expected_principal_ids = [
        source_dra_object_id, target_dra_object_id, vault_identity_id
    ]
    _verify_role_assignments(
        auth_client, storage_account_id, expected_principal_ids
    )


def update_amh_solution_storage(cmd,
                                project_uri,
                                amh_solution,
                                storage_account_id):
    """Update AMH solution with storage account ID if needed."""
    amh_solution_uri = (
        f"{project_uri}/solutions/"
        f"Servers-Migration-ServerMigration_DataReplication"
    )

    if (amh_solution
        .get('properties', {})
        .get('details', {})
        .get('extendedDetails', {})
            .get('replicationStorageAccountId')) != storage_account_id:
        extended_details = (amh_solution
                            .get('properties', {})
                            .get('details', {})
                            .get('extendedDetails', {}))
        extended_details['replicationStorageAccountId'] = (
            storage_account_id
        )

        solution_body = {
            "properties": {
                "details": {
                    "extendedDetails": extended_details
                }
            }
        }

        create_or_update_resource(
            cmd, amh_solution_uri, APIVersion.Microsoft_Migrate.value,
            solution_body
        )

        # Wait for the AMH solution update to fully propagate
        time.sleep(60)

    return amh_solution_uri
