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
    AzLocalInstanceTypes,
    FabricInstanceTypes
)
import json
from knack.util import CLIError
from knack.log import get_logger

logger = get_logger(__name__)


def process_site_type_hyperV(cmd,
                             rg_uri,
                             site_name,
                             machine_name,
                             subscription_id,
                             resource_group_name,
                             site_type):
    # Get HyperV machine
    machine_uri = (
        f"{rg_uri}/providers/Microsoft.OffAzure/HyperVSites"
        f"/{site_name}/machines/{machine_name}")
    machine = get_resource_by_id(
        cmd, machine_uri, APIVersion.Microsoft_OffAzure.value)
    if not machine:
        raise CLIError(
            f"Machine '{machine_name}' not in "
            f"resource group '{resource_group_name}' and "
            f"site '{site_name}'.")

    # Get HyperV site
    site_uri = (
        f"{rg_uri}/providers/Microsoft.OffAzure/HyperVSites/{site_name}")
    site_object = get_resource_by_id(
        cmd, site_uri, APIVersion.Microsoft_OffAzure.value)
    if not site_object:
        raise CLIError(
            f"Machine site '{site_name}' with Type '{site_type}' "
            f"not found.")

    # Get RunAsAccount
    properties = machine.get('properties', {})
    if properties.get('hostId'):
        # Machine is on a single HyperV host
        host_id_parts = properties['hostId'].split("/")
        if len(host_id_parts) < 11:
            raise CLIError(
                f"Invalid Hyper-V Host ARM ID '{properties['hostId']}'")

        host_resource_group = host_id_parts[4]
        host_site_name = host_id_parts[8]
        host_name = host_id_parts[10]

        host_uri = (
            f"/subscriptions/{subscription_id}/resourceGroups"
            f"/{host_resource_group}/providers/"
            f"Microsoft.OffAzure/HyperVSites"
            f"/{host_site_name}/hosts/{host_name}"
        )
        hyperv_host = get_resource_by_id(
            cmd, host_uri, APIVersion.Microsoft_OffAzure.value)
        if not hyperv_host:
            raise CLIError(
                f"Hyper-V host '{host_name}' not in "
                f"resource group '{host_resource_group}' and "
                f"site '{host_site_name}'.")

        run_as_account_id = (
            hyperv_host.get('properties', {}).get('runAsAccountId'))

    elif properties.get('clusterId'):
        # Machine is on a HyperV cluster
        cluster_id_parts = properties['clusterId'].split("/")
        if len(cluster_id_parts) < 11:
            raise CLIError(
                f"Invalid Hyper-V Cluster ARM ID "
                f"'{properties['clusterId']}'")

        cluster_resource_group = cluster_id_parts[4]
        cluster_site_name = cluster_id_parts[8]
        cluster_name = cluster_id_parts[10]

        cluster_uri = (
            f"/subscriptions/{subscription_id}/resourceGroups"
            f"/{cluster_resource_group}/providers/Microsoft.OffAzure"
            f"/HyperVSites/{cluster_site_name}/clusters/{cluster_name}"
        )
        hyperv_cluster = get_resource_by_id(
            cmd, cluster_uri, APIVersion.Microsoft_OffAzure.value)
        if not hyperv_cluster:
            raise CLIError(
                f"Hyper-V cluster '{cluster_name}' not in "
                f"resource group '{cluster_resource_group}' and "
                f"site '{cluster_site_name}'.")

        run_as_account_id = hyperv_cluster.get('properties', {}).get('runAsAccountId')

    return run_as_account_id, machine, site_object, AzLocalInstanceTypes.HyperVToAzLocal.value


