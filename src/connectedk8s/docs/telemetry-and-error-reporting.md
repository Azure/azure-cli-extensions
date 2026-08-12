# ConnectedK8s Telemetry and Error Reporting

This document describes the shared telemetry and customer-facing error reporting
constructs used by the `connectedk8s` Azure CLI extension.

## Goals

The construct provides:

- A connected-cluster ARM resource ID on extension telemetry events.
- Stable `AZK8Snnnn` error codes.
- Consistent error names and customer-facing messages.
- Existing `fault_type` compatibility for ADX queries.
- One rendered message shared by telemetry and the CLI exception shown to the customer.
- Optional troubleshooting links.

The error catalog is intentionally incremental. Definitions can be added before
their existing call sites are migrated.

## Components

| Component | Location | Purpose |
|---|---|---|
| ARM ID context | `_utils.py :: set_connected_cluster_arm_id_telemetry_context` | Builds and stores the connected-cluster ARM ID for the command |
| Event wrapper | `_utils.py :: add_connectedk8s_telemetry_event` | Adds the stored ARM ID to extension event properties |
| Error catalog | `_errors.py` | Defines stable error codes, names, messages, fault types, exception classes, and optional TSG links |
| Error reporter | `_utils.py :: report_connectedk8s_error` | Emits standardized telemetry and returns the matching CLI exception |
| Helm timeout reporter | `_utils.py :: report_helm_timeout_error` | Reports classified Helm timeout diagnostics through the standard reporter |

## High-level flow

```text
Command entry
    |
    | set_connected_cluster_arm_id_telemetry_context(...)
    v
cmd.cli_ctx.data["connectedk8s_arm_id"]
    |
    +-------------------------------+
    |                               |
    v                               v
add_connectedk8s_telemetry_event    report_connectedk8s_error
    |                               |
    | adds resourceid               | renders ArcError once
    v                               |
extension event                     +--> extension event with ARM ID
                                    +--> telemetry.set_exception
                                    +--> returned AzCLIError
                                             |
                                             v
                                      customer console
```

## ARM ID telemetry context

Commands that operate on a named connected cluster should establish the ARM ID
context near command entry:

```python
utils.set_connected_cluster_arm_id_telemetry_context(
    cmd,
    resource_group_name,
    cluster_name,
)
```

For custom-token flows, pass the subscription ID explicitly:

```python
utils.set_connected_cluster_arm_id_telemetry_context(
    cmd,
    resource_group_name,
    cluster_name,
    subscription_id,
)
```

The helper builds:

```text
/subscriptions/<subscription-id>
/resourceGroups/<resource-group>
/providers/Microsoft.Kubernetes/connectedClusters/<cluster-name>
```

and stores it in:

```python
cmd.cli_ctx.data[consts.Connected_Cluster_Arm_Id_Telemetry_Context_Key]
```

## Emitting a regular telemetry event

Use the wrapper instead of calling `telemetry.add_extension_event` directly:

```python
utils.add_connectedk8s_telemetry_event(
    cmd,
    {
        "Context.Default.AzureCLI.AgentVersion": agent_version,
    },
)
```

The wrapper copies the supplied dictionary and adds:

```text
Context.Default.AzureCLI.resourceid
```

when the command has an ARM ID context. It does not mutate the caller's
dictionary.

Passing `cmd=None` is supported for code paths that do not have cluster context,
but those events cannot include the connected-cluster ARM ID.

## Standard error definitions

Errors are defined once in `_errors.py`:

```python
INVALID_GATEWAY_ARM_ID = _define(
    code="AZK8S0106",
    name="InvalidGatewayArmId",
    description="The supplied Gateway ARM resource ID is invalid.",
    fault_type=consts.Gateway_ArmId_Is_Invalid_Fault_Type,
    az_error_cls=InvalidArgumentValueError,
)
```

### Required values

| Field | Description |
|---|---|
| `code` | Stable public code in `AZK8Snnnn` format |
| `name` | Stable, human-readable error name |
| `description` / `message` | Customer-facing message template |
| `fault_type` | Stable telemetry grouping value |

### Optional values

| Field | Description |
|---|---|
| `az_error_cls` | Azure CLI exception class; defaults to `CLIInternalError` |
| `fault_type_aliases` | Legacy fault types that should resolve to the same AZK8S error |
| `tsg_link` | Troubleshooting or documentation URL |

Use a `consts.*_Fault_Type` constant in a definition rather than copying a
string:

```python
fault_type=consts.Install_HelmRelease_Fault_Type
```

The field is typed as `str` because Azure CLI telemetry expects a string.
Referencing a constant prevents spelling drift and preserves existing ADX
queries.

Fault types should be stable identifiers, not customer messages or format
templates:

```python
# Correct
Gateway_ArmId_Is_Invalid_Fault_Type = "invalid-gateway-arm-id"

# Customer-facing template; not a fault type
Gateway_ArmId_Is_Invalid = (
    "The provided Gateway ArmID in --gateway-resource-id {} is invalid."
)
```

The `{}` or `{details}` placeholders are normal Python message substitution.
They are unrelated to ARM ID telemetry enrichment.

## Reporting a fatal error

Use `report_connectedk8s_error` when the operation must terminate:

```python
try:
    perform_operation()
except Exception as ex:
    raise utils.report_connectedk8s_error(
        cmd,
        errors.CONNECTED_CLUSTER_UPDATE_FAILED,
        exception=ex,
        details=str(ex),
    ) from ex
```

For a user-caused failure:

```python
raise utils.report_connectedk8s_error(
    cmd,
    errors.INVALID_ARGUMENT_VALUE,
    exception=ex,
    user_fault=True,
    details=str(ex),
) from ex
```

Additional event properties can be preserved during migration:

```python
raise utils.report_connectedk8s_error(
    cmd,
    errors.HELM_RELEASE_INSTALL_FAILED,
    exception=ex,
    telemetry_properties={
        consts.Telemetry_Onboarding_Error_Type_Key: existing_fault_type,
        consts.Telemetry_Onboarding_Error_Message_Key: existing_message,
    },
    operation="install",
    details=str(ex),
) from ex
```

The function returns an exception instead of raising it so callers can preserve
normal Python exception chaining with `raise ... from ex`.

## What the reporter emits

`report_connectedk8s_error` renders the message once and uses that value for the
extension event, telemetry summary, and CLI exception.

Example customer output:

```text
[AZK8S0506] AgentStateTimeout: Timed out waiting for the Azure Arc agent state during create.
```

Standard extension-event properties:

| Property | Source |
|---|---|
| `Context.Default.AzureCLI.resourceid` | Command ARM ID context |
| `Context.Default.AzureCLI.errorCode` | `ArcError.code` |
| `Context.Default.AzureCLI.errorFaultType` | Canonical or overridden fault type |
| `Context.Default.AzureCLI.errorName` | `ArcError.name` |
| `Context.Default.AzureCLI.errorMessage` | Fully rendered customer message |
| `Context.Default.AzureCLI.errorTsgLink` | Optional `ArcError.tsg_link` |

The reporter also calls:

```python
telemetry.set_exception(
    exception=exception,
    fault_type=error.fault_type,
    summary=rendered_message,
)
```

This retains Azure CLI's reserved fault fields while the extension event carries
the structured AZK8S fields and connected-cluster ARM ID.

## Non-fatal diagnostics

Some catalog entries describe informational or non-fatal diagnostics and have
`az_error_cls=None`. Calling `as_error()` for one of these definitions raises a
developer-facing `ValueError` instead of accidentally terminating the command.

For non-fatal telemetry, use the event wrapper:

```python
utils.add_connectedk8s_telemetry_event(
    cmd,
    {
        consts.Telemetry_Error_Code_Key: errors.DNS_NXDOMAIN.code,
        consts.Telemetry_Error_Fault_Type_Key: errors.DNS_NXDOMAIN.fault_type,
        consts.Telemetry_Error_Name_Key: errors.DNS_NXDOMAIN.name,
        consts.Telemetry_Error_Message_Key: errors.DNS_NXDOMAIN.format(
            details=details
        ),
    },
)
```

Do not call `report_connectedk8s_error` for a non-raising definition because
that helper is intended for command-terminating errors.

## Looking up definitions

Look up by public error code:

```python
error = errors.get_error("AZK8S0506")
```

Look up by an existing telemetry fault type:

```python
error = errors.get_error_by_fault_type(
    consts.Agent_State_Timeout_Fault_Type
)
```

The fault-type lookup includes values listed in `fault_type_aliases`.

## Adding a new error

1. Select an unused code in the appropriate range.
2. Add or reuse a stable fault-type constant in `_constants.py`.
3. Add a definition in `_errors.py`.
4. Add the definition to `ALL_ERRORS`.
5. Use `report_connectedk8s_error` at the fatal call site, or the event wrapper
   for a non-fatal diagnostic.
6. Pass `cmd` through helper layers so the ARM ID is retained.
7. Preserve an existing fault type through the definition or
   `fault_type_aliases`; do not silently rename telemetry dimensions.

Example:

```python
NEW_OPERATION_FAILED = _define(
    code="AZK8S0806",
    name="NewOperationFailed",
    description="The new operation failed.",
    fault_type=consts.New_Operation_Failed_Fault_Type,
    az_error_cls=CLIInternalError,
    tsg_link="https://aka.ms/example-tsg",
)
```

## Migration checklist

When migrating an existing error path:

- Keep the existing `fault_type` unless an intentional telemetry migration is
  planned.
- Move customer wording into the error definition.
- Pass dynamic context using named placeholders such as `{details}` or
  `{operation}`.
- Replace direct `telemetry.add_extension_event` calls with
  `add_connectedk8s_telemetry_event`.
- Replace paired `telemetry.set_exception` and `raise AzCLIError(...)` calls
  with `raise report_connectedk8s_error(...)`.
- Set `user_fault=True` where the existing path calls
  `telemetry.set_user_fault()`.
- Pass existing extension-event properties through `telemetry_properties`.
- Ensure the command establishes ARM ID context before the failure can occur.
- Verify the console message, telemetry summary, and extension-event
  `errorMessage` are identical.

## Current scope

The shared reporter is currently used by the command catch-all, agent-state
timeouts, Helm operation failures, and classified Helm timeout failures.
Pre-onboarding and troubleshoot extension events use the ARM ID-aware event
wrapper.

The catalog contains the supplied error-code allocation across the
`AZK8S0001` through `AZK8S0805` ranges, but not every historical call site has
been migrated.
