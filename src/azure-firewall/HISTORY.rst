.. :changelog:

Release History
===============

0.11.0
++++++
* Fix issue: `create_or_update` not found

0.10.0
++++++
* `az network firewall create`: Add new parameter `--tier`
* Migrate to Track2 SDK.

0.9.0
++++++
* `az network firewall policy rule-collection-group collection add-filter-collection`: Add parameter 'web-categories'
* `az network firewall policy rule-collection-group collection rule add`: Add parameter 'web-categories'

0.8.0
++++++
* `az network firewall policy create`: support `--sku` to create premium tier firewall policy
* `az network firewall policy create`: support `--key-vault-secret-id` to configure transport security
* `az network firewall policy rule-collection-group collection`: support `--target-urls` to configure target URLs and `--enable-terminate-tls` to enable TLS terminate for rules for premium tier firewall policy
* `az network firewall policy intrusion-detection`: new commad group to support to configure intrusion detection policy for premium tier firewall policy

0.6.2
++++++
* `az network firewall create`: improve documentation of application and network rules options
0.6.1
++++++
* `az network firewall create`: make Network.DNS.EnableProxy option value lowercase
0.6.0
++++++
* [Breaking Change] `az network firewall threat-intel-allowlist`: rename whitelist to allowlist

0.5.1
++++++
* `az network firewall create/update`: support new `--allow-active-ftp` argument.
* `az network firewall network-rule delete`: refine help message.

0.5.0
++++++
* `az network firewall create/update`: support multiple ip addresses for vhub firewall.
* `az network firewall policy rule-collection-group rule-collection`: support multiple DNAT rules and ip groups.

0.4.0
++++++
* `az network firewall create/update`: add --dns-servers, --enable-dns-proxy, --require-dns-proxy-for-network-rules to configure DNS proxy settings.
* `az network firewall policy create/update`: add --dns-servers, --enable-dns-proxy, --require-dns-proxy-for-network-rules to configure DNS proxy settings.
* `az network firewall policy create`: support threat white list arguments.
* `az network firewall create/update`: support --threat-intel-model argument.
0.3.1
++++++
* `az network firewall network-rule/nat-rule`: Bug fixes.

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
