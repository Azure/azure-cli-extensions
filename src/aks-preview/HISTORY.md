.. :changelog:

Release History
===============
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