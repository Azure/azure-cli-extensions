---
title: List of available Azure CLI extensions | Microsoft Docs
description: A complete list of officially supported Azure Command-Line Interface (CLI) extensions that are provided and maintained by Microsoft.
author: haroldrandom
ms.author: jianzen
manager: yonzhan,yungezz
ms.date: {{ date }}
ms.topic: article
ms.service: azure-cli
ms.devlang: azure-cli
ms.tool: azure-cli
ms.custom: devx-track-azurecli
keywords: az extension, azure cli extensions, azure extensions
---

# Available Azure CLI extensions

This article is a complete list of the available extensions for the Azure CLI which are supported by Microsoft.  The list of extensions is also available from the CLI. To get it, run [az extension list-available](/cli/azure/extension#az-extension-list-available):

```azurecli-interactive
az extension list-available --output table
```

You will be prompted to install an extension on first use.  

| Extension | Required Minimum CLI Version | Description | Status | Release Notes |
|----|-----------------|-------------|---------|---------------|{% for extension in extensions %}
|[{{ extension.name }}]({{ extension.project_url }}) | {{ extension.min_cli_core_version }} | {{ extension.desc }} | {{ extension.status }} | [{{extension.version}}]({{extension.history}}) |{% endfor %}
