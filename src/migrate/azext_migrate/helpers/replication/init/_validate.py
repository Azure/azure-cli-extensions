# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
from knack.util import CLIError
from knack.log import get_logger
from azext_migrate.helpers._utils import (
    get_resource_by_id,
    create_or_update_resource,
    APIVersion,
    ProvisioningState
)
import json


def validate_required_parameters(resource_group_name,
                                 project_name,
                                 source_appliance_name,
                                 target_appliance_name):
    # Validate required parameters
    if not resource_group_name:
        raise CLIError("resource_group_name is required.")
    if not project_name:
        raise CLIError("project_name is required.")
    if not source_appliance_name:
        raise CLIError("source_appliance_name is required.")
    if not target_appliance_name:
        raise CLIError("target_appliance_name is required.")


def get_and_validate_resource_group(cmd, subscription_id,
                                    resource_group_name):
    """Get and validate that the resource group exists."""
    rg_uri = (f"/subscriptions/{subscription_id}/"
              f"resourceGroups/{resource_group_name}")
    resource_group = get_resource_by_id(
        cmd, rg_uri, APIVersion.Microsoft_Resources.value)
    if not resource_group:
        raise CLIError(
            f"Resource group '{resource_group_name}' does not exist "
            f"in the subscription.")
    print(f"Selected Resource Group: '{resource_group_name}'")
    return rg_uri


def get_migrate_project(cmd, project_uri, project_name):
    """Get and validate migrate project."""
    migrate_project = get_resource_by_id(
        cmd, project_uri, APIVersion.Microsoft_Migrate.value)
    if not migrate_project:
        raise CLIError(f"Migrate project '{project_name}' not found.")

    if (migrate_project.get('properties', {}).get('provisioningState') !=
            ProvisioningState.Succeeded.value):
        raise CLIError(
            f"Migrate project '{project_name}' is not in a valid state.")

    return migrate_project


def get_data_replication_solution(cmd, project_uri):
    """Get Data Replication Service Solution."""
    amh_solution_name = (
        "Servers-Migration-ServerMigration_DataReplication")
    amh_solution_uri = f"{project_uri}/solutions/{amh_solution_name}"
    amh_solution = get_resource_by_id(
        cmd, amh_solution_uri, APIVersion.Microsoft_Migrate.value)
    if not amh_solution:
        raise CLIError(
            f"No Data Replication Service Solution "
            f"'{amh_solution_name}' found.")
    return amh_solution


def get_discovery_solution(cmd, project_uri):
    """Get Discovery Solution."""
    discovery_solution_name = "Servers-Discovery-ServerDiscovery"
    discovery_solution_uri = (
        f"{project_uri}/solutions/{discovery_solution_name}")
    discovery_solution = get_resource_by_id(
        cmd, discovery_solution_uri, APIVersion.Microsoft_Migrate.value)
    if not discovery_solution:
        raise CLIError(
            f"Server Discovery Solution '{discovery_solution_name}' "
            f"not found.")
    return discovery_solution


def get_and_setup_replication_vault(cmd, amh_solution, rg_uri):
    """Get and setup replication vault with managed identity."""
    # Validate Replication Vault
    vault_id = (amh_solution.get('properties', {})
                .get('details', {})
                .get('extendedDetails', {})
                .get('vaultId'))
    if not vault_id:
        raise CLIError(
            "No Replication Vault found. Please verify your "
            "Azure Migrate project setup.")

    replication_vault_name = vault_id.split("/")[8]
    vault_uri = (
        f"{rg_uri}/providers/Microsoft.DataReplication/"
        f"replicationVaults/{replication_vault_name}")
    replication_vault = get_resource_by_id(
        cmd, vault_uri, APIVersion.Microsoft_DataReplication.value)
    if not replication_vault:
        raise CLIError(
            f"No Replication Vault '{replication_vault_name}' found.")

    # Check if vault has managed identity, if not, enable it
    vault_identity = (
        replication_vault.get('identity') or
        replication_vault.get('properties', {}).get('identity')
    )
    if not vault_identity or not vault_identity.get('principalId'):
        print(
            f"Replication vault '{replication_vault_name}' does not "
            f"have a managed identity. "
            "Enabling system-assigned identity..."
        )

        # Update vault to enable system-assigned managed identity
        vault_update_body = {
            "identity": {
                "type": "SystemAssigned"
            }
        }

        replication_vault = create_or_update_resource(
            cmd, vault_uri, APIVersion.Microsoft_DataReplication.value,
            vault_update_body
        )

        # Wait for identity to be created
        time.sleep(30)

        # Refresh vault to get the identity
        replication_vault = get_resource_by_id(
            cmd, vault_uri, APIVersion.Microsoft_DataReplication.value)
        vault_identity = (
            replication_vault.get('identity') or
            replication_vault.get('properties', {}).get('identity')
        )

        if not vault_identity or not vault_identity.get('principalId'):
            raise CLIError(
                f"Failed to enable managed identity for replication "
                f"vault '{replication_vault_name}'")

        print(
            f"✓ Enabled system-assigned managed identity. "
            f"Principal ID: {vault_identity.get('principalId')}"
        )
    else:
        print(
            f"✓ Replication vault has managed identity. "
            f"Principal ID: {vault_identity.get('principalId')}")

    return replication_vault, replication_vault_name


