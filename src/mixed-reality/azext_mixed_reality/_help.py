# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

helps['spatial-anchors-account'] = """
    type: group
    short-summary: Manage spatial anchor account with mixed reality
"""

helps['spatial-anchors-account list'] = """
    type: command
    short-summary: List resources by resource group and list spatial anchors accounts by subscription.
    examples:
      - name: List spatial anchor accounts by resource group
        text: |-
               az spatial-anchors-account list --resource-group "MyResourceGroup"
      - name: List spatial anchors accounts by subscription
        text: |-
               az spatial-anchors-account list
"""

helps['spatial-anchors-account show'] = """
    type: command
    short-summary: Retrieve a spatial anchors account.
    examples:
      - name: Get spatial anchors account
        text: |-
               az spatial-anchors-account show -n "MyAccount" --resource-group \
"MyResourceGroup"
"""

helps['spatial-anchors-account create'] = """
    type: command
    short-summary: Create a spatial anchors account.
    parameters:
      - name: --sku
        short-summary: The SKU associated with this account
        long-summary: |
            Usage: --sku name=XX tier=XX size=XX family=XX capacity=XX

            name: Required. The name of the SKU. Ex - P3. It is typically a letter+number code
            tier: This field is required to be implemented by the resource provider if the service has more than one \
tier, but is not required on a PUT.
            size: The SKU size. When the name field is the combination of tier and some other value, this would be the \
standalone code.
            family: If the service has different generations of hardware, for the same SKU, then that can be captured \
here.
            capacity: If the SKU supports scale out/in then the capacity integer should be included. If scale out/in \
is not possible for the resource this may be omitted.
      - name: --kind
        short-summary: The kind of account, if supported
        long-summary: |
            Usage: --kind name=XX tier=XX size=XX family=XX capacity=XX

            name: Required. The name of the SKU. Ex - P3. It is typically a letter+number code
            tier: This field is required to be implemented by the resource provider if the service has more than one \
tier, but is not required on a PUT.
            size: The SKU size. When the name field is the combination of tier and some other value, this would be the \
standalone code.
            family: If the service has different generations of hardware, for the same SKU, then that can be captured \
here.
            capacity: If the SKU supports scale out/in then the capacity integer should be included. If scale out/in \
is not possible for the resource this may be omitted.
    examples:
      - name: Create spatial anchor account
        text: |-
               az spatial-anchors-account create -n "MyAccount" --resource-group "MyResourceGroup"
"""

helps['spatial-anchors-account update'] = """
    type: command
    short-summary: Update a spatial anchors account.
    parameters:
      - name: --sku
        short-summary: The SKU associated with this account
        long-summary: |
            Usage: --sku name=XX tier=XX size=XX family=XX capacity=XX

            name: Required. The name of the SKU. Ex - P3. It is typically a letter+number code
            tier: This field is required to be implemented by the resource provider if the service has more than one \
tier, but is not required on a PUT.
            size: The SKU size. When the name field is the combination of tier and some other value, this would be the \
standalone code.
            family: If the service has different generations of hardware, for the same SKU, then that can be captured \
here.
            capacity: If the SKU supports scale out/in then the capacity integer should be included. If scale out/in \
is not possible for the resource this may be omitted.
      - name: --kind
        short-summary: The kind of account, if supported
        long-summary: |
            Usage: --kind name=XX tier=XX size=XX family=XX capacity=XX

            name: Required. The name of the SKU. Ex - P3. It is typically a letter+number code
            tier: This field is required to be implemented by the resource provider if the service has more than one \
tier, but is not required on a PUT.
            size: The SKU size. When the name field is the combination of tier and some other value, this would be the \
standalone code.
            family: If the service has different generations of hardware, for the same SKU, then that can be captured \
here.
            capacity: If the SKU supports scale out/in then the capacity integer should be included. If scale out/in \
is not possible for the resource this may be omitted.
    examples:
      - name: Update spatial anchors account
        text: |-
               az spatial-anchors-account update -n "MyAccount" --resource-group \
"MyResourceGroup" --location "eastus2euap" --tags hero="romeo" heroine="juliet"
"""

helps['spatial-anchors-account delete'] = """
    type: command
    short-summary: Delete a spatial anchors account.
    examples:
      - name: Delete spatial anchors account
        text: |-
               az spatial-anchors-account delete -n "MyAccount" --resource-group \
"MyResourceGroup"
"""

helps['spatial-anchors-account key show'] = """
    type: command
    short-summary: List both of the 2 keys of a spatial anchors account.
    examples:
      - name: List spatial anchor account key
        text: |-
               az spatial-anchors-account key show -n "MyAccount" --resource-group \
"MyResourceGroup"
"""

helps['spatial-anchors-account key renew'] = """
    type: command
    short-summary: Regenerate specified key of a spatial anchors account.
    examples:
      - name: Regenerate spatial anchors account keys
        text: |-
               az spatial-anchors-account key renew -n "MyAccount" -k primary \
--resource-group "MyResourceGroup"
"""

