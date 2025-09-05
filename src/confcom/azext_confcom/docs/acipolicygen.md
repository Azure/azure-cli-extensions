# acipolicygen

- [Microsoft Azure CLI 'confcom acipolicygen' Extension Examples](#microsoft-azure-cli-confcom-acipolicygen-extension-examples)
- [AKS Virtual Node (VN2)](#aks-virtual-node)

## Microsoft Azure CLI 'confcom acipolicygen' Extension Examples

Run `az confcom acipolicygen --help` to see a list of supported arguments along with explanations.
The following commands demonstrate the usage of different arguments to generate confidential computing security policies.

### Prerequisites

View the [common documentation](./common.md) for information on how to install the `confcom` extension.

The `acipolicygen` command generates confidential computing security policies using an image, an input JSON file, or an ARM template.
You can control the format of the generated policies using arguments.
Note: It is recommended to use images with specific tags instead of the `latest` tag, as the `latest` tag can change at any time and images with different configurations may also have the latest tag.

### Examples

#### Example 1

The following command creates a CCE policy and outputs it to the command line:

```bash
az confcom acipolicygen -a .\template.json --print-policy
```

This command combines the information of images from the ARM template with other information such as mount, environment variables and commands from the ARM template to create a CCE policy.
The `--print-policy` argument is included to display the policy on the command line rather than injecting it into the input ARM template.

#### Example 2

This command injects a CCE policy into [ARM-template](arm.template.md) based on input from [parameters-file](template.parameters.md) so that there is no need to change the ARM template to pass variables into the CCE policy:

```bash
az confcom acipolicygen -a .\arm-template.json -p .\template.parameters.json
```

This is mainly for decoupling purposes so that an ARM template can remain the same and evolving variables can go into a different file.
When a security policy gets injected into the ARM Template, the corresponding sha256 hash of the decoded security policy gets printed to the command line.
This sha256 hash can be used for verifying the hostdata field of the SEV-SNP Attestation Report and/or used for key release policies using MAA (Microsoft Azure Attestation) or mHSM (managed Hardware Security Module)

#### Example 3

This command takes the input of an ARM template to create a human-readable CCE policy in pretty print JSON format and output the result to the console.
NOTE: Generating JSON policy is for use by the customer only, and is not used by ACI in most cases.
The default REGO format security policy is required.

```bash
az confcom acipolicygen -a ".\arm_template" --outraw-pretty-print
```

The default output of `acipolicygen` command is base64 encoded REGO format.
This example uses `--outraw-pretty-print` to indicate decoding policy in clear text with pretty print format and to print result to console.

#### Example 4

The following command takes the input of an ARM template to create a human-readable CCE policy in clear text and print to console:

```bash
az confcom acipolicygen -a ".\arm-template.json" --outraw
```

Use `--outraw` argument to output policy in clear text compact REGO format.

#### Example 5

Input an ARM template to create a human-readable CCE policy in pretty print REGO format and save the result to a file named ".\output-file.rego":

```bash
az confcom acipolicygen -a ".\arm-template" --outraw-pretty-print --save-to-file ".\output-file.rego"
```

#### Example 6

Validate the policy present in the ARM template under "ccepolicy" and the containers within the ARM template are compatible.
If they are incompatible, a list of reasons is given and the exit status code will be 2:

```bash
az confcom acipolicygen -a ".\arm-template.json" --diff
```

#### Example 7

Decode the existing CCE policy in ARM template and print to console in clear text.

```bash
az confcom acipolicygen -a ".\arm-template.json" --print-existing-policy
```

#### Example 8

Generate a CCE policy using `--disable-stdio` argument.
`--disable-stdio` argument disables container standard I/O access by setting `allow_stdio_access` to false.

```bash
az confcom acipolicygen -a ".\arm-template.json" --disable-stdio
```

#### Example 9

Inject a CCE policy into ARM template.
This command adds the `--debug-mode` argument to enable executing /bin/sh and /bin/bash in the container group:

```bash
az confcom acipolicygen -a .\sample-arm-input.json --debug-mode
```

In the above example, The `--debug-mode` modifies the following to allow users to shell into the container via portal or the command line:

1. Adds the following to container rule so that users can access bash process.

```json
"exec_processes": [
    {
        "command": ["/bin/sh"],
        "signals": []
    },
    {
        "command": ["/bin/bash"],
        "signals": []
    }
]
```

2. Changes the values of these three rules to true on the policy.
This is also for the purpose of allowing users to access logging, container properties and dump stack, all of which are part of loggings as well.
See [A Sample Policy that Uses Framework](./policy_enforcement_points.md) for details for the following rules:

    - allow_properties_access
    - allow_dump_stacks
    - allow_runtime_logging

#### Example 10

The confidential computing extension CLI is designed in such a way that generating a policy does not necessarily have to depend on network calls as long as users have the layers of the images they want to generate policies for saved in a tar file locally.
See the following example:

```bash
docker save ImageTag -o file.tar
```

Disconnect from network and delete the local image from the docker daemon.
Use the following command to generate CCE policy for the image.

```bash
az confcom acipolicygen -a .\sample-template-input.json --tar .\file.tar
```

Some users have unique scenarios such as cleanroom requirement.
In this case, users can still generate security policies without relying on network calls.
Users just need to make a tar file by using the `docker save` command above, include the `--tar` argument when making the `acipolicygen` command and make sure the input JSON file contains the same image tag.

When generating security policy without using `--tar` argument, the confcom extension CLI tool attempts to fetch the image remotely if it is not locally available.
However, the CLI tool does not attempt to fetch remotely if `--tar` argument is used.

#### Example 11

If it is necessary to put images in their own tarballs, an external file can be used that maps images to their respective tarball paths.
See the following example:

```bash
docker save image:tag1 -o file1.tar
docker save image:tag2 -o file2.tar
docker save image:tag3 -o file3.tar
```

Create the following file (as an example named "tar_mappings.json") on the local filesystem:

```json
{
    "image:tag1": "./file1.tar",
    "image:tag2": "./file2.tar",
    "image:tag3": "./file3.tar"
}
```

Disconnect from network and delete the local image from the docker daemon.
Use the following command to generate CCE policy for the image.

```bash
az confcom acipolicygen -a .\sample-template-input.json --tar .\tar_mappings.json
```

#### Example 12

Some use cases necessitate the use of regular expressions to allow for environment variables where either their values are secret, or unknown at policy-generation time.
For these cases, the workflow below can be used:

Create parameters in the ARM Template for each environment variable that has an unknown or secret value such as:

```json
{
    "parameters": {
        "placeholderValue": {
            "type": "string",
            "metadata": {
                "description": "This value will not be placed in the template.json"
            }
        }
    },
}
```

Note that this parameter declaration does not have a "defaultValue".
Once these parameters are defined, they may be used later in the ARM Template such as:

```json
{
    "environmentVariables": [
        {
            "name": "PATH",
            "value": "/customized/path/value"
        },
        {
            "name": "MY_SECRET",
            "value": "[parameters('placeholderValue')]"
        }
    ]
}
```

The policy can then be generated with:

```bash
az confcom acipolicygen -a template.json
```

Because the ARM Template does not have a value defined for the "placeholderValue", the regular expression ".*" is used in the Rego policy.
This allows for any value to be used.
If the value is contained in a parameters file, that can be used when deploying such as:

```bash
az deployment group create --template-file "template.json" --parameters "parameters.json"
```

#### Example 13

Another way to add additional flexibility to a security policy is by using a "pure json" approach to the config file.
This gives the flexibility of using regular expressions for environment variables and including fragments without the need for the `--fragments-json` flag.
It uses the same format as `acifragmentgen` such that if there needs to be different deployments with similar configs, very few changes are needed.
Note that a unique name for each container is required.

```json
{
    "fragments": [
        {
            "feed": "contoso.azurecr.io/example",
            "includes": [
                "containers",
                "fragments"
            ],
            "issuer": "did:x509:0:sha256:mLzv0uyBNQvC6hi4y9qy8hr6NSZuYFv6gfCwAEWBNqc::subject:CN:Contoso",
            "minimum_svn": "1"
        }
    ],
    "containers": [
        {
            "name": "my-image",
            "properties": {
                "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9",
                "environmentVariables": [
                    {
                        "name": "PATH",
                        "value": "/customized/path/value"
                    },
                    {
                        "name": "TEST_REGEXP_ENV",
                        "value": "test_regexp_env(.*)",
                        "regex": true
                    }
                ],
                "execProcesses": [
                    {
                        "command": [
                            "ls"
                        ]
                    }
                ],
                "volumeMounts": [
                    {
                        "name": "mymount",
                        "mountPath": "/mount/mymount",
                        "mountType": "emptyDir",
                        "readOnly": false
                    }
                ],
                "command": [
                    "python3",
                    "main.py"
                ]
            }
        }
    ]
}
```

```bash
az confcom acipolicygen -i config.json
```

## AKS Virtual Node

Azure Kubernetes Service (AKS) allows pods to be scheduled on Azure Container Instances (ACI) using the [AKS Virtual Node](https://learn.microsoft.com/en-us/azure/aks/virtual-nodes) feature.
The `confcom` tooling can generate security policies for these ACI-based pods in the same way as for standalone ACI container groups.
The key difference is that the `confcom` tooling will ingest an AKS pod specification (`pod.yaml`) instead of an ARM Template.
When the AKS pod specification is deployed, it must have an annotation `microsoft.containerinstance.virtualnode.ccepolicy` denoting its security policy.
This annotation is automatically added to the yaml file when the policy is created.

### Examples

#### Example 1

Use the following command to generate and print a security policy for an AKS pod running on ACI:

```bash
az confcom acipolicygen --virtual-node-yaml ./pod.yaml --print-policy
```

Where `pod.yaml` is a Kubernetes Pod resource:

```yaml
apiVersion: v1
kind: Pod
metadata:
    name: sample-mcr-pod
spec:
    containers:
        - name: helloworld
        image: mcr.microsoft.com/acc/samples/aci/helloworld:2.9
        ports:
            - containerPort: 80
```

The input can be other Kubernetes resource types like Deployments, Cronjobs, and StatefulSets.
If ConfigMaps or Secrets are used, they should be included in the same file as the Pod-creating resource.
If the ConfigMap or Secret is not included, a prompt will appear asking if the environment variable should be wildcarded.
To automate this process, the `-y` flag may be used.

#### Example 2

To generate a security policy using a policy config file for Virtual Node, the `scenario` field must be equal to `"vn2"`.
This looks like:

```json
{
    "version": "1.0",
    "scenario": "vn2",
    "containers": [
        {
            "name": "my-image",
            "properties": {
                "image": "mcr.microsoft.com/acc/samples/aci/helloworld:2.9"
            }
        }
    ]
}
```

And the policy is created with:

```bash
az confcom acipolicygen -i input.json
```

This `scenario` field adds the necessary environment variables and mount values to containers in the config file.
Currently `vn2` and `aci` are the only supported values for `scenario`, but others may be added in the future as more products onboard to the `confcom` extension.
`aci` is the default value.

### Workload Identity

To use workload identities with VN2, the associated label [described here](https://learn.microsoft.com/en-us/azure/aks/workload-identity-overview?tabs=dotnet#pod-labels) must be present.
Having this will add the requisite environment variables and mounts to each container's policy.
To generate a policy with workload identity capabilities for VN2 using the JSON format, the following label must be included:

```json
{
    "version": "1.0",
    "scenario": "vn2",
    "labels": {
        "azure.workload.identity/use": true
    },
    "containers": [
        ...
    ]
}
```

> [!NOTE]
> The `acipolicygen` command is specific to generating policies for ACI-based containers.
For generating security policies for the [Confidential Containers on AKS](https://learn.microsoft.com/en-us/azure/aks/confidential-containers-overview) feature, use the `katapolicygen` command.
