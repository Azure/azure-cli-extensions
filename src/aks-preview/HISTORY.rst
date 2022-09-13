.. :changelog:

Release History
===============

Guidance
++++++++
If there is no rush to release a new version, please just add a description of the modification under the *Pending* section.

To release a new version, please select a new version number (usually plus 1 to last patch version, X.Y.Z -> Major.Minor.Patch, more details in `\doc <https://semver.org/>`_), and then add a new section named as the new version number in this file, the content should include the new modifications and everything from the *Pending* section. Finally, update the `VERSION` variable in `setup.py` with this new version number.

Pending
+++++++

* Update to use 2022-08-02-preview api version.

0.5.100
+++++++

* Remove unused import to avoid failure in Python3.6, see issue `\#5303 <https://github.com/Azure/azure-cli-extensions/issues/5303>`_.

0.5.99
++++++

* Fix DRAFT CLI to 0.0.22.
* Fix the URL for Download.

0.5.98
++++++

* Fix auto download issue for Draft CLI.
* Remove host and certificates as draft tools update command no longer uses it.

0.5.97
++++++

* Add support for apiserver vnet integration public cluster.

0.5.96
++++++

* Add support for enabling ImageCleaner with `--enable-image-cleaner` flag.
* Add sub-command `operation-abort` for `az aks` and `az aks nodepool` to support canceling the previous operation.

0.5.95
++++++

* Add `--enable-node-restriction`/`--disable-node-restriction` to enable/disable node restriction feature
* Update the minimum required cli core version to `2.38.0` (actually since `0.5.92`).
* Add new value `Mariner` for option `--os-sku` in `az aks create` and `az aks nodepool add`.

0.5.94
++++++

* [BREAKING CHANGE] Since the service no longer supports updating source resource id for role binding, so remove --source-resource-id of `aks trustedaccess rolebinding update` command.
* Change the acceptable values of the `--roles` option to comma-seperated.
    * az aks trustedaccess rolebinding create
    * az aks trustedaccess rolebinding update
* Upgrade `az aks kollect` command to use Periscope version 0.0.10 supporting enhanced Windows log collection.
* Update to use 2022-07-02-preview api version.

0.5.93
++++++

* Fix for "'Namespace' object has no attribute 'nodepool_name' error" in command `az aks nodepool wait`, see issue `\#23468 <https://github.com/Azure/azure-cli/issues/23468>`_.

0.5.92
++++++

* Move Azure KeyVault KMS to GA.
* Support disabling Azure KeyVault KMS.
* Update to use 2022-06-02-preview api version.

0.5.91
++++++

* Fix compatibility issue when enabling Microsoft Defender via aks-preview.
    * az aks create
    * az aks update

0.5.90 (NOT RELEASED)
+++++++++++++++++++++

* Skip this version due to conflict.

0.5.89
++++++

* Fix for the az aks addon list command to return enable:true, if virtual-node addon is enabled for the AKS cluster.

0.5.88
++++++

* AKS Monitoring MSI Auth related code imported from Azure CLI to reuse the code between aks-preview and Azure CLI.

0.5.87
++++++

* Fix snapshot not resolved according to the subscriptions field in the `--snapshot-id`` option.

0.5.86
++++++

* Support network plugin mode for enabling Azure CNI Overlay preview feature.

0.5.85
++++++

* Add support for Blob csi driver.

0.5.84 (NOT RELEASED)
+++++++++++++++++++++

* Skip this version due to conflict.

0.5.83
++++++

* Update the minimum required cli core version to `2.37.0`.
* Enable v2 decorator pattern.
* Fix container name inconsistency for private clusters in kollect command.
* Temp fix for properties missing in KMS profile in update scenario.

0.5.82
++++++

* Support Key Vault with private link when enabling Azure KeyVault KMS.

0.5.81
++++++

* Add Trusted Access Role Binding commands
    * az aks trustedaccess rolebinding create
    * az aks trustedaccess rolebinding update
    * az aks trustedaccess rolebinding list
    * az aks trustedaccess rolebinding show
    * az aks trustedaccess rolebinding delete
* Fix: Remove permission prompt when saving config file to symlink with `az aks get-credentials`.

0.5.80
++++++

* Fix the value of option --zones not being transmitted correctly for `az aks nodepool add`, see issue `\#4953 <https://github.com/Azure/azure-cli-extensions/issues/4953>`_.

