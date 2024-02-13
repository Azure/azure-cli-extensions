# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# region VirtualHub
helps['network vhub get-effective-routes'] = """
    type: command
    short-summary: Get the effective routes configured for the Virtual Hub resource or the specified resource.
    examples:
    - name: Get the effective routes configured for route table in the virtual hub.
      text: |
          az network vhub get-effective-routes --resource-type RouteTable --resource-id /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/virtualHubs/MyHub/hubRouteTables/MyRouteTable -g MyRG -n MyHub
    - name: Get the effective routes configured for P2S connection in the virtual hub.
      text: |
          az network vhub get-effective-routes --resource-type P2SConnection --resource-id /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/p2sVpnGateways/MyGateway/p2sConnectionConfigurations/MyConnection -g MyRG -n MyHub
"""

helps['network vhub bgpconnection'] = """
    type: group
    short-summary: Manage virtual hub bgpconnections.
"""

helps['network vhub bgpconnection create'] = """
    type: command
    short-summary: Create a virtual hub bgpconnection.
    examples:
    - name: Create a virtual hub bgpconnection.
      text: |
          az network vhub bgpconnection create -n MyConnection -g MyRG --vhub-name MyHub --peer-asn 20000  --peer-ip "10.5.0.3"
            --vhub-conn <vhub_connection_resource_id>
"""

helps['network vhub bgpconnection list'] = """
    type: command
    short-summary: List virtual hub bgpconnections.
    examples:
    - name: List bgpconnections in a given virtual hub.
      text: |
          az network vhub bgpconnection list --vhub-name MyHub -g MyRG
"""

helps['network vhub bgpconnection show'] = """
    type: command
    short-summary: Get the details of a virtual hub bgpconnection.
    examples:
    - name: Get the details of a virtual hub bgpconnection.
      text: |
          az network vhub bgpconnection show -n MyConnection --vhub-name MyHub -g MyRG
"""

helps['network vhub bgpconnection delete'] = """
    type: command
    short-summary: Delete a virtual hub bgpconnection.
    examples:
    - name: Delete a virtual hub bgpconnection.
      text: |
          az network vhub bgpconnection delete -n MyConnection --vhub-name MyHub -g MyRG
"""

helps['network vhub bgpconnection update'] = """
    type: command
    short-summary: Update settings of a virtual hub bgpconnection.
    examples:
    - name: Update a virtual hub bgpconnection.
      text: |
          az network vhub bgpconnection update -n MyConnection --vhub-name MyHub -g MyRG --peer-asn 15000
"""

