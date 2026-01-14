# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger
from azext_migrate.helpers._utils import (
    send_get_request,
)

logger = get_logger(__name__)


# pylint: disable=too-many-locals
def get_discovered_server(cmd,
                          project_name,
                          resource_group,
                          display_name=None,
                          source_machine_type=None,
                          subscription_id=None,
                          name=None,
                          appliance_name=None):
    from azext_migrate.helpers._utils import APIVersion
    from azext_migrate.helpers._server import (
        validate_get_discovered_server_params,
        extract_machine_name_from_id,
        build_base_uri,
        fetch_all_servers,
        filter_servers_by_display_name,
        extract_server_info,
        print_server_info)

    # Validate required parameters
    validate_get_discovered_server_params(
        project_name, resource_group, source_machine_type)

    # Extract machine name if a full resource ID was provided for --name
    if name:
        name = extract_machine_name_from_id(name)

    # Use current subscription if not provided
    if not subscription_id:
        from azure.cli.core.commands.client_factory import \
            get_subscription_id
        subscription_id = get_subscription_id(cmd.cli_ctx)

    # Build the base URI
    base_uri = build_base_uri(
        subscription_id, resource_group, project_name,
        appliance_name, name, source_machine_type)

    # Construct the full URI with appropriate API version
    # Note: Azure Migrate API does not support OData $filter for machines endpoint
    # We'll apply client-side filtering after fetching all results
    api_version = (APIVersion.Microsoft_OffAzure.value if appliance_name
                   else APIVersion.Microsoft_Migrate.value)
    request_uri = (
        f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{base_uri}?"
        f"api-version={api_version}"
    )

    try:
        # Fetch all servers
        values = fetch_all_servers(cmd, request_uri, send_get_request)

        # Apply client-side filtering for display_name
        if display_name:
            values = filter_servers_by_display_name(values, display_name)

        # Format and display the discovered servers information
        for index, server in enumerate(values, 1):
            print_server_info(extract_server_info(server, index))

    except Exception as e:
        logger.error("Error retrieving discovered servers: %s", str(e))
        raise CLIError(
            f"Failed to retrieve discovered servers: {str(e)}")


def initialize_replication_infrastructure(cmd,
                                          resource_group,
                                          project_name,
                                          source_appliance_name,
                                          target_appliance_name,
                                          cache_storage_account_id=None,
                                          subscription_id=None,
                                          pass_thru=False):
    from azure.cli.core.commands.client_factory import \
        get_subscription_id
    from azext_migrate.helpers.replication.init._execute_init import (
        execute_replication_infrastructure_setup)
    from azext_migrate.helpers.replication.init._validate import (
        validate_required_parameters,
    )

    # Validate required parameters
    validate_required_parameters(resource_group,
                                 project_name,
                                 source_appliance_name,
                                 target_appliance_name)

    try:
        # Use current subscription if not provided
        if not subscription_id:
            subscription_id = get_subscription_id(cmd.cli_ctx)
        print(f"Selected Subscription Id: '{subscription_id}'")

        # Execute the complete setup workflow
        return execute_replication_infrastructure_setup(
            cmd, subscription_id, resource_group, project_name,
            source_appliance_name, target_appliance_name,
            cache_storage_account_id, pass_thru
        )

    except Exception as e:
        logger.error(
            "Error initializing replication infrastructure: %s", str(e))
        raise CLIError(
            f"Failed to initialize replication infrastructure: {str(e)}")


