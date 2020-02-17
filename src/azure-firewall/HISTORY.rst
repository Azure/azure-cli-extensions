.. :changelog:

Release History
===============

0.3.0
++++++
* `az network firewall ip-config`: Add management ip config args group.
* `az network firewall management-ip-config`: Delete create command since service doesn't support it.

0.2.0
++++++
* `az network firewall ip-config`: deprecate --private-ip-address
* `az network firewall create/update`: support --sku, --firewall-policy and --vhub.

0.1.9
++++++
* `az network firewall management-ip-config`: support creating/showing management ip configuration.

0.1.8
++++++
* `az network firewall create`: support private-ranges
* `az network firewall threat-intel-whitelist`:  support threat intelligence whitelist.

0.1.7
++++++
* `az network firewall network-rule/nat-rule/application-rule`: support ip-groups for firewall rules.

0.1.6
++++++
* `az network firewall ip-config`: bug fix to support multiple ip-config creation.

0.1.5
++++++
* `az network firewall application-rule`: bug fix.

0.1.4
++++++
* `az network firewall policy`: support firewall policy and its child resource.

0.1.3
++++++
* `az network firewall create/update`: added `--zones` argument to support Availability Zones.
