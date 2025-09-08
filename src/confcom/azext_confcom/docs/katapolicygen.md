# katapolicygen

- [Microsoft Azure CLI 'confcom katapolicygen' Extension Examples](#microsoft-azure-cli-confcom-katapolicygen-extension-examples)

## Microsoft Azure CLI 'confcom katapolicygen' Extension Examples

Run `az confcom katapolicygen --help` to see a list of supported arguments along with explanations.
The following commands demonstrate the usage of different arguments to generate confidential computing security policies.

### Prerequisites

View the [common documentation](./common.md) for information on how to install the `confcom` extension.

The `katapolicygen` command generates confidential computing security policies using a kubernetes pod spec.
You can control the format of the generated policies using arguments.
Note: It is recommended to use images with specific tags instead of the `latest` tag, as the `latest` tag can change at any time and images with different configurations may also have the latest tag.

### Examples

#### Example 1

The following command creates a security policy and outputs it to the command line:

```bash
az confcom katapolicygen -y ./pod.yaml --print-policy
```

This command combines the information of images from the pod spec with other information such as mount, environment variables and commands from the pod spec to create a security policy.
The `--print-policy` argument is included to display the policy on the command line in addition to injecting it into the input pod spec.

#### Example 2

This command injects a security policy into the pod spec based on input from a config map so that there is no need to change the pod spec to pass variables into the security policy:

```bash
az confcom katapolicygen -y ./pod.yaml -c ./config-map.yaml
```

#### Example 3

This command caches the layer hashes and stores them locally on your computer to make future computations faster if the same images are used:

```bash
az confcom katapolicygen -y ./pod.yaml -u
```