def process_site_type_vmware(cmd,
                             rg_uri,
                             site_name,
                             machine_name,
                             subscription_id,
                             resource_group_name,
                             site_type):
    # Get VMware machine
    machine_uri = (
        f"{rg_uri}/providers/Microsoft.OffAzure/VMwareSites"
        f"/{site_name}/machines/{machine_name}")
    machine = get_resource_by_id(
        cmd, machine_uri, APIVersion.Microsoft_OffAzure.value)
    if not machine:
        raise CLIError(
            f"Machine '{machine_name}' not in "
            f"resource group '{resource_group_name}' and "
            f"site '{site_name}'.")

    # Get VMware site
    site_uri = (
        f"{rg_uri}/providers/Microsoft.OffAzure/VMwareSites/{site_name}")
    site_object = get_resource_by_id(
        cmd, site_uri, APIVersion.Microsoft_OffAzure.value)
    if not site_object:
        raise CLIError(
            f"Machine site '{site_name}' with Type '{site_type}' "
            f"not found.")

    # Get RunAsAccount
    properties = machine.get('properties', {})
    if properties.get('vCenterId'):
        vcenter_id_parts = properties['vCenterId'].split("/")
        if len(vcenter_id_parts) < 11:
            raise CLIError(
                f"Invalid VMware vCenter ARM ID "
                f"'{properties['vCenterId']}'")

        vcenter_resource_group = vcenter_id_parts[4]
        vcenter_site_name = vcenter_id_parts[8]
        vcenter_name = vcenter_id_parts[10]

        vcenter_uri = (
            f"/subscriptions/{subscription_id}/resourceGroups"
            f"/{vcenter_resource_group}/providers/Microsoft.OffAzure"
            f"/VMwareSites/{vcenter_site_name}/vCenters/{vcenter_name}"
        )
        vmware_vcenter = get_resource_by_id(
            cmd,
            vcenter_uri,
            APIVersion.Microsoft_OffAzure.value)
        if not vmware_vcenter:
            raise CLIError(
                f"VMware vCenter '{vcenter_name}' not in "
                f"resource group '{vcenter_resource_group}' and "
                f"site '{vcenter_site_name}'.")

        run_as_account_id = vmware_vcenter.get('properties', {}).get('runAsAccountId')

    return run_as_account_id, machine, site_object, AzLocalInstanceTypes.VMwareToAzLocal.value


def process_amh_solution(cmd,
                         machine,
                         site_object,
                         project_name,
                         resource_group_name,
                         machine_name,
                         rg_uri):
    # Validate the VM for replication
    machine_props = machine.get('properties', {})
    if machine_props.get('isDeleted'):
        raise CLIError(
            f"Cannot migrate machine '{machine_name}' as it is marked as "
            "deleted."
        )

    # Get project name from site
    discovery_solution_id = (
        site_object.get('properties', {}).get('discoverySolutionId', '')
    )
    if not discovery_solution_id:
        raise CLIError(
            "Unable to determine project from site. Invalid site "
            "configuration."
        )

    if not project_name:
        project_name = discovery_solution_id.split("/")[8]

    # Get the migrate project resource
    migrate_project_uri = (
        f"{rg_uri}/providers/Microsoft.Migrate/migrateprojects/"
        f"{project_name}"
    )
    migrate_project = get_resource_by_id(
        cmd, migrate_project_uri, APIVersion.Microsoft_Migrate.value
    )
    if not migrate_project:
        raise CLIError(f"Migrate project '{project_name}' not found.")

    # Get Data Replication Service (AMH solution)
    amh_solution_name = "Servers-Migration-ServerMigration_DataReplication"
    amh_solution_uri = (
        f"{rg_uri}/providers/Microsoft.Migrate/migrateprojects/"
        f"{project_name}/solutions/{amh_solution_name}"
    )
    amh_solution = get_resource_by_id(
        cmd,
        amh_solution_uri,
        APIVersion.Microsoft_Migrate.value
    )
    if not amh_solution:
        raise CLIError(
            f"No Data Replication Service Solution "
            f"'{amh_solution_name}' found in resource group "
            f"'{resource_group_name}' and project '{project_name}'. "
            "Please verify your appliance setup."
        )
    return amh_solution, migrate_project, machine_props


