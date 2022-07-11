# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines

from knack.help_files import helps

helps['dns-resolver inbound-endpoint create'] = """
    type: command
    short-summary: "Create an inbound endpoint for a DNS resolver."
    parameters:
      - name: --ip-configurations
        short-summary: "IP configurations for the inbound endpoint."
        long-summary: |
            Usage: --ip-configurations private-ip-address=XX private-ip-allocation-method=XX id=XX

            private-ip-address: Private IP address of the IP configuration.
            private-ip-allocation-method: Private IP address allocation method.
            id: Resource ID.

            Multiple actions can be specified by using more than one --ip-configurations argument.
    examples:
      - name: Upsert inbound endpoint for DNS resolver
        text: |-
               az dns-resolver inbound-endpoint create --dns-resolver-name "sampleDnsResolver" --name \
"sampleInboundEndpoint" --location "westus2" --ip-configurations private-ip-address="" \
private-ip-allocation-method="Dynamic" id="/subscriptions/0403cfa9-9659-4f33-9f30-1f191c51d111/resourceGroups/sampleVnet\
ResourceGroupName/providers/Microsoft.Network/virtualNetworks/sampleVirtualNetwork/subnets/sampleSubnet" --tags \
key1="value1" --resource-group "sampleResourceGroup"
"""
