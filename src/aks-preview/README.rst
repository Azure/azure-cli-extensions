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
    * - 0.5.125 ~ 0.5.150
      - >= `\2.44.0 <https://github.com/Azure/azure-cli/releases/tag/azure-cli-2.44.0>`_, 2023/01/10
    * - 0.5.152 ~ 2.0.0b6
      - >= `\2.49.0 <https://github.com/Azure/azure-cli/releases/tag/azure-cli-2.49.0>`_, 2023/05/23
    * - 2.0.0b7 ~ latest
      - >= `\2.56.0 <https://github.com/Azure/azure-cli/releases/tag/azure-cli-2.56.0>`_, 2024/01/09

Released version and adopted API version
========================================

.. list-table::
    :widths: 35 35 30
    :header-rows: 1

    * - aks-preview
      - API version
      - Comment
    * - 0.4.53 ~ 0.4.62
      - 2020-06-01
      - 
    * - 0.4.63 ~ 0.4.66
      - 2020-09-01
      - 
    * - 0.4.67 ~ 0.4.72
      - 2020-11-01
      - 
    * - 0.4.73 ~ 0.5.0
      - 2020-12-01
      - 
    * - 0.5.1 ~ 0.5.7
      - 2021-02-01
      - 
    * - 0.5.8 ~ 0.5.14
      - 2021-03-01
      - 
    * - 0.5.15 ~ 0.5.27
      - 2021-05-01
      - 
    * - 0.5.28 ~ 0.5.35
      - 2021-07-01
      - 
    * - 0.5.36 ~ 0.5.45
      - 2021-09-01
      - 
    * - 0.5.46 ~ 0.5.48
      - 2021-10-01
      - 
    * - 0.5.49 ~ 0.5.52
      - 2021-11-01-preview
      - **Deprecated** on 2023/07/01
    * - 0.5.53 ~ 0.5.57
      - 2022-01-02-preview
      - **Deprecated** on 2023/09/01
    * - 0.5.58 ~ 0.5.60
      - 2022-02-02-preview
      - **Deprecated** on 2023/08/01
    * - 0.5.61 ~ 0.5.66
      - 2022-03-02-preview
      - **Deprecated** on 2023/09/01
    * - 0.5.67 ~ 0.5.78
      - 2022-04-02-preview
      - **Deprecated** on 2023/09/01
    * - 0.5.79 ~ 0.5.91
      - 2022-05-02-preview
      - **Deprecated** on 2023/09/01
    * - 0.5.92 ~ 0.5.93
      - 2022-06-02-preview
      - **Deprecated** on 2023/09/01
    * - 0.5.94 ~ 0.5.100
      - 2022-07-02-preview
      - **Deprecated** on 2024/02/14
    * - 0.5.101 ~ 0.5.104
      - 2022-08-02-preview
      - Plan to **retire** on 2024/05/20
    * - 0.5.105 ~ 0.5.107
      - 2022-08-03-preview
      - Plan to **retire** on 2024/05/20
    * - 0.5.108 ~ 0.5.115
      - 2022-09-02-preview
      - Plan to **retire** on 2024/05/20
    * - 0.5.116 ~ 0.5.121
      - 2022-10-02-preview
      - Plan to **retire** on 2024/05/20
    * - 0.5.122 ~ 0.5.128
      - 2022-11-02-preview
      - Plan to **retire** on 2024/05/20
    * - 0.5.129 ~ 0.5.132
      - 2023-01-02-preview
      - Plan to **retire** on 2024/05/20
    * - 0.5.133 ~ 0.5.137
      - 2023-02-02-preview
      - Plan to **retire** on 2024/05/20
    * - 0.5.138 ~ 0.5.139
      - 2023-03-02-preview
      - 
    * - 0.5.140 ~ 0.5.142
      - 2023-04-02-preview
      - 
    * - 0.5.143 ~ 0.5.149
      - 2023-05-02-preview
      - 
    * - 0.5.150 ~ 0.5.153
      - 2023-06-02-preview
      - 
    * - 0.5.154 ~ 0.5.161
      - 2023-07-02-preview
      - 
    * - 0.5.162 ~ 0.5.166
      - 2023-08-02-preview
      - 
    * - 0.5.167 ~ 0.5.171
      - 2023-09-02-preview
      - 
    * - 0.5.172 ~ 1.0.0b5
      - 2023-10-02-preview
      - 
    * - 1.0.0b6 ~ 1.0.0b6
      - 2023-11-02-preview
      - 
    * - 1.0.0b7 ~ 2.0.0b6
      - 2024-01-02-preview
      - 
    * - 2.0.0b7 ~ latest
      - 2024-02-02-preview
      - 
