## 2025-08-27

### Azure Machine Learning CLI (v2) v 2.39.0
- `az ml compute update`
  - Fix a bug compute update which caused Enable SSO property to reset.
- `az ml compute connect-ssh`
  - Fix proxy endpoint path

## 2025-05-15

### Azure Machine Learning CLI (v2) v 2.37.1
  - Handle keyerror for missing props in PAT url case in SDK.

## 2025-05-09

### Azure Machine Learning CLI (v2) v 2.37.0
- `az ml workspace create`
  - Hub and Project workspace marked as GA.

## 2025-04-24

### Azure Machine Learning CLI (v2) v 2.36.5
  - Pin major version of external dependencies in SDK.

## 2025-04-18

### Azure Machine Learning CLI (v2) v 2.36.4
  - Updated marshmallow dependency to restrict versions to >=3.5,<4.0.0 to ensure compatibility.

## 2025-04-16

### Azure Machine Learning CLI (v2) v 2.36.3
  - Removing reference of deprecated package distutils.

## 2025-04-10

### Azure Machine Learning CLI (v2) v 2.36.2
- `az ml capability-host create`
  - Made AI Search connections property optional.

## 2025-04-02

### Azure Machine Learning CLI (v2) v 2.36.1
  - Handle missing duration value in deployment poller result.

## 2025-03-14

### Azure Machine Learning CLI (v2) v 2.36.0
- `az ml compute update`
  - Fix updating compute when ssh is enabled.

## 2025-01-08

### Azure Machine Learning CLI (v2) v 2.34.0
- `az ml workspace update --network-acls`
  - Added `--network-acls` property to allow user to specify IPs or IP ranges in CIDR notation for workspace access.
- `az ml capability-host`
  - Added create operation
  - Added get operation
  - Added delete operation

## 2024-12-17

### Azure Machine Learning CLI (v2) v 2.33.0
- `az ml workspace create --provision-network-now`
  - Added `--provision-network-now` property to trigger the provisioning of the managed network when creating a workspace with the managed network enabled, or else it does nothing

## 2024-09-18

### Azure Machine Learning CLI (v2) v2.30.0
- `az ml workspace outbound-rule set`
  - Added support of Optional `--fqdns` property for private_endpoint outbound rule creation in a workspace managed network. Related to support of Application Gateway PE target.
  - Added support of Optional `--address-prefixes` property for service_tag outbound rule creation in workspace managed network.

## 2024-08-14

### Azure Machine Learning CLI (v2) v2.29.0
- `az ml compute enable-sso`
  - Added enable-sso to allow user to enable sso setting of a compute instance without any write permission set on compute.

## 2024-06-21

### Azure Machine Learning CLI (v2) v2.27.0
- `az ml workspace create --system-datastores-auth-mode`
  - Added `--system-datastores-auth-mode` to create for AzureML workspace.
- `az ml workspace update --system-datastores-auth-mode`
  - Added `--system-datastores-auth-mode` to update for AzureML workspace.
- `az ml workspace create --allow-roleassignment-on-rg`
  - Added `--allow-roleassignment-on-rg` to create for AzureML workspace with allow/disallow role assignment on RG level.
- `az ml workspace update --allow-roleassignment-on-rg`
  - Added `--allow-roleassignment-on-rg` to update for AzureML workspace with allow/disallow role assignment on RG level.

## 2023-09-11

### Azure Machine Learning CLI (v2) v2.20.0

- `az ml feature-store provision-network`
  - [Public review] Added this command to allow user to provision managed network for feature store

- `az ml feature-store create`
  - Added `--not-grant-permissions` to allow user to not grant materialization identity access to feature store

- `az ml feature-store update`
  - Added `--not-grant-permissions` to allow user to not grant materialization identity access to feature store

- `az ml feature-set`
  - Added `--feature-store-name` and deprecated `--workspace-name`, backward compatiblity will be removed in 6 month

