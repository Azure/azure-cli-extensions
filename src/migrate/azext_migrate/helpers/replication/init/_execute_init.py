# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_migrate.helpers._utils import (
    FabricInstanceTypes
)
from azext_migrate.helpers.replication.init._validate import (
    get_and_validate_resource_group,
    get_migrate_project,
    get_data_replication_solution,
    get_discovery_solution,
    get_and_setup_replication_vault,
    parse_appliance_mappings,
    validate_and_get_site_ids
)
from azext_migrate.helpers.replication.init._setup_policy import (
    determine_instance_types,
    find_fabric,
    get_fabric_agent,
    setup_replication_policy,
    setup_cache_storage_account,
    verify_storage_account_network_settings,
    get_all_fabrics
)
from azext_migrate.helpers.replication.init._setup_permissions import (
    grant_storage_permissions,
    update_amh_solution_storage
)
from azext_migrate.helpers.replication.init._setup_extension import (
    setup_replication_extension
)


def setup_project_and_solutions(cmd,
                                subscription_id,
                                resource_group_name,
                                project_name):
    """Setup and retrieve project and solutions."""
    rg_uri = get_and_validate_resource_group(
        cmd, subscription_id, resource_group_name)
    project_uri = (f"{rg_uri}/providers/Microsoft.Migrate/migrateprojects/"
                   f"{project_name}")
    migrate_project = get_migrate_project(cmd, project_uri, project_name)
    amh_solution = get_data_replication_solution(cmd, project_uri)
    discovery_solution = get_discovery_solution(cmd, project_uri)

    return (
        rg_uri,
        project_uri,
        migrate_project,
        amh_solution,
        discovery_solution
    )


def setup_appliances_and_types(discovery_solution,
                               source_appliance_name,
                               target_appliance_name):
    """Parse appliance mappings and determine instance types."""
    app_map = parse_appliance_mappings(discovery_solution)
    source_site_id, target_site_id = validate_and_get_site_ids(
        app_map, source_appliance_name, target_appliance_name
    )
    result = determine_instance_types(
        source_site_id, target_site_id, source_appliance_name,
        target_appliance_name
    )
    instance_type, fabric_instance_type = result
    return (
        source_site_id,
        instance_type,
        fabric_instance_type
    )


def setup_fabrics_and_dras(cmd, rg_uri, resource_group_name,
                           source_appliance_name, target_appliance_name,
                           project_name, fabric_instance_type,
                           amh_solution):
    """Get all fabrics and set up DRAs."""
    all_fabrics, replication_fabrics_uri = get_all_fabrics(
        cmd, rg_uri, resource_group_name, source_appliance_name,
        target_appliance_name, project_name
    )

    source_fabric = find_fabric(
        all_fabrics, source_appliance_name, fabric_instance_type,
        amh_solution, is_source=True)
    target_fabric_instance_type = FabricInstanceTypes.AzLocalInstance.value
    target_fabric = find_fabric(
        all_fabrics, target_appliance_name, target_fabric_instance_type,
        amh_solution, is_source=False)

    source_dra = get_fabric_agent(
        cmd, replication_fabrics_uri, source_fabric,
        source_appliance_name, fabric_instance_type)
    target_dra = get_fabric_agent(
        cmd, replication_fabrics_uri, target_fabric,
        target_appliance_name, target_fabric_instance_type)

    return source_fabric, target_fabric, source_dra, target_dra


def setup_storage_and_permissions(cmd, rg_uri, amh_solution,
                                  cache_storage_account_id, source_site_id,
                                  source_appliance_name, migrate_project,
                                  project_name, source_dra, target_dra,
                                  replication_vault, subscription_id):
    """Setup storage account and grant permissions."""
    cache_storage_account = setup_cache_storage_account(
        cmd, rg_uri, amh_solution, cache_storage_account_id,
        source_site_id, source_appliance_name, migrate_project, project_name
    )

    storage_account_id = cache_storage_account['id']
    verify_storage_account_network_settings(
        cmd, rg_uri, cache_storage_account)
    grant_storage_permissions(
        cmd, storage_account_id, source_dra, target_dra,
        replication_vault, subscription_id)

    return storage_account_id


def initialize_infrastructure_components(cmd, rg_uri, project_uri,
                                         amh_solution,
                                         replication_vault_name,
                                         instance_type, migrate_project,
                                         project_name,
                                         cache_storage_account_id,
                                         source_site_id,
                                         source_appliance_name, source_dra,
                                         target_dra, replication_vault,
                                         subscription_id):
    """Initialize policy, storage, and AMH solution."""
    setup_replication_policy(
        cmd, rg_uri, replication_vault_name, instance_type)

    storage_account_id = setup_storage_and_permissions(
        cmd, rg_uri, amh_solution, cache_storage_account_id,
        source_site_id, source_appliance_name, migrate_project, project_name,
        source_dra, target_dra, replication_vault, subscription_id
    )

    amh_solution_uri = update_amh_solution_storage(
        cmd, project_uri, amh_solution, storage_account_id)

    return storage_account_id, amh_solution_uri


def execute_replication_infrastructure_setup(cmd, subscription_id,
                                             resource_group_name,
                                             project_name,
                                             source_appliance_name,
                                             target_appliance_name,
                                             cache_storage_account_id,
                                             pass_thru):
    """Execute the complete replication infrastructure setup workflow."""
    # Setup project and solutions
    (rg_uri, project_uri, migrate_project, amh_solution,
     discovery_solution) = setup_project_and_solutions(
        cmd, subscription_id, resource_group_name, project_name
    )

    # Get and setup replication vault
    (replication_vault,
     replication_vault_name) = get_and_setup_replication_vault(
        cmd, amh_solution, rg_uri)

    # Setup appliances and determine types
    (source_site_id, instance_type,
     fabric_instance_type) = setup_appliances_and_types(
        discovery_solution, source_appliance_name, target_appliance_name
    )

    # Setup fabrics and DRAs
    (source_fabric, target_fabric, source_dra,
     target_dra) = setup_fabrics_and_dras(
        cmd, rg_uri, resource_group_name, source_appliance_name,
        target_appliance_name, project_name, fabric_instance_type,
        amh_solution
    )

    # Initialize policy, storage, and AMH solution
    (storage_account_id,
     amh_solution_uri) = initialize_infrastructure_components(
        cmd, rg_uri, project_uri, amh_solution, replication_vault_name,
        instance_type, migrate_project, project_name,
        cache_storage_account_id, source_site_id, source_appliance_name,
        source_dra, target_dra, replication_vault, subscription_id
    )

    # Setup Replication Extension
    return setup_replication_extension(
        cmd, rg_uri, replication_vault_name, source_fabric,
        target_fabric, instance_type, storage_account_id,
        amh_solution_uri, pass_thru
    )
