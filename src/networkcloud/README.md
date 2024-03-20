# Azure CLI Networkcloud Extension #
This is an extension to Azure CLI to manage Azure Operator Nexus - Network Cloud on-premises clusters and their resources, such as racks, bare metal hosts, virtual machines, workload networks and more.

## How to use ##

Install the latest version of the extension:

```
az extension add --name networkcloud
```

Validate that the extension is installed correctly:

```
az networkcloud --help
```

For list of available versions, see [the extension release history][az-cli-networkcloud-cli-versions].

To install a specific version of the networkcloud CLI extension, add `--version` parameter to the command. For example, below installs 0.4.1

```
az extension add --name networkcloud --version 0.4.1
```

## Included Features ##

Below is a high-level overview of networkcloud commands.

| Commands                                       | Description                                                                        |
|------------------------------------------------|------------------------------------------------------------------------------------|
| az networkcloud baremetalmachine               | Provides commands to manage bare metal machines.                                   |
| az networkcloud cluster                        | Provides commands to manage clusters.                                              |
| az networkcloud cluster baremetalmachinekeyset | Provides commands to manage cluster's bare metal machines access via SSH key sets. |
| az networkcloud cluster bmckeyset              | Provides commands to manage cluster's baseboard management controller key set.     |
| az networkcloud cluster metricsconfiguration   | Provides commands to manage cluster's metrics configurations.                      |
| az networkcloud clustermanager                 | Provides commands to manage cluster managers.                                      |
| az networkcloud kubernetescluster              | Provides commands to manage Kubernetes clusters.                                   |
| az networkcloud kubernetescluster agentpool    | Provides commands to manage Kubernetes cluster's agent pool.                       |
| az networkcloud l2network                      | Provides commands to manage layer 2 (L2) networks.                                 |
| az networkcloud l3network                      | Provides commands to manage layer 3 (L3) networks.                                 |
| az networkcloud rack                           | Provides commands to manage racks.                                                 |
| az networkcloud racksku                        | Provides commands to display rack Skus information.                                |
| az networkcloud storageappliance               | Provides commands to manage storage appliances.                                    |
| az networkcloud trunkednetwork                 | Provides commands to manage trunked networks.                                      |
| az networkcloud virtualmachine                 | Provides commands to manage virtual machines.                                      |
| az networkcloud virtualmachine console         | Provides commands to manage virtual machine's consoles.                            |
| az networkcloud volume                         | Provides commands to manage volumes.                                               |

For more details, please refer to [Azure Operator Nexus - NetworkCloud][networkcloud-microsoft-learn].


<!-- LINKS - External -->
[networkcloud-microsoft-learn]: https://learn.microsoft.com/en-us/azure/operator-nexus/

[az-cli-networkcloud-cli-versions]: https://github.com/Azure/azure-cli-extensions/blob/main/src/networkcloud/HISTORY.rst