- `az ml feature-store-entity`
  - Added `--feature-store-name` and deprecated `--workspace-name`, backward compatiblity will be removed in 6 months

- `az configure`
  - Added `--defaults feature-store=<name>` to allow user to configure default feature store

- `az ml job connect-ssh`
  - Added `--ssh-args/-c` to allow specifying additional ssh options + commands, eg to send signals to running processes or to attach to an interactive terminal

## 2023-05-09

### Azure Machine Learning CLI (v2) v2.17.0

- `az ml online-deployment create`
  - Added `--local-enable-gpu` to allow gpu access to local deployment.

- `az ml online-deployment update`
  - Added `--local-enable-gpu` to allow gpu access to local deployment.


## 2023-05-09

### Azure Machine Learning CLI (v2) v2.16.0

- `az ml job connect-ssh`
  - This command is marked as GA.

- `az ml job show-services`
  - This command is marked as GA.

- `az ml model download`
  - Fixed issue for download model from registry via the `--registry-name` argument, where workspace_name was mandatory.

- `az ml model create`
  - Add --stage(-s) flag to add the stage of the model.

- `az ml model update`
  - Add --stage(-s) flag to update the stage of the model.

- `az ml model list`
  - Add --stage(-s) flag to list by the stage of the model.

- `az ml workspace delete`
  - Add --purge(-p) flag to force to purge instead of soft delete.

- `az ml workspace create`
  - Add --enable-data-isolation(-e) flag to determine if a workspace has data isolation enabled.
  - Add --storage-account(-s) flag to allow specifying existing storage account at workspace creation.
  - Add --key-vault(-k) flag to allow specifying existing key vault at workspace creation.


## 2023-03-21

### Azure Machine Learning CLI (v2) v2.15.0

- `az ml compute`
  - Added `--tags` to create and update for AzureML Compute.

- `az ml data import`
  - Support create a data asset version by first importing data from database and file_system to Azure cloud storage.

- `az ml data list-materialization-status`
  - Support list status of data import materialization jobs that create data asset versions of <asset_name> via `--name` argumant.

- `az ml online-deployment update`
  - Added `--skip-script-validation` to create for AzureML Online Deployment.

- `az ml workspace provision-network`
  - Support to provision managed network for workspace


## 2023-02-03

### Azure Machine Learning CLI (v2) v2.14.0

- `az ml compute`
  - Added `--location` to create for AzureML Compute.
  - Added `--enable-node-public-ip` to create for Compute.

- `az ml data`
  - Minor edits to data help text

- `az ml data list`
  - Support list data asset in registry via the `--registry-name` argument

- `az ml data show`
  - Support show a data asset in registry via the `--registry-name` argument

- `az ml data create`
  - Support create a data asset in registry via the `--registry-name` argument
  - Support promoting a data asset from a workspace to a registry

- `az ml workspace create`
  - Support create a workspace with managed network with `--managed-network` argument

- `az ml workspace update`
  - Support update a workspace with managed network with `--managed-network` argument

- `az ml compute connect-ssh`
  - Command to connect to a compute instance via SSH

- `az ml workspace outbound-rule`
  - Support to list managed network outbound rules for workspace `az ml workspace outbound-rule list`
  - Support to show a managed network outbound rule for workspace `az ml workspace outbound-rule show`
  - Support to remove managed network outbound rule for workspace `az ml workspace outbound-rule remove`
  - Support to create or update managed network outbound rule for workspace `az ml workspace outbound-rule set`



## 2022-12-06

### Azure Machine Learning CLI (v2) v2.12.0

- Improve error message for `az ml` commands that are registry enabled, when neither workspace nor registry name is passed.
- `az ml compute`
  - Fixed issue caused by no-wait parameter.

## 2022-11-04

### Azure Machine Learning CLI (v2) v2.11.0

- `az ml registry`
  - List operation fixed to accept subscription scoping
  - Delete operation added.
  - Update operation added.
  - Made some minor edits to registry help text.

## 2022-10-10

