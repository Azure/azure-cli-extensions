## AutoRest Code Generation
[AutoRest for Python](https://github.com/Azure/autorest.python) was used to generate the code in `azext_vmware\vendored_sdks` using:
``` powershell
rm ..\azure-cli-extensions\src\vmware\azext_vmware\vendored_sdks -Recurse

autorest --python --output-folder=..\azure-cli-extensions\src\vmware\azext_vmware\vendored_sdks --use=@autorest/python@5.6.1 --tag=package-2021-01-01-preview --azure-arm=true --override-client-name=AVSClient specification\vmware\resource-manager\readme.md
```
It was run from a git clone of [azure-rest-api-specs](https://github.com/Azure/azure-rest-api-specs).
