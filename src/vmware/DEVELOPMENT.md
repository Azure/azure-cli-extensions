## AutoRest Code Generation
[AutoRest for Python](https://github.com/Azure/autorest.python) was used to generate the code in `azext_vmware\vendored_sdks` using:
``` powershell
rm ..\azure-cli-extensions\src\vmware\azext_vmware\vendored_sdks -Recurse

autorest --python --output-folder=..\azure-cli-extensions\src\vmware\azext_vmware\vendored_sdks --use=@autorest/python@5.8.0 --tag=package-2021-06-01 --azure-arm=true --namespace=avs_client --override-client-name=AVSClient specification\vmware\resource-manager\readme.md
```
It was run from a git clone of [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs).

## Linter
Use [azdev](https://github.com/Azure/azure-cli-dev-tools) to check for linter errors and warnings.
- `azdev style vmware`
- `azdev linter --include-whl-extensions vmware`
