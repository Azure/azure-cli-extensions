# Azure CLI AKS Live Test Pipeline & Azure CLI AKS Unit Test Pipeline

These pipelines are used to test newly added aks commands in module aks-preview (azure-cli-extensions) / acs (azure-cli, not covered by default).

## How to use

**By default**, these pipelines will be **triggered** when submitting a **PR** to the master branch of the official repo which involves modifying the files under src/aks-preview. Then they will test the aks-preview command group in azure-cli-extensions. For live test pipeline, the test will be performed in record mode first, and then in live mode. Due to some specific [reasons](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/157433/Live-Test-Failures-in-aks-preview-(with-bare-sub)), some test cases would fail. These test cases have been filtered out by file 'ext_matrix_default.json'. For unit test pipeline, the test will be perfomed with 'unittest' and 'pytest' modules. A code coverage report will be generated after the unit tests. You can find test reports and coverage report from pipeline artifacts.

You can also trigger this pipeline **manually**. For more details, you may refer to this [wiki](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/156735/Azure-CLI-AKS-Live-Test-Pipeline).
