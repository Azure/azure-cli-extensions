# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=possibly-used-before-assignment
from azure.cli.core.commands.client_factory import get_subscription_id
from azext_migrate.helpers._utils import (
    send_get_request,
    get_resource_by_id,
    APIVersion,
    ProvisioningState,
    validate_arm_id_format,
    IdFormats
)
import json
from knack.util import CLIError
from knack.log import get_logger
import re

logger = get_logger(__name__)


def _process_v2_dict(extended_details, app_map):
    try:
        app_map_v2 = json.loads(
            extended_details['applianceNameToSiteIdMapV2'])
        if isinstance(app_map_v2, list):
            for item in app_map_v2:
                if (isinstance(item, dict) and
                        'ApplianceName' in item and
                        'SiteId' in item):
                    # Store both lowercase and original case
                    app_map[item['ApplianceName'].lower()] = item['SiteId']
                    app_map[item['ApplianceName']] = item['SiteId']
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    return app_map


def _process_v3_dict_map(app_map_v3, app_map):
    for appliance_name_key, site_info in app_map_v3.items():
        if isinstance(site_info, dict) and 'SiteId' in site_info:
            app_map[appliance_name_key.lower()] = site_info['SiteId']
            app_map[appliance_name_key] = site_info['SiteId']
        elif isinstance(site_info, str):
            app_map[appliance_name_key.lower()] = site_info
            app_map[appliance_name_key] = site_info
    return app_map


def _process_v3_dict_list(app_map_v3, app_map):
    # V3 might also be in list format
    for item in app_map_v3:
        if isinstance(item, dict):
            # Check if it has ApplianceName/SiteId structure
            if 'ApplianceName' in item and 'SiteId' in item:
                app_map[item['ApplianceName'].lower()] = item['SiteId']
                app_map[item['ApplianceName']] = item['SiteId']
            else:
                # Or it might be a single key-value pair
                for key, value in item.items():
                    if isinstance(value, dict) and 'SiteId' in value:
                        app_map[key.lower()] = value['SiteId']
                        app_map[key] = value['SiteId']
                    elif isinstance(value, str):
                        app_map[key.lower()] = value
                        app_map[key] = value
    return app_map


def _process_v3_dict(extended_details, app_map):
    try:
        app_map_v3 = json.loads(extended_details['applianceNameToSiteIdMapV3'])
        if isinstance(app_map_v3, dict):
            app_map = _process_v3_dict_map(app_map_v3, app_map)
        elif isinstance(app_map_v3, list):
            app_map = _process_v3_dict_list(app_map_v3, app_map)
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    return app_map


