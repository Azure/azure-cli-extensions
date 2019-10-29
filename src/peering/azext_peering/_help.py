# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['peering legacy'] = """
    type: group
    short-summary: Commands to manage legacy peering.
"""

helps['peering legacy list'] = """
    type: command
    short-summary: list legacy peering.
"""

helps['peering asn'] = """
    type: group
    short-summary: Commands to manage peer asn.
"""

helps['peering asn create'] = """
    type: command
    short-summary: Create peer ASN.
    examples:
      - name: Create a peer ASN
        text: |-
               az peering asn create --name "MyPeerAsn" --peer-asn "65000" --emails \\
               "abc@contoso.com,xyz@contoso.com" --phone "+1 (234) 567-8900" --peer-name "Contoso" \\
               --validation-state Approved
"""

helps['peering asn update'] = """
    type: command
    short-summary: update peer asn.
"""

helps['peering asn delete'] = """
    type: command
    short-summary: Delete peer ASN.
    examples:
      - name: Delete a peer ASN
        text: |-
               az peering asn delete --name "MyPeerAsn"
"""

helps['peering asn list'] = """
    type: command
    short-summary: list peer asn.
"""

helps['peering asn show'] = """
    type: command
    short-summary: show peer asn.
"""

helps['peering location'] = """
    type: group
    short-summary: Commands to manage peering location.
"""

helps['peering location list'] = """
    type: command
    short-summary: list peering location.
"""

helps['peering'] = """
    type: group
    short-summary: Commands to manage peering.
"""

helps['peering create'] = """
    type: command
    short-summary: Create peering.
    examples:
      - name: Create a direct peering
        text: |-
               az peering create --resource-group "MyResourceGroup" --name "MyPeering" --sku-name \\
               "Basic_Direct_Free" --kind "Direct" --direct-direct-peering-type "Edge" \\
               --peering-location "peeringLocation0" --location "eastus" \\
               --direct-connections bandwidthInMbps=10000 sessionAddressProvider=Peer \\
               useForPeeringService=false peeringDBFacilityId=99999 sessionPrefixV4=192.168.0.0/31 \\
               sessionPrefixV6=fd00::0/127 maxPrefixesAdvertisedV4=1000 maxPrefixesAdvertisedV6=100 \\
               md5AuthenticationKey=test-md5-auth-key \\
               connectionIdentifier=5F4CB5C7-6B43-4444-9338-9ABC72606C16 \\
               --direct-connections bandwidthInMbps=10000 \\
               sessionAddressProvider=Microsoft useForPeeringService=true peeringDBFacilityId=99999 \\
               connectionIdentifier=8AB00818-D533-4504-A25A-03A17F61201C \\
               --direct-peer-asn /subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Peering/peerAsns/peerAsnName
"""

helps['peering update'] = """
    type: command
    short-summary: update peering.
    examples:
      - name: Update peering tags
        text: |-
               az peering update --resource-group "MyResourceGroup" --name "MyPeering"
"""

helps['peering delete'] = """
    type: command
    short-summary: delete peering.
    examples:
      - name: Delete a peering
        text: |-
               az peering delete --resource-group "MyResourceGroup" --name "MyPeering"
"""

helps['peering list'] = """
    type: command
    short-summary: list peering.
"""

helps['peering show'] = """
    type: command
    short-summary: show peering.
"""

helps['peering service location'] = """
    type: group
    short-summary: Commands to manage peering service location.
"""

helps['peering service location list'] = """
    type: command
    short-summary: list peering service location.
"""

helps['peering service prefix'] = """
    type: group
    short-summary: Commands to manage prefix.
"""

helps['peering service prefix create'] = """
    type: command
    short-summary: create prefix.
    examples:
      - name: Create or update a prefix for the peering service
        text: |-
               az peering service prefix create --resource-group "MyResourceGroup" \\
               --peering-service-name "MyPeeringService" --name "MyPeeringServicePrefix" --prefix \\
               "192.168.1.0/24"
"""

helps['peering service prefix update'] = """
    type: command
    short-summary: update prefix.
"""

helps['peering service prefix delete'] = """
    type: command
    short-summary: delete prefix.
    examples:
      - name: Delete a prefix associated with the peering service
        text: |-
               az peering service prefix delete --resource-group "MyResourceGroup" \\
               --peering-service-name "MyPeeringService" --name "MyPeeringServicePrefix"
"""

helps['peering service prefix list'] = """
    type: command
    short-summary: list prefix.
"""

helps['peering service prefix show'] = """
    type: command
    short-summary: show prefix.
"""

helps['peering service provider'] = """
    type: group
    short-summary: Commands to manage peering service provider.
"""

helps['peering service provider list'] = """
    type: command
    short-summary: list peering service provider.
"""

helps['peering service'] = """
    type: group
    short-summary: Commands to manage peering service.
"""

helps['peering service create'] = """
    type: command
    short-summary: create peering service.
    examples:
      - name: Create a  peering service
        text: |-
               az peering service create --resource-group "MyResourceGroup" --name "MyPeeringService" \\
               --peering-service-location "state1" --peering-service-provider "serviceProvider1" \\
               --location "eastus"
"""

helps['peering service update'] = """
    type: command
    short-summary: update peering service.
    examples:
      - name: Update peering service tags
        text: |-
               az peering service update --resource-group "MyResourceGroup" --name "MyPeeringService"
"""

helps['peering service delete'] = """
    type: command
    short-summary: delete peering service.
    examples:
      - name: Delete a peering service
        text: |-
               az peering service delete --resource-group "MyResourceGroup" --name "MyPeeringService"
"""

helps['peering service list'] = """
    type: command
    short-summary: list peering service.
"""

helps['peering service show'] = """
    type: command
    short-summary: show peering service.
"""
