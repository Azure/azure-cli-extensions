# Quantum CLI Extension Live tests

This folder contains Run.ps1, a script the will run all of the live tests for the Quantum CLI Extension.  Live tests are end-to-end tests that require an actual connection with Azure Quantum
to complete successfully.


## Running locally

1. Login to Azure using either:
    * the [Azure Account extension in VS Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.azure-account)
    * `az login` from the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/)

2. Use [`.\Run.ps1 -SkipInstall`](.\Run.ps1) to run all the tests.