def validate_server_parameters(
        cmd,
        machine_id,
        machine_index,
        project_name,
        resource_group_name,
        source_appliance_name,
        subscription_id):
    # Validate that either machine_id or machine_index is provided
    if not machine_id and not machine_index:
        raise CLIError(
            "Either machine_id or machine_index must be provided.")
    if machine_id and machine_index:
        raise CLIError(
            "Only one of machine_id or machine_index should be "
            "provided, not both.")

    if not subscription_id:
        subscription_id = get_subscription_id(cmd.cli_ctx)

    # Initialize rg_uri - will be set based on machine_id or resource_group_name
    rg_uri = None

    if machine_index:
        if not project_name:
            raise CLIError(
                "project_name is required when using machine_index.")
        if not resource_group_name:
            raise CLIError(
                "resource_group_name is required when using "
                "machine_index.")

        if not isinstance(machine_index, int) or machine_index < 1:
            raise CLIError(
                "machine_index must be a positive integer "
                "(1-based index).")

        rg_uri = (
            f"/subscriptions/{subscription_id}/"
            f"resourceGroups/{resource_group_name}")
        discovery_solution_name = "Servers-Discovery-ServerDiscovery"
        discovery_solution_uri = (
            f"{rg_uri}/providers/Microsoft.Migrate/migrateprojects"
            f"/{project_name}/solutions/{discovery_solution_name}"
        )
        discovery_solution = get_resource_by_id(
            cmd, discovery_solution_uri, APIVersion.Microsoft_Migrate.value)

        if not discovery_solution:
            raise CLIError(
                f"Server Discovery Solution '{discovery_solution_name}' "
                f"not in project '{project_name}'.")

        # Get appliance mapping to determine site type
        app_map = {}
        extended_details = (
            discovery_solution.get('properties', {})
            .get('details', {})
            .get('extendedDetails', {}))

        # Process applianceNameToSiteIdMapV2 and V3
        if 'applianceNameToSiteIdMapV2' in extended_details:
            app_map = _process_v2_dict(extended_details, app_map)

        if 'applianceNameToSiteIdMapV3' in extended_details:
            app_map = _process_v3_dict(extended_details, app_map)

        # Get source site ID - try both original and lowercase
        source_site_id = (
            app_map.get(source_appliance_name) or
            app_map.get(source_appliance_name.lower()))
        if not source_site_id:
            raise CLIError(
                f"Source appliance '{source_appliance_name}' "
                f"not in discovery solution.")

        # Determine site type from source site ID
        hyperv_site_pattern = "/Microsoft.OffAzure/HyperVSites/"
        vmware_site_pattern = "/Microsoft.OffAzure/VMwareSites/"

        if hyperv_site_pattern in source_site_id:
            site_name = source_site_id.split('/')[-1]
            machines_uri = (
                f"{rg_uri}/providers/Microsoft.OffAzure/"
                f"HyperVSites/{site_name}/machines")
        elif vmware_site_pattern in source_site_id:
            site_name = source_site_id.split('/')[-1]
            machines_uri = (
                f"{rg_uri}/providers/Microsoft.OffAzure/"
                f"VMwareSites/{site_name}/machines")
        else:
            raise CLIError(
                f"Unable to determine site type for source appliance "
                f"'{source_appliance_name}'.")

        # Get all machines from the site
        request_uri = (
            f"{cmd.cli_ctx.cloud.endpoints.resource_manager}"
            f"{machines_uri}?api-version={APIVersion.Microsoft_OffAzure.value}"
        )

        response = send_get_request(cmd, request_uri)
        machines_data = response.json()
        machines = machines_data.get('value', [])

        # Fetch all pages if there are more
        while machines_data.get('nextLink'):
            response = send_get_request(cmd, machines_data.get('nextLink'))
            machines_data = response.json()
            machines.extend(machines_data.get('value', []))

        # Check if the index is valid
        if machine_index > len(machines):
            raise CLIError(
                f"Invalid machine_index {machine_index}. "
                f"Only {len(machines)} machines found in site '{site_name}'.")

        # Get the machine at the specified index (convert 1-based to 0-based)
        selected_machine = machines[machine_index - 1]
        machine_id = selected_machine.get('id')
    else:
        # machine_id was provided directly
        # Check if it's in Microsoft.Migrate format and needs to be resolved
        if "/Microsoft.Migrate/MigrateProjects/" in machine_id or "/Microsoft.Migrate/migrateprojects/" in machine_id:
            # This is a Migrate Project machine ID, need to resolve to OffAzure machine ID
            migrate_machine = get_resource_by_id(
                cmd, machine_id, APIVersion.Microsoft_Migrate.value)

            if not migrate_machine:
                raise CLIError(
                    f"Machine not found with ID '{machine_id}'.")

            # Get the actual OffAzure machine ID from properties
            machine_props = migrate_machine.get('properties', {})
            discovery_data = machine_props.get('discoveryData', [])

            # Find the OS discovery data entry which contains the actual machine reference
            offazure_machine_id = None
            for data in discovery_data:
                if data.get('osType'):
                    # The extended data should contain the actual machine ARM ID
                    extended_data = data.get('extendedInfo', {})
                    # Try different possible field names for the OffAzure machine ID
                    offazure_machine_id = (
                        extended_data.get('sdsArmId') or
                        extended_data.get('machineArmId') or
                        extended_data.get('machineId')
                    )
                    if offazure_machine_id:
                        break

            # If not found in discoveryData, check other properties
            if not offazure_machine_id:
                offazure_machine_id = machine_props.get('machineId') or machine_props.get('machineArmId')

            if not offazure_machine_id:
                raise CLIError(
                    f"Could not resolve the OffAzure machine ID from Migrate machine '{machine_id}'. "
                    "Please provide the machine ID in the format "
                    "'/subscriptions/.../Microsoft.OffAzure/{{HyperVSites|VMwareSites}}/.../machines/...'")

            machine_id = offazure_machine_id

        # Extract resource_group_name from machine_id if not provided
        if not resource_group_name:
            machine_id_parts = machine_id.split("/")
            if len(machine_id_parts) >= 5:
                resource_group_name = machine_id_parts[4]
            else:
                raise CLIError(f"Invalid machine ARM ID format: '{machine_id}'")

        rg_uri = (
            f"/subscriptions/{subscription_id}/"
            f"resourceGroups/{resource_group_name}")

    return rg_uri, machine_id


