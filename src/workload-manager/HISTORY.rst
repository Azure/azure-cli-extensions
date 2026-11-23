.. :changelog:

Release History
===============

1.0.0b1
+++++++
* Add ``workload-space up`` to deploy a complete runtime composition through an incremental ARM deployment.
* Support managed AKS by default or an existing AKS cluster with ACI execution and runtime-link subnets.
* Default ``workload-space up`` to the configured location or the resource group location when ``--location`` is omitted.
* Support ``PodSnapshotRestore`` in ``workload-space capability create --kind``.
* Support an optional ``--subnet-resource-id`` in ``workload-space runtime-link create``.

0.1.0
++++++
* Initial release of the Workload Manager extension.
* Add commands to manage workload spaces, capabilities, runtime bindings, and runtime links.