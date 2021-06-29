---
title: Available extensions for the Azure CLI
description: A complete list of the officially supported extensions for the Azure CLI.
author: haroldrandom
ms.author: jianzen
manager: yonzhan,yungezz
ms.date: {{ date }}
ms.topic: article
ms.prod: azure
ms.technology: azure-cli
ms.devlang: azure-cli
ms.custom: devx-track-azurecli
---

# Available extensions for the Azure CLI

This article is a complete list of the available extensions for the Azure CLI which are supported by Microsoft.

The list of extensions is also available from the CLI. To get it, run [az extension list-available](/cli/azure/extension#az_extension_list_available):

```azurecli-interactive
az extension list-available --output table
```

| Extension | Required Minimum CLI Version | Description | Status | Release Notes |
|----|-----------------|-------------|---------|---------------|{% for extension in extensions %}
|[{{ extension.name }}]({{ extension.project_url }}) | {{ extension.min_cli_core_version }} | {{ extension.desc }} | {{ extension.status }} | [{{extension.version}}]({{extension.history}}) |{% endfor %}