### Azure Machine Learning CLI (v2) v2.10.0

- The CLI is depending on GA version of azure-ai-ml.
- Dropped support for Python 3.6.
- `az ml registry`
  - New command group added to manage ML asset registries.
- `az ml job`
  - Added `az ml job show-services` command.
  - Added model sweeping and hyperparameter tuning to AutoML NLP jobs.
- `az ml schedule`
  - Added `month_days` property in recurrence schedule.
- `az ml compute`
  - Added custom setup scripts support for compute instances.

## 2022-09-22

### Azure Machine Learning CLI (v2) v2.8.0

- `az ml job`
  - Added spark job support.
  - Added shm_size and docker_args to job.
- `az ml compute`
  - Compuate instance supports managed identity.
  - Added idle shutdown time support for compute instance.
- `az ml online-deployment`
  - Added support for data collection for eventhub and data storage.
  - Added syntax validation for scoring script.
- `az ml batch-deployment`
  - Added syntax validation for scoring script.

## 2022-08-10

### Azure Machine Learning CLI (v2) v2.7.0

- `az ml component`
  - Added AutoML component.
- `az ml dataset`
  - Deprecated command group (Use `az ml data` instead).

## 2022-07-16

### Azure Machine Learning CLI (v2) v2.6.0

- Added MoonCake cloud support.
- `az ml job`
  - Allow Git repo URLs to be used as code.
  - AutoML jobs use the same input schema as other job types.
  - Pipeline jobs now supports registry assets.
- `az ml component`
  - Allow Git repo URLs to be used as code.
- `az ml online-endpoint`
  - MIR now supports registry assets.

## 2022-05-24

### Azure Machine Learning CLI (v2) v2.4.0

- The Azure Machine Learning CLI (v2) is now GA.
- `az ml job`
  - The command group is marked as GA.
  - Added AutoML job type in public preview.
  - Added `schedules` property to pipeline job in public preview.
  - Added an option to list only archived jobs.
  - Improved reliability of `az ml job download` command.
- `az ml data`
  - The command group is marked as GA.
  - Added MLTable data type in public preview.
  - Added an option to list only archived data assets.
- `az ml environment`
  - Added an option to list only archived environments.
- `az ml model`
  - The command group is marked as GA.
  - Allow models to be created from job outputs.
  - Added an option to list only archived models.
- `az ml online-deployment`
  - The command group is marked as GA.
  - Removed timeout waiting for deployment creation.
  - Improved online deployment list view.
- `az ml online-endpoint`
  - The command group is marked as GA.
  - Added `mirror_traffic` property to online endpoints in public preview.
  - Improved online endpoint list view.
- `az ml batch-deployment`
  - The command group is marked as GA.
  - Added support for `uri_file` and `uri_folder` as invocation input.
  - Fixed a bug in batch deployment update.
  - Fixed a bug in batch deployment list-jobs output.
- `az ml batch-endpoint`
  - The command group is marked as GA.
  - Added support for `uri_file` and `uri_folder` as invocation input.
  - Fixed a bug in batch endpoint update.
  - Fixed a bug in batch endpoint list-jobs output.
- `az ml component`
  - The command group is marked as GA.
  - Added an option to list only archived components.
- `az ml code`
  - This command group is removed.

## 2022-03-14

### Azure Machine Learning CLI (v2) v2.2.1

