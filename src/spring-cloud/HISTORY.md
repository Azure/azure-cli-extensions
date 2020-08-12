Release History
===============
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
