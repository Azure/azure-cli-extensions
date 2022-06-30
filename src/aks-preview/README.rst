Azure CLI AKS Preview Extension
===============================

This is an extension for AKS features. After installing and enabling aks-preview, it will **override the implementation of the same aks commands in azure-cli**. 

How to use
==========

Install this extension using the following CLI command `az extension add --name aks-preview`. You may need to execute some invalid aks command (e.g., `az aks fake`) to refresh the command index to enable aks-preview.

Remove this extension using the following CLI command `az extension remove --name aks-preview`.
