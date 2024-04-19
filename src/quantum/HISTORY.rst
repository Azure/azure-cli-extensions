.. :changelog:

Release History
===============

1.0.0b3
++++++
* [2024-04-11] Version intended to work with QDK version 0.29.0
* Change role assignment for new Workspaces to linked Storage Accounts from Contributor to Storage Account Contributor.

1.0.0b2
++++++
* [2024-02-14] Version intended to work with QDK version 0.29.0
* Add azure quantum connection string/ api key functionalities.

1.0.0b1
++++++
* [2024-02-08] Version intended to work with QDK version 0.29.0
* Updated documentations and messages.

0.21.0
++++++
* [2024-01-10] Version intended to work with QDK version 0.29.0
* Updated documentation to support the Modern QDK. Users can now utilize the Modern QDK to generate QIR in human-readable LLVM code and submit it using CLI. For detailed instructions, please refer to: https://github.com/microsoft/qsharp/wiki/Differences-from-the-previous-QDK#qir-generation.
* Added a message to warn users that the Classic QDK is on its way to deprecation.

0.20.0
++++++
* [2023-12-13] Version intended to work with QDK version 0.29.0
* Adding an ability to get a job output (for certain targets) even if the job is in `Failed` state.

0.19.0
++++++
* [2023-02-27] Version intended to work with QDK version 0.27.253010
* You can specify --skip-autoadd when creating a workspace to only add the providers listed after the -r parameter, so provider plans in the "Credits for All" program will not be automatically added.
* Adding resource estimator batching job support to az quantum.

0.18.0
++++++
* [2023-02-08] Version intended to work with QDK version 0.27.253010 and Azure CLI 2.41.0 or greater.
* You can now submit QIR and pass-through jobs using the CLI.
* Fixed Azure/azure-cli-extensions Issue #5831 to eliminate some workspace creation errors.

0.17.0
++++++
* [2022-11-02] Update default QDK version to latest 0.27.238334 - See https://learn.microsoft.com/azure/quantum/release-notes.
* [2022-10-14] [Edited] The 0.17.0 release was originally intended to work with QDK version 0.26.233415, however additional functionality has been added to QDK version to 0.27.238334 that can be accessed by CLI extension 0.17.0.
* The `az quantum` reference documentation now indicates which command parameters are required, and missing-parameter error messages are more informative. See https://learn.microsoft.com/cli/azure/quantum
* You can submit jobs to the microsoft.simulator.resources-estimator target using the CLI.

0.16.0
++++++
* [2022-06-30] Version intended to work with QDK version 0.25.218240
* Providers participating in the "Credits for All" program will automatically be added when you create a workspace with the CLI. See https://docs.microsoft.com/en-us/azure/quantum/credits-faq
* You can pass a TargetCapability value to the Q# compiler by adding the --target-capability parameter to an az quantum run, execute, or job submit command.

0.15.0
++++++
* [2022-04-25] Version intended to work with QDK version v0.24.208024
* Extended error message and added help examples for provider/SKU '-r' parameter.
* Fixed issue azure-cli-extensions/4697, which allows setting a polling interval when waiting for an Azure Quantum job to complete.
* Outputting job submission progress messages to stderr so stdout will only contain valid JSON by default.
* Added 'Microsoft.AzureQuantum-' prefix to workspace creation deployment name.
* Increased workspace creation timeout to 15 minutes.

0.14.0
++++++
* [2022-03-30] Version intended to work with QDK version v0.24.201332
* Extended error message in failed jobs to include details originated from the provider.
* Completed support in workspace creation for all storage account types allowed in the Azure Quantum service.
* Improved visual feedback in 'az quantum execute' command indicating to the user that the process has started.

0.13.0
++++++
* [2022-03-03] Version intended to work with QDK version v0.23.195983
* Fixed workspace race condition using an Azure Resource Manager template to synchronize deployment.

0.12.0
++++++
* [2022-01-26] Version intended to work with QDK version v0.22.187631
* Updated data plane generated client to API version 2021-11-01-preview.
* Added support for displaying cost estimate for a job when available.

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
* [2021-07-22] Reduced the length of the user agent reported by the tool.

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
