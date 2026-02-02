# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# coding=utf-8
from knack.help_files import helps  # pylint: disable=unused-import


helps['migrate'] = """
    type: group
    short-summary: Manage Azure Migrate resources and operations.
    long-summary: |
        Commands to manage Azure Migrate projects,
        discover servers, and perform migrations
        to Azure and Azure Local/Stack HCI environments.
"""

helps['migrate local'] = """
    type: group
    short-summary: Manage Azure Local/Stack HCI migration operations.
    long-summary: |
        Commands to manage server discovery
        and replication for migrations to Azure Local
        and Azure Stack HCI environments.
        These commands support VMware and Hyper-V source
        environments.
"""

helps['migrate get-discovered-server'] = """
    type: command
    short-summary: Retrieve discovered servers from an Azure Migrate project.
    long-summary: |
        Get information about servers discovered by Azure Migrate appliances.
        You can list all discovered servers in a project,
        filter by display name or machine type,
        or get a specific server by name.
        This command supports both VMware and Hyper-V environments.
    parameters:
        - name: --project-name
          short-summary: Name of the Azure Migrate project.
          long-summary: >
            The Azure Migrate project that contains
            the discovered servers.
        - name: --display-name
          short-summary: Display name of the source machine to filter by.
          long-summary: >
            Filter discovered servers by their display name
            (partial match supported).
        - name: --source-machine-type
          short-summary: Type of the source machine.
          long-summary: >
            Filter by source machine type. Valid values are
            'VMware' or 'HyperV'.
        - name: --subscription-id
          short-summary: Azure subscription ID.
          long-summary: >
            The subscription containing the Azure Migrate project.
            Uses the default subscription if not specified.
        - name: --name
          short-summary: Internal name of the specific source machine.
          long-summary: >
            The internal machine name assigned by Azure Migrate
            (different from display name).
        - name: --appliance-name
          short-summary: Name of the appliance (site) containing the machines.
          long-summary: >
            Filter servers discovered by
            a specific Azure Migrate appliance.
    examples:
        - name: List all discovered servers in a project
          text: |
            az migrate get-discovered-server \\
                --project-name myMigrateProject \\
                --resource-group myRG
        - name: Get a specific discovered server by name
          text: |
            az migrate get-discovered-server \\
                --project-name myMigrateProject \\
                --resource-group myRG \\
                --name machine-12345
        - name: Filter discovered servers by display name
          text: |
            az migrate get-discovered-server \\
                --project-name myMigrateProject \\
                --resource-group myRG \\
                --display-name "web-server"
        - name: List VMware servers discovered by a specific appliance
          text: |
            az migrate get-discovered-server \\
                --project-name myMigrateProject \\
                --resource-group myRG \\
                --appliance-name myVMwareAppliance \\
                --source-machine-type VMware
        - name: Get a specific server from a specific appliance
          text: |
            az migrate get-discovered-server \\
                --project-name myMigrateProject \\
                --resource-group myRG \\
                --appliance-name myAppliance \\
                --name machine-12345 \\
                --source-machine-type HyperV
"""

helps['migrate local replication'] = """
    type: group
    short-summary: Manage replication for Azure Local/Stack HCI migrations.
    long-summary: |
        Commands to initialize replication infrastructure
        and create new server replications
        for migrations to Azure Local and Azure Stack HCI environments.
"""