helps['network vhub bgpconnection wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of virtual hub bgpconnection is met.
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

helps['network vhub route reset'] = """
    type: command
    short-summary: Reset virtual hub route when the route state is failed.
"""

helps['network vhub route-table'] = """
    type: group
    short-summary: Manage route table in the virtual hub.
"""

helps['network vhub route-table create'] = """
    type: command
    short-summary: Create a route table in the virtual hub.
    examples:
    - name: Create a v3 route table in the virtual hub.
      text: |
          az network vhub route-table create -n MyRouteTable -g MyResourceGroup --vhub-name MyVhub --route-name MyRoute --destination-type CIDR --destinations "10.4.0.0/16" "10.6.0.0/16" --next-hop-type ResourceId --next-hop /subscriptions/MySub/resourceGroups/MyResourceGroup/providers/Microsoft.Network/azureFirewalls/MyFirewall --labels label1 label2
"""

helps['network vhub route-table update'] = """
    type: command
    short-summary: Update a route table in the virtual hub.
    examples:
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
helps['network vpn-gateway connection'] = """
    type: group
    short-summary: Manage site-to-site VPN gateway connections.
"""

helps['network vpn-gateway connection create'] = """
    type: command
    short-summary: Create a site-to-site VPN gateway connection.
    examples:
      - name: Create a site-to-site VPN gateway connection
        text: |
            az network vpn-gateway connection create -g MyRG -n MyConnection --gateway-name MyGateway --remote-vpn-site /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/vpnSites/MyVPNSite --associated-route-table /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/virtualHubs/MyHub/hubRouteTables/MyRouteTable1 --propagated-route-tables /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/virtualHubs/MyHub/hubRouteTables/MyRouteTable1 /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/virtualHubs/MyHub/hubRouteTables/MyRouteTable2 --labels label1 label2
"""

helps['network vpn-gateway connection list'] = """
    type: command
    short-summary: List site-to-site VPN gateway connections.
    examples:
      - name: List all connections for a given site-to-site VPN gateway
        text: |
            az network vpn-gateway connection list -g MyRG --gateway-name MyGateway
"""

helps['network vpn-gateway connection show'] = """
    type: command
    short-summary: Get the details of a site-to-site VPN gateway connection.
    examples:
      - name: Get the details of a site-to-site VPN gateway connection
        text: |
            az network vpn-gateway connection show -g MyRG -n MyConnection --gateway-name MyGateway
"""

helps['network vpn-gateway connection delete'] = """
    type: command
    short-summary: Delete a site-to-site VPN gateway connection.
    examples:
      - name: Delete a site-to-site VPN gateway connection
        text: |
            az network vpn-gateway connection delete -g MyRG -n MyConnection --gateway-name MyGateway
"""

helps['network vpn-gateway connection update'] = """
    type: command
    short-summary: Update settings of VPN gateway connection.
    examples:
      - name: Add labels for propagated route tables under routing configuration.
        text: |
            az network vpn-gateway connection update -g MyRG -n MyConnection --gateway-name MyGateway --labels NewLabel1 NewLabels2
"""

helps['network vpn-gateway connection wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the site-to-site VPN gateway connection is met.
"""

helps['network vpn-gateway connection ipsec-policy'] = """
    type: group
    short-summary: Manage site-to-site VPN gateway connection IPSec policies.
"""

helps['network vpn-gateway connection ipsec-policy add'] = """
    type: command
    short-summary: Add an IPSec policy to a site-to-site VPN gateway connection.
"""

helps['network vpn-gateway connection ipsec-policy list'] = """
    type: command
    short-summary: List site-to-site VPN gateway connection IPSec policies.
"""

helps['network vpn-gateway connection ipsec-policy remove'] = """
    type: command
    short-summary: Remove an IPSec policy from a site-to-site VPN gateway connection.
"""

helps['network vpn-gateway connection vpn-site-link-conn'] = """
    type: group
    short-summary: Manage site-to-site VPN gateway connection VPN site link connection.
"""

helps['network vpn-gateway connection vpn-site-link-conn add'] = """
    type: command
    short-summary: Add a VPN site link connection to a site-to-site VPN gateway connection.
    examples:
      - name: Add a VPN site link connection to site-to-site VPN gateway connection
        text: |
            az network vpn-gateway connection vpn-site-link-conn add -g MyRG --connection-name MyConnection --gateway-name MyGateway -n MyVPNSiteLinkConn \
--vpn-site-link /subscriptions/MySub/resourceGroups/MyRG/providers/Microsoft.Network/vpnSites/MyVPNSite/vpnSiteLinks/vpnsitelink \
--vpn-connection-protocol-type IKEv2
"""

helps['network vpn-gateway connection vpn-site-link-conn list'] = """
    type: command
    short-summary: List site-to-site VPN gateway connection VPN site link connection.
    examples:
      - name: List VPN site link connections on site-to-site VPN gateway connection
        text: |
            az network vpn-gateway connection vpn-site-link-conn list -g MyRG --connection-name MyConnection --gateway-name MyGateway
"""

helps['network vpn-gateway connection vpn-site-link-conn remove'] = """
    type: command
    short-summary: Remove a VPN site link connection from a site-to-site VPN gateway connection.
    examples:
      - name: Remove aVPN site link connection from site-to-site VPN gateway connection
        text: |
            az network vpn-gateway connection vpn-site-link-conn remove -g MyRG --connection-name MyConnection --gateway-name MyGateway --index 1
"""

helps['network vpn-gateway connection vpn-site-link-conn ipsec-policy'] = """
    type: group
    short-summary: Manage site-to-site VPN gateway connection VPN site link IPSec policies.
"""

helps['network vpn-gateway connection vpn-site-link-conn ipsec-policy add'] = """
    type: command
    short-summary: Add an IPSec policy to a site-to-site VPN gateway connection VPN site link.
    examples:
      - name: Add an IPSec policy to a site-to-site VPN gateway connection VPN site link
        text: |
            az network vpn-gateway connection vpn-site-link-conn ipsec-policy add -g MyRG --connection-name MyConnection --gateway-name MyGateway -n MyVPNSiteLinkConn \
--ipsec-encryption AES256 --ipsec-integrity SHA256 --sa-lifetime 86471 \
--sa-data-size 429496 --ike-encryption AES256 --ike-integrity SHA384 --dh-group DHGroup14 --pfs-group PFS14
"""

helps['network vpn-gateway connection vpn-site-link-conn ipsec-policy list'] = """
    type: command
    short-summary: List site-to-site VPN gateway connection VPN site link IPSec policies.
    examples:
      - name: List IPSec policies on a site-to-site VPN gateway connection VPN site link
        text: |
            az network vpn-gateway connection vpn-site-link-conn ipsec-policy list -g MyRG --connection-name MyConnection --gateway-name MyGateway -n MyVPNSiteLinkConn
"""

helps['network vpn-gateway connection vpn-site-link-conn ipsec-policy remove'] = """
    type: command
    short-summary: Remove an IPSec policy from a site-to-site VPN gateway connection VPN site link.
    examples:
      - name: Remove an IPSec policy from a site-to-site VPN gateway connection VPN site link
        text: |
            az network vpn-gateway connection vpn-site-link-conn ipsec-policy remove -g MyRG --connection-name MyConnection --gateway-name MyGateway -n MyVPNSiteLinkConn --index 1
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


helps['network vpn-site link'] = """
    type: group
    short-summary: Manage VPN site link.
"""

helps['network vpn-site link add'] = """
    type: command
    short-summary: Add a VPN site link to VPN site configuration.
    examples:
      - name: Add a VPN site link to VPN site configuration
        text: |
            az network vpn-site link add -g MyRG --site-name VpnSite -n VpnSiteLinkName --ip-address 10.0.1.111 --asn 1234 --bgp-peering-address 192.168.0.0
"""

helps['network vpn-site link list'] = """
    type: command
    short-summary: List VPN site links on VPN site configuration.
    examples:
      - name: List VPN site links on VPN site configuration
        text: |
            az network vpn-site link list -g MyRG --site-name VpnSite
"""

helps['network vpn-site link remove'] = """
    type: command
    short-summary: Remove a VPN site link from VPN site configuration.
    examples:
      - name: Remove a VPN site links from VPN site configuration
        text: |
            az network vpn-site link remove -g MyRG --site-name VpnSite --index 1
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
    examples:
      - name: Add labels for propagated route tables under routing configuration.
        text: |
            az network p2s-vpn-gateway update -g MyRG -n MyP2SVPNGateway --labels Newlabel1 Newlabel2 Newlabel3
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

helps['network p2s-vpn-gateway vpn-client'] = """
    type: group
    short-summary: Download a VPN client configuration required to connect to Azure via point-to-site
"""

helps['network p2s-vpn-gateway vpn-client generate'] = """
    type: command
    short-summary: Generate VPN profile for P2S client of the P2SVpnGateway in the specified resource group
"""
# endregion
