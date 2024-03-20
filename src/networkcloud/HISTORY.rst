.. :changelog:

Release History
===============

2.0.0b2
++++++++
* Examples updated to include new property user-principal-name for baremetalmachinekeyset and bmckeyset create and update commands.

2.0.0b1
++++++++
* This beta version supports NetworkCloud 2023-10-01-preview APIs.
* Format restrictions and resource type validations are added to fields that represent ARM ID resources.
* New functionality supported in this release:
  * New configuration is added to cluster create and update commands for runtime protection scan, secret archive, and cluster update strategy.
  * New Cluster command scan-runtime is added to trigger the execution of a runtime protection scan.
  * baremetalmachine returns new properties with runtime protection status.
  * Additional status "Disconnected" is added to clusterConnectionStatus.
  * kubernetescluster update command allows modification of SSH keys for cluster administrator and control plane administrator.
  * kubernetescluster agentpool update command allows modification of SSH keys for the agent pool administrator.
* This version requires a minimum of 2.51 Azure core CLI.
* This version upgrades the internal generation tool aaz-dev-tools to 1.8.0. Refer to the release notes for more details: https://github.com/Azure/aaz-dev-tools/releases/tag/v1.8.0.

1.1.0
++++++++
* This version removes the experimental commands for defaultcninetwork and hybridakscluster as these resources are no longer available.

1.0.0
++++++++
* This is the first stable version of the CLI extension that supports NetworkCloud 2023-07-01 stable APIs.
* Virtualmachine console create and update commands have been enhanced to accept a file path for ssh_public_key parameter.

1.0.0b1
++++++++
* This is first beta version of the CLI extension that supports NetworkCloud 2023-07-01 stable APIs.
* The defaultcninetwork and hybridakscluster resources are no longer available.

0.4.1
++++++
* This version updates the kubernetescluster resource to not send an empty array `sshPubKeys` for control plane configuration and agent pool configuration if the input contains no ssh keys provided for these parameters.
* This version updates the agentpool child resource of kubernetescluster to not send an empty array `sshPubKeys` is not provided in the input.

0.4.0
++++++
* This version supports NetworkCloud 2023-05-01-preview APIs.
* It introduces a new resource kubernetescluster and its child resource agentpool.
* The defaultcninetwork and hybridakscluster resources are preserved and will continue using 2022-12-12-preview APIs.
* This version is experimental. Changes to the interface are expected but will be done in backward compatible way where possible.

0.3.0
++++++
* Initial release. This version supports NetworkCloud 2022-12-12-preview APIs.
* This version is experimental. Changes to the interface are expected but will be done in backward compatible way where possible.
