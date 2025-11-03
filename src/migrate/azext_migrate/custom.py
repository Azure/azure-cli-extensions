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


def get_discovered_server(cmd,
                          project_name,
                          resource_group_name,
                          display_name=None,
                          source_machine_type=None,
                          subscription_id=None,
                          name=None,
                          appliance_name=None):
    """
    Retrieve discovered servers from the Azure Migrate project.

    Args:
        cmd: The CLI command context
        project_name (str): Specifies the migrate project name (required)
        resource_group_name (str): Specifies the resource group name
            (required)
        display_name (str, optional): Specifies the source machine
            display name
        source_machine_type (str, optional): Specifies the source machine
            type (VMware, HyperV)
        subscription_id (str, optional): Specifies the subscription id
        name (str, optional): Specifies the source machine name
            (internal name)
        appliance_name (str, optional): Specifies the appliance name
            (maps to site)

    Returns:
        dict: The discovered server data from the API response

    Raises:
        CLIError: If required parameters are missing or the API request
            fails
    """
    from azext_migrate.helpers._utils import APIVersion
    from azext_migrate.helpers._server import (
        validate_get_discovered_server_params,
        build_base_uri,
        fetch_all_servers,
        filter_servers_by_display_name,
        extract_server_info,
        print_server_info)

    # Validate required parameters
    validate_get_discovered_server_params(
        project_name, resource_group_name, source_machine_type)

    # Use current subscription if not provided
    if not subscription_id:
        from azure.cli.core.commands.client_factory import \
            get_subscription_id
        subscription_id = get_subscription_id(cmd.cli_ctx)

    # Build the base URI
    base_uri = build_base_uri(
        subscription_id, resource_group_name, project_name,
        appliance_name, name, source_machine_type)

    # Use the correct API version
    api_version = (APIVersion.Microsoft_OffAzure.value if appliance_name
                   else APIVersion.Microsoft_Migrate.value)

    # Prepare query parameters
    query_params = [f"api-version={api_version}"]
    if not appliance_name and display_name:
        query_params.append(f"$filter=displayName eq '{display_name}'")

    # Construct the full URI
    request_uri = (
        f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{base_uri}?"
        f"{'&'.join(query_params)}"
    )

    try:
        # Fetch all servers
        values = fetch_all_servers(cmd, request_uri, send_get_request)

        # Apply client-side filtering for display_name when using site
        # endpoints
        if appliance_name and display_name:
            values = filter_servers_by_display_name(values, display_name)

        # Format and display the discovered servers information
        for index, server in enumerate(values, 1):
            server_info = extract_server_info(server, index)
            print_server_info(server_info)

    except Exception as e:
        logger.error("Error retrieving discovered servers: %s", str(e))
        raise CLIError(
            f"Failed to retrieve discovered servers: {str(e)}")


