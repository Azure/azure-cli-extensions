.. :changelog:

Release History
===============

2.1.0
++++++++++++++++++
* Introduce a new feature to disable health checks for kustomizations applied to the cluster.
* Bump pycryptodome to 3.21.0

2.0.0
++++++++++++++++++
* Remove the deprecated flux v1 `create` cmd

1.7.0
++++++++++++++++++
* Add support for Azure Blob Storage

1.6.0
++++++++++++++++++
* Add support for provisionedClusters

1.5.1
++++++++++++++++++
* Bump pycryptodome to 3.14.1 to support Python 3.10

1.5.0
++++++++++++++++++
* Update models to 2022-03-01 for GA
* Remove unneeded warning for HTTPS urls

1.4.1
++++++++++++++++++
* [BREAKING CHANGE] `--access-key` changed to `--bucket-access-key`
* [BREAKING CHANGE] `--secret-key` changed to `--bucket-secret-key`
* [BREAKING CHANGE] `--insecure` changed to `--bucket-insecure`
* Fix help text for bucket parameters

1.4.0
++++++++++++++++++
* Add `--kind bucket` for creation of S3 bucket as source for fluxConfigurations

1.3.0
++++++++++++++++++
* Add `deployed-object` command group for showing deployed Flux objects from configuration
* Show extension error when `microsoft.flux` extension is in a failed state

1.2.0
++++++++++++++++++
* Add Flux v2 support with command subgroups
* Add update support to Flux v2 resources

1.1.1
++++++++++++++++++
* Enable helm-operator chart version 1.4.0

1.1.0
++++++++++++++++++
* Update sourceControlConfiguration resource models to Track2

1.0.1
++++++++++++++++++
* Add provider registration check

1.0.0
++++++++++++++++++
* Support api-version 2021-03-01
* Update helm operator parameter aliases
* Migrate from k8sconfiguration to k8s-configuration
