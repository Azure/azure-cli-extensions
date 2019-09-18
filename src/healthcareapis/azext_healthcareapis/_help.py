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
    short-summary: create service.
    examples:
      - name: Create or Update a service with all parameters
        text: |-
               az healthcareapis create --resource-group "rg1" --name "service1" --kind "fhir-R4" \\
               --location "westus2" --cosmos-db-offer-throughput "1000" --authentication-authority \\
               "https://login.microsoftonline.com/common" --authentication-audience \\
               "https://azurehealthcareapis.com" --authentication-smart-proxy-enabled true \\
               --cors-max-age "1440" --cors-allow-credentials false \\
               --access-policies-object-id c487e7d1-3210-41a3-8ccc-e9372b78da47,5b307da8-43d4-492b-8b66-b0294ade872f \\
               --cors-origins "*" --cors-headers "*" --cors-methods "DELETE,GET,OPTIONS,PATCH,POST,PUT"
      - name: Create or Update a service with minimum parameters
        text: |-
               az healthcareapis create --resource-group "rg1" --name "service2" --kind "fhir-R4" \\
               --location "westus2" --access-policies-object-id c487e7d1-3210-41a3-8ccc-e9372b78da47
"""

helps['healthcareapis update'] = """
    type: command
    short-summary: update service.
    examples:
      - name: Patch Service
        text: |-
               az healthcareapis update --resource-group "rg1" --name "service2" --kind "fhir-R4" \\
               --location "westus2" --access-policies-object-id c487e7d1-3210-41a3-8ccc-e9372b78da47
"""

helps['healthcareapis delete'] = """
    type: command
    short-summary: delete service.
    examples:
      - name: Delete Service
        text: |-
               az healthcareapis delete --resource-group "rg1" --name "service1"
"""

helps['healthcareapis list'] = """
    type: command
    short-summary: list service.
"""

helps['healthcareapis show'] = """
    type: command
    short-summary: show service.
"""
