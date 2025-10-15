# Azure CLI AKS Live Test Pipeline & Azure CLI AKS Unit Test Pipeline

These pipelines are used to test newly added aks commands in module aks-preview (azure-cli-extensions) / acs (azure-cli, not covered by default). For more details, you may refer to this [wiki](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/358312/AZCLI-AKS-Live-Unit-Test-Pipelines).

## How to use

These pipelines (live and unit test pipelines) will be **triggered** when submitting a **PR** to the master branch of the official repo which involves modifying the files under *src/aks-preview*.

By default, for **live test pipeline**, the test will be performed in **record mode first**, and **then in live mode**. The test mainly uses test cases located in ```src/aks-preview/azext_aks_preview/tests/latest/test_aks_commands.py```. Due to some specific reasons (more details in another [wiki](https://dev.azure.com/msazure/CloudNativeCompute/_wiki/wikis/CloudNativeCompute.wiki/157433/Live-Test-Failures-in-aks-preview-(with-bare-sub))), some test cases would fail. These test cases have been filtered out by file 'ext_matrix_default.json' (more details in [section Filter](#Filter)). For **unit test pipeline**, the test will be perfomed with 'unittest' and 'pytest' modules. A code coverage report will be generated after the unit tests. For both of the test pipelines, you can find test reports and coverage report from pipeline artifacts. 

If the newly added commands and test cases use the **features** that are being previewed, that is, some feature under container service needs to be manually registered before using the command, then such cases will not be able to execute/pass the test temporarily, since the subscription used for testing does not (and does not intend to) enable these additional features. In the future, we will use customer header to pass these features in test cases, but for now you can just bypass these cases. For now,  you can follow the instructions in [section Bypass Test Case](#bypass-test-case) to **bypass such test cases**. 

You can also trigger this pipeline **manually** and adjust variables such as test coverage, test filter, test location, etc. as needed. For more details, you may refer to the following sections.
