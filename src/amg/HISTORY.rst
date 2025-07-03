.. :changelog:

Release History
===============

0.1.0
++++++
* Initial release.

0.1.1
++++++
* `az grafana delete`: automatically remove the default role assignment created for the managed identity

0.1.2
++++++
* `az grafana create`: support guest users

0.2.0
++++++
* `az grafana api-key`: support api keys

0.3.0
++++++
* `az grafana service-account`: support service accounts

1.0
++++++
* Command module GA

1.1
++++++
* `az grafana update`: support email contact point through new SMTP configuration arguments

1.2
++++++
* `az grafana backup`: backup a Grafana workspace
* `az grafana restore`: restore a Grafana workspace
* `az grafana dashboard sync`: sync dashboard between 2 Grafana workspaces

1.2.8
++++++
* `az grafana create`: support deterministic outbound IP argument

1.2.10
++++++
* `az grafana backup`: exclude provisioned dashboards during backup

1.3.0
++++++
* `az grafana update`: support Grafana major version argument

1.3.1
++++++
* `az grafana delete`: bump azure-mgmt-authorization package version

1.3.2
++++++
* Revert to vendored SDK to fix an issue caused by Homebrew dependencies for Mac users

1.3.3
++++++
* `az grafana dashboard sync`: support library panel sync
* `az grafana dashboard create`: use unique id instead of generic id for folder creation

1.3.4
++++++
* `az grafana dashboard sync`: use case-insensitive comparison for library panel folders

1.3.5
++++++
* `az grafana dashboard sync`: fix version mismatch issue for library panel sync

1.3.6
++++++
* `az grafana folder show`: remove folder lookup by id due to deprecated API
* `az grafana folder delete`: remove folder lookup by id due to deprecated API
* `az grafana dashboard import`: update call from deprecated dashboard import API to dashboard create/update API

2.0.0
++++++
* Move existing Grafana CRUD command implementations to AAZ CodeGen
* `az grafana create`: move implementation to AAZDev Tool & implicitly support role assignment principal types
* `az grafana update`: move implementation to AAZDev Tool
* `az grafana list`: move implementation to AAZDev Tool
* `az grafana show`: move implementation to AAZDev Tool
* `az grafana delete`: move implementation to AAZDev Tool

2.1.0
++++++
* `az grafana migrate`: migrate data from a self-hosted Grafana instance to Azure Managed Grafana instance

2.2.0
++++++
* `az grafana list-available-plugin`: list all available plugins available for installation

2.3.0
++++++
* `az grafana private-endpoint-connection`: support private endpoint connection management
* `az grafana mpe`: support managed private endpoint management

2.3.1
++++++
* `az grafana migrate`: fix issue with remapping logic for Grafana datasources with short uids

2.4.0
++++++
* `az grafana sync`: fix issues with syncing empty dashboards from Grafana 9 and syncing dashboards with collapsed rows
* `az grafana backup`: support skipping Grafana folder permissions argument

2.5.0
++++++
* `az grafana integrations monitor`: support Azure Monitor workspace integration

2.5.1
++++++
* `az grafana dashboard import`: validate JSON file content prior to import

2.5.2
++++++
* `az grafana create`: fix issue with principal type implicit selection during role assignment step

2.5.3
++++++
* `az grafana service-account token create`: set token default expiration time to 1 day as stated in the documentation

2.5.4
++++++
* `az grafana dashboard import`: fix issue with JSON file validation
* `az grafana folder update`: fix issue with overwrite setting

2.5.5
++++++
* `az grafana notification-channel test`: fix issue with test output parsing

2.6.0
++++++
* `az grafana integrations monitor add`: support optional subscription id argument for multi-subscription scenarios
* `az grafana integrations monitor delete`: support optional subscription id argument for multi-subscription scenarios
* `az grafana notification-channel`: deprecate command group as part of Grafana legacy alerting deprecation

2.6.1
++++++
* Remove msrestazure dependency

2.7.0
++++++
* `az grafana api-key`: deprecate command group as Grafana Labs is sunsetting API keys