helps['remote-rendering-account'] = """
    type: group
    short-summary: Manage remote rendering account with mixed reality
"""

helps['remote-rendering-account list'] = """
    type: command
    short-summary: List resources by resource group and list remote rendering accounts by subscription.
    examples:
      - name: List remote rendering accounts by resource group
        text: |-
               az remote-rendering-account list --resource-group "MyResourceGroup"
      - name: List remote rendering accounts by subscription
        text: |-
               az remote-rendering-account list
"""

helps['remote-rendering-account show'] = """
    type: command
    short-summary: Retrieve a remote rendering account.
    examples:
      - name: Get remote rendering account
        text: |-
               az remote-rendering-account show -n "MyAccount" --resource-group \
"MyResourceGroup"
"""

helps['remote-rendering-account create'] = """
    type: command
    short-summary: Create a remote rendering account.
    parameters:
      - name: --sku
        short-summary: The SKU associated with this account
        long-summary: |
            Usage: --sku name=XX tier=XX size=XX family=XX capacity=XX

            name: Required. The name of the SKU. Ex - P3. It is typically a letter+number code
            tier: This field is required to be implemented by the resource provider if the service has more than one \
tier, but is not required on a PUT.
            size: The SKU size. When the name field is the combination of tier and some other value, this would be the \
standalone code.
            family: If the service has different generations of hardware, for the same SKU, then that can be captured \
here.
            capacity: If the SKU supports scale out/in then the capacity integer should be included. If scale out/in \
is not possible for the resource this may be omitted.
      - name: --kind
        short-summary: The kind of account, if supported
        long-summary: |
            Usage: --kind name=XX tier=XX size=XX family=XX capacity=XX

            name: Required. The name of the SKU. Ex - P3. It is typically a letter+number code
            tier: This field is required to be implemented by the resource provider if the service has more than one \
tier, but is not required on a PUT.
            size: The SKU size. When the name field is the combination of tier and some other value, this would be the \
standalone code.
            family: If the service has different generations of hardware, for the same SKU, then that can be captured \
here.
            capacity: If the SKU supports scale out/in then the capacity integer should be included. If scale out/in \
is not possible for the resource this may be omitted.
    examples:
      - name: Create remote rendering account
        text: |-
               az remote-rendering-account create -n "MyAccount" --location "eastus2euap" \
--resource-group "MyResourceGroup"
"""

helps['remote-rendering-account update'] = """
    type: command
    short-summary: Update a remote rendering account.
    parameters:
      - name: --sku
        short-summary: The SKU associated with this account
        long-summary: |
            Usage: --sku name=XX tier=XX size=XX family=XX capacity=XX

            name: Required. The name of the SKU. Ex - P3. It is typically a letter+number code
            tier: This field is required to be implemented by the resource provider if the service has more than one \
tier, but is not required on a PUT.
            size: The SKU size. When the name field is the combination of tier and some other value, this would be the \
standalone code.
            family: If the service has different generations of hardware, for the same SKU, then that can be captured \
here.
            capacity: If the SKU supports scale out/in then the capacity integer should be included. If scale out/in \
is not possible for the resource this may be omitted.
      - name: --kind
        short-summary: The kind of account, if supported
        long-summary: |
            Usage: --kind name=XX tier=XX size=XX family=XX capacity=XX

            name: Required. The name of the SKU. Ex - P3. It is typically a letter+number code
            tier: This field is required to be implemented by the resource provider if the service has more than one \
tier, but is not required on a PUT.
            size: The SKU size. When the name field is the combination of tier and some other value, this would be the \
standalone code.
            family: If the service has different generations of hardware, for the same SKU, then that can be captured \
here.
            capacity: If the SKU supports scale out/in then the capacity integer should be included. If scale out/in \
is not possible for the resource this may be omitted.
    examples:
      - name: Update remote rendering account
        text: |-
               az remote-rendering-account update -n "MyAccount" --tags hero="romeo" heroine="juliet" \
--resource-group "MyResourceGroup"
"""

helps['remote-rendering-account delete'] = """
    type: command
    short-summary: Delete a remote rendering account.
    examples:
      - name: Delete remote rendering account
        text: |-
               az remote-rendering-account delete -n "MyAccount" --resource-group \
"MyResourceGroup"
"""

helps['remote-rendering-account key show'] = """
    type: command
    short-summary: List both of the 2 keys of a remote rendering account.
    examples:
      - name: List remote rendering account key
        text: |-
               az remote-rendering-account key show -n "MyAccount" --resource-group \
"MyResourceGroup"
"""

helps['remote-rendering-account key renew'] = """
    type: command
    short-summary: Regenerate specified key of a remote rendering account.
    examples:
      - name: Regenerate remote rendering account keys
        text: |-
               az remote-rendering-account key renew -n "MyAccount" -k primary \
--resource-group "MyResourceGroup"
"""

helps['spatial-anchors-account key'] = """
    type: group
    short-summary: Manage developer keys of a spatial anchors account.
"""

helps['remote-rendering-account key'] = """
    type: group
    short-summary: Manage developer keys of a remote rendering account.
"""
