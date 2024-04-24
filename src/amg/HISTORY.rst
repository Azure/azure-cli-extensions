.. :changelog:

Release History
===============

0.1.0
++++++
* Initial release.

0.1.1
++++++
* update 'az grafana delete' to automatically remove the default role assignment created for the managed identity

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
* `az grafana update`: support email through new SMTP configuration arguments

1.2
++++++
* `az grafana backup`: backup a grafana workspace
* `az grafana restore`: restore a grafana workspace
* `az grafana dashboard sync`: sync dashboard between 2 grafana workspaces

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