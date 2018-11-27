---
title: Available extensions for the Azure CLI
description: A complete list of the officially supported extensions for the Azure CLI.
author: sptramer
ms.author: sttramer
manager: carmonm
ms.date: {{ date }}
ms.topic: article
ms.prod: azure
ms.technology: azure-cli
ms.devlang: azure-cli
---

# Available extensions for the Azure CLI

This article is a complete list of the available extensions for the Azure CLI which are supported by Microsoft.

The list of extensions is also available  from the CLI. To get it, run [az extension list-available](/cli/azure/extension?view=azure-cli-latest#az-extension-list-available):

```azurecli-interactive
az extension list-available --output table
```

| Name | Version | Summary | Preview |
|------|---------|---------|---------|{% for extension in extensions %}
| [{{ extension.name }}]({{ extension.project_url }}) | {{ extension.version }} | {{ extension.desc }} | {{ extension.preview }} |{% endfor %}
