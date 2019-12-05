# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['healthcareapis'] = """
    type: group
    short-summary: Commands to manage service.
"""

helps['healthcareapis create'] = """
    type: command
    short-summary: Create service instance.
    examples:
      - name: Create a service with all parameters
        text: |-
               az healthcareapis create --resource-group "rg1" --name "service1" --kind "fhir-R4" \\
               --location "westus2" --access-policies-object-id \\
               "c487e7d1-3210-41a3-8ccc-e9372b78da47,5b307da8-43d4-492b-8b66-b0294ade872f" \\
               --cosmos-db-offer-throughput "1000" --authentication-authority \\
               "https://login.microsoftonline.com/abfde7b2-df0f-47e6-aabf-2462b07508dc" \\
               --authentication-audience "https://azurehealthcareapis.com" \\
               --authentication-smart-proxy-enabled true --cors-origins "*" --cors-headers "*" \\
               --cors-methods "DELETE,GET,OPTIONS,PATCH,POST,PUT" --cors-max-age "1440" \\
               --cors-allow-credentials false
      - name: Create a service with minimum parameters
        text: |-
               az healthcareapis create --resource-group "rg1" --name "service2" --kind "fhir-R4" \\
               --location "westus2" --access-policies-object-id "c487e7d1-3210-41a3-8ccc-e9372b78da47"
"""

helps['healthcareapis update'] = """
    type: command
    short-summary: Update service instance.
    examples:
      - name: Update a service with all parameters
        text: |-
               az healthcareapis update --resource-group "rg1" --name "service1" --kind "fhir-R4" \\
               --location "westus2" --access-policies-object-id \\
               "c487e7d1-3210-41a3-8ccc-e9372b78da47,5b307da8-43d4-492b-8b66-b0294ade872f" \\
               --cosmos-db-offer-throughput "1000" --authentication-authority \\
               "https://login.microsoftonline.com/abfde7b2-df0f-47e6-aabf-2462b07508dc" \\
               --authentication-audience "https://azurehealthcareapis.com" \\
               --authentication-smart-proxy-enabled true --cors-origins "*" --cors-headers "*" \\
               --cors-methods "DELETE,GET,OPTIONS,PATCH,POST,PUT" --cors-max-age "1440" \\
               --cors-allow-credentials false
      - name: Update a service with minimum parameters
        text: |-
               az healthcareapis update --resource-group "rg1" --name "service2" --kind "fhir-R4" \\
               --location "westus2" --access-policies-object-id c487e7d1-3210-41a3-8ccc-e9372b78da47
"""

helps['healthcareapis delete'] = """
    type: command
    short-summary: delete service.
    examples:
      - name: Delete service instance.
        text: |-
               az healthcareapis delete --resource-group "rg1" --name "service1"
"""

helps['healthcareapis list'] = """
    type: command
    short-summary: List service instances.
    examples:
      - name: List all servics in subscription
        text: |-
               az healthcareapis list
      - name: List all servics in resource group
        text: |-
               az healthcareapis list --resource-group "rg1"
"""

helps['healthcareapis show'] = """
    type: command
    short-summary: Show service instance.
    examples:
      - name: Show selected service
        text: |-
               az healthcareapis show --resource-group "rg1" --name "service1"
"""
