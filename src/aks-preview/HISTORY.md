.. :changelog:

Release History
===============
0.4.18
+++++
* Update to use 2019-10-01 api-version

0.4.17
+++++
* Add support for public IP per node during node pool creation
* Add support for taints during node pool creation
* Add support for low priority node pool

0.4.16
+++++
* Add support for `az aks kollect`
* Add support for `az aks upgrade --control-plane-only`

0.4.15
+++++
* Set default cluster creation to SLB and VMSS

0.4.14
+++++
* Add support for using managed identity to manage cluster resource group

0.4.13
++++++
* Rename a few options for ACR integration, which includes
  * Rename `--attach-acr <acr-name-or-resource-id>` in `az aks create` command, which allows for attach the ACR to AKS cluster.
  * Rename `--attach-acr <acr-name-or-resource-id>` and `--detach-acr <acr-name-or-resource-id>` in `az aks update` command, which allows to attach or detach the ACR from AKS cluster.
* Add "--enable-private-cluster" flag for enabling private cluster on creation.

0.4.12
+++++
* Bring back "enable-vmss" flag  for backward compatibility
* Revert "Set default availability type to VMSS" for backward compatibility
* Revert "Set default load balancer SKU to Standard" for backward compatibility

0.4.11
+++++
* Add support for load-balancer-profile
* Set default availability type to VMSS
* Set default load balancer SKU to Standard

0.4.10
+++++
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