helps['migrate local replication init'] = """
    type: command
    short-summary: Initialize Azure Migrate local replication infrastructure.
    long-summary: |
        Initialize the replication infrastructure required for
        migrating servers to Azure Local or Azure Stack HCI.
        This command sets up the necessary fabrics, policies, and mappings
        between source and target appliances.
        This is a prerequisite before creating any server replications.

        Note: This command uses a preview API version and
        may experience breaking changes in future releases.
    parameters:
        - name: --project-name
          short-summary: Name of the Azure Migrate project.
          long-summary: >
            The Azure Migrate project to be used
            for server migration.
        - name: --source-appliance-name
          short-summary: Source appliance name.
          long-summary: >
            Name of the Azure Migrate appliance that
            discovered the source servers.
        - name: --target-appliance-name
          short-summary: Target appliance name.
          long-summary: >
            Name of the Azure Local appliance that
            will host the migrated servers.
        - name: --subscription-id
          short-summary: Azure subscription ID.
          long-summary: >
            The subscription containing the Azure Migrate project.
            Uses the current subscription if not specified.
        - name: --pass-thru
          short-summary: Return true when the command succeeds.
          long-summary: >
            When enabled, returns a boolean value
            indicating successful completion.
    examples:
        - name: Initialize replication infrastructure
          text: |
            az migrate local replication init \\
                --resource-group myRG \\
                --project-name myMigrateProject \\
                --source-appliance-name myVMwareAppliance \\
                --target-appliance-name myAzStackHCIAppliance
        - name: Initialize and return success status
          text: |
            az migrate local replication init \\
                --resource-group myRG \\
                --project-name myMigrateProject \\
                --source-appliance-name mySourceAppliance \\
                --target-appliance-name myTargetAppliance \\
                --pass-thru
"""

helps['migrate local replication new'] = """
    type: command
    short-summary: Create a new replication for an Azure Local server.
    long-summary: |
        Create a new replication to migrate a discovered server to Azure Local.
        You can specify the source machine either
        by its ARM resource ID or by selecting it from
        a numbered list of discovered servers.

        The command supports two modes:
        - Default User Mode: Specify os-disk-id and target-virtual-switch-id
        - Power User Mode: Specify disk-to-include and nic-to-include

        Note: This command uses a preview API version
        and may experience breaking changes in
        future releases.
    parameters:
        - name: --machine-id
          short-summary: ARM resource ID of the discovered server to migrate.
          long-summary: >
            Full ARM resource ID of the discovered machine.
            Required if --machine-index is not provided.
        - name: --machine-index
          short-summary: Index of the discovered server from the list
          long-summary: >
            Select a server by its position
            in the discovered servers list.
            Required if --machine-id is not provided.
        - name: --project-name
          short-summary: Name of the Azure Migrate project.
          long-summary: >
            Required when using --machine-index
            to identify which project to query.
        - name: --target-storage-path-id
          short-summary: Storage path ARM ID where VMs will be stored.
          long-summary: >
            Full ARM resource ID of the storage path
            on the target Azure Local cluster.
        - name: --target-vm-cpu-core
          short-summary: Number of CPU cores for the target VM.
          long-summary: >
            Specify the number of CPU cores
            to allocate to the migrated VM.
        - name: --target-vm-ram
          short-summary: Target RAM size in MB.
          long-summary: >
            Specify the amount of RAM to
            allocate to the target VM in megabytes.
        - name: --disk-to-include
          short-summary: Disks to include for replication (power user mode).
          long-summary: >
            Space-separated list of disk IDs
            to replicate from the source server.
            Use this for power user mode.
        - name: --nic-to-include
          short-summary: NICs to include for replication (power user mode).
          long-summary: >
            Space-separated list of NIC IDs
            to replicate from the source server.
            Use this for power user mode.
        - name: --target-vm-name
          short-summary: Name of the VM to be created.
          long-summary: >
            The name for the virtual machine
            that will be created on the target environment.
        - name: --os-disk-id
          short-summary: Operating system disk ID.
          long-summary: >
            ID of the operating system disk for
            the source server. Required for default user mode.
        - name: --source-appliance-name
          short-summary: Source appliance name.
          long-summary: >
            Name of the Azure Migrate appliance
            that discovered the source server.
        - name: --target-appliance-name
          short-summary: Target appliance name.
          long-summary: >
            Name of the Azure Local appliance
            that will host the migrated server.
        - name: --subscription-id
          short-summary: Azure subscription ID.
          long-summary: >
            The subscription to use.
            Uses the current subscription if not specified.
    examples:
        - name: Create replication using machine ARM ID (default user mode)
          text: |
            az migrate local replication new \\
                --machine-id "XXXX" \\
                --target-storage-path-id "YYYY" \\
                --target-resource-group-id "ZZZZ" \\
                --target-vm-name migratedVM01 \\
                --source-appliance-name myVMwareAppliance \\
                --target-appliance-name myAzStackHCIAppliance \\
                --target-virtual-switch-id "XYXY" \\
                --os-disk-id "disk-0"
        - name: Create replication using machine index (power user mode)
          text: |
            az migrate local replication new \\
                --machine-index 1 \\
                --project-name myMigrateProject \\
                --resource-group myRG \\
                --target-storage-path-id "XZXZ" \\
                --target-resource-group-id "YZYZ" \\
                --target-vm-name migratedVM01 \\
                --source-appliance-name mySourceAppliance \\
                --target-appliance-name myTargetAppliance \\
                --disk-to-include "disk-0" "disk-1" \\
                --nic-to-include "nic-0"
        - name: Create replication with custom CPU and RAM settings
          text: |
            az migrate local replication new \\
                --machine-id "XXXX" \\
                --target-storage-path-id "YYYY" \\
                --target-resource-group-id "ZZZZ" \\
                --target-vm-name migratedVM01 \\
                --source-appliance-name mySourceAppliance \\
                --target-appliance-name myTargetAppliance \\
                --target-virtual-switch-id "XYXY" \\
                --os-disk-id "disk-0" \\
                --target-vm-cpu-core 4 \\
                --target-vm-ram 8192 \\
                --is-dynamic-memory-enabled false
        - name: Create replication with test virtual switch
          text: |
            az migrate local replication new \\
                --machine-id "XXXX" \\
                --target-storage-path-id "YYYY" \\
                --target-resource-group-id "ZZZZ" \\
                --target-vm-name migratedVM01 \\
                --source-appliance-name mySourceAppliance \\
                --target-appliance-name myTargetAppliance \\
                --target-virtual-switch-id "XYXY" \\
                --target-test-virtual-switch-id "XYXY" \\
                --os-disk-id "disk-0"
"""