0.5.79
++++++

* Add support for KEDA workload auto-scaler.
* Fix `az aks addon list`, `az aks addon list-available` and `az aks addon show` commands when dealing with the web application routing addon.
* Update to use 2022-05-02-preview api version.

0.5.78
++++++

* Prompt when disabling CSI Drivers.

0.5.77
++++++

* Add support to pass csi `disk-driver-version` for `az aks create` and `az aks update`.

0.5.76
++++++

* Add support for Custom CA Trust in `az aks create`, `az aks nodepool add`, `az aks nodepool update`.

0.5.75
++++++

* Add support for web application routing.
* Refactor: Removed redundant `--disable-workload-identity` flag. User can disable the workload identity feature by using `--enable-workload-identity False`.

0.5.74
++++++

* Add command `aks trustedaccess role list`.

0.5.73
++++++

* Fix import issues with command group `az aks draft`

0.5.72 (NOT RELEASED)
+++++++++++++++++++++

* First public release for `az aks draft`

0.5.71
++++++

* Fix: Updated validators for options --min-count and --max-count to support specifying values greater than 100. Related commands are
    * `az aks create`
    * `az aks update`
    * `az aks nodepool add`
    * `az aks nodepool update`

0.5.70
++++++

* Fix: Don't update storageProfile if not set.

0.5.69
++++++

* Fix: Raise error when user provides invalid value for `--os-sku`.

0.5.68
++++++

* Add option `Windows2019`, `Windows2022` to `--os-sku` for `az aks nodepool add`.

0.5.67
+++++++++++++++++++++

* Update the minimum required cli core version to `2.35.0`.
* Update to use 2022-04-02-preview api version.
* Add support for csi drivers extensibility.
* Add support for apiserver vnet integration.

0.5.66
++++++

* Prompt when no arguments are given to update and nodepool update to see if the customer wants to try goal seek to current settings.

0.5.65
++++++

* Add `--ignore-pod-disruption-budget` flag for `az aks nodepool delete` for ignoring PodDisruptionBudget.

0.5.64
++++++

* Add support for updating kubelet identity. Command is
    * `az aks update --assign-kubelet-identity <kubelelt-identity-resource-id>`

0.5.63
++++++

* Add support to create cluster with managed cluster snapshot. Command is
    * `az aks create --cluster-snapshot-id <snapshot-id>`

0.5.62
++++++

* Add support for managing workload identity feature.

0.5.61
++++++

* Update to use 2022-03-02-preview api version.
* Add support for `--format` parameter in `az aks get-credentials` command.

0.5.60
++++++

* BugFix: Keep aad profile in PUT request of ManagedCluster. Modified commands are
    * `az aks scale`
    * `az aks upgrade`
    * `az aks enable-addons`
    * `az aks disable-addons`
    * `az aks addon enable`
    * `az aks addon disable`
    * `az aks addon update`

0.5.59
++++++

* Add support for managed cluster snapshot commands and modify current nodepool snapshot commands.
* Breaking Change: `az aks nodepool snapshot` will be the command to manage nodepool snapshot. `az aks snapshot` is used for managed cluster snapshot instead.

  More specifically, for managed cluster snapshot, it will be

    * `az aks snapshot create`
    * `az aks snapshot delete`
    * `az aks snapshot list`
    * `az aks snapshot show`

  For nodepool snapshot, it will be

    * `az aks nodepool snapshot create`
    * `az aks nodepool snapshot delete`
    * `az aks nodepool snapshot list`
    * `az aks nodepool snapshot show`

0.5.58
++++++

* Update to use 2022-02-02-preview api version.
* Add support for enabling Azure KeyVault KMS with `--enable-azure-keyvault-kms` flag.

0.5.57
++++++

* Add support for updating HTTP proxy configuration via `az aks update --http-proxy-config file.json`.

0.5.56
++++++

* Add `--message-of-the-day` flag for `az aks create` and `az aks nodepool add` for Linux message of the day.

0.5.55
++++++

* Add option `none` to `--network-plugin` parameter to skip CNI installation during cluster creation.

