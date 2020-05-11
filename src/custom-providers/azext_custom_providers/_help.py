# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['custom-providers resource-provider'] = """
type: group
short-summary: Commands to manage custom resource provider.
"""

helps['custom-providers resource-provider create'] = """
type: command
short-summary: Create or update the custom resource provider.
parameters:
  - name: --action -a
    short-summary: Add an action to the custom resource provider.
    long-summary: |
        Usage: --action name=ping endpoint="https://test.azurewebsites.net/api/{requestPath}" routing_type=Proxy

        name: Required. The name of the action.
        endpoint: Required. The endpoint URI that the custom resource provider will proxy requests to.
        routing_type: The routing types that are supported for action requests. Possible values include: 'Proxy'.

        Multiple actions can be specified by using more than one `--action` argument.
  - name: --resource-type -r
    short-summary: Add a custom resource type to the custom resource provider.
    long-summary: |
        Usage: --resource-type name=user endpoint="https://test.azurewebsites.net/api/{requestPath}" routing_type="Proxy, Cache"

        name: Required. The name of the resource type.
        endpoint: Required. The endpoint URI that the custom resource provider will proxy requests to.
        routing_type: The routing types that are supported for resource requests. Possible values include: 'Proxy', 'Proxy,Cache'.

        Multiple resource types can be specified by using more than one `--resource-type` argument.
  - name: --validation -v
    short-summary: Add a validation to the custom resource provider.
    long-summary: |
        Usage: --validation specification="https://raw.githubusercontent.com/" validation_type="Swagger"

        specification: A link to the validation specification.vThe specification must be hosted on raw.githubusercontent.com.
        validation_type: The type of validation to run against a matching request. Possible values include: 'Swagger'.

        Multiple validations can be specified by using more than one `--validation` argument.
examples:
  - name: Create or update a custom resource provider.
    text: |-
           az custom-providers resource-provider create -n MyRP -g MyRG \\
           --action name=ping endpoint=https://test.azurewebsites.net/api routing_type=Proxy \\
           --resource-type name=users endpoint=https://test.azurewebsites.net/api routing_type="Proxy, Cache" \\
           --validation validation_type=swagger specification=https://raw.githubusercontent.com/test.json
"""

helps['custom-providers resource-provider update'] = """
type: command
short-summary: Update the custom resource provider. Only tags can be updated.
examples:
  - name: Update the tags for a custom resource provider.
    text: |-
           az custom-providers resource-provider update -g MyRG -n MyRP --tags a=b
"""

helps['custom-providers resource-provider delete'] = """
type: command
short-summary: Delete the custom resource provider.
examples:
  - name: Delete a custom resource provider.
    text: |-
           az custom-providers resource-provider delete -g MyRG -n MyRP
"""

helps['custom-providers resource-provider show'] = """
type: command
short-summary: Get the properties for the custom resource provider.
examples:
  - name: Get a custom resource provider.
    text: |-
           az custom-providers resource-provider show -g MyRG -n MyRP
"""

helps['custom-providers resource-provider list'] = """
type: command
short-summary: Get all the custom resource providers within a resource group or in the current subscription.
examples:
  - name: List all custom resource providers in the resource group.
    text: |-
           az custom-providers resource-provider list -g MyRG
  - name: List all custom resource providers in the current subscription.
    text: |-
           az custom-providers resource-provider list
"""
