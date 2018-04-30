# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import sys
import collections
from pkg_resources import parse_version

from jinja2 import Template  # pylint: disable=import-error

from util import get_index_data

DOC_TEMPLATE = """---
title: Available extensions for the Azure CLI 2.0
description: A complete list of the officially supported extensions for the Azure CLI 2.0.
author: derekbekoe
ms.author: debekoe
manager: routlaw
ms.date: 04/27/2018
ms.topic: article
ms.prod: azure
ms.technology: azure-cli
ms.devlang: azure-cli
---

# Available extensions for the Azure CLI 2.0

This article is a complete list of the available extensions for the Azure CLI 2.0 which are offered and supported by Microsoft.

The list of extensions is also available directly from the CLI. To get it, run [az extension list-available](/cli/azure/extension?view=azure-cli-latest#az-extension-list-available):

```azurecli
az extension list-available --output table
```

| Name | Version | Summary | Preview |
|------|---------|---------|---------|{% for extension in extensions %}
| [{{ extension.name }}]({{ extension.project_url }}) | {{ extension.version }} | {{ extension.desc }} | {{ extension.preview }} |{% endfor %}
"""


def get_extensions():
    extensions = []
    index_extensions = collections.OrderedDict(sorted(get_index_data()['extensions'].items()))
    for _, exts in index_extensions.items():
        # Get latest version
        exts = sorted(exts, key=lambda c: parse_version(c['metadata']['version']), reverse=True)
        extensions.append({
            'name': exts[0]['metadata']['name'],
            'desc': exts[0]['metadata']['summary'],
            'version': exts[0]['metadata']['version'],
            'project_url': exts[0]['metadata']['extensions']['python.details']['project_urls']['Home'],
            'preview': 'Yes' if exts[0]['metadata'].get('azext.isPreview') else ''
        })
    return extensions


def main():
    extensions = get_extensions()
    template = Template(DOC_TEMPLATE)
    print(template.render(extensions=extensions), file=sys.stdout)


if __name__ == '__main__':
    main()