0.5.54
++++++

* Add --host-group-id to `az aks create` and `az aks nodepool add` commands to support Azure Dedicated Host Group, which requires registering the feature flag "Microsoft.ContainerService/DedicatedHostGroupPreview".
    * `az aks create --host-group-id`
    * `az aks nodepool add --host-group-id`

0.5.53
++++++

* Update the minimum required cli core version to `2.32.0`.
* Update to use 2022-01-02-preview api version.
* Add support for cluster creating with Capacity Reservation Group.
    * `az aks create --crg-id`
* Add support for nodepool adding with Capacity Reservation Group.
    * `az aks nodepool add --crg-id`

0.5.52
++++++

* Add yaml template files to package data to fix issue `\#148 <https://github.com/Azure/aks-periscope/issues/148>`_.
* Add support for using empty string to remove existing nodepool label by `az aks update --nodepool-labels` or `az aks nodepool update --labels`.
* Add support for using empty string to remove existing node taints by `az nodepool update --node-taints`.
* Correct the option for time control in `maintenanceconfiguration` series commands to `hourSlot`.
* GA (General Availability) for the snapshot feature.

0.5.51
++++++

* Add currentKubernetesVersion column for `az aks show --output table`.

0.5.50
++++++

* Add support for enabling OIDC issuer with `--enable-oidc-issuer` flag.

0.5.49
++++++

* Update the minimum required cli core version to `2.31.0`.
* Add support for Alias Minor Version.

0.5.48
++++++

* Fix: `aks update` issue with load balancer profile defaults being set when CLI arguments only include outbound IPs or outbound prefixes.

0.5.47
++++++

* Add support for IPv4/IPv6 dual-stack networking AKS clusters. Commands is
    * `az aks create --pod-cidrs --service-cidrs --ip-families --load-balancer-managed-outbound-ipv6-count`.

0.5.46
++++++

* Update to use 2021-10-01 api-version.

0.5.45
++++++

* Update the minimum required cli core version to `2.30.0`.
* Remove the snapshot name trimming in `az aks snapshot create` command.

0.5.44
++++++

* In AKS Monitoring addon, fix DCR resource naming convention from DCR-<workspaceName> to MSCI-<workspaceName> to make consistent naming across.

0.5.43 (NOT RELEASED)
+++++++++++++++++++++

* Enable the new implementation in command `aks create`.

0.5.42
++++++

* Update the minimum required cli core version to `2.27.0`.
* Fix default value behavior for pod identity exception pod labels in upgrade/scale calls.

0.5.41
++++++

* Fix default value behavior for pod identity exception pod labels.

0.5.40
++++++

* Update the minimum required cli core version to `2.23.0`.
* Add support for new snapshot commands.
    * `az aks snapshot create`
    * `az aks snapshot delete`
    * `az aks snapshot list`
    * `az aks snapshot show`
* Add --snapshot-id to creating/upgrading commands.
    * `az aks create --snapshot-id`
    * `az aks nodepool add --snapshot-id`
    * `az aks nodepool upgrade --snapshot-id`

0.5.39
++++++

* Add commands for agentpool start stop feature.

0.5.38
++++++

* Add parameter `--rotation-poll-interval` for Azure Keyvault Secrets Provider Addon.

0.5.37
++++++

* Add Windows gMSA v2 support. Add parameters `--enable-windows-gmsa`, `--gmsa-dns-server` and `--gmsa-root-domain-name`.

0.5.36
++++++

* Update to use 2021-09-01 api-version.

0.5.35
++++++

* Add support for multi-instance GPU configuration (`--gpu_instance_profile`) in `az aks create` and `az aks nodepool add`.

0.5.34
++++++

* Add support for WASM nodepools (`--workload-runtime WasmWasi`) in `az aks create` and `az aks nodepool add`.

0.5.33
++++++

* Add support for new addon commands
    * `az aks addon list`
    * `az aks addon list-available`
    * `az aks addon show`
    * `az aks addon enable`
    * `az aks addon disable`
    * `az aks addon update`
* Refactored code to bring addon specific functionality into a separate file.

0.5.32
++++++

* Update to use 2021-08-01 api-version.

0.5.31
++++++

