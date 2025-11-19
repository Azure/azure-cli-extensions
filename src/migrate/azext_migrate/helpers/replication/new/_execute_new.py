# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=possibly-used-before-assignment
from azext_migrate.helpers._utils import (
    get_resource_by_id,
    create_or_update_resource,
    APIVersion,
    ProvisioningState,
    SiteTypes,
    VMNicSelection
)
import re
from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def get_ARC_resource_bridge_info(target_fabric, migrate_project):
    target_fabric_custom_props = (
        target_fabric.get('properties', {}).get('customProperties', {}))
    target_cluster_id = (
        target_fabric_custom_props.get('cluster', {})
        .get('resourceName', ''))

    if not target_cluster_id:
        target_cluster_id = (target_fabric_custom_props
                             .get('azStackHciClusterName', ''))

    if not target_cluster_id:
        target_cluster_id = (target_fabric_custom_props
                             .get('clusterName', ''))

    # Extract custom location from target fabric
    custom_location_id = (target_fabric_custom_props
                          .get('customLocationRegion', ''))

    if not custom_location_id:
        custom_location_id = (target_fabric_custom_props
                              .get('customLocationId', ''))

    if not custom_location_id:
        if target_cluster_id:
            cluster_parts = target_cluster_id.split('/')
            if len(cluster_parts) >= 5:
                custom_location_region = (
                    migrate_project.get('location', 'eastus'))
                custom_location_id = (
                    f"/subscriptions/{cluster_parts[2]}/"
                    f"resourceGroups/{cluster_parts[4]}/providers/"
                    f"Microsoft.ExtendedLocation/customLocations/"
                    f"{cluster_parts[-1]}-customLocation"
                )
            else:
                custom_location_region = (
                    migrate_project.get('location', 'eastus'))
        else:
            custom_location_region = (
                migrate_project.get('location', 'eastus'))
    else:
        custom_location_region = migrate_project.get('location', 'eastus')
    return custom_location_id, custom_location_region, target_cluster_id


def construct_disk_and_nic_mapping(is_power_user_mode,
                                   disk_to_include,
                                   nic_to_include,
                                   machine_props,
                                   site_type,
                                   os_disk_id,
                                   target_virtual_switch_id,
                                   target_test_virtual_switch_id):
    disks = []
    nics = []

    if is_power_user_mode:
        if not disk_to_include or len(disk_to_include) == 0:
            raise CLIError(
                "At least one disk must be included for replication.")

        # Validate that exactly one disk is marked as OS disk
        os_disks = [d for d in disk_to_include if d.get('isOSDisk', False)]
        if len(os_disks) != 1:
            raise CLIError(
                "Exactly one disk must be designated as the OS disk.")

        # Process disks
        for disk in disk_to_include:
            disk_obj = {
                'diskId': disk.get('diskId'),
                'diskSizeGb': disk.get('diskSizeGb'),
                'diskFileFormat': disk.get('diskFileFormat', 'VHDX'),
                'isDynamic': disk.get('isDynamic', True),
                'isOSDisk': disk.get('isOSDisk', False)
            }
            disks.append(disk_obj)

        # Process NICs
        for nic in nic_to_include:
            nic_obj = {
                'nicId': nic.get('nicId'),
                'targetNetworkId': nic.get('targetNetworkId'),
                'testNetworkId': nic.get('testNetworkId',
                                         nic.get('targetNetworkId')),
                'selectionTypeForFailover': nic.get(
                    'selectionTypeForFailover',
                    VMNicSelection.SelectedByUser.value)
            }
            nics.append(nic_obj)
    else:
        machine_disks = machine_props.get('disks', [])
        machine_nics = machine_props.get('networkAdapters', [])

        # Find OS disk and validate
        os_disk_found = False
        for disk in machine_disks:
            if site_type == SiteTypes.HyperVSites.value:
                disk_id = disk.get('instanceId')
                disk_size = disk.get('maxSizeInBytes', 0)
            else:  # VMware
                disk_id = disk.get('uuid')
                disk_size = disk.get('maxSizeInBytes', 0)

            is_os_disk = disk_id == os_disk_id
            if is_os_disk:
                os_disk_found = True
            # Round up to GB
            disk_size_gb = (disk_size + (1024 ** 3 - 1)) // (1024 ** 3)
            disk_obj = {
                'diskId': disk_id,
                'diskSizeGb': disk_size_gb,
                'diskFileFormat': 'VHDX',
                'isDynamic': True,
                'isOSDisk': is_os_disk
            }
            disks.append(disk_obj)

        # Validate that the specified OS disk was found
        if not os_disk_found:
            available_disks = [d['diskId'] for d in disks]
            raise CLIError(
                f"The specified OS disk ID '{os_disk_id}' was not found in the machine's disks. "
                f"Available disk IDs: {', '.join(available_disks)}"
            )

        for nic in machine_nics:
            nic_id = nic.get('nicId')
            test_network_id = (target_test_virtual_switch_id or
                               target_virtual_switch_id)

            nic_obj = {
                'nicId': nic_id,
                'targetNetworkId': target_virtual_switch_id,
                'testNetworkId': test_network_id,
                'selectionTypeForFailover': VMNicSelection.SelectedByUser.value
            }
            nics.append(nic_obj)
    return disks, nics


