.. :changelog:

Release History
===============

1.0.13
++++++
* Add support for hosted control plane clusters via `az aro hcp` and its subcommands.

1.0.12
++++++
* Switch managed identity and workload identity features to the stable 2025-07-25 API.
* Add managed identity and platform workload identity update support.
* Add automated managed identity cleanup during cluster deletion.
* Default new production clusters to Dsv5 worker virtual machines.
* Fix `az aro get-versions` and compatibility with newer Azure CLI releases.

1.0.11
++++++
* Switch to the 2024-08-12-preview API.
* Add managed identity and platform workload identity options to `az aro create`.

1.0.10
++++++
* Move multiple public IP support to the stable 2023-11-22 API.

1.0.9
++++++
* Add --load-balancer-managed-outbound-ip-count to `az aro create`.

1.0.8
++++++
* Switch to the 2023-07-01-preview API.
* Add --load-balancer-managed-outbound-ip-count to `az aro update`.

1.0.7
++++++
* Add support for get-versions (lists available installation versions of OpenShift per location)
* Adds an aro create 'version' parameter (for specifying the cluster installation version)

1.0.6
++++++
* Fixed backwards compatibility with Python3.6

1.0.5
++++++
* Fixed get-admin-kubeconfig Enums for Feature state no longer available in AzureCLI
* Added saving kubeconfig to file

1.0.4
++++++
* Remove unused code (identifier URLs)

1.0.3
++++++
* Fix role assignment bug

1.0.2
++++++
* Add support for list admin credentials (getting kubeconfig)

1.0.1
++++++
* Switch to new preview API

1.0.0
++++++
* Remove preview flag.

0.4.0
++++++
* Default worker VM size to Standard_D4s_v3.

0.3.0
++++++
* Add --pull-secret argument to `az aro create`.
* Stop advertising Python 2.7, 3.5 support.
* Migrate to GA API.

0.2.0
++++++
* Use API paging.
* Remove azext.maxCliCoreVersion.

0.1.0
++++++
* Initial release.