helps['migrate local replication list'] = """
    type: command
    short-summary: List all protected items (replicating servers) in a project.
    long-summary: |
        Lists all servers that have replication enabled
        in an Azure Migrate project.
        This command shows the replication status, health,
        and configuration details for each protected server.

        The command returns information including:
        - Protection state (e.g., Protected, ProtectedReplicating, EnablingFailed)
        - Replication health (Normal, Warning, Critical)
        - Source machine name and target VM name
        - Replication policy name
        - Resource IDs (used for remove command)
        - Health errors if any

        Note: This command uses a preview API version
        and may experience breaking changes in future releases.
    parameters:
        - name: --resource-group -g
          short-summary: Resource group containing the Azure Migrate project.
          long-summary: >
            The name of the resource group where
            the Azure Migrate project is located.
        - name: --project-name
          short-summary: Name of the Azure Migrate project.
          long-summary: >
            The Azure Migrate project that contains
            the replicating servers.
        - name: --subscription-id
          short-summary: Azure subscription ID.
          long-summary: >
            The subscription containing the Azure Migrate project.
            Uses the default subscription if not specified.
    examples:
        - name: List all replicating servers in a project
          text: |
            az migrate local replication list \\
                --resource-group myRG \\
                --project-name myMigrateProject
        - name: List replicating servers with a specific subscription
          text: |
            az migrate local replication list \\
                --resource-group myRG \\
                --project-name myMigrateProject \\
                --subscription-id 00000000-0000-0000-0000-000000000000
"""