def validate_required_parameters(machine_id,
                                 target_storage_path_id,
                                 target_resource_group_id,
                                 target_vm_name,
                                 source_appliance_name,
                                 target_appliance_name,
                                 disk_to_include,
                                 nic_to_include,
                                 target_virtual_switch_id,
                                 os_disk_id,
                                 is_dynamic_memory_enabled):
    # Validate required parameters
    if not machine_id:
        raise CLIError("machine_id could not be determined.")
    if not target_storage_path_id:
        raise CLIError("target_storage_path_id is required.")
    if not target_resource_group_id:
        raise CLIError("target_resource_group_id is required.")
    if not target_vm_name:
        raise CLIError("target_vm_name is required.")
    if not source_appliance_name:
        raise CLIError("source_appliance_name is required.")
    if not target_appliance_name:
        raise CLIError("target_appliance_name is required.")

    # Validate parameter set requirements
    is_power_user_mode = (disk_to_include is not None or
                          nic_to_include is not None)
    is_default_user_mode = (target_virtual_switch_id is not None or
                            os_disk_id is not None)

    if is_power_user_mode and is_default_user_mode:
        raise CLIError(
            "Cannot mix default user mode parameters "
            "(target_virtual_switch_id, os_disk_id) with power user mode "
            "parameters (disk_to_include, nic_to_include).")

    if is_power_user_mode:
        # Power user mode validation
        if not disk_to_include:
            raise CLIError(
                "disk_to_include is required when using power user mode.")
        if not nic_to_include:
            raise CLIError(
                "nic_to_include is required when using power user mode.")
    else:
        # Default user mode validation
        if not target_virtual_switch_id:
            raise CLIError(
                "target_virtual_switch_id is required when using "
                "default user mode.")
        if not os_disk_id:
            raise CLIError(
                "os_disk_id is required when using default user mode.")

    is_dynamic_ram_enabled = None
    if is_dynamic_memory_enabled:
        if is_dynamic_memory_enabled not in ['true', 'false']:
            raise CLIError(
                "is_dynamic_memory_enabled must be either "
                "'true' or 'false'.")
        is_dynamic_ram_enabled = is_dynamic_memory_enabled == 'true'
    return is_dynamic_ram_enabled, is_power_user_mode


