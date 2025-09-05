# Enforcement Points

- [Security Policy Rules Documentation](#security-policy-rules-documentation)
  - [mount_device](#mount_device)
  - [unmount_device](#unmount_device)
  - [mount_overlay](#mount_overlay)
  - [unmount_overlay](#unmount_overlay)
  - [create_container](#create_container)
  - [exec_in_container](#exec_in_container)
  - [exec_external](#exec_external)
  - [shutdown_container](#shutdown_container)
  - [signal_container_process](#signal_container_process)
  - [plan9_mount](#plan9_mount)
  - [plan9_unmount](#plan9_unmount)
  - [scratch_mount](#scratch_mount)
  - [scratch_unmount](#scratch_unmount)
  - [load_fragment](#load_fragment)
  - [policy fragments](#policy-fragments)
  - [reason](#reason)
  - [A Sample Policy that Uses Framework](#a-sample-policy-that-uses-framework)
  - [allow_properties_access](#a-sample-policy-that-uses-framework)
  - [allow_dump_stack](#a-sample-policy-that-uses-framework)
  - [allow_runtime_logging](#a-sample-policy-that-uses-framework)
  - [allow_environment_variable_dropping](#allow_environment_variable_dropping)
  - [allow_unencrypted_scratch](#allow_unencrypted_scratch)
  - [allow_capabilities_dropping](#allow_capabilities_dropping)

## Security Policy Rules Documentation

This document describes every enforcement point that a security policy must implement and the input each rule receives.
All rules live in the policy's namespace and must return an object with at least the member allowed (boolean) that states whether the requested action is permitted.

Below is an example rego policy:

```rego
package mypolicy

import future.keywords.every
import future.keywords.in

api_version := "0.10.0"
framework_version := "0.1.0"

fragments := [...]

containers := [...]

allow_properties_access := true
allow_dump_stacks := false
allow_runtime_logging := false
allow_environment_variable_dropping := true
allow_unencrypted_scratch := false
allow_capabilities_dropping := true



mount_device := data.framework.mount_device
unmount_device := data.framework.unmount_device
mount_overlay := data.framework.mount_overlay
unmount_overlay := data.framework.unmount_overlay
create_container := data.framework.create_container
exec_in_container := data.framework.exec_in_container
exec_external := data.framework.exec_external
shutdown_container := data.framework.shutdown_container
signal_container_process := data.framework.signal_container_process
plan9_mount := data.framework.plan9_mount
plan9_unmount := data.framework.plan9_unmount
get_properties := data.framework.get_properties
dump_stacks := data.framework.dump_stacks
runtime_logging := data.framework.runtime_logging
load_fragment := data.framework.load_fragment
scratch_mount := data.framework.scratch_mount
scratch_unmount := data.framework.scratch_unmount

reason := {"errors": data.framework.errors}
```

We document each rule as follows:

## mount_device

Receives an input object with the following members:

```json
{
    "name": "mount_device",
    "target": "<path>",
    "deviceHash": "<dm-verity root hash>"
}
```

## unmount_device

Receives an input object with the following members:

```json
{
    "name": "unmount_device",
    "unmountTarget": "<path>"
}
```

## mount_overlay

Describe the layers to mount:

```json
{
    "name": "mount_overlay",
    "containerID": "<unique ID for the container>",
    "layerPaths": [
        "<path>",
        "<path>",
        "<path>",
        /*...*/
    ],
    "target": "<target>"
}
```

## unmount_overlay

Receives an input object with the following members:

```json
{
    "name": "unmount_overlay",
    "unmountTarget": "<target>"
}
```

## create_container

Indicates whether the UVM (Utility-VM) is allowed to create a specific container with the exact parameters provided to the method.
Provided in the following input object, the framework rule checks the exact parameters such as (command, environment variables, mounts etc.)

```json
{
    "name": "create_container",
    "containerID": "<unique container ID>",
    "argList": [
        "<command>",
        "<arg0>",
        "<arg1>",
        /*...*/
    ],
    "envList": [
        "<env>=<value>",
        /*...*/
    ],
    "workingDir": "<path>",
    "sandboxDir": "<path>",
    "hugePagesDir": "<path>",
    "mounts": [
        {
            "destination": "<path>",
            "options": [
                "<option0>",
                "<option1>",
                /*...*/
            ],
            "source": "<uri>",
            "type": "<mount type>"},
    ],
    "privileged": "<true|false>"
}
```

## exec_in_container

Determines if a process should be executed in a container based on its command, arguments, environment variables, and working directory.
Receives an input object with the following elements:

```json
{
    "containerID": "<unique container ID>",
    "argList": [
        "<command>",
        "<arg0>",
        "<arg1>",
        /*...*/
    ],
    "envList": [
        "<env>=<value>",
        /*...*/
    ],
    "workingDir": "<path>"
}
```

## exec_external

Determines whether a process may run directly inside the UVM, outside of the container sandbox.
Receives an input object with the following elements:

```json
{
    "name": "exec_external",
    "argList": [
        "<command>",
        "<arg0>",
        "<arg1>",
        /*...*/
    ],
    "envList": [
        "<env>=<value>",
        /*...*/
    ],
    "workingDir": "<path>"
}
```

## shutdown_container

Receives an input object with the following elements:

```json
{
    "name": "shutdown_container",
    "containerID": "<unique container ID>"
}
```

## signal_container_process

Describe the signal sent to the container.
Receives an input object with the following elements:

```json
{
    "name": "signal_container_process",
    "containerID": "<unique container ID>",
    "signal": "<signal ID>",
    "isInitProcess": "<true|false>",
    "argList":  [
        "<command>",
        "<arg0>",
        "<arg1>",
        /*...*/
    ]
}
```

## plan9_mount

Controls which host directories may be mounted via the 9P (Plan 9) protocol into the UVM, so that the UVM can bind‑mount those directories into containers later.
Azure Confidential Computing evaluates this host → UVM → container path because an attacker could overwrite an attested directory on the UVM and have malicious data flow into containers.
The target field therefore designates exactly where the mount is created, allowing the policy to block dangerous destinations.
It receives an input with the following elements:

```json
{
    "name": "plan9_mount",
    "target": "<target>"
}
```

## plan9_unmount

Receives an input with the following elements:

```json
{
    "name": "plan9_unmount",
    "unmountTarget": "<target>"
}
```

## scratch_mount

Scratch is writable storage from the UVM to the container.
It receives an input with the following elements:

```json
{
    "name": "scratch_mount",
    "target": "<target>",
    "encrypted": "true|false"
}
```

## scratch_unmount

Receives an input with the following elements:

```json
{
    "name": "scratch_unmount",
    "unmountTarget": "<target>",
}
```

## load_fragment

This rule is used to determine whether a policy fragment can be loaded.
See [policy fragments](#policy-fragments) for detailed explanation.

## policy fragments

Why do we need policy fragments?

Confidential Containers provide the core primitives for allowing customers to build container-based application solutions that leave Microsoft and Microsoft operators outside of the TCB (Trusted Computing Base).

A policy fragment is a small, customer‑signed, COSE‑sealed Rego module that extends the baseline policy. The typical use‑case is to allow updated ACI sidecar images to run without widening the overall trust boundary or adding Microsoft operators to the TCB. In practice the fragment says:

> “Alongside the digests pinned in my baseline policy, I also trust images from feed X that is in the allowed list of signers.”

Because the fragment is signed by the customer and verified inside the guest, you stay in full control of what expands the trusted set—Microsoft does not gain new power over your TCB.

In order to achieve this, our environment has to implement enforcement policies that not only dictate which containers are allowed to run, but also the explicit versions of each container that are allowed to run.
The implication of this is that in the case of Confidential ACI, if the customer is allowing ACI provided sidecars into their TCB, the customer environment won't be able to be start if ACI updates any of their sidecars for regular maintenance.

Given that some customers will want to allow ACI sidecars into their trusted environment, we need to provide a way for customers to indicate a level of trust in ACI so that sidecars that ACI has indicated are theirs and that the customer has agreed to accept can be run.

In order to achieve this, We will allow additional constraints to be provided to a container environment.
And we call these additionally defined constraints "policy fragments".
Policy fragments can serve a number of use-cases.
For now, we will focus on the ACI sidecar use case.
See the following example and how it defines a policy fragment.
The following policy fragment states that my confidential computing environment should trust containers published by the DID `did:web:accdemo.github.io` on the feed named `accdemo/utilities`.

```rego
fragments := [
    {
        "feed": "accdemo/utilities",
        "iss": "did:web:accdemo.github.io",
        "includes": [<"containers"|"fragments"|"external_processes"|"namespace">]
    }
]

default load_fragment := []
load_fragment := includes {
    some fragment in fragments
    input.iss == fragment.iss
    input.feed == fragment.feed
    includes := fragment.includes
}
```

Every time a policy fragment is presented to the enclosing system (e.g. GCS), the enclosing system is provided with a COSE_Sign1 signed envelope.
The header in the envelope contains the feed and the issuer and these information are included in the `input` context.
The logic of load_fragment rule selects a policy fragment from the list of policy fragments which matches the issuer and feed.
The enclosing system loads the policy fragment and queries it for the `includes` e.g. `container` and inserts them into the data context for later use.

## reason

A policy can optionally define this rule, which will be called when a policy issues a denial.
This is used to populate an informative error message.

## A Sample Policy that Uses Framework

A more detailed explanation is provided for the following rules that seem to appear more than once on the CCE policy:
`allow_properties_access`, `get_properties`, `allow_dump_stacks`, `dump_stacks`, `allow_runtime_logging` and `runtime_logging`

Rego framework supports policy authors by both describing the form that user policies should take, and consequently the form that Microsoft-provided Rego modules will follow.
It also provides some pre-built policy components that can make policy authoring easier.
Microsoft provides a [Rego Framework](https://github.com/microsoft/hcsshim/blob/main/pkg/securitypolicy/framework.rego) to make writing policies easier.
It contains a collection of helper functions, which in turn provide default implementations of the required rules.
These functions operate on Rego data with expected formats.
We include a [sample policy](sample_policy.md) which uses this framework.

The difference between `allow_properties_access` vs `get_properties`:

There is an API that defines a rule called `get_properties`.
A custom user policy can implement this however it wants.
However, a policy that uses the framework indicates their desired behavior to the framework with a flag called `allow_get_properties`. If you look at the framework implementation for get_properties you will see that it returns data.policy.allow_get_properties.
The same logic applies to both dump_stack and runtime_logging.

`allow_properties_access` VS `get_properties`
When set to true, this indicates that `get_properties` should be allowed.
It indicates whether the host can fetch properties from a container.

`allow_dump_stacks` VS `dump_stacks`
When set to true, this indicates that `dump_stacks` should be allowed.

`allow_runtime_logging` VS `runtime_logging`
When `allow_runtime_logging` is set to true, this indicates that `runtime_logging` should be allowed.
Runtime logging is logging done by the UVM, i.e. outside of containers and their processes.

## allow_environment_variable_dropping

The allow_environment_variable_dropping flag allows the framework, if set, to try to drop environment variables if there are no matching containers/processes.
This is an important aspect of serviceability, as it allows customer policies to be robust to the addition of extraneous environment variables which are unused by their containers.
Note throughout this that the existing logic of required environment variables holds.
The logic of dropping env vars is a bit complex but in general the framework looks at the intersection of the set of provided variables and the environment variable rules of each container/process and finds the largest set, which happens to be the one that requires dropping the least number of env vars.
It then tests to see if that set satisfies any containers.

## allow_unencrypted_scratch

This rule determines whether unencrypted writable storage from the UVM to the container is allowed.

## allow_capabilities_dropping

Whether to allow capabilities to be dropped in the same manner as allow_environment_variable_dropping.