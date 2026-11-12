Microsoft Azure CLI ``workload-manager`` Extension
==================================================

This package provides commands for managing Microsoft Compute Workload Manager resources.

Commands
--------

* ``az workload-manager workload-space``
* ``az workload-manager workload-space runtime-binding``
* ``az workload-manager workload-space runtime-link``
* ``az workload-manager workload-space capability``

Provision a complete workload space
----------------------------------

Use ``az workload-manager workload-space up`` to provision a workload space
with AKS and ACI runtime bindings, a runtime link, and the AgentSandbox and
PodSnapshotRestore capabilities.

Use an existing resource group in the selected subscription. Configure the required
provider and feature registrations and Workload Manager service permissions before
running the command. Choose a deployment location supported by the service.

Managed AKS and managed ACI are the default::

    az workload-manager workload-space up -g MyResourceGroup -n MySpace

The command uses your configured default location, or the resource group's location
if no default is configured. Specify ``--location`` or ``-l`` to select another
location::

    az workload-manager workload-space up -g MyResourceGroup -n MySpace -l eastus2

To reference an existing AKS cluster, supply all three options together::

    az workload-manager workload-space up -g MyResourceGroup -n MySpace -l eastus2 --managed-cluster-resource-id <aks-resource-id> --workload-execution-subnet-id <aci-subnet-id> --runtime-link-subnet-id <link-subnet-id>

The AKS cluster must be in the selected subscription and region. Both subnets
must be in that subscription and the cluster's VNet. The runtime-link subnet
must be empty and distinct from the AKS and ACI subnets. AKS topology and other
service prerequisites are validated by the resource provider.

The child resources are named ``aks``, ``aci``, ``link``, ``agent-sandbox`` and
``pod-snapshot-restore``. Rerunning the command updates these same resources and
reapplies the supplied configuration, including workload-space tags. Existing
runtime bindings must retain their managed or referenced mode.

The deployment preserves unrelated resources. If it fails, resources already
created remain available; review the deployment errors before retrying.

``--deployment-name`` defaults to the workload-space name. The command returns
the ARM deployment result, including ``outputs.workloadSpaceId.value``.
Use ``--no-wait`` to return after submission while deployment continues::

    az workload-manager workload-space up -g MyResourceGroup -n MySpace --no-wait

Inspect deployment progress or errors with::

    az deployment group show -g MyResourceGroup -n MySpace

API version
-----------

The extension targets API version ``2026-11-01-preview`` from
the `public Workload Manager API specification <https://github.com/Azure/azure-rest-api-specs/blob/main/specification/compute/resource-manager/Microsoft.Compute/WorkloadManager/preview/2026-11-01-preview/WorkloadManager.json>`_.