def process_replication_vault(cmd,
                              amh_solution,
                              resource_group_name):
    # Validate replication vault
    vault_id = (
        amh_solution.get('properties', {})
        .get('details', {})
        .get('extendedDetails', {})
        .get('vaultId')
    )
    if not vault_id:
        raise CLIError(
            "No Replication Vault found. Please verify your Azure Migrate "
            "project setup."
        )

    replication_vault_name = vault_id.split("/")[8]
    replication_vault = get_resource_by_id(
        cmd, vault_id, APIVersion.Microsoft_DataReplication.value
    )
    if not replication_vault:
        raise CLIError(
            f"No Replication Vault '{replication_vault_name}' "
            f"found in Resource Group '{resource_group_name}'. "
            "Please verify your Azure Migrate project setup."
        )

    prov_state = replication_vault.get('properties', {})
    prov_state = prov_state.get('provisioningState')
    if prov_state != ProvisioningState.Succeeded.value:
        raise CLIError(
            f"The Replication Vault '{replication_vault_name}' is not in a "
            f"valid state. "
            f"The provisioning state is '{prov_state}'. "
            "Please verify your Azure Migrate project setup."
        )
    return replication_vault_name


def process_replication_policy(cmd,
                               replication_vault_name,
                               instance_type,
                               rg_uri):
    # Validate Policy
    policy_name = f"{replication_vault_name}{instance_type}policy"
    policy_uri = (
        f"{rg_uri}/providers/Microsoft.DataReplication"
        f"/replicationVaults/{replication_vault_name}"
        f"/replicationPolicies/{policy_name}"
    )
    policy = get_resource_by_id(
        cmd, policy_uri, APIVersion.Microsoft_DataReplication.value
    )

    if not policy:
        raise CLIError(
            f"The replication policy '{policy_name}' not found. "
            "The replication infrastructure is not initialized. "
            "Run the 'az migrate local replication init "
            "initialize' command."
        )
    prov_state = policy.get('properties', {}).get('provisioningState')
    if prov_state != ProvisioningState.Succeeded.value:
        raise CLIError(
            f"The replication policy '{policy_name}' is not in a valid "
            f"state. "
            f"The provisioning state is '{prov_state}'. "
            "Re-run the 'az migrate local replication init "
            "initialize' command."
        )
    return policy_name


def _validate_appliance_map_v3(app_map, app_map_v3):
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


def process_appliance_map(cmd, rg_uri, project_name):
    # Access Discovery Solution to get appliance mapping
    discovery_solution_name = "Servers-Discovery-ServerDiscovery"
    discovery_solution_uri = (
        f"{rg_uri}/providers/Microsoft.Migrate/migrateprojects/"
        f"{project_name}/solutions/{discovery_solution_name}"
    )
    discovery_solution = get_resource_by_id(
        cmd, discovery_solution_uri, APIVersion.Microsoft_Migrate.value
    )

    if not discovery_solution:
        raise CLIError(
            f"Server Discovery Solution '{discovery_solution_name}' not "
            "found."
        )

    # Get Appliances Mapping
    app_map = {}
    extended_details = (
        discovery_solution.get('properties', {})
        .get('details', {})
        .get('extendedDetails', {})
    )

    # Process applianceNameToSiteIdMapV2
    if 'applianceNameToSiteIdMapV2' in extended_details:
        try:
            app_map_v2 = json.loads(
                extended_details['applianceNameToSiteIdMapV2']
            )
            if isinstance(app_map_v2, list):
                for item in app_map_v2:
                    is_dict = isinstance(item, dict)
                    has_keys = ('ApplianceName' in item and
                                'SiteId' in item)
                    if is_dict and has_keys:
                        app_map[item['ApplianceName'].lower()] = (
                            item['SiteId']
                        )
                        app_map[item['ApplianceName']] = item['SiteId']
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(
                "Failed to parse applianceNameToSiteIdMapV2: %s", str(e)
            )

    # Process applianceNameToSiteIdMapV3
    if 'applianceNameToSiteIdMapV3' in extended_details:
        try:
            app_map_v3 = json.loads(
                extended_details['applianceNameToSiteIdMapV3']
            )
            if isinstance(app_map_v3, dict):
                for appliance_name_key, site_info in app_map_v3.items():
                    is_dict_w_site = (isinstance(site_info, dict) and
                                      'SiteId' in site_info)
                    if is_dict_w_site:
                        app_map[appliance_name_key.lower()] = (
                            site_info['SiteId']
                        )
                        app_map[appliance_name_key] = site_info['SiteId']
                    elif isinstance(site_info, str):
                        app_map[appliance_name_key.lower()] = site_info
                        app_map[appliance_name_key] = site_info
            elif isinstance(app_map_v3, list):
                app_map = _validate_appliance_map_v3(
                    app_map, app_map_v3
                )

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(
                "Failed to parse applianceNameToSiteIdMapV3: %s", str(e)
            )
    return app_map


