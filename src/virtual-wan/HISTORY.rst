.. :changelog:

Release History
===============

1.0.0
++++++
* add new command: `az network p2s-vpn-gateway disconnect`.
* add new command: `az network p2s-vpn-gateway reset`.
* add new command: `az network vpn-gateway connection packet-capture start`.
* add new command group: `az network vpn-gateway nat-rule`.

0.3.0
++++++
* `az network vhub connection`: Fix cross-tenant connection cannot be created.

0.2.17
++++++
* `az network vhub create`: Add new parameter `allow-b2b-traffic` and `auto-scale-config`.
* `az network vhub update`: Add new parameter `allow-b2b-traffic` and `auto-scale-config`.

0.2.16
++++++
* `az network vhub`: Add new subgroup `route-map` to support managing virtual hub route map.
* `az network vhub connection create`: Add new parameter `associated_inbound_routemap` and `associated_outbound_routemap`.
* `az network vhub connection update`: Add new parameter `associated_inbound_routemap` and `associated_outbound_routemap`.
* `az network p2s-vpn-gateway create`: Add new parameter `associated_inbound_routemap` and `associated_outbound_routemap`.
* `az network p2s-vpn-gateway update`: Add new parameter `associated_inbound_routemap` and `associated_outbound_routemap`.
* `az network vpn-gateway connection create`: Add new parameter `associated_inbound_routemap` and `associated_outbound_routemap`.
* `az network vpn-gateway connection update`: Add new parameter `associated_inbound_routemap` and `associated_outbound_routemap`.

0.2.15
++++++
* Deprecate route table v2 parameters.

0.2.14
++++++
* `az network vhub create`: Add new parameter `--asn`.
* `az network vhub update`: Add new parameter `--asn`.

0.2.13
++++++
* add new command group: `az network vhub routing-intent`.

0.2.12
++++++
* `az network vhub create`: Add new parameter `--hub-routing-preference`.
* `az network vhub update`: Add new parameter `--hub-routing-preference`.
* Bump api version from 2020-05-01 to 2021-08-01.

0.2.11
++++++
* add new command group: `az network vpn-gateway connection vpn-site-link-conn`.
* add new command group: `az network vpn-gateway connection vpn-site-link-conn ipsec-policy`.
* add new command group: `az network vpn-site link`.
* `az network vpn-gateway connection`: support new parameters `--vpn-site-link` and `--with-link`.
* `az network vpn-site`: support new parameter `--with-link`.

0.2.10
++++++
* add new command group: `az network vhub bgpconnection`.

0.2.9
++++++
* bugfix: `az network vpn-gateway connection ipsec-policy add/remove` doesn't migrate to track2.
* bugfix: `network vhub route reset/remove` doesn't migrate to track2.

0.2.8
++++++
* bugfix: `az network vpn-gateway connection ipsec-policy add ` ipsec_policies is NoneType.

0.2.7
++++++
* bugfix: `az network vhub get-effective-routes` always returns empty value list.

0.2.6
++++++
* `az network vhub get-effective-routes` support `-o table` outputs.

0.2.5
++++++
* Migrate to Track2 SDK.

0.2.4
++++++
* `az network vhub connection`: Support command `update`
* `az network vpn-gateway connection`: Support command `update`

0.2.3
++++++
* `az network vpn-gateway connection`: Change the underlying operations from VpnGatewayOperations to VpnConnectionOperations
* [BREAKING CHANGE] `az network vpn-gateway connection create`: the response data structure of successful creation is `VpnConnection` instead of `VpnGateway`

0.2.2
++++++
* `az network p2s-vpn-gateway vpn-client`: Support to generate download URL to get VPN client configuration

0.2.1
++++++
* [BREAKING CHANGE] `az network vwan create/update`: Remove the stale argument `--vnet-to-vnet-traffic`.

0.2.0
++++++
* `az network vhub route-table`: Support virtual hub v3 route table.
* Support Routing Configuration property on Express Route, Vpn, P2S Connection Configuration and Hub Virtual Network Connection resources.
• `az network vhub get-effective-routes`: Support getting effective routes which would take input parameter as Route Table or Connection (ER,S2S, P2S, Hub Virtual Network Connection) Resource ID.
• Support the virtual network connections to be created/updated/deleted only using direct PUT/DELETE calls on the Virtual Network connection.
* `az network vhub route reset`: Reset this route when the routingState is set to Failed.

0.1.0
++++++
* Initial release.
