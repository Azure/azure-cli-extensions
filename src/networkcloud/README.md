# Azure CLI Networkcloud Extension #
This is an extension to Azure CLI to manage Azure Operator Nexus - Network Cloud on-premises clusters and their resources, such as racks, bare metal hosts, virtual machines, workload networks and more.

## How to use ##

Install the extension:

```
az extension add --name networkcloud
```

Validate that the extension is installed correctly:

```
az networkcloud --help
```

## Included Features ##

Below is a high-level overview of networkcloud commands.

| Commands  | Description|
| ------------- | ------------- |
| az networkcloud baremetalmachine | Provides commands to manage bare metal machines.  |
| az networkcloud cluster | Provides commands to manage clusters. |
| az networkcloud cluster baremetalmachinekeyset | Provides commands to manage cluster's bare metal machines access via SSH key sets. |
| az networkcloud cluster bmckeyset | Provides commands to manage cluster's baseboard management controller key set. |
| az networkcloud cluster metricsconfiguration | Provides commands to manage cluster's metrics configurations. |
| az networkcloud clustermanager | Provides commands to manage cluster managers. |
| az networkcloud defaultcninetwork | Provides commands to manage default CNI networks. |
| az networkcloud hybridakscluster | Provides commands to manage additional details of Hybrid Aks provisioned clusters. |
| az networkcloud l2network | Provides commands to manage layer 2 (L2) networks. |
| az networkcloud l3network | Provides commands to manage layer 3 (L3) networks. |
| az networkcloud rack | Provides commands to manage racks. |
| az networkcloud racksku | Provides commands to display rack Skus information. |
| az networkcloud storageappliance | Provides commands to manage storage appliances. |
| az networkcloud trunkednetwork | Provides commands to manage trunked networks. |
| az networkcloud virtualmachine | Provides commands to manage virtual machines. |

For more details, please refer to [Azure Operator Nexus - NetworkCloud](https://learn.microsoft.com/en-us/azure/operator-nexus/).
