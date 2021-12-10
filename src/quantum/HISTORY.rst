.. :changelog:

Release History
===============

0.11.0
++++++
* [2021-12-14] Version intended to work with QDK version v0.21.2112.180703
* Job result histograms will be left-aligned (not centered) in console output.

0.10.0
++++++
* [2021-11-22] Version intended to work with QDK version v0.20.2111.177148
* Fixed issue where the update prompt shows during test automation and should be suppressed.

0.9.0
++++++
* [2021-10-25] Version intended to work with QDK version v0.20.2110.171573
* Aligned the extension tests with the Azure Quantum E2E test infrastructure.
* Replaced deprecated CLIError class with new error types.
* Appended 'CLI' to UserAgent to distinguish Azure Quantum calls from different clients.

0.8.0
++++++
* [2021-09-27] Version intended to work with QDK version v0.19.2109.165653
* Users will receive recommendation at most once a day, to update the az quantum extension if the version installed is out-of-date.
* Added parameter `--job-params` to job submission commands to pass additional metadata.
* Fixed trimming issue in processing the output of some jobs.

0.7.0
++++++
* [2021-08-31] Version intended to work with QDK version v0.18.2108.160310
* Provide compiler output to users in case of error for easier troubleshooting.
* Fixed bug in which retrieving output from workspaces in a location different to another set as default failed.
* Processing jobs that produce no output is allowed.
* Simplification of resources used in extension tests and allowing overrides via environment variables.

0.6.1
++++++
* [2021-07-22] Reduced the lenghth of the user agent reported by the tool.

0.6.0
++++++
* [2021-07-20] Version intended to work with QDK version v0.18.2106.148911
* Adding command to request job cancellation: `az quantum job cancel`.
* Fixed a bug in which job submissions in Azure Quantum that emit standard output were reported as failed, even if the job succeeded.
* Fixed issue with job submissions from a different directory.

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
