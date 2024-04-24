.. :changelog:

Release History
===============

1.6.1
++++++++++++++++++
* minor fixes to dataprotection aks ext CLI
* Rename WorkloadIAM to EntraWorkloadIAM

1.6.0
++++++++++++++++++
* AAD related changes in dataprotection aks ext CLI
* microsoft.azuremonitor.containers: Make containerlogv2 as default as true and remove region dependency for ARC
* microsoft.workloadiam: Refactor subcommand invocation

1.5.3
++++++++++++++++++
* Add WorkloadIAM extension support and tests.

1.5.2
++++++++++++++++++
* Update help text on configuration-settings and configuration-protected-settings properties.

1.5.1
++++++++++++++++++
* microsoft.kubernetes.azuredefender: Fixed installation bug where LogAnalytics Workspace details were not being fetched correctly.

1.5.0
++++++++++++++++++
* add support for extensionsType api
* Breaking change introduced with API version 2023-05-01 adds validation will begin rejecting calls (PUT and PATCH) that provide a version for the extension and also set autoUpgradeMinorVersion to true
* microsoft.openservicemesh: Update OSM-Arc version check for beta and CI tags

1.4.5
++++++++++++++++++
* fix bugs while dropping 'azure-mgmt-relay'

1.4.4
++++++++++++++++++
* drop 'azure-mgmt-relay' sdk dependency

1.4.3
++++++++++++++++++
* microsoft.azuremonitor.containers: Extend ContainerInsights Extension dataCollectionSettings with streams and containerlogv2 field. Also, add a kind tag in DCR creation for the ContainerInsights extension.
* microsoft.dapr: Use semver instead of packaging
* microsoft.azuremonitor.containers.metrics: update logic to sanitize cluster name for dc* objects
* microsoft.openservicemesh: Fix osm-arc version check for CI tags
* add support to skip provisioning of prerequisites for Azure Monitor K8s extensions

1.4.2
++++++++++++++++++
* microsoft.azuremonitor.containers: ContainerInsights Extension Managed Identity Auth Enabled by default

1.4.1
++++++++++++++++++
* microsoft.azureml.kubernetes: Fix sslSecret parameter in update operation
* microsoft.azuremonitor.containers.metrics : public preview support for managed prometheus in ARC clusters

1.4.0
++++++++++++++++++
* microsoft.dapr: Update version comparison logic to use semver based comparison
* microsoft.azuremonitor.containers: Make ContainerInsights DataCollectionRuleName consistent with portal and other onboarding clients

1.3.9
++++++++++++++++++
* Deprecating  --config-settings alias for --configuration-settings
* Deprecating  --configuration-protected-settings alias for --config-protected-settings
* Deprecating  --configuration-settings-file alias for --config-settings-file
* Deprecating  --configuration-protected-settings-file alias for --config-protected-file

1.3.8
++++++++++++++++++
* Fixes to address the bug with msi auth mode for azuremonitor-containers extension version >= 3.0.0
* microsoft.dapr: disable apply-CRDs hook if auto-upgrade is disabled
* microsoft.azuremonitor.containers: ContainerInsights Extension add dataCollectionSettings to configuration settings
* k8s-extension Adding GA api version 2022-11-01 exposing isSystemExtension and support

1.3.7
++++++++++++++++++
* microsoft.dapr: prompt user for existing dapr installation during extension create

1.3.6
++++++++++++++++++
* Update the api version and add tests for extension type calls
* Fix the TypeError: cf_k8s_extension() takes 1 positional argument but 2 were given while running all az k8s-extension extension-types commands
* microsoft.azuremonitor.containers: Update DCR creation to Clusters resource group instead of workspace
* microsoft.dataprotection.kubernetes: Authoring a new k8s partner extension for the BCDR solution of AKS clusters

1.3.5
++++++++++++++++++
* Use the api-version 2022-04-02-preview in the CLI command az k8s-extension extension-types list

1.3.4
++++++++++++++++++
* Fix to address the error TypeError: cf_k8s_extension() takes 1 positional argument but 2 were given while running command az k8s-extension extension-types list

1.3.3
++++++++++++++++++
* microsoft.azuremonitor.containers: add condition to use different api version for provisioned clusters

1.3.2
++++++++++++++++++
* Create identity for Appliances clusters

1.3.1
++++++++++++++++++
* microsoft.azureml.kubernetes: Always show TSG link for AzureMLKubernetes extension at the head.
* microsoft.azuremonitor.containers: add omsagent rename changes
* microsoft.azuremonitor.containers: fix script to support provisionedClusters

1.3.0
++++++++++++++++++
* Add support for provisionedClusters

1.2.6
++++++++++++++++++
* k8s-extension new sub command group for extension types

1.2.5
++++++++++++++++++
* microsoft.azuremonitor.containers: ContainerInsights Extension Managed Identity Auth Onboarding related bug fixes.
* microsoft.openservicemesh: Fix osm-arc installations for non-connectedClusters
* k8s-extension azuredefender namespace to mdc

