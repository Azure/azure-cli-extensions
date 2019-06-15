.. :changelog:

Release History
===============
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