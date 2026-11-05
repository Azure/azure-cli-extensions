.. :changelog:

Release History
===============

0.2.0
++++++
* Add ``workload-space up`` to deploy a complete runtime composition through an incremental ARM deployment.
* Support managed AKS by default or an existing AKS cluster with ACI execution and runtime-link subnets.
* Add ``PodSnapshotRestore`` to the supported kinds for ``workload-space capability create``.
* Add ``--subnet-resource-id`` to ``workload-space runtime-link create`` for customer-network compositions.

0.1.0
++++++
* Initial release of the Workload Manager extension.
* Add commands to manage workload spaces, capabilities, runtime bindings, and runtime links.