helps['migrate local replication get'] = """
    type: command
    short-summary: Get detailed information about a specific replicating server.
    long-summary: |
        Retrieves comprehensive details about a specific protected item (replicating server)
        including its protection state, replication health, configuration settings,
        and historical information about failover operations.

        You can retrieve the protected item either by:
        - Full ARM resource ID (--protected-item-id or --id)
        - Name with project context (--protected-item-name with --resource-group and --project-name)

        The command returns detailed information including:
        - Basic information (name, resource ID, correlation ID)
        - Protection status (state, health, resync requirements)
        - Configuration (policy, replication extension)
        - Failover history (test, planned, unplanned)
        - Allowed operations
        - Machine details (source and target information)
        - Health errors with recommended actions (if any)

        Note: This command uses a preview API version
        and may experience breaking changes in future releases.
    parameters:
        - name: --protected-item-id
          short-summary: Full ARM resource ID of the protected item.
          long-summary: >
            The complete ARM resource ID of the protected item.
            If provided, --resource-group and --project-name are not required.
            This ID can be obtained from the 'list' or 'new' commands.
        - name: --protected-item-name
          short-summary: Name of the protected item (replicating server).
          long-summary: >
            The name of the protected item to retrieve.
            When using this option, both --resource-group and --project-name
            are required to locate the item.
        - name: --resource-group -g
          short-summary: Resource group containing the Azure Migrate project.
          long-summary: >
            The name of the resource group where the Azure Migrate project is located.
            Required when using --protected-item-name.
        - name: --project-name
          short-summary: Name of the Azure Migrate project.
          long-summary: >
            The Azure Migrate project that contains the replicating server.
            Required when using --protected-item-name.
        - name: --subscription-id
          short-summary: Azure subscription ID.
          long-summary: >
            The subscription containing the Azure Migrate project.
            Uses the default subscription if not specified.
    examples:
        - name: Get a protected item by its full ARM resource ID
          text: |
            az migrate local replication get \\
                --protected-item-id "/subscriptions/xxxx/resourceGroups/myRG/providers/Microsoft.DataReplication/replicationVaults/myVault/protectedItems/myItem"
        - name: Get a protected item by name using project context
          text: |
            az migrate local replication get \\
                --protected-item-name myProtectedItem \\
                --resource-group myRG \\
                --project-name myMigrateProject
        - name: Get a protected item with specific subscription
          text: |
            az migrate local replication get \\
                --name myProtectedItem \\
                --resource-group myRG \\
                --project-name myMigrateProject \\
                --subscription-id 00000000-0000-0000-0000-000000000000
        - name: Get a protected item using short parameter names
          text: |
            az migrate local replication get \\
                --id "/subscriptions/xxxx/resourceGroups/myRG/providers/Microsoft.DataReplication/replicationVaults/myVault/protectedItems/myItem"
"""

helps['migrate local replication remove'] = """
    type: command
    short-summary: Stop replication for a migrated server.
    long-summary: |
        Stops the replication for a migrated server and removes
        the replication configuration.
        This command disables protection for the specified server.

        Note: This command uses a preview API version
        and may experience breaking changes in future releases.
    parameters:
        - name: --target-object-id
          short-summary: Replicating server ARM ID to disable replication.
          long-summary: >
            Specifies the ARM resource ID of the replicating server
            for which replication needs to be disabled.
            The ID should be retrieved using a get or list command
            for replication items.
        - name: --force-remove
          short-summary: Force remove the replication.
          long-summary: >
            Specifies whether the replication needs to be
            force removed. Default is false.
            Use this option to remove replication even if
            the cleanup process encounters errors.
        - name: --subscription-id
          short-summary: Azure subscription ID.
          long-summary: >
            The subscription containing the replication resources.
            Uses the current subscription if not specified.
    examples:
        - name: Stop replication for a migrated server
          text: |
            az migrate local replication remove \\
                --target-object-id "XXXX"
        - name: Force remove replication for a server
          text: |
            az migrate local replication remove \\
                --target-object-id "XXXX" \\
                --force-remove true
        - name: Stop replication using short parameter names
          text: |
            az migrate local replication remove \\
                --id "XXXX" \\
                --force
"""

