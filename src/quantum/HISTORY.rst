.. :changelog:

Release History
===============

0.5.0
++++++
* [2021-05-25] Version intended to work with QDK version v0.17.2105.143879
* Adapted to 'az' tool version 2.23.0
* Added user agent information on calls to Azure Quantum Service.

0.4.0
++++++
* [2021-05-07] Version intended to work with QDK version v0.16.2104.138035
* Updated generated clients for Azure Quantum control plane to include support for restricted plans.
* Fixed regression on offerings commands dependent on Azure Markeplace APIs.

0.3.0
++++++
* [2021-03-31] Version intended to work with QDK version v0.15.2103.133969
* Fix issue with incorrect location parameter during job submission.
* Updating command 'az quantum workspace create' to require an explicit list of Quantum providers and remove a default.

0.2.0
++++++
* [2021-03-08] Version targeting QDK version 0.15.2102.129448
* Adding command group 'az quantum offerings' with 'list', 'accept-terms' and 'show-terms'
* Adding parameter '--provider-sku-list' to 'az quantum workspace create' to allow specification of Quantum providers.
* Specified time unit in Azure Quantum Target table description.

0.1.0
++++++
* [2021-02-01] Initial release. Version targeting QDK version 0.15.2101125897
