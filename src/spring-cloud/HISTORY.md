Release History
===============
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
