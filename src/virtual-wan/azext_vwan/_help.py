# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps


# region VirtualHub
helps['network vhub'] = """
    type: group
    short-summary: Manage virtual hubs.
"""

helps['network vhub create'] = """
    type: command
    short-summary: Create a virtual hub.
"""

helps['network vhub list'] = """
    type: command
    short-summary: List virtual hubs.
"""

helps['network vhub show'] = """
    type: command
    short-summary: Get the details of a virtual hub.
"""

helps['network vhub update'] = """
    type: command
    short-summary: Update settings of a virtual hub.
"""

helps['network vhub delete'] = """
    type: command
    short-summary: Delete a virtual hub.
"""

helps['network vhub connection'] = """
    type: group
    short-summary: Manage virtual hub VNet connections.
"""

helps['network vhub connection create'] = """
    type: command
    short-summary: Create a virtual hub VNet connection.
"""

helps['network vhub connection list'] = """
    type: command
    short-summary: List virtual hub VNet connections.
"""

helps['network vhub connection show'] = """
    type: command
    short-summary: Get the details of a virtual hub VNet connection.
"""

helps['network vhub connection delete'] = """
    type: command
    short-summary: Delete a virtual hub VNet connection.
"""

helps['network vhub connection wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of virtual hub VNet connection is met.
"""

helps['network vhub route'] = """
    type: group
    short-summary: Manage entries in the virtual hub route table.
"""

helps['network vhub route add'] = """
    type: command
    short-summary: Add a route to the virtual hub route table.
"""

helps['network vhub route list'] = """
    type: command
    short-summary: List routes in the virtual hub route table.
"""

helps['network vhub route remove'] = """
    type: command
    short-summary: Remove a route from the virtual hub route table.
"""

helps['network vhub route-table'] = """
    type: group
    short-summary: Manage route table in the virtual hub.
"""

helps['network vhub route-table create'] = """
    type: command
    short-summary: Create a route table in the virtual hub.
    examples:
    - name: Create a v2 route table in the virtual hub.
      text: |
          az network vhub route-table create -n MyRouteTable -g MyResourceGroup --vhub-name MyVhub --connections All_Vnets --destination-type CIDR --destinations "10.4.0.0/16" "10.6.0.0/16" --next-hop-type IPAddress --next-hops "10.0.0.68"
    - name: Create a v3 route table in the virtual hub.
      text: |
          az network vhub route-table create -n MyRouteTable -g MyResourceGroup --vhub-name MyVhub --route-name MyRoute --destination-type CIDR --destinations "10.4.0.0/16" "10.6.0.0/16" --next-hop-type ResourceId --next-hop /subscriptions/MySub/resourceGroups/MyResourceGroup/providers/Microsoft.Network/azureFirewalls/MyFirewall --labels label1 label2
"""

helps['network vhub route-table update'] = """
    type: command
    short-summary: Update a route table in the virtual hub.
    examples:
    - name: Update the connections for a v2 route table in the virtual hub.
      text: |
          az network vhub route-table update -n MyRouteTable -g MyResourceGroup --vhub-name MyVhub --connections All_Vnets All_Branches
    - name: Update the labels for a v3 route table in the virtual hub.
      text: |
          az network vhub route-table update -n MyRouteTable -g MyResourceGroup --vhub-name MyVhub --labels label1 label2
"""

helps['network vhub route-table delete'] = """
    type: command
    short-summary: Delete a route table in the virtual hub.
    examples:
    - name: Delete a route table in the virtual hub.
      text: |
          az network vhub route-table delete -n MyRouteTable -g MyResourceGroup --vhub-name MyVhub
"""

helps['network vhub route-table show'] = """
    type: command
    short-summary: Show a route table in the virtual hub.
"""

helps['network vhub route-table list'] = """
    type: command
    short-summary: List all route tables in the virtual hub.
"""

helps['network vhub route-table wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the vhub route-table is met.
    examples:
      - name: Pause executing next line of CLI script until the route table is successfully provisioned.
        text: az network vhub route-table wait -n MyRouteTable -g MyResourceGroup --vhub-name MyVhub --created
"""

helps['network vhub route-table route'] = """
    type: group
    short-summary: Manage routes of route table in the virtual hub.
"""

helps['network vhub route-table route add'] = """
    type: command
    short-summary: Add a route into route table of the virtual hub.
    examples:
      - name: Add a route with CIDR destination into route table of the virtual hub (route table v2).
        text: |
            az network vhub route-table route add -n MyRouteTable -g MyResourceGroup --vhub-name MyVhub --destination-type CIDR --destinations "10.4.0.0/16" "10.6.0.0/16" --next-hop-type IPAddress --next-hops "10.0.0.68"
      - name: Add a route with Service destination into route table of the virtual hub (route table v2).
        text: |
            az network vhub route-table route add -n MyRouteTable -g MyResourceGroup --vhub-name MyVhub --destination-type Service --destinations Skype Sharepoint --next-hop-type IPAddress --next-hops "10.0.0.68"
      - name: Add a route with firewall as next hop into route table of the virtual hub (route table v3).
        text: |
            az network vhub route-table route add -n MyRouteTable -g MyResourceGroup --vhub-name MyVhub --destination-type CIDR --destinations "10.4.0.0/16" "10.6.0.0/16" --next-hop-type ResourceId --next-hop /subscriptions/MySub/resourceGroups/MyResourceGroup/providers/Microsoft.Network/azureFirewalls/MyFirewall
"""

helps['network vhub route-table route list'] = """
    type: command
    short-summary: List routes in the virtual hub route table.
"""

helps['network vhub route-table route remove'] = """
    type: command
    short-summary: Remove a route from route table of the virtual hub.
"""
# endregion

# region VirtualWAN
helps['network vwan'] = """
    type: group
    short-summary: Manage virtual WANs.
"""

helps['network vwan create'] = """
    type: command
    short-summary: Create a virtual WAN.
"""

helps['network vwan list'] = """
    type: command
    short-summary: List virtual WANs.
"""

helps['network vwan show'] = """
    type: command
    short-summary: Get the details of a virtual WAN.
"""

helps['network vwan update'] = """
    type: command
    short-summary: Update settings of a virtual WAN.
"""

helps['network vwan delete'] = """
    type: command
    short-summary: Delete a virtual WAN.
"""
# endregion

# region VpnGateway
helps['network vpn-gateway'] = """
    type: group
    short-summary: Manage VPN gateways.
"""

helps['network vpn-gateway create'] = """
    type: command
    short-summary: Create a VPN gateway.
"""

helps['network vpn-gateway list'] = """
    type: command
    short-summary: List VPN gateways.
"""

helps['network vpn-gateway show'] = """
    type: command
    short-summary: Get the details of a VPN gateway.
"""

helps['network vpn-gateway update'] = """
    type: command
    short-summary: Update settings of a VPN gateway.
"""

helps['network vpn-gateway delete'] = """
    type: command
    short-summary: Delete a VPN gateway.
"""

helps['network vpn-gateway connection'] = """
    type: group
    short-summary: Manage VPN gateway connections.
"""

helps['network vpn-gateway connection create'] = """
    type: command
    short-summary: Create a VPN gateway connection.
    examples:
      - name: Create a VPN gateway connection
        text: |
            az network vpn-gateway connection create -g MyRG -n MyConnection --gateway-name MyGateway --remote-vpn-site /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/vpnSites/MyVPNSite --associated-route-table /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/virtualHubs/MyHub/hubRouteTables/MyRouteTable1 --propagated-route-tables /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/virtualHubs/MyHub/hubRouteTables/MyRouteTable1 /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/virtualHubs/MyHub/hubRouteTables/MyRouteTable2 --labels label1 label2
"""

helps['network vpn-gateway connection list'] = """
    type: command
    short-summary: List VPN gateway connections.
    examples:
      - name: List all connections for a given VPN gateway
        text: |
            az network vpn-gateway connection list -g MyRG --gateway-name MyGateway
"""

helps['network vpn-gateway connection show'] = """
    type: command
    short-summary: Get the details of a VPN gateway connection.
    examples:
      - name: Get the details of a VPN gateway connection
        text: |
            az network vpn-gateway connection show -g MyRG -n MyConnection --gateway-name MyGateway
"""

helps['network vpn-gateway connection delete'] = """
    type: command
    short-summary: Delete a VPN gateway connection.
    examples:
      - name: Delete a VPN gateway connection
        text: |
            az network vpn-gateway connection delete -g MyRG -n MyConnection --gateway-name MyGateway
"""

helps['network vpn-gateway connection wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the VPN gateway connection is met.
"""

helps['network vpn-gateway connection ipsec-policy'] = """
    type: group
    short-summary: Manage VPN gateway connection IPSec policies.
"""

helps['network vpn-gateway connection ipsec-policy add'] = """
    type: command
    short-summary: Add an IPSec policy to a VPN gateway connection.
"""

helps['network vpn-gateway connection ipsec-policy list'] = """
    type: command
    short-summary: List VPN gateway connection IPSec policies.
"""

helps['network vpn-gateway connection ipsec-policy remove'] = """
    type: command
    short-summary: Remove an IPSec policy from a VPN gateway connection.
"""
# endregion

# region VpnSite
helps['network vpn-site'] = """
    type: group
    short-summary: Manage VPN site configurations.
"""

helps['network vpn-site create'] = """
    type: command
    short-summary: Create a VPN site configuration.
"""

helps['network vpn-site list'] = """
    type: command
    short-summary: List VPN site configurations.
"""

helps['network vpn-site show'] = """
    type: command
    short-summary: Get the details of a VPN site configuration.
"""

helps['network vpn-site update'] = """
    type: command
    short-summary: Update settings of a VPN site configuration.
"""

helps['network vpn-site delete'] = """
    type: command
    short-summary: Delete a VPN site configuration.
"""

helps['network vpn-site download'] = """
    type: command
    short-summary: Provide a SAS-URL to download the configuration for a VPN site.
"""
# endregion

# region VpnServerConfig
helps['network vpn-server-config'] = """
    type: group
    short-summary: Manage VPN server configuration.
"""

helps['network vpn-server-config create'] = """
    type: command
    short-summary: Create a VPN server configuration.
    examples:
      - name: Create a VPN server configuration with VPN auth type
        text: |
            az network vpn-server-config create -n MyVPNServerConfig -g MyRG --vpn-client-root-certs "ApplicationGatewayAuthCert.cer" --vpn-client-revoked-certs "ApplicationGatewayAuthCert.pem"
"""

helps['network vpn-server-config list'] = """
    type: command
    short-summary: List all VPN server configuration.
"""

helps['network vpn-server-config show'] = """
    type: command
    short-summary: Show the details of a VPN server configuration.
"""

helps['network vpn-server-config set'] = """
    type: command
    short-summary: Set settings of a VPN server configuration.
    examples:
      - name: Set a VPN server configuration with Radius auth type
        text: |
            az network vpn-server-config set -n MyVPNServerConfig -g MyRG --radius-client-root-certs "ApplicationGatewayAuthCert.cer" --radius-server-root-certs "ApplicationGatewayAuthCert.pem" --radius-servers address=test1 secret=clitest score=10 --radius-servers address=test2 secret=clitest score=10
"""

helps['network vpn-server-config delete'] = """
    type: command
    short-summary: Delete a VPN server configuration.
"""

helps['network vpn-server-config wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the VPN server configuration is met.
"""

helps['network vpn-server-config ipsec-policy'] = """
    type: group
    short-summary: Manage VPN server configuration IPSec policies.
"""

helps['network vpn-server-config ipsec-policy add'] = """
    type: command
    short-summary: Add an IPSec policy to a VPN server configuration.
"""

helps['network vpn-server-config ipsec-policy list'] = """
    type: command
    short-summary: List VPN server configuration IPSec policies.
"""

helps['network vpn-server-config ipsec-policy remove'] = """
    type: command
    short-summary: Remove an IPSec policy from a VPN server configuration.
"""

helps['network vpn-server-config ipsec-policy wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the IPSec policy of a VPN server configuration is met.
"""
# endregion

# region VpnServerConfig
helps['network p2s-vpn-gateway'] = """
    type: group
    short-summary: Manage point-to-site VPN gateway.
"""

helps['network p2s-vpn-gateway create'] = """
    type: command
    short-summary: Create a point-to-site VPN gateway.
    examples:
      - name: Create a point-to-site VPN gateway.
        text: |
            az network p2s-vpn-gateway create -g MyRG -n MyP2SVPNGateway --scale-unit 2 --vhub MyVhub --vpn-server-config MyVPNServerConfig --address-space 10.0.0.0/24 11.0.0.0/24
      - name: Create a point-to-site VPN gateway with routing configuration.
        text: |
            az network p2s-vpn-gateway create -g MyRG -n MyP2SVPNGateway --scale-unit 2 --vhub MyVhub --vpn-server-config MyVPNServerConfig --address-space 10.0.0.0/24 11.0.0.0/24 --associated-route-table /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/virtualHubs/MyHub/hubRouteTables/MyRouteTable1 --propagated-route-tables /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/virtualHubs/MyHub/hubRouteTables/MyRouteTable1 /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/virtualHubs/MyHub/hubRouteTables/MyRouteTable2 --labels label1 label2
"""

helps['network p2s-vpn-gateway list'] = """
    type: command
    short-summary: List all point-to-site VPN gateway.
"""

helps['network p2s-vpn-gateway show'] = """
    type: command
    short-summary: Show the details of a point-to-site VPN gateway.
"""

helps['network p2s-vpn-gateway update'] = """
    type: command
    short-summary: Update settings of a point-to-site VPN gateway.
"""

helps['network p2s-vpn-gateway delete'] = """
    type: command
    short-summary: Delete a point-to-site VPN gateway.
"""

helps['network p2s-vpn-gateway wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the point-to-site VPN gateway is met.
"""

helps['network p2s-vpn-gateway connection'] = """
    type: group
    short-summary: Manage point-to-site VPN gateway connections.
"""

helps['network p2s-vpn-gateway connection list'] = """
    type: command
    short-summary: List all connections for a given point-to-site VPN gateway.
    examples:
      - name: List all connections for a given point-to-site VPN gateway
        text: |
            az network p2s-vpn-gateway connection list -g MyRG --gateway-name MyP2SVPNGateway
"""

helps['network p2s-vpn-gateway connection show'] = """
    type: command
    short-summary: Show the details of a point-to-site VPN gateway connection.
    examples:
      - name: Show the details of a point-to-site VPN gateway connection
        text: |
            az network p2s-vpn-gateway connection show -g MyRG -n connection --gateway-name MyP2SVPNGateway
"""
# endregion
