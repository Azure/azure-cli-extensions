Release History
===============
2.12.3
---
* Fix the deploy jar failure.

2.12.2
---
* Add support for custom container image.

2.12.1
-----
* Fix list services by subscription issue

2.12.0
-----
* Add --disable-probe argument into 'az spring-cloud app create', 'az spring-cloud app update', 'az spring-cloud app deploy' and 'az spring-cloud app deployment create'

2.11.2
-----
* Add support to stop and start Azure Spring Cloud service instance
* Add new command `spring-cloud stop` to stop a running Azure Spring Cloud service instance
* Add new command `spring-cloud start` to start a stopped Azure Spring Cloud service instance

2.11.1
-----
* Add support for Diagnostic Operation. Heap dump: 'spring-cloud app deployment generate-heap-dump'. Thread Dump: 'spring-cloud app deployment generate-thread-dump'. JFR: 'spring-cloud app deployment start-jfr'
* Add support for public certificate crud, source could be either key vault or local file
* Application could load public certificate by using argument `--loaded_public_certificate_file` in batch or
  directly using `spring-cloud app append-loaded-public-certificate` one by one
* Add support to list all apps which have loaded the certificate `spring-cloud certificate list-reference-app`

2.11.0
-----
* Support functions for Persistent Storage feature.
* Add new command group 'az spring-cloud storage' to register your own storage to Azure Spring Cloud
* Add new command `append-persistent-storage` into 'az spring-cloud app' to append persistent storage to applications
* Add new parameter `--persistent-storage` into 'az spring-cloud app create' and 'az spring-cloud app update' to accept a json file to create persistent storages

2.10.0
-----
* Support functions for Java In-Process Agent feature General Available.
* For Application Insights configuration, support both `connection_string` and `instrumentation_key`,
  and we recommended to use `connection_string`.
* Enabling In-Process Agent is equivalent to enabling application insights.
* Mark `enable-java-agent` as deprecated, since IPA is GA-ed.
* Mark application insights related parameter as deprecated in `az spring-cloud update`,
  it's still supported, but will de decommissioned in the future,
  and we recommended to use `az spring-cloud app-insights update`.
* Support `--sampling-rate` in `az spring-cloud create`.
* Decommissioned `disable-distributed-tracing` parameter.

2.9.0
-----
* Add --source-path argument into 'az spring-cloud app deploy' and 'az spring-cloud app deployment create'
* Deprecate source code deploy without --source-path argument in 'az spring-cloud app deploy' and 'az spring-cloud app deployment create'
* Add Support to create banner deployment in 'az spring-cloud app deployment create'

2.8.0
-----
* Add support to validate jar before create/update deployment
* Add support to delete deployment with no-wait

2.7.1
-----
* Fix source code deployment build log issues

2.7.0
-----
* Migrate to track2 SDK

2.6.0
-----
* Add support for 0.5 core, 512 Mi resource requests in app deployment

2.5.1
-----
* Revert `2.5.0` as a quick fix for incompatibility with old api-version.

~~2.5.0~~
-----
* Deprecated
* ~~Migration from `instrumentation_key` to `connection_string` when update java agent configurations.~~

2.4.0
-----
* Add support to format log streaming of structured JSON output

2.3.1
-----
* Fix disable-ssl in redis binding.

2.3.0
-----
* Support End-to-end TLS.

2.2.1
-----
* Fix exception in app service binding

2.2.0
-----
* Add bring your own route tables support

2.1.2
-----
* Add optional '--deployment' to 'az spring-cloud app logs' command
* Add a parameter '--assign-endpoint' into 'az spring-cloud app create' and 'az spring-cloud app update'
* Deprecate the parameter '--is-public' in 'az spring-cloud app create' and 'az spring-cloud app update'

2.1.1
-----
* Remove preview parameter '--enable-java-agent' from 'az spring-cloud update'.
* Fix warning message of '--disable-distributed-tracing'.

2.1.0
-----
* Support Java In-Process Agent.

2.0.1
-----
* Fix 'az spring-cloud app list' command issues.

2.0.0
-----
* Switch api-version from 2019-05-01-preview to 2020-07-01

1.2.0
-----
* Add support for sovereign cloud.

1.1.1
-----
* Reimport the updated version of Python SDK.

1.1.0
-----
* Support Steeltoe feature.

1.0.1
-----
* Optimize VNet Injection validator

1.0.0
-----
* Bump version to 1.0.0

0.5.1
-----
* Stream the build logs when deploying from source code
* Fix distributed tracing issues

0.5.0
-----
* Support Virtual Network injection feature.

0.4.0
-----
* Remove 'cpu', 'memory' and 'instance-count' from 'az spring-cloud app deploy' command
* Fix log streaming feature proxy issues

0.3.1
-----
* Remove azure-storage-blob dependency

0.3.0
-----
* Enable distributed tracing by default when creating the service
* Enable to update tags and distributed tracing settings by using "az spring-cloud update"

0.2.6
-----
* Fix required sku issue

0.2.5
-----
* Enable to specified sku when create or update service instance

0.2.4
-----
* Add command "az spring-cloud app identity" to support Managed Identity feature

0.2.3
-----
* Add command "az spring-cloud app custom-domain" and "az spring-cloud certificate" to support Custom Domain feature.

0.2.2
-----
* Remove the limitation of max compatible cli core version

0.2.1
-----
* Add command "az spring-cloud app logs" to replace "az spring-cloud app log tail" for log streaming.
* "az spring-cloud app log tail" will be deprecated in a future release
* Fix Python 3 and Python 2 compatible issues.

0.2.0
-----
* Support the log streaming feature.
* Add command for log streaming: az spring-cloud app log tail.

0.1.1
-----
* Improve the verbosity for the long running commands.
* Refine the descriptions and error messages for the command.

0.1.0
-----
* Initial release.