* Add support for new outbound types: 'managedNATGateway' and 'userAssignedNATGateway'.

0.5.30
++++++

* Add preview support for setting scaleDownMode field on nodepools. Requires registering the feature flag "Microsoft.ContainerService/AKS-ScaleDownModePreview" for setting the value to "Deallocate".

0.5.29
++++++

* Fix update (failed due to "ERROR: (BadRequest) Feature Microsoft.ContainerService/AutoUpgradePreview is not enabled" even when autoupgrade was not specified).
* Add podMaxPids argument for kubelet-config.

0.5.28
++++++

* Update to adopt 2021-07-01 api-version.

0.5.27
++++++

* GA private cluster public FQDN feature, breaking change to replace create parameter `--enable-public-fqdn` with `--disable-public-fqdn` since now it's enabled by default for private cluster during cluster creation.

0.5.26
++++++

* Correct containerLogMaxSizeMb to containerLogMaxSizeMB in customized kubelet config.

0.5.25
++++++

* Add support for http proxy.

0.5.24
++++++

* * Add "--aks-custom-headers" for "az aks nodepool upgrade".

0.5.23
++++++

* Fix issue that `maintenanceconfiguration add` subcommand cannot work.

0.5.22
++++++

* Fix issue in dcr template.

0.5.21
++++++

* Fix issue when disable monitoring on an AKS cluster would fail in regions where Data Collection Rules are not enabled

0.5.20
++++++

* Support enabling monitoring on AKS clusters with msi auth
* Add `--enable-msi-auth-for-monitoring` option in aks create and aks enable-addons

0.5.19
++++++

* Remove azure-defender from list of available addons to install via `az aks enable-addons` command

0.5.18
++++++

* Fix issue with node config not consuming logging settings

0.5.17
++++++

* Add parameter '--enable-ultra-ssd' to enable UltraSSD on agent node pool

0.5.16
++++++

* Vendor SDK using latest swagger with optional query parameter added
* Support private cluster public fqdn feature

0.5.15
++++++

* Update to use 2021-05-01 api-version.

0.5.14
++++++

* Add os-sku argument for cluster and nodepool creation

0.5.13
++++++

* Add compatible logic for the track 2 migration of resource dependence

0.5.12
++++++

* Add --enable-azure-rbac and --disable-azure-rbac in aks update
* Support disabling local accounts
* Add addon `azure-defender` to list of available addons under `az aks enable-addons` command

0.5.11
++++++

* Add get OS options support
* Fix wrong behavior when enabling pod identity addon for cluster with addon enabled

0.5.10
++++++

* Add `--binding-selector` to AAD pod identity add sub command
* Support using custom kubelet identity
* Support updating Windows password
* Add FIPS support to CLI extension

0.5.9
+++++

* Display result better for `az aks command invoke`, while still honor output option
* Fix the bug that checking the addon profile whether it exists

0.5.8
+++++

* Update to use 2021-03-01 api-version

0.5.7
+++++

* Add command invoke for run-command feature

0.5.6
+++++

* Fix issue that assigning identity in another subscription will fail

0.5.5
+++++

* Add support for Azure KeyVault Secrets Provider as an AKS addon

0.5.4
+++++

* Add operations of maintenance configuration

0.5.3
+++++

* Add `--enable-pod-identity-with-kubenet` for enabling AAD Pod Identity in Kubenet cluster
* Add `--fqdn-subdomain parameter` to create private cluster with custom private dns zone scenario

0.5.2
+++++

* Add support for node public IP prefix ID '--node-public-ip-prefix-id'

0.5.1
+++++

* Update to use 2021-02-01 api-version

0.5.0
+++++

* Modify addon confcom behavior to only enable SGX device plugin by default.
* Introducte argument '--enable-sgx-quotehelper'
* Breaking Change: remove argument '--diable-sgx-quotehelper'.

0.4.73
++++++

* Update to use 2020-12-01 api-version
* Add argument '--enable-encryption-at-host'

0.4.72
+++++++

* Add --no-uptime-sla
* Create MSI clusters by default.

0.4.71
+++++++

* Add support using custom private dns zone resource id for parameter '--private-dns-zone'

0.4.70
+++++++