def _store_appliance_site_mapping(app_map, appliance_name, site_id):
    """Store appliance name to site ID mapping in both lowercase and
    original case."""
    app_map[appliance_name.lower()] = site_id
    app_map[appliance_name] = site_id


def _process_v3_dict_map(app_map, app_map_v3):
    """Process V3 appliance map in dict format."""
    for appliance_name_key, site_info in app_map_v3.items():
        if isinstance(site_info, dict) and 'SiteId' in site_info:
            _store_appliance_site_mapping(
                app_map, appliance_name_key, site_info['SiteId'])
        elif isinstance(site_info, str):
            _store_appliance_site_mapping(
                app_map, appliance_name_key, site_info)


def _process_v3_list_item(app_map, item):
    """Process a single item from V3 appliance list."""
    if not isinstance(item, dict):
        return

    # Check if it has ApplianceName/SiteId structure
    if 'ApplianceName' in item and 'SiteId' in item:
        _store_appliance_site_mapping(
            app_map, item['ApplianceName'], item['SiteId'])
        return

    # Or it might be a single key-value pair
    for key, value in item.items():
        if isinstance(value, dict) and 'SiteId' in value:
            _store_appliance_site_mapping(
                app_map, key, value['SiteId'])
        elif isinstance(value, str):
            _store_appliance_site_mapping(app_map, key, value)


def _process_v3_appliance_map(app_map, app_map_v3):
    """Process V3 appliance map data structure."""
    if isinstance(app_map_v3, dict):
        _process_v3_dict_map(app_map, app_map_v3)
    elif isinstance(app_map_v3, list):
        for item in app_map_v3:
            _process_v3_list_item(app_map, item)


def parse_appliance_mappings(discovery_solution):
    """Parse appliance name to site ID mappings from discovery solution."""
    app_map = {}
    extended_details = (discovery_solution.get('properties', {})
                        .get('details', {})
                        .get('extendedDetails', {}))

    # Process applianceNameToSiteIdMapV2
    if 'applianceNameToSiteIdMapV2' in extended_details:
        try:
            app_map_v2 = json.loads(
                extended_details['applianceNameToSiteIdMapV2'])
            if isinstance(app_map_v2, list):
                for item in app_map_v2:
                    if (isinstance(item, dict) and
                            'ApplianceName' in item and
                            'SiteId' in item):
                        # Store both lowercase and original case
                        app_map[item['ApplianceName'].lower()] = (
                            item['SiteId'])
                        app_map[item['ApplianceName']] = item['SiteId']
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            get_logger(__name__).warning(
                "Failed to parse applianceNameToSiteIdMapV2: %s", str(e))

    # Process applianceNameToSiteIdMapV3
    if 'applianceNameToSiteIdMapV3' in extended_details:
        try:
            app_map_v3 = json.loads(
                extended_details['applianceNameToSiteIdMapV3'])
            _process_v3_appliance_map(app_map, app_map_v3)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            get_logger(__name__).warning(
                "Failed to parse applianceNameToSiteIdMapV3: %s", str(e))

    if not app_map:
        raise CLIError(
            "Server Discovery Solution missing Appliance Details. "
            "Invalid Solution.")

    return app_map


def validate_and_get_site_ids(app_map, source_appliance_name,
                              target_appliance_name):
    """Validate appliance names and get their site IDs."""
    # Validate SourceApplianceName & TargetApplianceName - try both
    # original and lowercase
    source_site_id = (app_map.get(source_appliance_name) or
                      app_map.get(source_appliance_name.lower()))
    target_site_id = (app_map.get(target_appliance_name) or
                      app_map.get(target_appliance_name.lower()))

    if not source_site_id:
        # Provide helpful error message with available appliances
        # (filter out duplicates)
        available_appliances = list(set(k for k in app_map
                                        if k not in app_map or
                                        not k.islower()))
        if not available_appliances:
            # If all keys are lowercase, show them
            available_appliances = list(set(app_map.keys()))
        raise CLIError(
            f"Source appliance '{source_appliance_name}' not in "
            f"discovery solution. "
            f"Available appliances: {','.join(available_appliances)}"
        )
    if not target_site_id:
        # Provide helpful error message with available appliances
        # (filter out duplicates)
        available_appliances = list(set(k for k in app_map
                                        if k not in app_map or
                                        not k.islower()))
        if not available_appliances:
            # If all keys are lowercase, show them
            available_appliances = list(set(app_map.keys()))
        raise CLIError(
            f"Target appliance '{target_appliance_name}' not in "
            f"discovery solution. "
            f"Available appliances: {','.join(available_appliances)}"
        )

    return source_site_id, target_site_id