def validate_ARM_id_formats(machine_id,
                            target_storage_path_id,
                            target_resource_group_id,
                            target_virtual_switch_id,
                            target_test_virtual_switch_id):
    # Validate ARM ID formats
    if not validate_arm_id_format(
            machine_id,
            IdFormats.MachineArmIdTemplate):
        raise CLIError(
            f"Invalid -machine_id '{machine_id}'. "
            f"A valid machine ARM ID should follow the format "
            f"'{IdFormats.MachineArmIdTemplate}'.")

    if not validate_arm_id_format(
            target_storage_path_id,
            IdFormats.StoragePathArmIdTemplate):
        raise CLIError(
            f"Invalid -target_storage_path_id "
            f"'{target_storage_path_id}'. "
            f"A valid storage path ARM ID should follow the format "
            f"'{IdFormats.StoragePathArmIdTemplate}'.")

    if not validate_arm_id_format(
            target_resource_group_id,
            IdFormats.ResourceGroupArmIdTemplate):
        raise CLIError(
            f"Invalid -target_resource_group_id "
            f"'{target_resource_group_id}'. "
            f"A valid resource group ARM ID should follow the format "
            f"'{IdFormats.ResourceGroupArmIdTemplate}'.")

    if (target_virtual_switch_id and
            not validate_arm_id_format(
                target_virtual_switch_id,
                IdFormats.LogicalNetworkArmIdTemplate)):
        raise CLIError(
            f"Invalid -target_virtual_switch_id "
            f"'{target_virtual_switch_id}'. "
            f"A valid logical network ARM ID should follow the format "
            f"'{IdFormats.LogicalNetworkArmIdTemplate}'.")

    if (target_test_virtual_switch_id and
            not validate_arm_id_format(
                target_test_virtual_switch_id,
                IdFormats.LogicalNetworkArmIdTemplate)):
        raise CLIError(
            f"Invalid -target_test_virtual_switch_id "
            f"'{target_test_virtual_switch_id}'. "
            f"A valid logical network ARM ID should follow the format "
            f"'{IdFormats.LogicalNetworkArmIdTemplate}'.")

    machine_id_parts = machine_id.split("/")
    if len(machine_id_parts) < 11:
        raise CLIError(f"Invalid machine ARM ID format: '{machine_id}'")

    resource_group_name = machine_id_parts[4]
    site_type = machine_id_parts[7]
    site_name = machine_id_parts[8]
    machine_name = machine_id_parts[10]

    run_as_account_id = None
    instance_type = None
    return site_type, site_name, machine_name, run_as_account_id, instance_type, resource_group_name


def validate_replication_extension(cmd,
                                   rg_uri,
                                   source_fabric,
                                   target_fabric,
                                   replication_vault_name):
    source_fabric_id = source_fabric['id']
    target_fabric_id = target_fabric['id']
    source_fabric_short_name = source_fabric_id.split('/')[-1]
    target_fabric_short_name = target_fabric_id.split('/')[-1]
    replication_extension_name = (
        f"{source_fabric_short_name}-{target_fabric_short_name}-"
        f"MigReplicationExtn")
    extension_uri = (
        f"{rg_uri}/providers/Microsoft.DataReplication"
        f"/replicationVaults/{replication_vault_name}"
        f"/replicationExtensions/{replication_extension_name}"
    )
    replication_extension = get_resource_by_id(
        cmd, extension_uri, APIVersion.Microsoft_DataReplication.value)

    if not replication_extension:
        raise CLIError(
            f"The replication extension '{replication_extension_name}' "
            f"not found. Run 'az migrate local replication init' first.")

    extension_state = (replication_extension.get('properties', {})
                       .get('provisioningState'))

    if extension_state != ProvisioningState.Succeeded.value:
        raise CLIError(
            f"The replication extension '{replication_extension_name}' "
            f"is not ready. State: '{extension_state}'")
    return replication_extension_name


def validate_target_VM_name(target_vm_name):
    if len(target_vm_name) == 0 or len(target_vm_name) > 64:
        raise CLIError(
            "The target virtual machine name must be between 1 and 64 "
            "characters long.")

    vm_name_pattern = r"^[^_\W][a-zA-Z0-9\-]{0,63}(?<![-._])$"

    if not re.match(vm_name_pattern, target_vm_name):
        raise CLIError(
            "The target VM name must begin with a letter or number, "
            "contain only letters, numbers, or hyphens, and not end with "
            "'.' or '-'.")
