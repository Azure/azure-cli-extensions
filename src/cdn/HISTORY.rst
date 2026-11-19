.. :changelog:

Release History
===============

1.0.0b4
+++++++
* Upgrade AFD commands to API version 2026-09-01-preview, preserving Classic CDN commands on 2026-04-01-preview and other pinned API versions through separate profile command models.
* Add preview AFD authentication policy commands with Microsoft Entra ID configuration, domain and route associations, Block/Log actions, and token forwarding.
* Add AFD custom domain server TLS group policies and configurable TLS groups.
* Add AFD origin certificate name validation modes and custom certificate subjects.
* Add AFD origin group capacity distribution settings and gRPC health probes, and AFD route gRPC settings.
* Add ClientResponse invocation support for AFD EdgeAction rule actions, including rule action subcommands and batch rules.
* Add offline regression tests for the new API surface and preserved API version pins.

1.0.0b3
++++++
* Update CDN and AFD generated command models to API version 2026-04-01-preview, including AFD MTLS, origin authentication, rule-set batch rules, and refreshed scenario recordings.
* Add support for configuring profile-level Web Application Firewall policies and route associations on AFD security policies.
* Update AFD/CDN AAZ-generated command models and tests to use native JSON support, including AFD rule action and condition subcommands.
* Add post-migration endpoint cutover guidance after committing a classic CDN profile migration.

1.0.0b1
+++++++
* Initial release. Migrated from azure-cli core CDN command module.