def _validate_site_ids(app_map,
                       source_appliance_name,
                       target_appliance_name):
    source_site_id = (
        app_map.get(source_appliance_name) or
        app_map.get(source_appliance_name.lower())
    )
    target_site_id = (
        app_map.get(target_appliance_name) or
        app_map.get(target_appliance_name.lower())
    )

    if not source_site_id:
        available_appliances = list(
            set(k for k in app_map if not k.islower())
        )
        if not available_appliances:
            available_appliances = list(set(app_map.keys()))
        raise CLIError(
            f"Source appliance '{source_appliance_name}' not in "
            "discovery solution. "
            f"Available appliances: {','.join(available_appliances)}"
        )

    if not target_site_id:
        available_appliances = list(
            set(k for k in app_map if not k.islower())
        )
        if not available_appliances:
            available_appliances = list(set(app_map.keys()))
        raise CLIError(
            f"Target appliance '{target_appliance_name}' not in "
            "discovery solution. "
            f"Available appliances: {','.join(available_appliances)}"
        )
    return source_site_id, target_site_id


def _process_source_fabrics(all_fabrics,
                            source_appliance_name,
                            amh_solution,
                            fabric_instance_type):
    source_fabric = None
    source_fabric_candidates = []

    for fabric in all_fabrics:
        props = fabric.get('properties', {})
        custom_props = props.get('customProperties', {})
        fabric_name = fabric.get('name', '')
        prov_state = props.get('provisioningState')
        is_succeeded = prov_state == ProvisioningState.Succeeded.value

        fabric_solution_id = (
            custom_props.get('migrationSolutionId', '').rstrip('/')
        )
        expected_solution_id = amh_solution.get('id', '').rstrip('/')
        is_correct_solution = (
            fabric_solution_id.lower() == expected_solution_id.lower()
        )
        is_correct_instance = (
            custom_props.get('instanceType') == fabric_instance_type
        )

        name_matches = (
            fabric_name.lower().startswith(
                source_appliance_name.lower()
            ) or
            source_appliance_name.lower() in fabric_name.lower() or
            fabric_name.lower() in source_appliance_name.lower() or
            f"{source_appliance_name.lower()}-" in fabric_name.lower()
        )

        # Collect potential candidates even if they don't fully match
        if custom_props.get('instanceType') == fabric_instance_type:
            source_fabric_candidates.append({
                'name': fabric_name,
                'state': props.get('provisioningState'),
                'solution_match': is_correct_solution,
                'name_match': name_matches
            })

        if is_succeeded and is_correct_instance and name_matches:
            # If solution doesn't match, log warning but still consider it
            if not is_correct_solution:
                logger.warning(
                    "Fabric '%s' matches name and type but has different "
                    "solution ID",
                    fabric_name
                )
            source_fabric = fabric
            break
    return source_fabric, source_fabric_candidates


