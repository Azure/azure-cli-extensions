# Azure CLI AksSafeguards Extension #
This is an extension to Azure CLI to manage AksSafeguards resources.

## Commands ##

### az aks safeguards create

Enable Deployment Safeguards for an AKS cluster

#### Examples

| Example | Description |
|---------|-------------|
| `az aks safeguards create --resource-group MyResourceGroup --name MyAKSCluster --level Warn` | Enable Deployment Safeguards for an AKS cluster at Warn level |
| `az aks safeguards create --resource-group MyResourceGroup --name MyAKSCluster --level Warn --excluded-namespaces [ns1,ns2]` | Enable Deployment Safeguards at Warn level for an AKS cluster with excluded namespaces |
| `az aks safeguards create --managed-cluster "/subscriptions/MySubscriptionID/resourceGroups/MyResourceGroup/providers/Microsoft.ContainerService/managedClusters/MyAKSCluster" --level Warn` | Enable Deployment Safeguards at Warn level for an AKS cluster by its resource ID |

### az aks safeguards update

Update Deployment Safeguards for an AKS cluster

#### Examples

| Example | Description |
|---------|-------------|
| `az aks safeguards update --resource-group MyResourceGroup --name MyAKSCluster --level Enforce` | Update Deployment Safeguards to Enforce level for an AKS cluster with a specific name and resource group |
| `az aks safeguards update --resource-group MyResourceGroup --name MyAKSCluster --excluded-namespaces [ns1,ns2] --level Warn` | Update Deployment Safeguards to Warn level for an AKS cluster with excluded namespaces |
| `az aks safeguards update --managed-cluster "/subscriptions/MySubscriptionID/resourceGroups/MyResourceGroup/providers/Microsoft.ContainerService/managedClusters/MyAKSCluster" --level Enforce` | Update Deployment Safeguards to Enforce level for an AKS cluster by its resource ID |

### az aks safeguards show

Show Deployment Safeguards configuration for a Managed Cluster

#### Examples

| Example | Description |
|---------|-------------|
| `az aks safeguards show --resource-group MyResourceGroup --name MyAKSCluster` | Show Deployment Safeguards for an AKS cluster with a specific name and resource group |
| `az aks safeguards show --managed-cluster "/subscriptions/MySubscriptionID/resourceGroups/MyResourceGroup/providers/Microsoft.ContainerService/managedClusters/MyAKSCluster"` | Show Deployment Safeguards for an AKS cluster by its resource ID |

### az aks safeguards delete

Delete Deployment Safeguards configuration for a Managed Cluster

#### Examples

| Example | Description |
|---------|-------------|
| `az aks safeguards delete --resource-group MyResourceGroup --name MyAKSCluster` | Delete Deployment Safeguards for an AKS cluster with a specific name and resource group |
| `az aks safeguards delete --managed-cluster "/subscriptions/MySubscriptionID/resourceGroups/MyResourceGroup/providers/Microsoft.ContainerService/managedClusters/MyAKSCluster"` | Delete Deployment Safeguards for an AKS cluster by its resource ID |

