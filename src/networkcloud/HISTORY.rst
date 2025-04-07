.. :changelog:

Release History
===============

3.0.0
++++++++
* This stable version supports NetworkCloud 2025-02-01 APIs.
* Concurency control parameters have been introduced and include `ETag` property on resources and the ability to pass it via `--if-match` or `--if-none-match` parameters to create and update commands.
* Alias `--mrg` is added to the `--managed-resource-group-configuration` parameter of the Cluster and Cluster Manager create commands for convenience.

3.0.0b1
++++++++
* This beta version supports NetworkCloud 2024-10-01-preview APIs.
* This version requires a minimum of 2.67 Azure core CLI. See release notes for more details: https://github.com/MicrosoftDocs/azure-docs-cli/blob/main/docs-ref-conceptual/release-notes-azure-cli.md
* This version upgrades the internal generation tool aaz-dev-tools to 3.2.0. Refer to the release notes for more details: https://github.com/Azure/aaz-dev-tools/releases/tag/v3.2.0.
* A bug fix for delete commands returning 204 without content is included in this release.
* New `identity` command group is added to Cluster Manager for handling system-assigned and user-assigned identity updates.
* Breaking change: Cluster create and update commands support new parameter `--analytics-output-settings` for configuring Log Analytics Workspace, which replaces the deprecated `--analytics-workspace-id`.
* Breaking change: Cluster create and update commands support new parameter `--secret-archive-settings` to hold credentials for the cluster, which replaces the deprecated `--secret-archive`.
* Cluster includes `--vulnerability-scanning-settings`, featuring a single field called containerScan, which determines how security vulnerability scanning is applied to the cluster.
* VirtualMachine is updated to display the extended location to use for creation of a VirtualMachine console resource.
* VirtualMachine is updated to support persistent storage for OS disk.
* VirtualMachine's property `--vm-device-model` gets a new option 'T3'. When 'T3' is selected, SecureBoot and vTPM are automatically enabled. This is to support Windows users.
* Eliminated password fields from Infrastructure resources (Cluster, BMM, Storage Appliance)

2.0.0
++++++++
* This is the stable version of the CLI extension that supports NetworkCloud 2024-07-01 APIs.
* Additional validation is added to Cluster create and update commands for the containerUrl child property within the `--command-output-settings`.

2.0.0b7
++++++++
* This version requires a minimum of 2.66 Azure core CLI. See release notes for more details: https://github.com/MicrosoftDocs/azure-docs-cli/blob/main/docs-ref-conceptual/release-notes-azure-cli.md
* This version upgrades the internal generation tool aaz-dev-tools to 3.1.0. Refer to the release notes for more details: https://github.com/Azure/aaz-dev-tools/releases/tag/v3.1.0.
* Optional Cluster properties can be now set to null during update (PATCH) operation. This includes `--cluster-service-principal`, `--command-output-settings`, `--compute-deployment-threshold`, `--update-strategy`, `--secret-archive`, and `--runtime-protection`. In that case, the value will be reset to the default if defined by the API.
* This version introduces custom code to validate the `--command-output-settings` property of a cluster for both create and update operations. When the `identity-type` is `SystemAssignedIdentity`, the UAI(User Assigned Identity) should not be provided and will be set to None to erase any previous value. When the `identity-type` is `UserAssignedIdentity`, the UAI must be provided.

2.0.0b6
++++++++
* This is a maintenace update to the internal auto-generation tools (3.0.0) to ensure compatibility with the Python 3.12. 

2.0.0b5
++++++++
* This version updates the baremetalmachine resource commands (run-command, run-read-command, and run-data-extract) to utilize a customer-provided Storage Account for storing command execution results.

2.0.0b4
++++++++
* This beta version supports NetworkCloud 2024-07-01 APIs.

2.0.0b3
++++++++
* This beta version supports NetworkCloud 2024-06-01-preview APIs.
* Note is added regarding Virtual machine memory and disk size being in gibibytes. Avoid using property names `--memory-size-gb` and `--disk-size-gb`.
* New functionality supported in this release:
  * ClusterManager commands are updated with custom parameters --mi-system-assigned --mi-user-assigned to support managing identity.
  * Cluster commands are updated with custom parameters --mi-system-assigned --mi-user-assigned to support managing identity.
  * Cluster can now configure a storage account that will be used for downloading BareMetalMachine command execution results.
  * Cluster rack pause functionality support is added with the new command `continue-update-version`.
  * KubernetesCluster feature commands are added to manage addons for the Kubernetes cluster.
  * BareMetalMachines and StorageAppliance are updated with new properties for secret rotation status.
  * KubernetesClusters commands are enhanced to support an alternative load balancer configuration that represents an L2 load balancer in property `l2ServiceLoadBalancerConfiguration`.
  * KubernetesClusters commands are enhanced to support additional upgrade settings `drainTimeout` and `maxUnavailable` for initial agent pools.
  * KubernetesClusters agentpool commands are enhanced to support additional upgrade settings `drainTimeout` and `maxUnavailable`.
* This version requires a minimum of 2.61 Azure core CLI.

2.0.0b2
++++++++
* Examples updated to include new property user-principal-name for baremetalmachinekeyset and bmckeyset create and update commands.

2.0.0b1
++++++++
* This beta version supports NetworkCloud 2023-10-01-preview APIs.
* Format restrictions and resource type validations are added to fields that represent ARM ID resources.
* New functionality supported in this release:
  * New configuration is added to cluster create and update commands for runtime protection scan, secret archive, and cluster update strategy.
  * New Cluster command scan-runtime is added to trigger the execution of a runtime protection scan.
  * baremetalmachine returns new properties with runtime protection status.
  * Additional status "Disconnected" is added to clusterConnectionStatus.
  * kubernetescluster update command allows modification of SSH keys for cluster administrator and control plane administrator.
  * kubernetescluster agentpool update command allows modification of SSH keys for the agent pool administrator.
* This version requires a minimum of 2.51 Azure core CLI.
* This version upgrades the internal generation tool aaz-dev-tools to 1.8.0. Refer to the release notes for more details: https://github.com/Azure/aaz-dev-tools/releases/tag/v1.8.0.

1.1.0
++++++++
* This version removes the experimental commands for defaultcninetwork and hybridakscluster as these resources are no longer available.

1.0.0
++++++++
* This is the first stable version of the CLI extension that supports NetworkCloud 2023-07-01 stable APIs.
* Virtualmachine console create and update commands have been enhanced to accept a file path for ssh_public_key parameter.

1.0.0b1
++++++++
* This is first beta version of the CLI extension that supports NetworkCloud 2023-07-01 stable APIs.
* The defaultcninetwork and hybridakscluster resources are no longer available.

0.4.1
++++++
* This version updates the kubernetescluster resource to not send an empty array `sshPubKeys` for control plane configuration and agent pool configuration if the input contains no ssh keys provided for these parameters.
* This version updates the agentpool child resource of kubernetescluster to not send an empty array `sshPubKeys` is not provided in the input.

0.4.0
++++++
* This version supports NetworkCloud 2023-05-01-preview APIs.
* It introduces a new resource kubernetescluster and its child resource agentpool.
* The defaultcninetwork and hybridakscluster resources are preserved and will continue using 2022-12-12-preview APIs.
* This version is experimental. Changes to the interface are expected but will be done in backward compatible way where possible.

0.3.0
++++++
* Initial release. This version supports NetworkCloud 2022-12-12-preview APIs.
* This version is experimental. Changes to the interface are expected but will be done in backward compatible way where possible.