# pylint: disable=too-many-locals
def new_local_server_replication(cmd,
                                 target_storage_path_id,
                                 target_resource_group_id,
                                 target_vm_name,
                                 source_appliance_name,
                                 target_appliance_name,
                                 machine_id=None,
                                 machine_index=None,
                                 project_name=None,
                                 resource_group=None,
                                 target_vm_cpu_core=None,
                                 target_virtual_switch_id=None,
                                 target_test_virtual_switch_id=None,
                                 is_dynamic_memory_enabled=None,
                                 target_vm_ram=None,
                                 disk_to_include=None,
                                 nic_to_include=None,
                                 os_disk_id=None,
                                 subscription_id=None):
    from azext_migrate.helpers._utils import SiteTypes
    from azext_migrate.helpers.replication.new._validate import (
        validate_server_parameters,
        validate_required_parameters,
        validate_ARM_id_formats,
        validate_replication_extension,
        validate_target_VM_name
    )
    from azext_migrate.helpers.replication.new._process_inputs import (
        process_site_type_hyperV,
        process_site_type_vmware,
        process_amh_solution,
        process_replication_vault,
        process_replication_policy,
        process_appliance_map,
        process_source_fabric,
        process_target_fabric
    )
    from azext_migrate.helpers.replication.new._execute_new import (
        get_ARC_resource_bridge_info,
        ensure_target_resource_group_exists,
        construct_disk_and_nic_mapping,
        create_protected_item
    )

    # Use current subscription if not provided
    if not subscription_id:
        from azure.cli.core.commands.client_factory import \
            get_subscription_id
        subscription_id = get_subscription_id(cmd.cli_ctx)
        print(f"Selected Subscription Id: '{subscription_id}'")

    rg_uri, machine_id, subscription_id = validate_server_parameters(
        cmd,
        machine_id,
        machine_index,
        project_name,
        resource_group,
        source_appliance_name,
        subscription_id)

    is_dynamic_ram_enabled, is_power_user_mode = \
        validate_required_parameters(
            machine_id,
            target_storage_path_id,
            target_resource_group_id,
            target_vm_name,
            source_appliance_name,
            target_appliance_name,
            disk_to_include,
            nic_to_include,
            target_virtual_switch_id,
            os_disk_id,
            is_dynamic_memory_enabled)

    try:
        site_type, site_name, machine_name, run_as_account_id, \
            instance_type, resource_group_name = validate_ARM_id_formats(
                machine_id,
                target_storage_path_id,
                target_resource_group_id,
                target_virtual_switch_id,
                target_test_virtual_switch_id)

        if site_type == SiteTypes.HyperVSites.value:
            run_as_account_id, machine, site_object, instance_type = \
                process_site_type_hyperV(
                    cmd,
                    rg_uri,
                    site_name,
                    machine_name,
                    subscription_id,
                    resource_group_name,
                    site_type)

        elif site_type == SiteTypes.VMwareSites.value:
            run_as_account_id, machine, site_object, instance_type = \
                process_site_type_vmware(
                    cmd,
                    rg_uri,
                    site_name,
                    machine_name,
                    subscription_id,
                    resource_group_name,
                    site_type)

        else:
            raise CLIError(
                f"Site type of '{site_type}' in -machine_id is not "
                f"supported. Only '{SiteTypes.HyperVSites.value}' and "
                f"'{SiteTypes.VMwareSites.value}' are supported.")

        if not run_as_account_id:
            raise CLIError(
                f"Unable to determine RunAsAccount for "
                f"site '{site_name}' from machine '{machine_name}'. "
                "Please verify your appliance setup and provided "
                "-machine_id.")

        amh_solution, migrate_project, machine_props = process_amh_solution(
            cmd,
            machine,
            site_object,
            project_name,
            resource_group_name,
            machine_name,
            rg_uri
        )

        replication_vault_name = process_replication_vault(
            cmd,
            amh_solution,
            resource_group_name)

        policy_name = process_replication_policy(
            cmd,
            replication_vault_name,
            instance_type,
            rg_uri
        )
        app_map = process_appliance_map(cmd, rg_uri, project_name)

        if not app_map:
            raise CLIError(
                "Server Discovery Solution missing Appliance Details. "
                "Invalid Solution.")

        source_fabric, fabric_instance_type, instance_type, \
            all_fabrics = process_source_fabric(
                cmd,
                rg_uri,
                app_map,
                source_appliance_name,
                target_appliance_name,
                amh_solution,
                resource_group_name,
                project_name
            )

        target_fabric, source_dra, target_dra = process_target_fabric(
            cmd,
            rg_uri,
            source_fabric,
            fabric_instance_type,
            all_fabrics,
            source_appliance_name,
            target_appliance_name,
            amh_solution)

        # 2. Validate Replication Extension
        replication_extension_name = validate_replication_extension(
            cmd,
            rg_uri,
            source_fabric,
            target_fabric,
            replication_vault_name
        )

        # 3. Get ARC Resource Bridge info
        custom_location_id, custom_location_region, \
            target_cluster_id = get_ARC_resource_bridge_info(
                cmd,
                target_fabric,
                migrate_project
            )

        # 4. Ensure target resource group exists
        ensure_target_resource_group_exists(
            cmd,
            target_resource_group_id,
            custom_location_region,
            project_name
        )

        # 5. Validate target VM name
        validate_target_VM_name(target_vm_name)

        # 6. Construct disk and NIC mappings
        disks, nics = construct_disk_and_nic_mapping(
            is_power_user_mode,
            disk_to_include,
            nic_to_include,
            machine_props,
            site_type,
            os_disk_id,
            target_virtual_switch_id,
            target_test_virtual_switch_id)

        # 7. Create the protected item
        create_protected_item(
            cmd,
            subscription_id,
            resource_group_name,
            replication_vault_name,
            machine_name,
            machine_props,
            target_vm_cpu_core,
            target_vm_ram,
            custom_location_id,
            custom_location_region,
            site_type,
            instance_type,
            disks,
            nics,
            target_vm_name,
            target_resource_group_id,
            target_storage_path_id,
            is_dynamic_ram_enabled,
            source_dra,
            target_dra,
            policy_name,
            replication_extension_name,
            machine_id,
            run_as_account_id,
            target_cluster_id
        )

    except Exception as e:
        logger.error("Error creating replication: %s", str(e))
        raise