* Revert to use CLIError to be compatible with azure cli versions < 2.15.0

0.4.69
+++++++

* Add argument 'subnetCIDR' to replace 'subnetPrefix' when using ingress-azure addon.

0.4.68
+++++++

* Add support for AAD Pod Identity resources configuration in Azure CLI.

0.4.67
++++++

* Add support for node configuration when creating cluster or agent pool.
* Support private DNS zone for AKS private cluster.

0.4.66
++++++

* Add support for GitOps as an AKS addon
* Update standard load balancer (SLB) max idle timeout from 120 to 100 minutes

0.4.65
++++++

* Honor addon names defined in Azure CLI
* Add LicenseType support for Windows
* Remove patterns for adminUsername and adminPassword in WindowsProfile

0.4.64
++++++

* Add support for Open Service Mesh as an AKS addon
* Add support to get available upgrade versions for an agent pool in AKS

0.4.63
++++++

* Enable the September (2020-09-01) for use with the AKS commands
* Support Start/Stop cluster feature in preview
* Support ephemeral OS functionality
* Add new properties to the autoscaler profile: max-empty-bulk-delete, skip-nodes-with-local-storage, skip-nodes-with-system-pods, expander, max-total-unready-percentage, ok-total-unready-count and new-pod-scale-up-delay
* Fix case sensitive issue for AKS dashboard addon
* Remove PREVIEW from azure policy addon

0.4.62
++++++

* Add support for enable/disable confcom (sgx) addon.

0.4.61
++++++

* Fix AGIC typo and remove preview label from VN #2141
* Set network profile when using basic load balancer. #2137
* Fix bug that compare float number with 0 #2213

0.4.60
++++++

* Fix regression due to a change in the azure-mgmt-resource APIs in CLI 2.10.0

0.4.59
++++++

* Support bring-your-own VNET scenario for MSI clusters which use user assigned identity in control plane.

0.4.58
++++++

* Added clearer error message for invalid addon names

0.4.57
++++++

* Support "--assign-identity" for specifying an existing user assigned identity for control plane's usage in MSI clusters.

0.4.56
++++++

* Support "--enable-aad" for "az aks update" to update an existing RBAC-enabled non-AAD cluster to the new AKS-managed AAD experience

0.4.55
++++++

* Add "--enable-azure-rbac" for enabling Azure RBAC for Kubernetes authorization

0.4.54
++++++

* Support "--enable-aad" for "az aks update" to update an existing AAD-Integrated cluster to the new AKS-managed AAD experience

0.4.53
++++++

* Add --ppg for "az aks create" and "az aks nodepool add"

0.4.52
++++++

* Add --uptime-sla for az aks update

0.4.51
++++++

* Remove --appgw-shared flag from AGIC addon
* Handle role assignments for AGIC addon post-cluster creation
* Support --yes for "az aks upgrade"
* Revert default VM SKU to Standard_DS2_v2

0.4.50
++++++

* Add "--max-surge" for az aks nodepool add/update/upgrade

0.4.49
++++++

* Fix break in get-versions since container service needs to stay on old api.

0.4.48
++++++

* Fix issues of storage account name for az aks kollect

0.4.47
++++++

* Add "--node-image-only" for "az aks nodepool upgrade" and "az aks upgrade"".

0.4.46
++++++

* Fix issues for az aks kollect on private clusters

0.4.45
++++++

* Add "--aks-custom-headers" for "az aks nodepool add" and "az aks update"

0.4.44
++++++

* Fix issues with monitoring addon enabling with CLI versions 2.4.0+

0.4.43
++++++

* Add support for VMSS node public IP.

0.4.38
++++++

* Add support for AAD V2.

0.4.37
++++++

* Added slb outbound ip fix

0.4.36
++++++

* Added --uptime-sla for paid service

0.4.35
++++++

* Added support for creation time node labels

0.4.34
++++++

* Remove preview flag for private cluster feature.

0.4.33
++++++

* Adding az aks get-credentials --context argument

0.4.32
++++++

* Adding support for user assigned msi for monitoring addon.

0.4.31
++++++

* Fixed a regular agent pool creation bug.

0.4.30
++++++