def _handle_no_source_fabric_error(source_appliance_name,
                                   source_fabric_candidates,
                                   fabric_instance_type,
                                   all_fabrics):
    error_msg = (
        f"Couldn't find connected source appliance "
        f"'{source_appliance_name}'.\n"
    )
    if source_fabric_candidates:
        error_msg += (
            f"Found {len(source_fabric_candidates)} fabric(s) with "
            f"matching type '{fabric_instance_type}': \n"
        )
        for candidate in source_fabric_candidates:
            error_msg += (
                f" - {candidate['name']} (state: "
                f"{candidate['state']}, "
            )
            error_msg += (
                f"solution_match: {candidate['solution_match']}, "
            )
            error_msg += f"name_match: {candidate['name_match']})\n"
        error_msg += "\nPlease verify:\n"
        error_msg += "1. The appliance name matches exactly\n"
        error_msg += "2. The fabric is in 'Succeeded' state\n"
        error_msg += (
            "3. The fabric belongs to the correct migration solution"
        )
    else:
        error_msg += (
            f"No fabrics found with instance type "
            f"'{fabric_instance_type}'.\n"
        )
        error_msg += "\nThis usually means:\n"
        error_msg += (
            f"1. The source appliance '{source_appliance_name}' is not "
            "properly configured\n"
        )
        if fabric_instance_type == FabricInstanceTypes.VMwareInstance.value:
            appliance_type = 'VMware'
        else:
            appliance_type = 'HyperV'
        error_msg += (
            f"2. The appliance type doesn't match (expecting "
            f"{appliance_type})\n"
        )
        error_msg += (
            "3. The fabric creation is still in progress - wait a few "
            "minutes and retry"
        )

        # List all available fabrics for debugging
        if all_fabrics:
            error_msg += "\n\nAvailable fabrics in resource group:\n"
            for fabric in all_fabrics:
                props = fabric.get('properties', {})
                custom_props = props.get('customProperties', {})
                error_msg += (
                    f" - {fabric.get('name')} "
                    f"(type: {custom_props.get('instanceType')})\n"
                )

    raise CLIError(error_msg)


def process_source_fabric(cmd,
                          rg_uri,
                          app_map,
                          source_appliance_name,
                          target_appliance_name,
                          amh_solution,
                          resource_group_name,
                          project_name):
    # Validate and get site IDs
    source_site_id, target_site_id = _validate_site_ids(
        app_map,
        source_appliance_name,
        target_appliance_name)

    # Determine instance types based on site IDs
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

    # Get healthy fabrics in the resource group
    fabrics_uri = (
        f"{rg_uri}/providers/Microsoft.DataReplication/"
        f"replicationFabrics"
        f"?api-version={APIVersion.Microsoft_DataReplication.value}"
    )
    fabrics_response = send_get_request(cmd, fabrics_uri)
    all_fabrics = fabrics_response.json().get('value', [])

    if not all_fabrics:
        raise CLIError(
            f"No replication fabrics found in resource group "
            f"'{resource_group_name}'. Please ensure that: \n"
            f"1. The source appliance '{source_appliance_name}' is "
            f"deployed and connected\n"
            f"2. The target appliance '{target_appliance_name}' is "
            f"deployed and connected\n"
            f"3. Both appliances are registered with the Azure Migrate "
            f"project '{project_name}'"
        )

    source_fabric, source_fabric_candidates = _process_source_fabrics(
        all_fabrics,
        source_appliance_name,
        amh_solution,
        fabric_instance_type)

    if not source_fabric:
        _handle_no_source_fabric_error(
            source_appliance_name,
            source_fabric_candidates,
            fabric_instance_type,
            all_fabrics)
    return source_fabric, fabric_instance_type, instance_type, all_fabrics


def _process_target_fabrics(all_fabrics,
                            target_appliance_name,
                            amh_solution):
    # Filter for target fabric - make matching more flexible and diagnostic
    target_fabric_instance_type = FabricInstanceTypes.AzLocalInstance.value
    target_fabric = None
    target_fabric_candidates = []

    for fabric in all_fabrics:
        props = fabric.get('properties', {})
        custom_props = props.get('customProperties', {})
        fabric_name = fabric.get('name', '')
        is_succeeded = (props.get('provisioningState') ==
                        ProvisioningState.Succeeded.value)

        fabric_solution_id = (custom_props.get('migrationSolutionId', '')
                              .rstrip('/'))
        expected_solution_id = amh_solution.get('id', '').rstrip('/')
        is_correct_solution = (fabric_solution_id.lower() ==
                               expected_solution_id.lower())
        is_correct_instance = (custom_props.get('instanceType') ==
                               target_fabric_instance_type)

        name_matches = (
            fabric_name.lower().startswith(target_appliance_name.lower()) or
            target_appliance_name.lower() in fabric_name.lower() or
            fabric_name.lower() in target_appliance_name.lower() or
            f"{target_appliance_name.lower()}-" in fabric_name.lower()
        )

        # Collect potential candidates
        if (custom_props.get('instanceType') ==
                target_fabric_instance_type):
            target_fabric_candidates.append({
                'name': fabric_name,
                'state': props.get('provisioningState'),
                'solution_match': is_correct_solution,
                'name_match': name_matches
            })

        if is_succeeded and is_correct_instance and name_matches:
            if not is_correct_solution:
                logger.warning(
                    "Fabric '%s' matches name and type but has different "
                    "solution ID", fabric_name)
            target_fabric = fabric
            break
    return target_fabric, target_fabric_candidates, \
        target_fabric_instance_type