def initialize_replication_infrastructure(cmd,
                                          resource_group_name,
                                          project_name,
                                          source_appliance_name,
                                          target_appliance_name,
                                          cache_storage_account_id=None,
                                          subscription_id=None,
                                          pass_thru=False):
    """
    Initialize Azure Migrate local replication infrastructure.

    This function is based on a preview API version and may experience
    breaking changes in future releases.

    Args:
        cmd: The CLI command context
        resource_group_name (str): Specifies the Resource Group of the
            Azure Migrate Project (required)
        project_name (str): Specifies the name of the Azure Migrate
            project to be used for server migration (required)
        source_appliance_name (str): Specifies the source appliance name
            for the AzLocal scenario (required)
        target_appliance_name (str): Specifies the target appliance name
            for the AzLocal scenario (required)
        cache_storage_account_id (str, optional): Specifies the Storage
            Account ARM Id to be used for private endpoint scenario
        subscription_id (str, optional): Azure Subscription ID. Uses
            current subscription if not provided
        pass_thru (bool, optional): Returns True when the command
            succeeds

    Returns:
        bool: True if the operation succeeds (when pass_thru is True),
            otherwise None

    Raises:
        CLIError: If required parameters are missing or the API request
            fails
    """
    from azure.cli.core.commands.client_factory import \
        get_subscription_id
    from azext_migrate.helpers.replication.init._execute_init import (
        execute_replication_infrastructure_setup)
    from azext_migrate.helpers.replication.init._validate import (
        validate_required_parameters,
    )

    # Validate required parameters
    validate_required_parameters(resource_group_name,
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
            cmd, subscription_id, resource_group_name, project_name,
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
                                 resource_group_name=None,
                                 target_vm_cpu_core=None,
                                 target_virtual_switch_id=None,
                                 target_test_virtual_switch_id=None,
                                 is_dynamic_memory_enabled=None,
                                 target_vm_ram=None,
                                 disk_to_include=None,
                                 nic_to_include=None,
                                 os_disk_id=None,
                                 subscription_id=None):
    """
    Create a new replication for an Azure Local server.

    This cmdlet is based on a preview API version and may experience
    breaking changes in future releases.

    Args:
        cmd: The CLI command context
        target_storage_path_id (str): Specifies the storage path ARM ID
            where the VMs will be stored (required)
        target_resource_group_id (str): Specifies the target resource
            group ARM ID where the migrated VM resources will reside
            (required)
        target_vm_name (str): Specifies the name of the VM to be created
            (required)
        source_appliance_name (str): Specifies the source appliance name
            for the AzLocal scenario (required)
        target_appliance_name (str): Specifies the target appliance name
            for the AzLocal scenario (required)
        machine_id (str, optional): Specifies the machine ARM ID of the
            discovered server to be migrated (required if machine_index
            not provided)
        machine_index (int, optional): Specifies the index of the
            discovered server from the list (1-based, required if
            machine_id not provided)
        project_name (str, optional): Specifies the migrate project name
            (required when using machine_index)
        resource_group_name (str, optional): Specifies the resource group
            name (required when using machine_index)
        target_vm_cpu_core (int, optional): Specifies the number of CPU
            cores
        target_virtual_switch_id (str, optional): Specifies the logical
            network ARM ID that the VMs will use (required for default
            user mode)
        target_test_virtual_switch_id (str, optional): Specifies the test
            logical network ARM ID that the VMs will use
        is_dynamic_memory_enabled (str, optional): Specifies if RAM is
            dynamic or not. Valid values: 'true', 'false'
        target_vm_ram (int, optional): Specifies the target RAM size in
            MB
        disk_to_include (list, optional): Specifies the disks on the
            source server to be included for replication (power user
            mode)
        nic_to_include (list, optional): Specifies the NICs on the source
            server to be included for replication (power user mode)
        os_disk_id (str, optional): Specifies the operating system disk
            for the source server to be migrated (required for default
            user mode)
        subscription_id (str, optional): Azure Subscription ID. Uses
            current subscription if not provided

    Returns:
        dict: The job model from the API response

    Raises:
        CLIError: If required parameters are missing or validation fails
    """
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
        construct_disk_and_nic_mapping,
        create_protected_item
    )

    rg_uri, machine_id = validate_server_parameters(
        cmd,
        machine_id,
        machine_index,
        project_name,
        resource_group_name,
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
                target_fabric,
                migrate_project
            )

        # 4. Validate target VM name
        validate_target_VM_name(target_vm_name)

        # 5. Construct disk and NIC mappings
        disks, nics = construct_disk_and_nic_mapping(
            is_power_user_mode,
            disk_to_include,
            nic_to_include,
            machine_props,
            site_type,
            os_disk_id,
            target_virtual_switch_id,
            target_test_virtual_switch_id)

        # 6. Create the protected item
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


def _format_job_output(job_details):
    """
    Format job details into a clean, user-friendly output.
    
    Args:
        job_details (dict): Raw job details from the API
        
    Returns:
        dict: Formatted job information
    """
    props = job_details.get('properties', {})
    
    # Extract key information
    formatted = {
        'jobName': job_details.get('name'),
        'displayName': props.get('displayName'),
        'state': props.get('state'),
        'vmName': props.get('objectInternalName'),
        'startTime': props.get('startTime'),
        'endTime': props.get('endTime'),
        'duration': _calculate_duration(props.get('startTime'), props.get('endTime'))
    }
    
    # Add error information if present
    errors = props.get('errors', [])
    if errors:
        formatted['errors'] = [
            {
                'message': err.get('message'),
                'code': err.get('code'),
                'recommendation': err.get('recommendation')
            }
            for err in errors
        ]
    
    # Add task progress
    tasks = props.get('tasks', [])
    if tasks:
        formatted['tasks'] = [
            {
                'name': task.get('taskName'),
                'state': task.get('state'),
                'duration': _calculate_duration(task.get('startTime'), task.get('endTime'))
            }
            for task in tasks
        ]
    
    return formatted


