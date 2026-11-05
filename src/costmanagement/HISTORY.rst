.. :changelog:

Release History
===============

1.1.0
++++++
* Fix Azure/azure-cli-extensions#10007: az costmanagement export: Update Exports API version from ``2020-06-01`` to ``2025-03-01`` to support exports created via the Azure portal and newer API versions

1.0.0
++++++
* Remove ADAL dependencies

0.3.0
++++++
* Add command ``az costmanagement show-operation-result``

0.2.1
++++++
* [BREAKING CHANGE] Remove the command ``az costmanagement query``. You can aggregate or filter the raw data from ``az costmanagement export`` instead.
* [BREAKING CHANGE] Remove the argument ``--dataset-grouping`` from the command ``az costmanagement export create/update``. You can group the raw data from ``az costmanagement export`` instead.

0.1.1
++++++
* Command group ``az costmanagement`` GA

0.1.0
++++++
* Initial release.
