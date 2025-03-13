.. :changelog:

Release History
===============

1.7.0
++++++
* Add support for metrics reference identity. Metrics reference identity can be set using `--metrics-reference-identity` argument in 'az load test create' and 'az load test update' commands. Metrics reference identity set in YAML config file under key `referenceIdentities` with `kind` as `Metrics` will also be honoured.


1.6.0
++++++
* Add support for engine reference identity using CLI. Engine reference identity can be set using `--engine-ref-id-type` and `--engine-ref-ids` argument in 'az load test create' and 'az load test update' commands. Engine reference identity set in YAML config file under key `referenceIdentities` with `kind` as `Engine` will also be honoured.


1.5.0
++++++
* Add support for Locust based load tests.


1.4.3
++++++
* Updated the vendored_sdks to include 2024-12-01-preview data plane API version.


1.4.2
++++++
* Update minimum required version of azure-cli-core to 2.66.0. This is needed to use `from azure.cli.core.util import run_az_cmd`, which is used in download-files command for high-scale load tests.


1.4.1
++++++
* Move the `from azure.cli.core.util import run_az_cmd` to function scope to unblock users of existing features and most of the new features. Only the high scale download files feature requires this import, and it will be fixed in the next release.


1.4.0
++++++
* Add support for multi-region load test configuration. Multi-region load test configuration can be set using `--regionwise-engines` argument in 'az load test create' and 'az load test update' commands. Multi-region load test configuration set in YAML config file under key `regionalLoadTestConfig` will also be honoured.
* Bug fix for `engineInstances` being reset to 1 and not getting backfilled using test's existing configuration when engine instances are not explicitly specified either in YAML config file or CLI argument.
* Add support for advanced URL test with multiple HTTP request using JSON file. Add `--test-type` argument to 'az load test create' and honor `testType` key in YAML config file.
* Add CLI parameter `--report` to 'az load test-run download-files' to download the dashboard reports.
* Enable debug level logging using `--debug-mode` argument in 'az load test-run create' command .
* Return the SAS URL to copy artifacts to storage accounts using command 'az load test-run get-artifacts-url'.
* Add config for high-scale load tests and extend 'az load test-run download-files' to support download of logs and results from artifacts container for such tests.
* Add command 'az load test convert-to-jmx' to convert URL type tests to JMX tests.
* Add commands 'az load test set-baseline' to set the baseline for a test and 'az load test compare-to-baseline' to compare recent test runs to the baseline test run.


1.3.1
++++++
* Bug fix for `splitAllCSVs` not being honoured from config file due to CLI argument being set as false by default leading to configuration not being selected from the config file.
* Bug fix for `keyVaultReferenceIdentity` not being honoured from config file as the key being looked up while YAML parsing was incorrect.
* Change 'VALIDATION_FAILED' to 'VALIDATION_FAILURE' as a terminal status for File Validation.
* Add 'NOT_VALIDATED' as a terminal status for File Validation in Async IO.

1.3.0
++++++
* Add support for autostop criteria. Autostop error rate and time window in seconds can be set using `--autostop-error-rate` and `--autostop-time-window` arguments in 'az load test create' and 'az load test update' commands. Autostop can be disabled by using `--autostop disable` in 'az load test create' and 'az load test update' commands. Autostop criteria set in YAML config file will now also be honoured.

1.2.0
++++++
* Added support for disable public IP in test creation and update. This can be done by using --disable-public-ip argument in 'az load test create' and 'az load test update' commands.

1.1.1
++++++
* Fix empty response object on CLI when using 'az load test file upload'
* Add 'NOT_VALIDATED' as a terminal status for File Validation

1.1.0
++++++
* Add support for ZIP artifacts upload to a test. Artifacts can be uploaded through YAML config when using --load-test-config-file and through cmd `az load test file upload`, the associate --file-type is `ZIPPED_ARTIFACTS`
* Upgrade vendored_sdks to use API version '2024-05-01-preview'
* Fix for uploading files from YAML config when relative path is provided for configurationFiles
* Add test cases for ZIP artifacts upload

1.0.2
++++++
* Patch for removing msrestazure dependency and using azure.mgmt.core.

1.0.1
++++++
* Fix for sending correct failureCriteria request payload when using `az load test create` and `az load test update` commands with `--load-test-config-file` option and config file having failureCriteria.

1.0.0
++++++
* Adding support for "az load test" in AzureUSGovernment cloud.
* Fix '(InvalidRequestBody) Secret "xxxxx" value can't be null' error that occurs when using 'az load test create/update' with a config file that contains secrets.

0.3.3
++++++
* Fix for 'az load test update' command when using --load-test-config-file option failing due to accessing undefined object.
* Added support to update test run display in "az load test-run update" command by providing --display-name argument.

0.3.2
++++++
* Added null support for argument --certificate and --subnet in commands "az load update" and "az load create" to remove those properties from test.
* Added support to remove certificate, subnet from config file when provided in commands "az load update" and "az load create".
* Logical implementation changed when using config file using argument --load-test-config-file in commands "az load test update" and "az load test create".  
* Added test cases test_load_test_update_with_config to test the new fixes.

0.3.1
++++++
* Enhanced data plane test cases.
* Fix for failure criteria when 'az load test create' and 'az load test update' commands when using --load-test-config-file option.

0.3.0
++++++
* Initial release of Azure Load Testing data plane command groups.

0.2.0
++++++
* Stable version release.

0.1.0
++++++
* Initial release.