1.2.4
++++++++++++++++++
* microsoft.azureml.kubernetes: Do not invoke `create_or_update` for already existed resources.
* microsoft.azuremonitor.containers: ContainerInsights Extension Managed Identity Auth Onboarding updates.

1.2.3
++++++++++++++++++
* Fix warning message returned on PATCH
* microsoft.azureml.kubernetes: remove deprecated warning message.
* microsoft.azureml.kubernetes: Use cluster scale to control clusterPurpose and inferenceRouterHA

1.2.2
++++++++++++++++++
* microsoft.azureml.kubernetes: Disable service bus by default, do not create relay for managed clusters.
* microsoft.azureml.kubernetes: Rename inferenceLoadBalancerHA to inferenceRouterHA and unify related logic.

1.2.1
++++++++++++++++++
* Provide no default values for Patch of Extension
* microsoft.azureml.kubernetes: clusterip

1.2.0
++++++++++++++++++
* microsoft.azureml.kubernetes: Update AzureMLKubernetes install parameters on inferenceRouterServiceType and internalLoadBalancerProvider
* microsoft.openservicemesh: Change extension validation logic osm-arc
* microsoft.azuremonitor.containers: Add Managed Identity Auth support for ContainerInsights Extension
* microsoft.azuremonitor.containers: Bring back containerInsights solution addition in MSI mode

1.1.0
++++++++++++++++++
* Migrate Extensions api-version to 2022-03-01
* microsoft.azureml.kubernetes: Remove inference private review warning message
* microsoft.openservicemesh: Enable System-assigned identity

1.0.4
++++++++++++++++++
* microsoft.azureml.kubernetes: Support SSL secret

1.0.3
++++++++++++++++++
* Remove identity creation for calls to Microsoft.ResourceConnector

1.0.2
++++++++++++++++++
* Update api-version for calls to Microsoft.ResourceConnector to 2021-10-31-preview
* Update api-version for calls to Microsoft.ContainerService to 2021-10-01
* Update api-version for calls to Microsoft.Kubernetes to 2021-10-01
* microsoft.azureml.kubernetes: Add one more prompt for amlarc extension update

1.0.1
++++++++++++++++++
* microsoft.azureml.kubernetes: Retrieve relay and service bus connection string when update the configuration protected settings of the extension.

1.0.0
++++++++++++++++++
* Switch to GA api-version of Extensions (2021-09-01)
* Support Extensions PATCH
* Enable Dapr extension type
* Enable ManagedClusters clusterType

0.7.1
++++++++++++++++++
* Fix DF resource manager endpoint check

0.7.0
++++++++++++++++++
* Enable identity by default for extensions
* Use custom delete confirmation for partners
* microsoft.azureml.kubernetes: Adding a flag for AKS to AMLARC migration and set up corresponding FE helm values
* microsoft.openservicemesh: Remove version requirement and auto upgrade minor version check
* Adds -t as alternative to --cluster-type

0.6.1
++++++++++++++++++
* Remove sending identity for clusters in Dogfood
* Provide fix for getting tested distros for microsoft.openservicemesh
* Add location to model for identity

0.6.0
++++++++++++++++++
* Update extension resource models to Track2

0.5.1
++++++++++++++++++
* Remove pyhelm dependency

0.5.0
++++++++++++++++++
* Add microsoft.openservicemesh customization to check distros
* Delete customization for partners

0.4.3
++++++++++++++++++
* Add SSL support for AzureML

0.4.2
++++++++++++++++++

* Hotfix servicebus namespace creation for Track 2 changes
* Change resource tag from 'amlk8s' to 'Azure Arc-enabled ML' in microsoft.azureml.kubernetes

0.4.1
++++++++++++++++++

* Add compatible logic for the track 2 migration of resource dependence

0.4.0
++++++++++++++++++

* Release customization for microsoft.openservicemesh

0.3.1
++++++++++++++++++

* Add provider registration to check to validations
* Only validate scoring fe settings when inference is enabled in microsoft.azureml.kubernetes

0.3.0
++++++++++++++++++

* Release customization for microsoft.azureml.kubernetes

0.2.1
++++++++++++++++++

* Remove `k8s-extension update` until PATCH is supported
* Improved logging for overwriting extension name with default

0.2.0
++++++++++++++++++

* Refactor for clear separation of extension-type specific customizations
* OpenServiceMesh customization.
* Fix clusterType of Microsoft.ResourceConnector resource
* Update clusterType validation to allow 'appliances'
* Update identity creation to use the appropriate parent resource's type and api-version
* Throw error if cluster type is not one of the 3 supported types
* Rename azuremonitor-containers extension type to microsoft.azuremonitor.containers
* Move CLI errors to non-deprecated error types
* Remove support for update

0.1.3
++++++++++++++++++

* Customization for microsoft.openservicemesh

0.1.2
++++++++++++++++++

* Add support for Arc Appliance cluster type

0.1.1
++++++++++++++++++
* Add support for microsoft-azure-defender extension type

0.1.0
++++++++++++++++++
* Initial release.
