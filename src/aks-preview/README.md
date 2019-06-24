#Azure CLI AKS Preview Extension#
This is an extension for AKS features. This will replace the full AKS module.

## How to use ##
Install this extension using the below CLI command
```
az extension add --name aks-preview
```

## Included Features
### Cluster Auto Scaler:
[more info](https://docs.microsoft.com/en-us/azure/aks/autoscaler)


#### create aks cluster with enabled cluster autoscaler
*Examples:*
```
az aks create \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 5 \
    --node-count 3 \
    --kubernetes-version 1.11.3
```

#### enable cluster autoscaler for existing cluster
Note: make sure following setting:
1. min-count <= node-count
2. max-count >= node-count
3. kubernetes-version >= 1.10.6
*Examples:*
```
az aks update \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 5
```

#### disable cluster autoscaler for exisiting enabled cluster
*Examples:*
```
az aks update \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --disable-cluster-autoscaler
```

#### update min-count/max-count for exisiting enabled cluster
*Examples:*
```
az aks update \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --update-cluster-autoscaler \
    --min-count 1 \
    --max-count 5
```

#### Enable apiserver authorized IP ranges

*Examples:*

```
az aks update \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --api-server-authorized-ip-ranges "172.0.0.10/16,168.10.0.10/18"
```

#### Disable apiserver authorized IP ranges

*Examples:*

```
az aks update \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --api-server-authorized-ip-ranges ""
```

#### Enable VMSS for new cluster
*Examples:*
```
az aks create \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --enable-VMSS \
```

#### Enable VMSS for new cluster with availability zone feature
*Examples:*
```
az aks create \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --enable-VMSS \
    --node-zones 1 2 3
```

#### Enable pod security policy for new cluster
*Examples:*
```
az aks create \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --enable-pod-security-policy \
```

#### Enable pod security policy for existing cluster
*Examples:*
```
az aks update \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --enable-pod-security-policy \
```

#### Disable pod security policy for existing cluster
*Examples:*
```
az aks update \
    -g MyResourceGroup \
    -n MyManagedCluster \
    --disable-pod-security-policy \
```

#### Enable cluster auto scaler for a node pool
*Examples:*
```
az aks nodepool update \
    -g MyResourceGroup \
    -n nodepool1
    --cluster-name MyManagedCluster \
    --enable-cluster-autoscaler \
    --max-count 10 \
    --min-count 3
```

#### Update cluster auto scaler settings for a node pool
*Examples:*
```
az aks nodepool update \
    -g MyResourceGroup \
    -n nodepool1
    --cluster-name MyManagedCluster \
    --update-cluster-autoscaler \
    --max-count 10 \
    --min-count 3
```