def _handle_no_target_fabric_error(target_appliance_name,
                                   target_fabric_candidates,
                                   target_fabric_instance_type):
    # Provide more detailed error message
    error_msg = (f"Couldn't find connected target appliance "
                 f"'{target_appliance_name}'.\n")

    if target_fabric_candidates:
        error_msg += (f"Found {len(target_fabric_candidates)} fabric(s) "
                      f"with matching type "
                      f"'{target_fabric_instance_type}': \n")
        for candidate in target_fabric_candidates:
            error_msg += (f" - {candidate['name']} "
                          f"(state: {candidate['state']}, ")
            error_msg += (f"solution_match: "
                          f"{candidate['solution_match']}, "
                          f"name_match: "
                          f"{candidate['name_match']})\n")
    else:
        error_msg += (f"No fabrics found with instance type "
                      f"'{target_fabric_instance_type}'.\n")
        error_msg += "\nThis usually means:\n"
        error_msg += (f"1. The target appliance '{target_appliance_name}' "
                      f"is not properly configured for Azure Local\n")
        error_msg += ("2. The fabric creation is still in progress - wait "
                      "a few minutes and retry\n")
        error_msg += ("3. The target appliance is not connected to the "
                      "Azure Local cluster")

    raise CLIError(error_msg)


def process_target_fabric(cmd,
                          rg_uri,
                          source_fabric,
                          fabric_instance_type,
                          all_fabrics,
                          source_appliance_name,
                          target_appliance_name,
                          amh_solution):
    # Get source fabric agent (DRA)
    source_fabric_name = source_fabric.get('name')
    dras_uri = (
        f"{rg_uri}/providers/Microsoft.DataReplication"
        f"/replicationFabrics/{source_fabric_name}/fabricAgents"
        f"?api-version={APIVersion.Microsoft_DataReplication.value}"
    )
    source_dras_response = send_get_request(cmd, dras_uri)
    source_dras = source_dras_response.json().get('value', [])

    source_dra = None
    for dra in source_dras:
        props = dra.get('properties', {})
        custom_props = props.get('customProperties', {})
        if (props.get('machineName') == source_appliance_name and
                custom_props.get('instanceType') == fabric_instance_type and
                bool(props.get('isResponsive'))):
            source_dra = dra
            break

    if not source_dra:
        raise CLIError(
            f"The source appliance '{source_appliance_name}' is in a "
            f"disconnected state.")

    target_fabric, target_fabric_candidates, \
        target_fabric_instance_type = _process_target_fabrics(
            all_fabrics,
            target_appliance_name,
            amh_solution)

    if not target_fabric:
        _handle_no_target_fabric_error(
            target_appliance_name,
            target_fabric_candidates,
            target_fabric_instance_type
        )

    # Get target fabric agent (DRA)
    target_fabric_name = target_fabric.get('name')
    target_dras_uri = (
        f"{rg_uri}/providers/Microsoft.DataReplication"
        f"/replicationFabrics/{target_fabric_name}/fabricAgents"
        f"?api-version={APIVersion.Microsoft_DataReplication.value}"
    )
    target_dras_response = send_get_request(cmd, target_dras_uri)
    target_dras = target_dras_response.json().get('value', [])

    target_dra = None
    for dra in target_dras:
        props = dra.get('properties', {})
        custom_props = props.get('customProperties', {})
        if (props.get('machineName') == target_appliance_name and
                custom_props.get('instanceType') ==
                target_fabric_instance_type and
                bool(props.get('isResponsive'))):
            target_dra = dra
            break

    if not target_dra:
        raise CLIError(
            f"The target appliance '{target_appliance_name}' is in a "
            f"disconnected state.")

    return target_fabric, source_dra, target_dra
