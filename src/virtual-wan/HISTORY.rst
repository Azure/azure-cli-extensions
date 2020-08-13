.. :changelog:

Release History
===============

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
