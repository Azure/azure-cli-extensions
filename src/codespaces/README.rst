Microsoft Azure CLI 'codespaces' Extension
==========================================

Visual Studio Codespaces - Cloud-powered development environments accessible from anywhere.

https://azure.microsoft.com/en-us/services/visual-studio-online/

Updating the vendored SDK
-------------------------

```
cd /specification/vsonline/resource-manager
autorest --python readme.md
```

Custom changes made to auto-generated SDK:
1. Remove trailing `/` from `list_by_resource_group` and `list_by_subscription` plan operations as server will reject request otherwise.
2. Add support for custom API version to be set.

Before submitting a PR
----------------------

```
azdev style codespaces
azdev linter codespaces
azdev test codespaces
```

Test extension on fresh set up:
```
azdev extension build codespaces
docker run -v .../azure-cli-extensions/dist:/ext -it microsoft/azure-cli
az extension add --source /ext/codespaces-VERSION-py2.py3-none-any.whl
```
