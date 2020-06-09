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
