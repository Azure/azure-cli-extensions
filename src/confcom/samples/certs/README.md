# Create a Key and Cert for Signing

## Prerequisites

- Must have OpenSSL installed (tested with version 3.0.2)
- Must have Azure CLI installed (tested with version 2.46.0)
- Must have the [`confcom` extension version 1.1.0 or greater](../../README.md) installed
- Must have [ORAS CLI](https://oras.land/docs/installation/) installed (tested with version 1.1.0)

## Update Config

*This step sets up the configuration for creating certs to sign the fragment policy. This only needs to be done once.*

`create_certchain.sh` should have `<your-username>` specified at the top for `RootPath`

The image in `fragment_config.json` must be updated from `<your-image>` to the image you want to attach the fragment to. This is likely going to be in Azure Container Registry but can be in any of these [supported registries](https://oras.land/docs/compatible_oci_registries/).

## Run the Script

*This step will create the necessary certificates and private keys to sign the fragment policy, including generating a root private key, intermediate private key, and a server private key. These keys are used to create the certificate chain required for signing. This step only needs to be done once.*

```bash
./create_certchain.sh
```

You will need to select (y) for four prompts to sign the certs needed to create a cert chain.

After completion, this will create the following files to be used in the confcom signing process:

- `intermediate/private/ec_p384_private.pem`
- `intermediateCA/certs/www.contoso.com.chain.cert.pem`

## Run confcom

*This step will generate the fragment policy, sign it with the certs created in the previous step, and upload the fragment to the container registry.*

You may need to change the path to the chain and key files in the following command:

```bash
az confcom acifragmentgen --chain ./samples/certs/intermediateCA/certs/www.contoso.com.chain.cert.pem --key ./samples/certs/intermediateCA/private/ec_p384_private.pem --svn 1 --namespace contoso --config ./samples/config.json --upload-fragment
```

After running the command, there will be the following files created:

- `contoso.rego`
- `contoso.rego.cose`

Where `contoso.rego` is the fragment policy and `contoso.rego.cose` is the signed policy in COSE format.

The `--upload-fragment` flag will attempt to attach the fragment to the container image in the ORAS-compliant registry. You may need to login to the registry before running the command via something like `az acr login`.

The fragment can be seen in the Azure portal under the container repo's artifacts By going through the following steps:

1. Go to the Azure portal
2. Go to the image's associated Azure Container Registry instance
3. Go to the specific image's repository
4. Click the tag of the image the fragment was attached to
5. Click the `Referrers` tab
6. The fragment should be listed as an artifact

## Generate Security Policy for an ARM Template

*This step will generate a security policy for an ARM template and include the fragment policy created in the previous step.*

To create an import statement for the newly created rego fragment, run the following command:

```bash
az confcom acifragmentgen --generate-import -p ./contoso.rego.cose --minimum-svn 1
```

Which will output the fragment's import in json format. **Place this import statement into a new `fragments.json` file.**

example output:

```json
{
    "issuer": "did:x509:0:sha256:I__iuL25oXEVFdTP_aBLx_eT1RPHbCQ_ECBQfYZpt9s::eku:1.3.6.1.4.1.311.76.59.1.3",
    "feed": "contoso.azurecr.io/infra",
    "minimum_svn": "1",
    "includes": [
        "containers"
    ]
}
```

To generate a security policy for an ARM template, run the following command:

```bash
az confcom acipolicygen -a template.json --include-fragments --fragments-json fragments.json
```

This will insert the fragment policy into the ARM template and include the mentioned fragments in the `fragments.json` file.