def _handle_configuration_validation(cmd,
                                     subscription_id,
                                     resource_group_name,
                                     replication_vault_name,
                                     machine_name,
                                     machine_props,
                                     target_vm_cpu_core,
                                     target_vm_ram,
                                     site_type):
    protected_item_name = machine_name
    protected_item_uri = (
        f"/subscriptions/{subscription_id}/resourceGroups"
        f"/{resource_group_name}/providers/Microsoft.DataReplication"
        f"/replicationVaults/{replication_vault_name}"
        f"/protectedItems/{protected_item_name}"
    )

    try:
        existing_item = get_resource_by_id(
            cmd,
            protected_item_uri,
            APIVersion.Microsoft_DataReplication.value)
        if existing_item:
            protection_state = existing_item.get('properties', {}).get('protectionState')
            logger.warning(f"Found existing protected item: {existing_item.get('id', 'unknown')}, state: {protection_state}")

            # If in failed state, offer helpful guidance
            if protection_state in ['EnablingFailed', 'DisablingFailed', 'Failed']:
                raise CLIError(
                    f"A failed replication exists for machine '{machine_name}' (state: {protection_state}). "
                    f"Please delete it first using Azure Portal or contact Azure Support. "
                    f"Protected item ID: {protected_item_uri}"
                )
            else:
                raise CLIError(
                    f"A replication already exists for machine '{machine_name}' (state: {protection_state}). "
                    "Remove it first before creating a new one.")
    except (CLIError, ValueError, KeyError, TypeError) as e:
        # Check if it's a 404 Not Found error - that's expected and fine
        error_str = str(e)
        logger.info(f"Exception during protected item check: {error_str}")
        if ("ResourceNotFound" in error_str or "404" in error_str or
                "Not Found" in error_str):
            existing_item = None
        else:
            # Some other error occurred, re-raise it
            raise

    # Determine Hyper-V generation
    if site_type == SiteTypes.HyperVSites.value:
        hyperv_generation = machine_props.get('generation', '1')
        is_source_dynamic_memory = machine_props.get(
            'isDynamicMemoryEnabled', False)
    else:  # VMware
        firmware = machine_props.get('firmware', 'BIOS')
        hyperv_generation = '2' if firmware != 'BIOS' else '1'
        is_source_dynamic_memory = False

    # Determine target CPU and RAM
    source_cpu_cores = machine_props.get('numberOfProcessorCore', 2)
    source_memory_mb = machine_props.get('allocatedMemoryInMB', 4096)

    if not target_vm_cpu_core:
        target_vm_cpu_core = source_cpu_cores

    if not target_vm_ram:
        target_vm_ram = max(source_memory_mb, 512)  # Minimum 512MB

    if target_vm_cpu_core < 1 or target_vm_cpu_core > 240:
        raise CLIError("Target VM CPU cores must be between 1 and 240.")

    if hyperv_generation == '1':
        if target_vm_ram < 512 or target_vm_ram > 1048576:  # 1TB
            raise CLIError(
                "Target VM RAM must be between 512 MB and 1048576 MB "
                "(1 TB) for Generation 1 VMs.")
    else:
        if target_vm_ram < 32 or target_vm_ram > 12582912:  # 12TB
            raise CLIError(
                "Target VM RAM must be between 32 MB and 12582912 MB "
                "(12 TB) for Generation 2 VMs.")

    return (hyperv_generation, source_cpu_cores, is_source_dynamic_memory,
            source_memory_mb, protected_item_uri, target_vm_cpu_core,
            target_vm_ram)


