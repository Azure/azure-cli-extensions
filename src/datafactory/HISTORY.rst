.. :changelog:

Release History
===============
0.7.0
+++++
* az datafactory data-flow: Support create/update/list/show/delete data flows.

0.6.0
+++++
* Bug fix for `az datafactory pipeline list`.

0.5.0
+++++
* az datafactory managed-virtual-network: Support create/update/list/show managed virtual network.
* az datafactory managed-private-endpoint: Support create/update/list/show/delete managed private endpoint.

0.4.0
+++++
* GA the whole module

0.3.0
+++++
* [BREAKING CHANGE] Renamed command subgroup `az datafactory factory` to `az datafactory`.
* [BREAKING CHANGE] `az datafactory integration-runtime managed create`: `--type-properties-compute-properties` renamed to `--compute-properties`,
  `--type-properties-ssis-properties` renamed to `--ssis-properties`.
* [BREAKING CHANGE] `az datafactory integration-runtime self-hosted create`: `--type-properties-linked-info` renamed to `--linked-info`.
* [BREAKING CHANGE] `az datafactory integration-runtime update`: `--properties` renamed to `--linked-service`.
* [BREAKING CHANGE] `az datafactory linked-service delete`: `--properties` renamed to `--dataset`.
* [BREAKING CHANGE] `az datafactory trigger list`: `--properties` renamed to `--trigger`.

0.2.1
+++++
* az datafactory factory create: Enable managed identity by default

0.2.0
++++++
* add update command for linked services and triggers and datasets

0.1.0
++++++
* Initial release.