helps['migrate local replication get-job'] = """
    type: command
    short-summary: Retrieve the status of an Azure Migrate job.
    long-summary: |
        Get the status and details of an Azure Migrate replication job.
        You can retrieve a specific job by its ARM ID or name,
        or list all jobs in a migrate project.

        Note: This command uses a preview API version
        and may experience breaking changes in future releases.
    parameters:
        - name: --job-id
          short-summary: Job ARM ID for which details need to be retrieved.
          long-summary: >
            Specifies the full ARM resource ID of the job.
            When provided, retrieves the specific job details.
        - name: --resource-group -g
          short-summary: Resource group name where the vault is present.
          long-summary: >
            The name of the resource group containing
            the recovery services vault.
            Required when using --project-name.
        - name: --project-name
          short-summary: Name of the migrate project.
          long-summary: >
            The name of the Azure Migrate project.
            Required when using --resource-group.
        - name: --job-name
          short-summary: Job identifier/name.
          long-summary: >
            The name of the specific job to retrieve.
            If not provided, lists all jobs in the project.
        - name: --subscription-id
          short-summary: Azure subscription ID.
          long-summary: >
            The subscription containing the migrate project.
            Uses the current subscription if not specified.
    examples:
        - name: Get a specific job by ARM ID
          text: |
            az migrate local replication get-job \\
                --job-id "/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.DataReplication/replicationVaults/{vault}/jobs/{job-name}"
        - name: Get a specific job by name
          text: |
            az migrate local replication get-job \\
                --resource-group myRG \\
                --project-name myMigrateProject \\
                --job-name myJobName
        - name: List all jobs in a project
          text: |
            az migrate local replication get-job \\
                --resource-group myRG \\
                --project-name myMigrateProject
        - name: Get job using short parameter names
          text: |
            az migrate local replication get-job \\
                --id "/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.DataReplication/replicationVaults/{vault}/jobs/{job-name}"
        - name: Get job with specific subscription
          text: |
            az migrate local replication get-job \\
                -g myRG \\
                --project-name myMigrateProject \\
                --name myJobName \\
                --subscription-id "12345678-1234-1234-1234-123456789012"
"""

helps['migrate local start-migration'] = """
    type: command
    short-summary: Start migration for a replicating server to Azure Local.
    long-summary: |
        Initiates the migration (failover) process for a server that
        has been configured for replication to Azure Local or Azure Stack HCI.
        This command triggers the final migration step, which creates
        the virtual machine on the target Azure Local/Stack HCI environment.

        The protected item must be in a healthy replication state
        before migration can be initiated.
        You can optionally specify whether to turn off the source server
        after migration completes.

        Note: This command uses a preview API version
        and may experience breaking changes in future releases.
    parameters:
        - name: --protected-item-id
          short-summary: Full ARM resource ID of the protected item to migrate.
          long-summary: >
            The complete ARM resource ID of the replicating server.
            This ID can be obtained from the 'az migrate local replication list'
            or 'az migrate local replication get' commands.
            Required parameter.
        - name: --turn-off-source-server
          short-summary: Turn off the source server after migration.
          long-summary: >
            Specifies whether the source server should be powered off
            after the migration completes successfully.
            Default is False. Use this option to automatically shut down
            the source server to prevent conflicts.
        - name: --subscription-id
          short-summary: Azure subscription ID.
          long-summary: >
            The subscription containing the migration resources.
            Uses the current subscription if not specified.
    examples:
        - name: Start migration for a protected item
          text: |
            az migrate local start-migration \\
                --protected-item-id "/subscriptions/xxxx/resourceGroups/myRG/providers/Microsoft.DataReplication/replicationVaults/myVault/protectedItems/myItem"
        - name: Start migration and turn off source server
          text: |
            az migrate local start-migration \\
                --protected-item-id "/subscriptions/xxxx/resourceGroups/myRG/providers/Microsoft.DataReplication/replicationVaults/myVault/protectedItems/myItem" \\
                --turn-off-source-server
        - name: Start migration using short parameter names
          text: |
            az migrate local start-migration \\
                --id "/subscriptions/xxxx/resourceGroups/myRG/providers/Microsoft.DataReplication/replicationVaults/myVault/protectedItems/myItem" \\
                --turn-off-source-server
        - name: Start migration with specific subscription
          text: |
            az migrate local start-migration \\
                --protected-item-id "/subscriptions/xxxx/resourceGroups/myRG/providers/Microsoft.DataReplication/replicationVaults/myVault/protectedItems/myItem" \\
                --subscription-id "12345678-1234-1234-1234-123456789012"
"""