def _calculate_duration(start_time, end_time):
    """Calculate duration between two timestamps."""
    if not start_time:
        return None
    
    from datetime import datetime
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if end_time:
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration = end - start
            total_seconds = int(duration.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            hours, minutes = divmod(minutes, 60)
            
            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        else:
            # Job still running
            now = datetime.utcnow()
            duration = now - start
            total_seconds = int(duration.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            hours, minutes = divmod(minutes, 60)
            
            if hours > 0:
                return f"{hours}h {minutes}m (in progress)"
            elif minutes > 0:
                return f"{minutes}m {seconds}s (in progress)"
            else:
                return f"{seconds}s (in progress)"
    except Exception:
        return None


def _format_job_summary(job_details):
    """
    Format job details into a summary for list output.
    
    Args:
        job_details (dict): Raw job details from the API
        
    Returns:
        dict: Formatted job summary
    """
    props = job_details.get('properties', {})
    errors = props.get('errors') or []
    
    return {
        'jobName': job_details.get('name'),
        'displayName': props.get('displayName'),
        'state': props.get('state'),
        'vmName': props.get('objectInternalName'),
        'startTime': props.get('startTime'),
        'endTime': props.get('endTime'),
        'duration': _calculate_duration(props.get('startTime'), props.get('endTime')),
        'hasErrors': len(errors) > 0
    }


def get_local_replication_job(cmd,
                              job_id=None,
                              resource_group_name=None,
                              project_name=None,
                              job_name=None,
                              subscription_id=None):
    """
    Retrieve the status of an Azure Migrate job.

    This cmdlet is based on a preview API version and may experience
    breaking changes in future releases.

    Args:
        cmd: The CLI command context
        job_id (str, optional): Specifies the job ARM ID for which
            the details need to be retrieved
        resource_group_name (str, optional): The name of the resource
            group where the recovery services vault is present
        project_name (str, optional): The name of the migrate project
        job_name (str, optional): Job identifier/name
        subscription_id (str, optional): Azure Subscription ID. Uses
            current subscription if not provided

    Returns:
        dict or list: Job details (single job or list of jobs)

    Raises:
        CLIError: If required parameters are missing or the job is not found
    """
    from azure.cli.core.commands.client_factory import \
        get_subscription_id
    from azext_migrate.helpers._utils import (
        get_resource_by_id,
        send_get_request,
        APIVersion
    )

    # Use current subscription if not provided
    if not subscription_id:
        subscription_id = get_subscription_id(cmd.cli_ctx)

    # Determine the operation mode based on provided parameters
    if job_id:
        # Mode: Get job by ID
        vault_name, resource_group_name, job_name = \
            _parse_job_id(job_id)
    elif resource_group_name and project_name:
        # Mode: Get job by name or list jobs
        vault_name = _get_vault_name_from_project(
            cmd, resource_group_name, project_name, subscription_id)
    else:
        raise CLIError(
            "Either --job-id or both --resource-group-name and "
            "--project-name must be provided.")

    # Build the job URI
    if job_name:
        # Get a specific job
        job_uri = (
            f"/subscriptions/{subscription_id}/"
            f"resourceGroups/{resource_group_name}/"
            f"providers/Microsoft.DataReplication/"
            f"replicationVaults/{vault_name}/"
            f"jobs/{job_name}"
        )

        logger.info(
            "Retrieving job '%s' from vault '%s'",
            job_name, vault_name)

        try:
            job_details = get_resource_by_id(
                cmd,
                job_uri,
                APIVersion.Microsoft_DataReplication.value
            )

            if not job_details:
                raise CLIError(
                    f"Job '{job_name}' not found in vault '{vault_name}'.")

            return _format_job_output(job_details)

        except CLIError:
            raise
        except Exception as e:
            logger.error(
                "Error retrieving job '%s': %s", job_name, str(e))
            raise CLIError(f"Failed to retrieve job: {str(e)}")
    else:
        # List all jobs in the vault
        if not vault_name:
            raise CLIError("Unable to determine vault name. Please check your project configuration.")
            
        jobs_uri = (
            f"/subscriptions/{subscription_id}/"
            f"resourceGroups/{resource_group_name}/"
            f"providers/Microsoft.DataReplication/"
            f"replicationVaults/{vault_name}/"
            f"jobs?api-version={APIVersion.Microsoft_DataReplication.value}"
        )

        request_uri = (
            f"{cmd.cli_ctx.cloud.endpoints.resource_manager}{jobs_uri}")

        logger.info(
            "Listing jobs from vault '%s'", vault_name)

        try:
            response = send_get_request(cmd, request_uri)
            
            if not response:
                logger.warning("Empty response received when listing jobs")
                return []
            
            response_data = response.json() if hasattr(response, 'json') else {}
            
            if not response_data:
                logger.warning("No data in response when listing jobs")
                return []

            jobs = response_data.get('value', [])
            
            if not jobs:
                logger.info("No jobs found in vault '%s'", vault_name)
                return []

            # Handle pagination if nextLink is present
            while response_data and response_data.get('nextLink'):
                next_link = response_data['nextLink']
                response = send_get_request(cmd, next_link)
                response_data = response.json() if (response and hasattr(response, 'json')) else {}
                if response_data and response_data.get('value'):
                    jobs.extend(response_data['value'])

            logger.info("Retrieved %d jobs from vault '%s'", len(jobs), vault_name)
            
            # Format the jobs for cleaner output
            formatted_jobs = []
            for job in jobs:
                try:
                    formatted_jobs.append(_format_job_summary(job))
                except Exception as format_error:
                    logger.warning("Error formatting job: %s", str(format_error))
                    # Skip jobs that fail to format
                    continue
            
            return formatted_jobs

        except Exception as e:
            logger.error("Error listing jobs: %s", str(e))
            raise CLIError(f"Failed to list jobs: {str(e)}")


def _parse_job_id(job_id):
    """
    Parse a job ARM ID to extract vault name, resource group, and job name.

    Args:
        job_id (str): The job ARM ID

    Returns:
        tuple: (vault_name, resource_group_name, job_name)

    Raises:
        CLIError: If the job ID format is invalid
    """
    try:
        job_id_parts = job_id.split("/")
        if len(job_id_parts) < 11:
            raise ValueError("Invalid job ID format")

        resource_group_name = job_id_parts[4]
        vault_name = job_id_parts[8]
        job_name = job_id_parts[10]

        return vault_name, resource_group_name, job_name

    except (IndexError, ValueError) as e:
        raise CLIError(
            f"Invalid job ID format: {job_id}. "
            "Expected format: /subscriptions/{{subscription-id}}/"
            "resourceGroups/{{resource-group}}/providers/"
            "Microsoft.DataReplication/replicationVaults/{{vault-name}}/"
            f"jobs/{{job-name}}. Error: {str(e)}"
        )


def _get_vault_name_from_project(cmd, resource_group_name,
                                 project_name, subscription_id):
    """
    Get the vault name from the Azure Migrate project solution.

    Args:
        cmd: The CLI command context
        resource_group_name (str): Resource group name
        project_name (str): Migrate project name
        subscription_id (str): Subscription ID

    Returns:
        str: The vault name

    Raises:
        CLIError: If the solution or vault is not found
    """
    from azext_migrate.helpers._utils import get_resource_by_id, APIVersion

    # Get the migration solution
    solution_name = "Servers-Migration-ServerMigration_DataReplication"
    solution_uri = (
        f"/subscriptions/{subscription_id}/"
        f"resourceGroups/{resource_group_name}/"
        f"providers/Microsoft.Migrate/migrateProjects/{project_name}/"
        f"solutions/{solution_name}"
    )

    logger.info(
        "Retrieving solution '%s' from project '%s'",
        solution_name, project_name)

    try:
        solution = get_resource_by_id(
            cmd,
            solution_uri,
            APIVersion.Microsoft_Migrate.value
        )

        if not solution:
            raise CLIError(
                f"Solution '{solution_name}' not found in project "
                f"'{project_name}'.")

        # Extract vault ID from solution extended details
        properties = solution.get('properties', {})
        details = properties.get('details', {})
        extended_details = details.get('extendedDetails', {})
        vault_id = extended_details.get('vaultId')

        if not vault_id:
            raise CLIError(
                "Vault ID not found in solution. The replication "
                "infrastructure may not be initialized.")

        # Parse vault name from vault ID
        vault_id_parts = vault_id.split("/")
        if len(vault_id_parts) < 9:
            raise CLIError(f"Invalid vault ID format: {vault_id}")

        vault_name = vault_id_parts[8]
        return vault_name

    except CLIError:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving vault from project '%s': %s",
            project_name, str(e))
        raise CLIError(
            f"Failed to retrieve vault information: {str(e)}")

def remove_local_server_replication(cmd,
                                    target_object_id,
                                    force_remove=False,
                                    subscription_id=None):
    """
    Stop replication for a migrated server.

    This cmdlet is based on a preview API version and may experience
    breaking changes in future releases.

    Args:
        cmd: The CLI command context
        target_object_id (str): Specifies the replicating server ARM ID
            for which replication needs to be disabled (required)
        force_remove (bool, optional): Specifies whether the replication
            needs to be force removed. Default is False
        subscription_id (str, optional): Azure Subscription ID. Uses
            current subscription if not provided

    Returns:
        dict: The job model from the API response

    Raises:
        CLIError: If the protected item is not found or cannot be
            removed in its current state
    """
    from azure.cli.core.commands.client_factory import \
        get_subscription_id
    from azext_migrate.helpers._utils import (
        get_resource_by_id,
        APIVersion
    )

    # Use current subscription if not provided
    if not subscription_id:
        subscription_id = get_subscription_id(cmd.cli_ctx)

    # Validate target_object_id
    if not target_object_id:
        raise CLIError(
            "The --target-object-id parameter is required.")

    # Parse the protected item ID to extract components
    # Expected format: /subscriptions/{sub}/resourceGroups/{rg}/providers/
    # Microsoft.DataReplication/replicationVaults/{vault}/
    # protectedItems/{item}
    try:
        protected_item_id_parts = target_object_id.split("/")
        if len(protected_item_id_parts) < 11:
            raise ValueError("Invalid protected item ID format")

        resource_group_name = protected_item_id_parts[4]
        vault_name = protected_item_id_parts[8]
        protected_item_name = protected_item_id_parts[10]
    except (IndexError, ValueError) as e:
        raise CLIError(
            f"Invalid target object ID format: {target_object_id}. "
            "Expected format: /subscriptions/{{subscription-id}}/"
            "resourceGroups/{{resource-group}}/providers/"
            "Microsoft.DataReplication/replicationVaults/{{vault-name}}/"
            f"protectedItems/{{item-name}}. Error: {str(e)}"
        )

    logger.info(
        "Attempting to remove replication for protected item '%s' "
        "in vault '%s'",
        protected_item_name, vault_name)

    # Get the protected item to validate it exists and check its state
    try:
        protected_item = get_resource_by_id(
            cmd,
            target_object_id,
            APIVersion.Microsoft_DataReplication.value
        )

        if not protected_item:
            raise CLIError(
                f"Replication item is not found with Id "
                f"'{target_object_id}'.")

        # Check if the protected item allows DisableProtection operation
        properties = protected_item.get('properties', {})
        allowed_jobs = properties.get('allowedJobs', [])

        if "DisableProtection" not in allowed_jobs:
            protection_state = properties.get(
                'protectionStateDescription', 'Unknown')
            raise CLIError(
                f"Replication item with Id '{target_object_id}' cannot "
                f"be removed at this moment. Current protection state is "
                f"'{protection_state}'.")

    except CLIError:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving protected item '%s': %s",
            target_object_id, str(e))
        raise CLIError(
            f"Failed to retrieve replication item: {str(e)}")

    # Construct the DELETE request URI with forceDelete parameter
    force_delete_param = "true" if force_remove else "false"
    delete_uri = (
        f"{target_object_id}?"
        f"api-version={APIVersion.Microsoft_DataReplication.value}&"
        f"forceDelete={force_delete_param}"
    )

    # Send the delete request
    try:
        from azure.cli.core.util import send_raw_request

        full_uri = cmd.cli_ctx.cloud.endpoints.resource_manager + delete_uri

        logger.info(
            "Sending DELETE request to remove protected item '%s' "
            "(force=%s)",
            protected_item_name, force_delete_param)

        response = send_raw_request(
            cmd.cli_ctx,
            method='DELETE',
            url=full_uri,
        )

        if response.status_code >= 400:
            error_message = (
                f"Failed to remove replication. "
                f"Status: {response.status_code}")
            try:
                error_body = response.json()
                if 'error' in error_body:
                    error_details = error_body['error']
                    error_code = error_details.get('code', 'Unknown')
                    error_msg = error_details.get(
                        'message', 'No message provided')
                    raise CLIError(f"{error_code}: {error_msg}")
            except (ValueError, KeyError):
                error_message += f", Response: {response.text}"
            raise CLIError(error_message)

        # The DELETE operation returns a job reference in the response
        # Extract the job name from the response headers or body
        operation_location = response.headers.get(
            'Azure-AsyncOperation') or response.headers.get('Location')

        if operation_location:
            # Extract job name from the operation location
            # Format: .../jobs/{jobName}?... or .../jobs/{jobName}
            job_parts = operation_location.split('/')
            job_name = None
            for i, part in enumerate(job_parts):
                if part == 'jobs' and i + 1 < len(job_parts):
                    # Get the job name and remove query string if present
                    job_name = job_parts[i + 1].split('?')[0]
                    break

            if job_name:
                # Get and return the job details
                job_uri = (
                    f"/subscriptions/{subscription_id}/"
                    f"resourceGroups/{resource_group_name}/"
                    f"providers/Microsoft.DataReplication/"
                    f"replicationVaults/{vault_name}/"
                    f"jobs/{job_name}"
                )

                try:
                    job_details = get_resource_by_id(
                        cmd,
                        job_uri,
                        APIVersion.Microsoft_DataReplication.value
                    )

                    if job_details:
                        logger.info(
                            "Successfully initiated removal of replication "
                            "for '%s'. Job: %s",
                            protected_item_name, job_name)
                        
                        # Display job ID and helpful command for user
                        print(f"Successfully initiated removal of replication for "
                              f"'{protected_item_name}'.")
                        print(f"Job ID: {job_name}")
                        print(f"\nTo check removal job status, run:")
                        print(f"  az migrate local replication get-job "
                              f"--job-name {job_name} "
                              f"--resource-group {resource_group_name} "
                              f"--project-name <project-name>")
                        
                        return job_details
                except Exception as job_error:
                    logger.warning(
                        "Could not retrieve job details: %s. "
                        "Replication removal was initiated.",
                        str(job_error))
                    # Still show the job name even if we can't get details
                    print(f"Successfully initiated removal of replication for "
                          f"'{protected_item_name}'.")
                    print(f"Job ID: {job_name}")
                    print(f"\nTo check removal job status, run:")
                    print(f"  az migrate local replication get-job "
                          f"--job-name {job_name} "
                          f"--resource-group {resource_group_name} "
                          f"--project-name <project-name>")

        # If we can't get job details, return success message
        logger.info(
            "Successfully initiated removal of replication for '%s'",
            protected_item_name)
        
        print(f"Successfully initiated removal of replication for "
              f"'{protected_item_name}'.")

    except CLIError:
        raise
    except Exception as e:
        logger.error(
            "Error removing replication for '%s': %s",
            protected_item_name, str(e))
        raise CLIError(
            f"Failed to remove replication: {str(e)}")