def get_local_replication_job(cmd,
                              job_id=None,
                              resource_group=None,
                              project_name=None,
                              job_name=None,
                              subscription_id=None):
    from azure.cli.core.commands.client_factory import \
        get_subscription_id
    from azext_migrate.helpers.replication.job._parse import (
        parse_job_id,
        get_vault_name_from_project
    )
    from azext_migrate.helpers.replication.job._retrieve import (
        get_single_job,
        list_all_jobs
    )
    from azext_migrate.helpers.replication.job._format import (
        format_job_output,
        format_job_summary
    )

    # Use current subscription if not provided
    if not subscription_id:
        subscription_id = get_subscription_id(cmd.cli_ctx)

    # Determine the operation mode based on provided parameters
    if job_id:
        # Mode: Get job by ID
        vault_name, resource_group_name, job_name = \
            parse_job_id(job_id)
    elif resource_group and project_name:
        # Mode: Get job by name or list jobs
        vault_name = get_vault_name_from_project(
            cmd, resource_group, project_name, subscription_id)
        resource_group_name = resource_group
    else:
        raise CLIError(
            "Either --job-id or both --resource-group and "
            "--project-name must be provided.")

    # Get a specific job or list all jobs
    if job_name:
        return get_single_job(
            cmd, subscription_id, resource_group_name,
            vault_name, job_name, format_job_output)

    return list_all_jobs(
        cmd, subscription_id, resource_group_name,
        vault_name, format_job_summary)


def list_local_server_replications(cmd,
                                   resource_group=None,
                                   project_name=None,
                                   subscription_id=None):
    from azure.cli.core.commands.client_factory import \
        get_subscription_id
    from azext_migrate.helpers.replication.list._execute_list import (
        get_vault_name_from_project,
        list_protected_items
    )

    # Validate required parameters
    if not resource_group or not project_name:
        raise CLIError(
            "Both --resource-group and --project-name are required.")

    # Use current subscription if not provided
    if not subscription_id:
        subscription_id = get_subscription_id(cmd.cli_ctx)

    # Get the vault name from the project
    vault_name = get_vault_name_from_project(
        cmd, resource_group, project_name, subscription_id)

    # List all protected items
    list_protected_items(
        cmd, subscription_id, resource_group, vault_name)


def get_local_server_replication(cmd,
                                 protected_item_name=None,
                                 protected_item_id=None,
                                 resource_group=None,
                                 project_name=None,
                                 subscription_id=None):
    from azure.cli.core.commands.client_factory import \
        get_subscription_id
    from azext_migrate.helpers.replication.get._execute_get import (
        get_protected_item_by_id,
        get_protected_item_by_name
    )

    # Use current subscription if not provided
    if not subscription_id:
        subscription_id = get_subscription_id(cmd.cli_ctx)

    # Validate that either ID or name is provided
    if not protected_item_id and not protected_item_name:
        raise CLIError(
            "Either --protected-item-id or --protected-item-name must be provided.")

    # If both are provided, prefer ID
    if protected_item_id:
        return get_protected_item_by_id(cmd, protected_item_id)

    # If using name, require resource_group and project_name
    if not resource_group or not project_name:
        raise CLIError(
            "When using --protected-item-name, both --resource-group and "
            "--project-name are required.")

    return get_protected_item_by_name(
        cmd, subscription_id, resource_group, project_name, protected_item_name)


def remove_local_server_replication(cmd,
                                    target_object_id,
                                    force_remove=False,
                                    subscription_id=None):
    from azure.cli.core.commands.client_factory import \
        get_subscription_id
    from azext_migrate.helpers.replication.remove._parse import (
        parse_protected_item_id
    )
    from azext_migrate.helpers.replication.remove._validate import (
        validate_protected_item
    )
    from azext_migrate.helpers.replication.remove._execute_delete import (
        execute_removal
    )

    # Use current subscription if not provided
    if not subscription_id:
        subscription_id = get_subscription_id(cmd.cli_ctx)

    # Parse the protected item ID to extract components
    resource_group_name, vault_name, protected_item_name = \
        parse_protected_item_id(target_object_id)

    # Validate the protected item exists and can be removed
    validate_protected_item(cmd, target_object_id)

    # Execute the removal workflow
    return execute_removal(
        cmd, subscription_id, target_object_id,
        resource_group_name, vault_name,
        protected_item_name, force_remove
    )


def start_local_server_migration(cmd,
                                 protected_item_id=None,
                                 turn_off_source_server=False,
                                 subscription_id=None):
    from azure.cli.core.commands.client_factory import \
        get_subscription_id
    from azext_migrate.helpers.migration.start._parse import (
        parse_protected_item_id
    )
    from azext_migrate.helpers.migration.start._execute_migrate import (
        execute_migration
    )

    # Use current subscription if not provided
    if not subscription_id:
        subscription_id = get_subscription_id(cmd.cli_ctx)

    # Validate that either ID or name is provided
    if not protected_item_id:
        raise CLIError(
            "The --protected-item-id parameter must be provided."
        )

    # Determine the operation mode
    target_object_id = protected_item_id

    # Mode: Use provided ID
    resource_group_name, vault_name, protected_item_name = \
        parse_protected_item_id(protected_item_id)

    # Execute the migration workflow
    return execute_migration(
        cmd,
        subscription_id,
        target_object_id,
        resource_group_name,
        vault_name,
        protected_item_name,
        turn_off_source_server
    )
