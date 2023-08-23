Azure CLI AKS Preview Extension
===============================

This is an extension for AKS features. After installing and enabling aks-preview, it will **override the implementation of the same aks commands in azure-cli**. 

How to use
==========

Install this extension using the following CLI command `az extension add --name aks-preview`. You may need to execute some invalid aks command (e.g., `az aks fake`) to refresh the command index to enable aks-preview.

Remove this extension using the following CLI command `az extension remove --name aks-preview`.

Dependency between aks-preview and azure-cli/acs (azure-cli-core)
=================================================================

.. list-table::
    :widths: 50 50
    :header-rows: 1

    * - aks-preview
      - azure-cli/acs (azure-cli-core), release date
    * - 0.4.4 ~ 0.5.39
      - >= 2.0.49
    * - 0.5.40 ~ 0.5.41
      - >= `\2.23.0 <https://github.com/Azure/azure-cli/releases/tag/azure-cli-2.23.0>`_, 2021/05/06
    * - 0.5.42 ~ 0.5.44
      - >= `\2.27.0 <https://github.com/Azure/azure-cli/releases/tag/azure-cli-2.27.0>`_, 2021/08/03
    * - 0.5.45 ~ 0.5.48
      - >= `\2.30.0 <https://github.com/Azure/azure-cli/releases/tag/azure-cli-2.30.0>`_, 2021/11/02
    * - 0.5.49 ~ 0.5.52
      - >= `\2.31.0 <https://github.com/Azure/azure-cli/releases/tag/azure-cli-2.31.0>`_, 2021/12/07
    * - 0.5.53 ~ 0.5.66
      - >= `\2.32.0 <https://github.com/Azure/azure-cli/releases/tag/azure-cli-2.32.0>`_, 2022/01/04
    * - 0.5.67 ~ 0.5.82
      - >= `\2.35.0 <https://github.com/Azure/azure-cli/releases/tag/azure-cli-2.35.0>`_, 2022/04/06
    * - 0.5.83 ~ 0.5.91
      - >= `\2.37.0 <https://github.com/Azure/azure-cli/releases/tag/azure-cli-2.37.0>`_, 2022/05/24
    * - 0.5.92 ~ 0.5.118
      - >= `\2.38.0 <https://github.com/Azure/azure-cli/releases/tag/azure-cli-2.38.0>`_, 2022/07/05
    * - 0.5.119 ~ 0.5.124
      - >= `\2.43.0 <https://github.com/Azure/azure-cli/releases/tag/azure-cli-2.43.0>`_, 2022/12/06
    * - 0.5.125 ~ latest
      - >= `\2.44.0 <https://github.com/Azure/azure-cli/releases/tag/azure-cli-2.44.0>`_, 2023/01/10