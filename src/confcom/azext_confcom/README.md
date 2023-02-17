# Microsoft Azure CLI 'confcom' Extension Examples and Security Policy Rules Documentation

- [Microsoft Azure CLI 'confcom' Extension Examples and Security Policy Rules Documentation](#microsoft-azure-cli-confcom-Extension-examples-and-security-policy-rules-documentation)
  - [Microsoft Azure CLI 'confcom' Extension Examples](#microsoft-azure-cli-confcom-extension-examples)
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
      - [fragments](#fragments)
      - [reason](#reason)
      - [A Sample Policy that Uses Framework](#a-sample-policy-that-uses-framework)
      - [allow_properties_access](#a-sample-policy-that-uses-framework)
      - [allow_dump_stack](#a-sample-policy-that-uses-framework)
      - [allow_runtime_logging](#a-sample-policy-that-uses-framework)
      - [allow_environment_variable_dropping](#allow_environment_variable_dropping)
      - [allow_unencrypted_scratch](#allow_unencrypted_scratch)

      


## Microsoft Azure CLI 'confcom' Extension Examples 

Run `az confcom acipolicygen --help` to see a list of supported arguments along with explanations. The following commands demonstrate the usage of different arguments to generate confidential computing security policies. 

**Note:** The Azure Confidential Computing CLI extension is in public preview and is subject to change. Some arguments may be added or removed and the way `confcom acipolicygen` command is called to achieve specific functionality may change as well. This documentation will be updated as changes to the tooling are published. 

**Prerequisites:**
Install the Azure CLI and Confidential Computing extension. 

See the most recently released version of `confcom` extension.

    az extension list-available -o table | grep confcom 

To add the most recent confcom extension, run:

    az extension add --name confcom

Use the `--version` argument to specify a version to add. 


The `acipolicygen` command generates confidential computing security policies using an image, an input JSON file, or an ARM template. You can control the format of the generated policies using arguments. Note: It is recommended to use images with specific tags instead of the `latest` tag, as the `latest` tag can change at any time and images with different configurations may also have the latest tag.

**Examples:**

Example 1: The following command creates a CCE policy and outputs it to the command line: <br /> 

    az confcom acipolicygen -a .\template.json --print-policy

This command combines the information of images from the ARM template with other information such as mount, environment variables and commands from the ARM template to create a CCE policy. 
The `--print-policy` argument is included to display the policy on the command line rather than injecting it into the input ARM template.

Example 2: This command injects a CCE policy into [ARM-template](arm.template.md) based on input from [parameters-file](template.parameters.md) so that there is no need to change the ARM template to pass variables into the CCE policy: <br />

    az confcom acipolicygen -a .\arm-template.json -p .\template.parameters.json

This is mainly for decoupling purposes so that an ARM template can remain the same and evolving variables can go into a different file. 

Example 3: This command takes the input of an ARM template to create a human-readable CCE policy in pretty print JSON format and output the result to the console. 
NOTE: Generating JSON policy is for use by the customer only, and is not used by ACI In most cases. The default REGO format security policy is required. <br />

    az confcom acipolicygen -a ".\arm_template" --outraw-pretty-print --json

The default output of `acipolicygen` command is base64 encoded REGO format. 
This example uses the `--json` argument to generate output in JSON format, use `--outraw-pretty-print` to indicate decoding policy in clear text and in pretty print format and print result to console. 

Example 4: The following command takes the input of an ARM template to create a human-readable CCE policy in clear text and print to console: <br />
    
    az confcom acipolicygen -a ".\arm-template.json" --outraw

Use `--outraw` argument to output policy in clear text compact REGO format.

Example 5: Input an ARM template to create a human-readable CCE policy in pretty print REGO format and save the result to a file named ".\output-file.rego": <br />

    az confcom acipolicygen -a ".\arm-template" --outraw-pretty-print --save-to-file ".\output-file.rego"

Example 6: Validate the policy present in the ARM template under "ccepolicy" and the containers within the ARM template are compatible. If they are incompatible, a list of reasons is given and the exit status code will be 2: <br />

    az confcom acipolicygen -a ".\arm-template.json" --diff

Example 7: Decode the existing CCE policy in ARM template and print to console in clear text. 

    az confcom acipolicygen -a ".\arm-template.json" --print-existing-policy

Example 8: Generate a CCE policy using `--disable-stdio` argument. 
`--disable-stdio` argument disables container standard I/O access by setting `allow_stdio_access` to false. 

    az confcom acipolicygen -a ".\arm-template.json" --disable-stdio

Example 9: Inject a CCE policy into ARM template. 
This command adds the `--debug-mode` argument to enable executing /bin/sh and /bin/bash in the container group: <br />

    az confcom acipolicygen -a .\sample-arm-input.json --debug-mode

In the above example, The `--debug-mode` modifies the following to allow users to shell into the container via portal or the command line:

1. Adds the following to container rule so that users can access bash process. 

```
   "exec_processes": [
      {
        "command": [
          "/bin/sh"
        ],
        "signals": []
      },
      {
        "command": [
          "/bin/bash"
        ],
        "signals": []
      }
    ]
```
2. Changes the values of these three rules to true on the policy. 
This is also for the purpose of allowing users to access logging, container properties and dump stack,  all of which are part of loggings as well. 
See [A Sample Policy that Uses Framework](#a-sample-policy-that-uses-framework) for details for the following rules: 

    - allow_properties_access
    - allow_dump_stacks
    - allow_runtime_logging
    
    
Example 10: The confidential computing extension CLI is designed in such a way that generating policy does not necessarily have to depend on network calls as long as users have the layers of the images they want to generate policies for saved in a tar file locally. See the following example: <br />

    docker save ImageTag -o file.tar

Disconnect from network and delete the local image from the docker daemon.
Use the following command to generate CCE policy for the image. 

    az confcom acipolicygen -a .\sample-template-input.json --tar .\file.tar

Some users have unique scenarios such as cleanroom requirement. 
In this case, users can still generate security policies witout relying on network calls. 
Users just need to make a tar file by using the `docker save` command above, include the `--tar` argument when making the `acipolicygen` command and make sure the input JSON file contains the same image tag. 

When generating security policy without using `--tar` argument, the confcom extension CLI tool attemps to fetch the image remotely if it is not locally available. 
However, the CLI tool does not attempt to fetch remotely if `--tar` argument is used. 

## Security Policy Rules Documentation

Below is an example rego policy: 

```
package policy

import future.keywords.every
import future.keywords.in

api_svn := "0.10.0" 
framework_svn := "0.1.0"

fragments := [...]

containers := [...]

allow_properties_access := false
allow_dump_stacks := false
allow_runtime_logging := false
allow_environment_variable_dropping := true
allow_unencrypted_scratch := false



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

Every valid policy contain rules with the following names in the policy namespace. 
Each rule must return a Rego object with a member named allowed, which indicates whether the action is allowed by policy. 
We document each rule as follow: 

## mount_device
Receives an input object with the following members:
```
{
    "name": "mount_device",
    "target": "<path>",
    "deviceHash": "<dm-verity root hash>"
}
```

## unmount_device
Receives an input object with the following members:
```
{
    "name": "unmount_device",
    "unmountTarget": "<path>"
}
```

## mount_overlay
Describe the layers to mount: 
```
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
```
{
    "name": "unmount_overlay",
    "unmountTarget": "<target>"
}
```

## create_container 
Indicates whether the UVM is allowed to create a specific container with the exact parameters provided to the method. 
Provided in the following input object, the framework rule checks the exact parameters such as (command, environment variables, mounts etc.) 
```
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
    privileged: "<true|false>"
}
```

## exec_in_container
Determines if a process should be executed in a container. 
Receives an input object with the following elements: 
```
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
Determines if a process should be executed in the UVM. 
Receives an input object with the following elements:
```
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
```
{
    "name": "shutdown_container",
    "containerID": "<unique container ID>"
}
```

## signal_container_process
Describe the signal sent to the container. 
Receives an input object with the following elements:
```
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
Controls what directories on the host are allowed to be mounted into the UVM so that they can later be used as mounts within containers. 
Azure confidential computing evaluated the mount channel from host machine to guest machine and eventually to containers. 
A serious attack consists of overwriting attested directories on the UVM and then subsequently gets loaded into containers. 
This rule contains a target that designates destination mount so that the mentioned attack does not happen. 
It receives an input with the following elements:
```
{
    "name": "plan9_mount",
    "target": "<target>"
}
```

## plan9_unmount
Receives an input with the following elements:
```
{
    "name": "plan9_unmount",
    "unmountTarget": "<target>"
}
```

## scratch_mount
Scratch is writable storage from the UVM to the container. 
It receives an input with the following elements:
```
{
    "name": "scratch_mount",
    "target": "<target>",
    "encrypted": "true|false"
}
```

## scratch_unmount
Receives an input with the following elements:
```
{
    "name": "scratch_unmount",
    "unmountTarget": "<target>",
}
```

## load_fragment
This rule is used to determine whether a fragment can be loaded. 
See [fragments](#fragments) for detailed explanation. 

## fragments

What is a fragment? 

Confidential Container provides the core primitives for allowing customers to build container based application solutions that leave Microsoft and Microsoft operators outside of TCB(Trusted Computing Base). 
In order to achieve this, our environment has to implement enforcement policies that not only dictates which containers are allowed to run, but also the explicit versions of each container that are allowed to run. 
The implication of this is that in the case of Confidential ACI, if the customer is allowing ACI provided sidecars into their TCB, the customer environment won't be able to be start if ACI updates any of their sidecars for regular maintenance. 
Given that some customers will want to allow ACI sidecars into their trusted environment, we need to provide a way for customers to indicate a level of trust in ACI so that sidecars that ACI has indicated are theirs and that the customer has agreed to accept can be run. 
In order to achieve this, We will allow additional constraints to be provided to a container environment. 
And we call these additionally defined constraints "fragments". 
Fragments can serve a number of use-cases. 
For now, we will focus on the ACI sidecar use case. 
See the following example and how it defines a fragment. 
The following fragment states that my confidential computing environment should trust containers published by the DID `did:web:accdemo.github.io` on the feed named `accdemo/utilities`. 

```
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

Every time a fragment is presented to the enclosing system (e.g. GCS), the enclosing system is provided with a COSE_Sign1 signed envelope. 
The header in the envelope contains the feed and the issuer and these information are included in the `input` context. 
The logic of load_fragment rule selects a fragment from the list of fragments which matches the issuer and feed. 
The enclosing system loads the fragment and queries it for the `includes` e.g. `container` and inserts them into the data context for later use.

## reason
A policy can optionally define this rule, which will be called when a policy issues a denial. 
This is used to populate an informative error message.

## A Sample Policy that Uses Framework

A more detailed explanation is provided for the following rules that seem to appear more than once on the CCE policy:
`allow_properties_access`, `get_properties`, `allow_dump_stack`, `dump_stack`, `allow_runtime_logging` and `runtime_logging`

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

`allow_dump_stack` VS `dump_stack`
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








