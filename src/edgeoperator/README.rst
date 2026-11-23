Microsoft Azure CLI ``edgeoperator`` Extension
==============================================

This package provides Azure CLI commands for Azure Local Disconnected Operations.

Use ``az aldo system-readiness show`` to retrieve the current system readiness status.

The command uses the public `Microsoft.EdgeOperator SystemReadiness REST API specification <https://github.com/Azure/azure-rest-api-specs/tree/main/specification/edgeoperator/resource-manager/Microsoft.EdgeOperator/SystemReadiness>`_.

Use ``az aldo observability-configuration show`` to retrieve the active observability configuration.

The command uses the public `Microsoft.EdgeOperator ObservabilityConfiguration REST API specification <https://github.com/Azure/azure-rest-api-specs/tree/main/specification/edgeoperator/resource-manager/Microsoft.EdgeOperator/ObservabilityConfiguration>`_.

Use ``az aldo system-configuration show`` to retrieve the active system configuration.

Use ``az aldo system-configuration create`` to create or fully replace the configuration with
``--dns-forwarder-ip``, ``--connection-intent``, ``--stamp-id``, and ``--device-resource-id``.
This command uses PUT, not PATCH: omitted writable fields are not preserved. Supply all writable
values on every PUT; the service requires all four. Both commands require the Operator subscription.

The commands use the public `Microsoft.EdgeOperator SystemConfiguration REST API specification <https://github.com/Azure/azure-rest-api-specs/tree/main/specification/edgeoperator/resource-manager/Microsoft.EdgeOperator/SystemConfiguration>`_.

Use ``az aldo log-collection collect`` or ``az aldo log-collection collect-indirect`` to collect logs for a
time range. Both commands wait for the job to finish and return it; with ``--no-wait``, use
``az aldo log-collection list --from-date`` to find the job and ``az aldo log-collection wait`` to wait for it.
Use ``az aldo log-collection show`` to retrieve a job by its GUID.
For indirect collection, ``--save-to-path`` must be an absolute UNC path to a file share
accessible to the backend, for example ``\\fileserver\share\logs``.

The commands use the public `Microsoft.EdgeOperator LogCollections REST API specification <https://github.com/Azure/azure-rest-api-specs/tree/301e9ae1f39ceef22c00ddcb169b2635ae3e71c4/specification/edgeoperator/resource-manager/Microsoft.EdgeOperator/LogCollections>`_
at commit ``301e9ae1f39ceef22c00ddcb169b2635ae3e71c4`` (API version ``2026-06-01-preview``).
Log collection commands require the Operator subscription.