- `az ml job`
  - For all job types, flattened the `code` section of the YAML schema. Instead of `code.local_path` to specify the path to the source code directory, it is now just `code`
  - For all job types, changed the schema for defining data inputs to the job in the job YAML. Instead of specifying the data path using either the `file` or `folder` fields, use the `path` field to specify either a local path, a URI to a cloud path containing the data, or a reference to an existing registered Azure ML data asset via `path: azureml:<data_name>:<data_version>`. Also specify the `type` field to clarify whether the data source is a single file (`uri_file`) or a folder (`uri_folder`). If `type` field is omitted, it defaults to `type: uri_folder`. For more information, see the section of any of the [job YAML references](reference-yaml-job-command.md) that discuss the schema for specifying input data.
  - In the [sweep job YAML schema](reference-yaml-job-sweep.md), changed the `sampling_algorithm` field from a string to an object in order to support additional configurations for the random sampling algorithm type
  - Removed the component job YAML schema. With this release, if you want to run a command job inside a pipeline that uses a component, just specify the component to the `component` field of the command job YAML definition.
  - For all job types, added support for referencing the latest version of a nested asset in the job YAML configuration. When referencing a registered environment or data asset to use as input in a job, you can alias by latest version rather than having to explicitly specify the version. For example: `environment: azureml:AzureML-Minimal@latest`
  - For pipeline jobs, introduced the `${{ parent }}` context for binding inputs and outputs between steps in a pipeline. For more information, see [Expression syntax for binding inputs and outputs between steps in a pipeline job](reference-yaml-core-syntax.md#binding-inputs-and-outputs-between-steps-in-a-pipeline-job).
  - Added support for downloading named outputs of job via the `--output-name` argument for the `az ml job download` command
- `az ml data`
  - Deprecated the `az ml dataset` subgroup, now using `az ml data` instead
  - There are two types of data that can now be created, either from a single file source (`type: uri_file`) or a folder (`type: uri_folder`). When creating the data asset, you can either specify the data source from a local file / folder or from a URI to a cloud path location. See the [data YAML schema](reference-yaml-data.md) for the full schema
- `az ml environment`
  - In the [environment YAML schema](reference-yaml-environment.md), renamed the `build.local_path` field to `build.path`
  - Removed the `build.context_uri` field, the URI of the uploaded build context location will be accessible via `build.path` when the environment is returned
- `az ml model`
  - In the [model YAML schema](reference-yaml-model.md), `model_uri` and `local_path` fields removed and consolidated to one `path` field that can take either a local path or a cloud path URI. `model_format` field renamed to `type`; the default type is `custom_model`, but you can specify one of the other types (`mlflow_model`, `triton_model`) to use the model in no-code deployment scenarios
  - For `az ml model create`, `--model-uri` and `--local-path` arguments removed and consolidated to one `--path` argument that can take either a local path or a cloud path URI
  - Added the `az ml model download` command to download a model's artifact files
- `az ml online-deployment`
  - In the [online deployment YAML schema](reference-yaml-deployment-managed-online.md), flattened the `code` section of the `code_configuration` field. Instead of `code_configuration.code.local_path` to specify the path to the source code directory containing the scoring files, it is now just `code_configuration.code`
  - Added an `environment_variables` field to the online deployment YAML schema to support configuring environment variables for an online deployment
- `az ml batch-deployment`
  - In the [batch deployment YAML schema](reference-yaml-deployment-batch.md), flattened the `code` section of the `code_configuration` field. Instead of `code_configuration.code.local_path` to specify the path to the source code directory containing the scoring files, it is now just `code_configuration.code`
- `az ml component`
  - Flattened the `code` section of the [command component YAML schema](reference-yaml-component-command.md). Instead of `code.local_path` to specify the path to the source code directory, it is now just `code`
  -  Added support for referencing the latest version of a registered environment to use in the component YAML configuration. When referencing a registered environment, you can alias by latest version rather than having to explicitly specify the version. For example: `environment: azureml:AzureML-Minimal@latest`
  -  Renamed the component input and output type value from `path` to `uri_folder` for the `type` field when defining a component input or output
- Removed the `delete` commands for assets (model, component, data, environment). The existing delete functionality is only a soft delete, so the `delete` commands will be reintroduced in a later release once hard delete is supported
- Added support for archiving and restoring assets (model, component, data, environment) and jobs, e.g. `az ml model archive` and `az ml model restore`. You can now archive assets and jobs, which will hide the archived entity from list queries (e.g. `az ml model list`).

## 2021-10-04

### Azure Machine Learning CLI (v2) v2.0.2

- `az ml workspace`
  - Updated [workspace YAML schema](reference-yaml-workspace.md)
- `az ml compute`
  - Updated YAML schemas for [AmlCompute](reference-yaml-compute-aml.md) and [Compute Instance](reference-yaml-compute-instance.md)
  - Removed support for legacy AKS attach via `az ml compute attach`. Azure Arc-enabled Kubernetes attach will be supported in the next release
- `az ml datastore`
  - Updated YAML schemas for [Azure blob](reference-yaml-datastore-blob.md), [Azure file](reference-yaml-datastore-files.md), [Azure Data Lake Gen1](reference-yaml-datastore-data-lake-gen1.md), and [Azure Data Lake Gen2](reference-yaml-datastore-data-lake-gen2.md) datastores
  - Added support for creating Azure Data Lake Storage Gen1 and Gen2 datastores
- `az ml job`
  - Updated YAML schemas for [command job](reference-yaml-job-command.md) and [sweep job](reference-yaml-job-sweep.md)
  - Added support for running pipeline jobs ([pipeline job YAML schema](reference-yaml-job-pipeline.md))
  - Added support for job input literals and input data URIs for all job types
  - Added support for job outputs for all job types
  - Changed the expression syntax from `{ <expression> }` to `${{ <expression> }}`. For more information, see [Expression syntax for configuring Azure ML jobs](reference-yaml-core-syntax.md#expression-syntax-for-configuring-azure-ml-jobs-and-components)
- `az ml environment`
  - Updated [environment YAML schema](reference-yaml-environment.md)
  - Added support for creating environments from Docker build context
- `az ml model`
  - Updated [model YAML schema](reference-yaml-model.md)
  - Added new `model_format` property to Model for no-code deployment scenarios
- `az ml dataset`
  - Renamed `az ml data` subgroup to `az ml dataset`
  - Updated dataset YAML schema
- `az ml component`
  - Added the `az ml component` commands for managing Azure ML components
  - Added support for command components ([command component YAML schema](reference-yaml-component-command.md))
- `az ml online-endpoint`
  - `az ml endpoint` subgroup split into two separate groups: `az ml online-endpoint` and `az ml batch-endpoint`
  - Updated [online endpoint YAML schema](reference-yaml-endpoint-online.md)
  - Added support for local endpoints for dev/test scenarios
  - Added interactive VSCode debugging support for local endpoints (added the `--vscode-debug` flag to `az ml batch-endpoint create/update`)
- `az ml online-deployment`
  - `az ml deployment` subgroup split into two separate groups: `az ml online-deployment` and `az ml batch-deployment`
  - Updated [managed online deployment YAML schema](reference-yaml-deployment-managed-online.md)
  - Added autoscaling support via integration with Azure Monitor Autoscale
  - Added support for updating multiple online deployment properties in the same update operation
  - Added support for performing concurrent operations on deployments under the same endpoint
- `az ml batch-endpoint`
  - `az ml endpoint` subgroup split into two separate groups: `az ml online-endpoint` and `az ml batch-endpoint`
  - Updated [batch endpoint YAML schema](reference-yaml-endpoint-batch.md)
  - Removed `traffic` property; replaced with a configurable default deployment property
  - Added support for input data URIs for `az ml batch-endpoint invoke`
  - Added support for VNet ingress (private link)
- `az ml batch-deployment`
  - `az ml deployment` subgroup split into two separate groups: `az ml online-deployment` and `az ml batch-deployment`
  - Updated [batch deployment YAML schema](reference-yaml-deployment-batch.md)

## 2021-05-25

### Announcing the CLI (v2) (preview) for Azure Machine Learning

The `ml` extension to the Azure CLI is the next-generation interface for Azure Machine Learning. It enables you to train and deploy models from the command line, with features that accelerate scaling data science up and out while tracking the model lifecycle. [Install and get started](how-to-configure-cli.md).
