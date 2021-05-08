# Azure CLI AKS Live Test Pipeline

This is a pipeline to test newly added aks commands in aks-preview/acs.

## How to use

**By default**, this pipeline will be **triggered** when submitting a **PR** to the master branch of the official repo which involves modifying the file under src/aks-preview and test the acs command group in azure-cli and the aks-preview command group in azure-cli-extensions. If the variables of the pipeline are not modified, the test will be executed based on the latest commit of the dev branch in the offical repo of azure-cli. The test will be performed in record mode first, and then in live mode. After the test, you can get the test results from the pipeline artifact (for different modes (record/live) and different modules (cli/ext)).

You can also trigger this pipeline **manually**. In this way, you **must** set the variable *MANUAL_EXT* to true before running the pipeline, and provide the your *EXT_REPO/CLI_REPO* url and *EXT_BRANCH/CLI_BRANCH* name at the same time.

For more details, you may refer to this [wiki](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/156735/Azure-CLI-AKS-Live-Test-Pipeline).
