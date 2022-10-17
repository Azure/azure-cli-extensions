## AutoRest Code Generation

[AutoRest for Python](https://github.com/Azure/autorest.python) was used to generate the code in `azext_vmware\vendored_sdks` using:

```powershell
rm ..\azure-cli-extensions\src\vmware\azext_vmware\vendored_sdks -Recurse

autorest --python --output-folder=..\azure-cli-extensions\src\vmware\azext_vmware\vendored_sdks\avs_client --use=@autorest/python@5.8.0 --tag=package-2022-05-01 --azure-arm=true --namespace=avs_client --override-client-name=AVSClient specification\vmware\resource-manager\readme.md
```

It was run from a git clone of [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs) within the python virtual environment (env\scripts\Activate.ps1). Ensure that no proxy has been set.

## Linter

Use [azdev](https://github.com/Azure/azure-cli-dev-tools) to check for linter errors and warnings.

- `azdev style vmware`
- `azdev linter --include-whl-extensions vmware`

## Developing New Commands

1. Set up [local development environment](https://github.com/Azure/azure-cli-dev-tools#setting-up-your-development-environment)

2. Add vmware extension

```powershell
azdev extension add vmware
```

3. Set up local extension repo (first cd into 'azure-cli-extensions repo')

```powershell
(env) PS dev\azure-cli-extensions> azdev setup -r $PWD
```

4. Confirm extension was installed properly

```powershell
(env) PS dev> az extension list
[
  {
    "experimental": false,
    "extensionType": "dev",
    "name": "vmware",
    "path": "C:\\Users\\jonathanhe\\Documents\\dev\\azure-cli-extensions\\src\\vmware",
    "preview": false,
    "version": "3.1.0"
  }
]
```

## Running Mock Server

The mock server provides an environment to testing newly developed commands without modifying any actual environments. Follow the steps to [set up the mock server](https://dev.azure.com/msazure/One/_git/Azure-Dedicated-AVS?path=%2Fsrc%2Ffct%2Fmock_api%2FREADME.md&_a=preview).

- Note: for development in the python environment, the self-signed certificate is located inside of the '\env\Lib\site-packages\certifi' directory, not under 'Program Files (x86)'