* Remove "Low" option from --priority
* Add "Spot" option to --priority
* Add float value option "--spot-max-price" for Spot Pool
* Add "--cluster-autoscaler-profile" for configuring autoscaler settings

0.4.29
++++++

* Add option '--nodepool-tags for create cluster'
* Add option '--tags' for add or update node pool

0.4.28
++++++

* Add option '--outbound-type' for create
* Add options '--load-balancer-outbound-ports' and '--load-balancer-idle-timeout' for create and update

0.4.27
++++++

* Fixed aks cluster creation error

0.4.26
++++++

* Update to use 2020-01-01 api-version
* Support cluster creation with server side encryption using customer managed key

0.4.25
++++++

* List credentials for different users via parameter `--user`

0.4.24
++++++

* added custom header support

0.4.23
++++++

* Enable GA support of apiserver authorized IP ranges via parameter `--api-server-authorized-ip-ranges` in `az aks create` and `az aks update`

0.4.21
++++++

* Support cluster certificate rotation operation using `az aks rotate-certs`
* Add support for `az aks kanalyze`

0.4.20
++++++

* Add commands '--zones' and '-z' for availability zones in aks

0.4.19
++++++

* Refactor and remove a custom way of getting subscriptions

0.4.18
++++++

* Update to use 2019-10-01 api-version

0.4.17
++++++

* Add support for public IP per node during node pool creation
* Add support for taints during node pool creation
* Add support for low priority node pool

0.4.16
++++++

* Add support for `az aks kollect`
* Add support for `az aks upgrade --control-plane-only`

0.4.15
++++++

* Set default cluster creation to SLB and VMSS

0.4.14
++++++

* Add support for using managed identity to manage cluster resource group

0.4.13
+++++++

* Rename a few options for ACR integration, which includes
  * Rename `--attach-acr <acr-name-or-resource-id>` in `az aks create` command, which allows for attach the ACR to AKS cluster.
  * Rename `--attach-acr <acr-name-or-resource-id>` and `--detach-acr <acr-name-or-resource-id>` in `az aks update` command, which allows to attach or detach the ACR from AKS cluster.
* Add "--enable-private-cluster" flag for enabling private cluster on creation.

0.4.12
++++++

* Bring back "enable-vmss" flag  for backward compatibility
* Revert "Set default availability type to VMSS" for backward compatibility
* Revert "Set default load balancer SKU to Standard" for backward compatibility

0.4.11
++++++

* Add support for load-balancer-profile
* Set default availability type to VMSS
* Set default load balancer SKU to Standard

0.4.10
++++++

* Add support for `az aks update --disable-acr --acr <name-or-id>`

0.4.9
+++++

* Use https if dashboard container port is using https

0.4.8
+++++

* Add update support for `--enable-acr` together with `--acr <name-or-id>`
* Merge `az aks create --acr-name` into `az aks create --acr <name-or-id>`

0.4.7
+++++

* Add support for `--enable-acr` and `--acr-name`

0.4.4
+++++

* Add support for per node pool auto scaler settings.
* Add `az aks nodepool update` to allow users to change auto scaler settings per node pool.
* Add support for Standard sku load balancer.

0.4.1
+++++

* Add `az aks get-versions -l location` to allow users to see all managed cluster versions.
* Add `az aks get-upgrades` to get all available versions to upgrade.
* Add '(preview)' suffix if kubernetes version is preview when using `get-versions` and `get-upgrades`

0.4.0
+++++

* Add support for Azure policy add-on.

0.3.2
+++++

* Add support of customizing node resource group

0.3.1
+++++

* Add support of pod security policy.

0.3.0
+++++

* Add support of feature `--node-zones`

0.2.3
+++++

* `az aks create/scale --nodepool-name` configures nodepool name, truncated to 12 characters, default - nodepool1
* Don't require --nodepool-name in "az aks scale" if there's only one nodepool

0.2.2
+++++

* Add support of Network Policy when creating new AKS clusters

0.2.1
+++++

* add support of apiserver authorized IP ranges

0.2.0
+++++

* Breaking Change: Set default agentType to VMAS
* opt-in VMSS by --enable-VMSS when creating AKS

0.1.0
+++++

* new feature `enable-cluster-autoscaler`
* default agentType is VMSS
