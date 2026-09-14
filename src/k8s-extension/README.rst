Microsoft Azure CLI 'k8s-extension' Extension
=============================================

This package is for the 'k8s-extension' extension.
i.e. 'az k8s-extension'

This package includes the 'extension-types' subgroup.
i.e. 'az k8s-extension extension-types'

### How to use ###
Install this extension using the below CLI command
```
az extension add --name k8s-extension
```

### Included Features
#### Chaos Studio (private preview)

`Microsoft.ChaosStudio` supports cluster-scoped AKS installations. Pass
`chaos-workspace-id=<workspace-resource-id>` in `--configuration-settings` to
validate AKS Workload Identity, OIDC and Azure RBAC prerequisites and configure
the subscriber identity, federated credential, workspace identity role assignment
and workspace connection. The workspace must have a system-assigned identity or
exactly one user-assigned identity. The subscriber endpoint comes from the service.

The partner defaults to the `dev` train, version `0.1.0`, namespace
`chaos-infrastructure`, with automatic upgrades disabled. Supply `--version` for
another available chart version and any chart-required configuration settings.
Without `chaos-workspace-id`, prerequisite provisioning is not performed.

`chaos-existing-role-definition-id=<role-resource-id>` explicitly reuses a
compatible custom role in the cluster subscription without modifying it.
Updates retain existing configuration and reconcile prerequisites. Changing the
workspace or release namespace requires deleting and recreating the extension.
Delete removes the matching owned connection before owned prerequisites; it
preserves shared role definitions and resources that fail ownership checks.

##### Tested private-preview installation

Use a CLI build containing this partner customization and an existing workspace.
The following configuration was used for installation and pod-delete validation
with dev chart `0.1.3`. Replace the resource placeholders with your own values:

```bash
az k8s-extension create \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type managedClusters \
    --name chaos-studio \
    --extension-type Microsoft.ChaosStudio \
    --scope cluster \
    --release-namespace chaos-infrastructure \
    --release-train dev \
    --version 0.1.3 \
    --configuration-settings \
        "chaos-workspace-id=/subscriptions/<subscription-id>/resourceGroups/<workspace-group>/providers/Microsoft.Chaos/workspaces/<workspace-name>" \
        "experiments.stressToolsImage=PLACEHOLDER.invalid/never-pulled:0"
```

The chart requires `experiments.stressToolsImage`. This inert placeholder was
used only for pod-delete validation, which doesn't pull a stress-tools image.
It isn't usable for CPU or memory faults; those require a supported, pullable
stress-tools image. If reusing a compatible custom role, also include
`"chaos-existing-role-definition-id=/subscriptions/<subscription-id>/providers/Microsoft.Authorization/roleDefinitions/<role-definition-id>"`
in the configuration settings.

Installation and authorized data-plane polling succeeded with this configuration.
A five-minute pod-delete test passed in Litmus and the workload recovered to
2/2 replicas, but the ARM run failed/remained Stopping. This isn't a successful
ARM end-to-end result or proof of live update/delete behavior. The explicit
`--version 0.1.3` here doesn't change the partner's `0.1.0` default.

#### Kubernetes Extensions:
Kubernetes Extensions: [more info](https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/extensions)\
*Examples:*

##### Create a KubernetesExtension
```
az k8s-extension create \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name extensionName \
    --extension-type extensionType \
    --scope scopeType \
    --release-train releaseTrain \
    --version versionNumber \
    --auto-upgrade-minor-version autoUpgrade \
    --configuration-settings exampleSetting=exampleValue \
    --plan-name examplePlanName \
    --plan-publisher examplePublisher \
    --plan-product exampleOfferId \

```

##### Get a KubernetesExtension
```
az k8s-extension show \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name extensionName
```

##### Delete a KubernetesExtension
```
az k8s-extension delete \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name extensionName
```

##### List all KubernetesExtension of a cluster
```
az k8s-extension list \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType
```

##### Update an existing KubernetesExtension of a cluster
```
az k8s-extension update \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name extensionName \
    --auto-upgrade true/false \
    --version extensionVersion \
    --release-train releaseTrain \
    --configuration-settings settingsKey=settingsValue \
    --configuration-protected-settings protectedSettingsKey=protectedValue \
    --configuration-settings-file configSettingsFile \
    --configuration-protected-settings-file protectedSettingsFile
```

##### List available extension types of a cluster
```
az k8s-extension extension-types list \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType 
```

##### List available extension types by location 
```
az k8s-extension extension-types list-by-location \
    --location location 
```

##### Show an extension types of a cluster
```
az k8s-extension extension-types show \
    --resource-group groupName \
    --cluster-name clusterName \
    --cluster-type clusterType \
    --name extensionName 
```

##### List all versions of an extension type by release train
```
az k8s-extension extension-types list-versions \
    --location location \
    --name extensionName
```
