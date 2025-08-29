# acifragmentgen

- [Microsoft Azure CLI 'confcom acifragmentgen' Extension Examples](#microsoft-azure-cli-confcom-acifragmentgen-extension-examples)
  - [Types of Policy Fragments](#types-of-policy-fragments)
  - [Examples](#examples)

## Microsoft Azure CLI 'confcom acifragmentgen' Extension Examples

Run `az confcom acifragmentgen --help` to see a list of supported arguments along with explanations.
The following commands demonstrate the usage of different arguments to generate confidential computing security fragments.

For information on what a policy fragment is, see [policy fragments](./policy_enforcement_points.md).
For a full walkthrough on how to generate a policy fragment and use it in a policy, see [Create a Key and Cert for Signing](../samples/certs/README.md).

### Types of Policy Fragments

There are two types of policy fragments:

1. Image-attached fragments: These are fragments that are attached to an image in an ORAS-compliant registry.
They are used to provide additional security information about the image and are to be used for a single image.
Image-attached fragments are currently in development.
Note that nested image-attached fragments are *not* supported.
2. Standalone fragments: These are fragments that are uploaded to an ORAS-compliant registry independent of a specific image and can be used for multiple images.
Standalone fragments are currently not supported.
Once implemented, nested standalone fragments will be supported.

### Examples

#### Example 1

The following command creates a security fragment and prints it to stdout as well as saving it to a file `contoso.rego`:

```bash
az confcom acifragmentgen --input ./fragment_config.json --svn 1 --namespace contoso
```

The config file is a JSON file that contains the following information:

```json
{
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
                "command": [
                    "python3",
                    "main.py"
                ]
            }
        }
    ]
}
```

The `--svn` argument is used to specify the security version number of the fragment and should be an integer.
The `--namespace` argument is used to specify the namespace of the fragment and cannot conflict with some built-in names.
If a conflicting name occurs, there will be an error message.
This list of reserved names can be found [here under 'reserved_fragment_namespaces'](./data/internal_config.json).
The format of the config file generally follows that of the [ACI resource in an ARM template](https://learn.microsoft.com/en-us/azure/templates/microsoft.containerinstance/containergroups?pivots=deployment-language-arm-template).

#### Example 2

This command creates a signed security fragment and attaches it to a container image in an ORAS-compliant registry:

```bash
az confcom acifragmentgen --chain ./samples/certs/intermediateCA/certs/www.contoso.com.chain.cert.pem --key ./samples/certs/intermediateCA/private/ec_p384_private.pem --svn 1 --namespace contoso --input ./samples/config.json --upload-fragment
```

#### Example 3

This command creates a file to be used by `acipolicygen` that says which fragments should be included in the policy.
Note that the policy must be [COSE](https://www.iana.org/assignments/cose/cose.xhtml) signed:

```bash
az confcom acifragmentgen --generate-import -p ./contoso.rego.cose --minimum-svn 1 --fragments-json fragments.json
```

This outputs a file `fragments.json` that contains the following information:

```json
{
    "fragments": [
        {
            "feed": "contoso.azurecr.io/example",
            "includes": [
                "containers",
                "fragments"
            ],
            "issuer":
                "did:x509:0:sha256:mLzv0uyBNQvC6hi4y9qy8hr6NSZuYFv6gfCwAEWBNqc::subject:CN:Contoso",
            "minimum_svn": "1"
        }
    ]
}
```

This file is then used by `acipolicygen` to generate a policy that includes custom fragments.

#### Example 4

The command creates a signed policy fragment and attaches it to a specified image in an ORAS-compliant registry:

```bash
az confcom acifragmentgen --chain ./samples/certs/intermediateCA/certs/www.contoso.com.chain.cert.pem --key ./samples/certs/intermediateCA/private/ec_p384_private.pem --svn 1 --namespace contoso --input ./samples/<my-config>.json --upload-fragment --image-target contoso.azurecr.io/<my-image>:latest --feed contoso.azurecr.io/<my-feed>
```

This could be useful in scenarios where an image-attached fragment is required but the fragment's feed is different from the image's location.

#### Example 5

This format can also be used to generate fragments used for VN2. VN2 is described in more depth [in this file](./acipolicygen.md).
Adding the `scenario` key with the value `vn2` tells confcom which default values need to be added.
Save this file as `fragment_config.json`:

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

Using the same command, the default mounts and environment variables used by VN2 will be added to the policy fragment.

```bash
az confcom acifragmentgen --input ./fragment_config.json --svn 1 --namespace contoso
```

#### Example 6

Create an import statement from a signed fragment in a remote repo:

```bash
az confcom acifragmentgen --generate-import --fragment-path contoso.azurecr.io/<my-fragment>:v1 --minimum-svn 1
```

This is assuming there is a standalone fragment present at the specified location of `contoso.azurecr.io/<my-fragment>:v1`. Fragment imports can also be created using local paths to signed fragment files such as:

```bash
az confcom acifragmentgen --generate-import --fragment-path ./contoso.rego.cose --minimum-svn 1
```

#### Example 7

Create an import statement from a signed image-attached fragment in a remote repo:

```bash
az confcom acifragmentgen --generate-import --image contoso.azurecr.io/<my-image>:<my-tag> --minimum-svn 1
```

Note that since the fragment is image-attached, the `--image` argument is used instead of `--fragment-path` and the image cannot be a local image in the docker daemon.
