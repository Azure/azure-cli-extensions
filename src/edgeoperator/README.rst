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