def _build_custom_properties(instance_type, custom_location_id,
                             custom_location_region,
                             machine_id, disks, nics, target_vm_name,
                             target_resource_group_id,
                             target_storage_path_id, hyperv_generation,
                             target_vm_cpu_core,
                             source_cpu_cores, is_dynamic_ram_enabled,
                             is_source_dynamic_memory,
                             source_memory_mb, target_vm_ram, source_dra,
                             target_dra,
                             run_as_account_id, target_cluster_id):
    """Build custom properties for protected item creation."""
    return {
        "instanceType": instance_type,
        "targetArcClusterCustomLocationId": custom_location_id or "",
        "customLocationRegion": custom_location_region,
        "fabricDiscoveryMachineId": machine_id,
        "disksToInclude": [
            {
                "diskId": disk["diskId"],
                "diskSizeGB": disk["diskSizeGb"],
                "diskFileFormat": disk["diskFileFormat"],
                "isOsDisk": disk["isOSDisk"],
                "isDynamic": disk["isDynamic"],
                "diskPhysicalSectorSize": 512
            }
            for disk in disks
        ],
        "targetVmName": target_vm_name,
        "targetResourceGroupId": target_resource_group_id,
        "storageContainerId": target_storage_path_id,
        "hyperVGeneration": hyperv_generation,
        "targetCpuCores": target_vm_cpu_core,
        "sourceCpuCores": source_cpu_cores,
        "isDynamicRam": (is_dynamic_ram_enabled
                         if is_dynamic_ram_enabled is not None
                         else is_source_dynamic_memory),
        "sourceMemoryInMegaBytes": float(source_memory_mb),
        "targetMemoryInMegaBytes": int(target_vm_ram),
        "nicsToInclude": [
            {
                "nicId": nic["nicId"],
                "selectionTypeForFailover": nic["selectionTypeForFailover"],
                "targetNetworkId": nic["targetNetworkId"],
                "testNetworkId": nic.get("testNetworkId", "")
            }
            for nic in nics
        ],
        "dynamicMemoryConfig": {
            "maximumMemoryInMegaBytes": 1048576,  # Max for Gen 1
            "minimumMemoryInMegaBytes": 512,       # Min for Gen 1
            "targetMemoryBufferPercentage": 20
        },
        "sourceFabricAgentName": source_dra.get('name'),
        "targetFabricAgentName": target_dra.get('name'),
        "runAsAccountId": run_as_account_id,
        "targetHCIClusterId": target_cluster_id
    }


# pylint: disable=too-many-locals
def create_protected_item(cmd,
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
                          target_cluster_id):

    config_result = _handle_configuration_validation(
        cmd,
        subscription_id,
        resource_group_name,
        replication_vault_name,
        machine_name,
        machine_props,
        target_vm_cpu_core,
        target_vm_ram,
        site_type
    )
    (hyperv_generation, source_cpu_cores, is_source_dynamic_memory,
     source_memory_mb, protected_item_uri, target_vm_cpu_core,
     target_vm_ram) = config_result

    # Construct protected item properties with only the essential properties
    custom_properties = _build_custom_properties(
        instance_type, custom_location_id, custom_location_region,
        machine_id, disks, nics, target_vm_name, target_resource_group_id,
        target_storage_path_id, hyperv_generation, target_vm_cpu_core,
        source_cpu_cores, is_dynamic_ram_enabled, is_source_dynamic_memory,
        source_memory_mb, target_vm_ram, source_dra, target_dra,
        run_as_account_id, target_cluster_id
    )

    protected_item_body = {
        "properties": {
            "policyName": policy_name,
            "replicationExtensionName": replication_extension_name,
            "customProperties": custom_properties
        }
    }

    response = create_or_update_resource(
        cmd,
        protected_item_uri,
        APIVersion.Microsoft_DataReplication.value,
        protected_item_body)

    # Extract job ID from response if available
    job_id = None
    if response and 'properties' in response:
        props = response['properties']
        if 'lastSuccessfulEnableProtectionJob' in props:
            job_info = props['lastSuccessfulEnableProtectionJob']
            if 'id' in job_info:
                # Extract just the job name from the full ARM ID
                job_id = job_info['id'].split('/')[-1]
        elif 'lastEnableProtectionJob' in props:
            job_info = props['lastEnableProtectionJob']
            if 'id' in job_info:
                job_id = job_info['id'].split('/')[-1]

    print("Successfully initiated replication for machine '{}'.".format(machine_name))
    if job_id:
        print("Job ID: {}".format(job_id))
        print("\nTo check job status, run:")
        print("  az migrate local replication get-job --job-name {} "
              "--resource-group {} "
              "--project-name <project-name>".format(job_id, resource_group_name))

    return response
