.. :changelog:

Release History
===============
upcoming
++++++
* 'az containerapp up/create/update': Wait longer time for logstream of Cloud Build to make sure the container start
* 'az containerapp env java-component config-server-for-spring': Support create/update/show/delete Spring Cloud Config; deprecation of 'az containerapp env java-component spring-cloud-config'
* 'az containerapp env java-component eureka-server-for-spring': Support create/update/show/delete Spring Cloud Eureka; deprecation of 'az containerapp env java-component spring-cloud-eureka'

0.3.50
++++++
* 'az containerapp env telemetry data-dog show': Support show environment data dog configuration
* 'az containerapp env telemetry app-insights show': Support show environment app insights configuration
* 'az containerapp env telemetry otlp add': Support add environment otlp configuration with --otlp-name, --endpoint, --insecure, --headers, --enable-open-telemetry-traces, --enable-open-telemetry-logs and --enable-open-telemetry-metrics
* 'az containerapp env telemetry otlp update': Support update environment otlp configuration with --otlp-name, --endpoint, --insecure, --headers, --enable-open-telemetry-traces, --enable-open-telemetry-logs and --enable-open-telemetry-metrics
* 'az containerapp env telemetry otlp remove': Support remove environment otlp configuration with --otlp-name
* 'az containerapp env telemetry otlp show': Support show environment otlp configuration with --otlp-name
* 'az containerapp env telemetry otlp list': Support show environment otlp configurations

0.3.49
++++++
* 'az containerapp env telemetry data-dog set': Support update environment data dog configuration with --site, --key, --enable-open-telemetry-traces and --enable-open-telemetry-metrics
* 'az containerapp env telemetry data-dog delete': Support delete environment data dog configuration
* 'az containerapp env telemetry app-insights set': Support update environment app insights configuration with --connection-string, --enable-open-telemetry-traces and --enable-open-telemetry-logs
* 'az containerapp env telemetry app-insights delete': Support delete environment app insights configuration
* 'az containerapp update/up': Explicitly set container name to container app name for source to cloud builds.
* 'az containerapp env create/update': Add support for environment custom domain from azure key vault using managed identity
* 'az containerapp env certificate upload': Add support for environment certificate from azure key vault using managed identity

0.3.48
++++++
* 'az containerapp service': Remove deprecated command group altogether, only keep 'az containerapp add-on' for add-ons
* 'az containerapp env dapr-component resiliency': Add support for Dapr Component Resiliency Circuit Breakers
* 'az containerapp create/update/up': Don't compress jar/war/zip file before upload source code
* 'az containerapp create/update/up': Update source to cloud builder to 20240124.1
* 'az containerapp up': Fix registry not found error in subscription when registry server parameters are provided for ACR from another subscription
* 'az containerapp env java-component': Support list Java components
* 'az containerapp env java-component spring-cloud-config': Support create/update/show/delete Spring Cloud Config
* 'az containerapp env java-component spring-cloud-eureka': Support create/update/show/delete Spring Cloud Eureka
* 'az containerapp create/update': Support bind Java component with --bind
* 'az containerapp create/update/up': Fix issue with logs when the Cloud Build project to use generates UTF-8 logs.
* 'az containerapp update/up': Fix bug for multiple containers provisioned for source to cloud build

0.3.47
++++++
* 'az containerapp add-on' : support for add-on milvus create and delete commands
* [Breaking Change] 'az containerapp service': deprecate command from Azure CLI version 2.59.0
* 'az containerapp add-on' : support for add-on weaviate create and delete commands
* Upgrade api-version to 2023-11-02-preview
* 'az containerapp create/update/up': support --build-env-vars to set environment variables for build
* 'az containerapp create/update': support --max-inactive-revisions
* 'az containerapp env create': support --mi-system-assigned and --mi-user-assigned for environment create commands
* 'az containerapp env identity': support for container app environment assign/remove/show commands
* 'az containerapp env storage set': Support create or update managed environment storage with NFS Azure File.
* 'az containerapp up': Update the Docker error string used to identify unauthorized push.

0.3.46
++++++
* 'az containerapp create': Fix BadRequest Error about the clientType with --bind
* 'az containerapp update': Fix bug for --min-replicas is not set when the value is 0

0.3.45
++++++
* 'az containerapp up': Cloud Build Bugfix - 500 Internal Server Error (Wrong env selected to create builder)
* 'az containerapp up': support to create or update a containerapp on connected environment as well as any associated resources (extension on connected cluster, custom location) with --custom-location or --connected-cluster-id

0.3.44
++++++
* 'az containerapp env workload-profile set': deprecate command
* 'az containerapp add-on': support for az containerapp add-on commands; deprecation of az containerapp service commands
* 'az containerapp env dapr-component resiliency': Add Dapr Component Resiliency commands
* 'az containerapp resiliency': Add Container App Resiliency commands
* 'az containerapp env create': Support --enable-dedicated-gpu
* 'az containerapp job create': fix problem of parsing parameters minExecutions and maxExecutions from --yaml
* 'az containerapp env dapr-component init': support initializing Dapr components and dev services for an environment
* 'az containerapp patch apply': support image patching for java application
* Upgrade api-version to 2023-08-01-preview
* 'az containerapp env create/update': Support --logs-dynamic-json-columns/-j to configure whether to parse json string log into dynamic json columns
* 'az containerapp create/update/up': Remove the region check for the Cloud Build feature
* 'az containerapp create/update/up': Improve logs on the local buildpack source to cloud flow
* 'az containerapp create/update': Support --customized-keys and clientType in --bind for dev service

0.3.43
++++++
* Update azure cli dependency version >= "2.53.0"
* Remove GA commands which exists in azure-cli of version 2.53.0
* 'az containerapp create/update': fix an issue for transforming sensitive values when the scale rules metadata not exists
* 'az containerapp up': update builder image used when --source is provided with no Dockerfile to support building applications targeting a wider range of platform versions
* Add Cloud Build support (build without Dockerfile or Docker) in Stage/Canary regions to the 'az containerapp up'/'az containerapp create' and 'az containerapp update' commands

0.3.42
++++++
* 'az containerapp job create': Fix AttributeError when --trigger-type is None
* 'az containerapp update': fix bug for mounting secret volumes using --secret-volume-mount
* 'az containerapp compose create': fixed an issue where the environment's resource group was not resolved from --environment when the input value was a resource id.
* 'az containerapp replica count', returns the replica count of a container app
* [Breaking Change] 'az containerapp job create': add default values for container app job properties --replica-completion-count, --replica-retry-limit, --replica-timeout, --parallelism, --min-executions, --max-executions, --polling-interval
* 'az containerapp create/update': hide environment variables, scale rules metadata
* 'az containerapp job create/update': hide environment variables, scale rules metadata, eventTriggerConfig for job
* [Breaking Change] 'az containerapp env create': update the default value of --enable-workload-profiles to `True`
* 'az containerapp compose create': fix containerapp invalid memory resource

0.3.41
++++++
* 'az containerapp up/create': enable support for no Dockerfile cases with --repo

0.3.40
++++++
* 'az containerapp service': add support for creation and deletion of Qdrant vector database as a container app dev service
* Add command group 'az containerapp connected-env', support show/list/delete/create connected environment
* 'az containerapp create': support --source and --repo properties
* 'az containerapp update': support --source property
* Add command group 'az containerapp connected-env certificate', support list/upload/delete connectedEnvironments certificate
* Add command group 'az containerapp connected-env dapr-component', support list/show/set/remove connectedEnvironments daprComponents
* Add command group 'az containerapp connected-env storage', support list/show/set/remove connectedEnvironments storage
* 'az containerapp env': --infrastructure-resource-group, supports custom rg name for byovnet env creations in WP enabled envs

0.3.39
++++++
* 'az containerapp update': fix bug for populating secret value with --yaml

0.3.38
++++++
* Add support for binding managed MySQL Flexible server to a containerapp
* Removed preview tag for some command groups and params (e.g. 'az containerapp job', 'az containerapp env storage', 'az containerapp env workload-profile')
* 'az containerapp env': --enable-workload-profiles allowed values:true, false
* 'az containerapp auth': support --token-store, --sas-url-secret, --sas-url-secret-name, --yes
* 'az containerapp create'/'az containerapp job create': When --environment is provided and the environmentId value does not exist in --yaml, use the value in --environment as environmentId
* 'az containerapp job create': support --environment-type parameter
* 'az containerapp show-custom-domain-verification-id': show verfication id used for binding custom domain
* 'az containerapp list-usages': list usages in subscription
* 'az containerapp env list-usages': list usages in environment
* 'az containerapp update': --yaml support property additionalPortMappings for api-version 2023-05-02-preview
* 'az containerapp create/update': raise ValidationError when value in --yaml is None

0.3.37
++++++
* 'az containerapp job start': update start execution payload format to exlude template property from API version 2023-05-01 onwards
* 'az containerapp service': add support for creation and deletion of MariaDB
* 'az containerapp create/list': support --environment-type parameter
* 'az containerapp logs show': fix raising error for response status code is not OK
* 'az containerapp auth show/update': support api-version 2023-05-02-preview
* 'az containerapp create': --yaml support property additionalPortMappings for api-version 2023-05-02-preview
* 'az containerapp create': add support for insecure ingress with flag --allow-insecure

0.3.36
++++++
* 'az containerapp hostname bind': fix exception when not bringing --validation-method inputs

0.3.35
++++++
* 'az containerapp create/update': --termination-grace-period support custom termination grace period
* 'az containerapp env logs show': fix issue of constructing connection url
* 'az containerapp create/update': --revision-suffix allow revision suffix to start with numbers
* 'az containerapp create/show/list/delete': refactor with containerapp decorator

0.3.34
++++++
* 'az containerapp job execution show/list': improve table output format
* 'az containerapp create/update': --yaml support properties for api-version 2023-04-01-preview (e.g. subPath, mountOptions)
* 'az containerapp service': add support for creation and deletion of kafka
* 'az containerapp create': --registry-server support registry with custom port
* 'az containerapp create': fix containerapp create not waiting for ready environment
* Add regex to fix validation for containerapp name
* Add 'az containerapp ingress cors' for CORS support
* 'az container app env create/update': support --enable-mtls parameter
* 'az containerapp up': fix issue where --repo throws KeyError

0.3.33
++++++
* 'az containerapp create': fix --registry-identity "system" with --revision-suffix
* 'az containerapp up': fix --target-port value not being propagated when buildpack is used to build image from --source
* Fix for 'az containerapp job create' with --yaml option to create a Container App job
* Support 'az containerapp job secret' to manage secrets for Container App jobs
* Support 'az containerapp job identity' to manage identity for Container App jobs
* Fix for issue with --user-assigned identity for Container App jobs where identities were getting split incorrectly
* Add new parameters `--mi-system-assigned` and `--mi-user-assigned` to replace the deprecated parameters `--system-assigned` and `--user-assigned` for `az containerapp job create` command

0.3.32
++++++
* Fix for 'az containerapp job update' command when updating Container App job with a trigger configuration

0.3.31
++++++
* Fix issue when using 'az containerapp up' to create a container app from a local source with a Dockerfile

0.3.30
++++++
* Add 'az containerapp service' for binding a service to a container app
* Add 'az containerapp patch' to enable the local source to cloud
* Add 'az containerapp job' to manage Container Apps jobs
* Split 'az containerapp env workload-profile set' into 'az containerapp env workload-profile add' and 'az containerapp env workload-profile update'
* Add 'az containerapp env workload-profile add' to support creating a workload profile in an environment
* Add 'az containerapp env workload-profile update' to support updating an existing workload profile in an environment
* 'az containerapp auth update': fix excluded paths first and last character being cutoff
* 'az containerapp update': remove the environmentId in the PATCH payload if it has not been changed
* Upgrade api-version to 2023-04-01-preview

0.3.29
++++++
* 'az containerapp create': support for assigning acrpull permissions to managed identity in cross-subscription; warn when ACR resourceNotFound, do not block the process
* 'az containerapp hostname bind': fix bug where the prompt for validation method didn't take value in
* Make --validation-method parameter case insensitive for 'az containerapp hostname bind' and 'az containerapp env certificate create'
* 'az containerapp auth update': remove unsupported argument --enable-token-store
* 'az containerapp update'/'az containerapp env update': fix --no-wait
* 'az containerapp update': fix the --yaml update behavior to respect the empty array in patch-request
* 'az containerapp create/update': add support for secret volumes yaml and --secret-volume-mount

0.3.28
++++++
* 'az containerapp secret set': fix help typo
* 'az containerapp secret set': add more format validation for key vault secrets
* 'az containerapp up': fix --location comparison logic
* 'az containerapp update': change --max-replicas limit
* Add CLI support for containerapp ingress sticky-sessions'
* Change quickstart image
* 'az containerapp create': fix yaml not detecting workloadProfileName

0.3.27
++++++
* 'az containerapp secret set': add support for secrets from Key Vault
* 'az containerapp secret show': add support for secrets from Key Vault

0.3.26
++++++
* 'az containerapp exec': fix bugs for consumption workload based environment
* 'az containerapp env create': fix bug causing --enable-workload-profiles to require an argument

0.3.25
++++++
* 'az containerapp create/update': --yaml support properties for api-version 2022-10-01 (e.g. exposedPort,clientCertificateMode,corsPolicy)
* 'az containerapp env update': fix bugs in update environment.
* Fix YAML create with user-assigned identity
* Fix polling logic for long running operations.
* 'az containerapp env create': add support for workload profiles
* 'az containerapp env update': add support for workload profiles
* 'az containerapp create': add support for workload profiles
* 'az containerapp update': add support for workload profiles
* Add 'az containerapp env workload-profile delete' to support deleting a workload profile from an environment
* Add 'az containerapp env workload-profile list' to support listing all workload profiles in an environment
* Add 'az containerapp env workload-profile list-supported' to support listing all available workload profile types in a region
* Add 'az containerapp env workload-profile set' to support creating or updating an existing workload profile in an environment
* Add 'az containerapp env workload-profile show' to support showing details of a single workload profile in an environment
* Upgrade api-version from 2022-10-01 to 2022-11-01-preview
* Add `az containerapp ingress update` Command to Update Container App Ingress

0.3.24
++++++
* Decouple with the `network` module.

0.3.23
++++++
* BREAKING CHANGE: 'az containerapp env certificate list' returns [] if certificate not found, instead of raising an error.
* Added 'az containerapp env certificate create' to create managed certificate in a container app environment
* Added 'az containerapp hostname add' to add hostname to a container app without binding
* 'az containerapp env certificate delete': add support for managed certificate deletion
* 'az containerapp env certificate list': add optional parameters --managed-certificates-only and --private-key-certificates-only to list certificates by type
* 'az containerapp hostname bind': change --thumbprint to an optional parameter and add optional parameter --validation-method to support managed certificate bindings
* 'az containerapp ssl upload': log messages to indicate which step is in progress
* Upgrade api-version from 2022-06-01-preview to 2022-10-01
* Fix error when running `az containerapp up` on local source that doesn't contain a Dockerfile
* Fix the 'TypeError: 'NoneType' object does not support item assignment' error obtained while running the CLI command 'az containerapp dapr enable'

0.3.21
++++++
* Fix the PermissionError caused for the Temporary files while running `az containerapp up` command on Windows
* Fix the empty IP Restrictions object caused running `az containerapp update` command on Windows with a pre existing .yaml file
* Added model mapping to support add/update of init Containers via `az containerapp create` & `az containerapp update` commands.

0.3.20
++++++
* Fix custom domain null issue for `az containerapp hostname list` and `az containerapp hostname delete` command

0.3.19
++++++
* Fix "'NoneType' object is not iterable" error in `az containerapp hostname bind` command

0.3.18
++++++
* Fix "'NoneType' object has no attribute 'get'" error in `az containerapp up` with no ingress arguments

0.3.17
++++++
* Fix polling logic for long running operations.

0.3.16
++++++
* Remove quota check for 'az containerapp up' and 'az containerapp env create'.

0.3.15
++++++
* Add 'az containerapp containerapp ingress ip-restriction' command group to manage IP restrictions on the ingress of a container app.

0.3.14
++++++
* 'az containerapp logs show'/'az containerapp exec': Fix "KeyError" bug

0.3.13
++++++
* 'az containerapp compose create': Migrated from containerapp-compose extension
* Add parameters --logs-destination and --storage-account support for new logs destinations to `az containerapp env create` and `az containerapp env update`

0.3.12
++++++
* Add 'az containerapp env update' to update managed environment properties
* Add custom domains support to 'az containerapp env create' and 'az containerapp env update'
* 'az containerapp logs show': add new parameter "--type" to allow showing system logs
* Show system environment logs with new command 'az containerapp env logs show'
* Add tcp support for ingress transport and scale rules
* `az containerapp up/github-action add`: Retrieve workflow file name from github actions API
* 'az containerapp create/update': validate revision suffixes

0.3.11
++++++
* Add keda scale rule parameters to 'az containerapp create', 'az containerapp update' and 'az containerapp revision copy'
* Add new dapr params to 'az containerapp dapr enable' and 'az containerapp create'
* 'az containerapp up': autogenerate a docker container with --source when no dockerfile present

0.3.10
++++++
* 'az containerapp create': Fix bug with --image caused by assuming a value for --registry-server
* 'az containerapp hostname bind': Remove location set automatically by resource group
* 'az containerapp env create': Add location validation

0.3.9
++++++
* 'az containerapp create': Allow authenticating with managed identity (MSI) instead of ACR username & password
* 'az containerapp show': Add parameter --show-secrets to show secret values
* 'az containerapp env create': Add better message when polling times out
* 'az containerapp env certificate upload': Fix bug where certificate uploading failed with error "Certificate must contain one private key"
* 'az containerapp env certificate upload': Fix bug where replacing invalid character in certificate name failed

0.3.8
++++++
* 'az containerapp update': Fix bug where --yaml would error out due to secret values
* 'az containerapp update': use PATCH API instead of GET and PUT
* 'az containerapp up': Fix bug where using --source with an invalid name parameter causes ACR build to fail
* 'az containerapp logs show'/'az containerapp exec': Fix bug where ssh/logstream they would fail on apps with networking restrictions

0.3.7
++++++
* Fixed bug with 'az containerapp up' where --registry-server was ignored
* 'az containerapp env create': fixed bug where "--internal-only" didn't work
* 'az containerapp registry set': remove username/password if setting identity and vice versa

0.3.6
++++++
* BREAKING CHANGE: 'az containerapp revision list' now shows only active revisions by default, added flag --all to show all revisions
* BREAKING CHANGE: 'az containerapp env certificate upload' does not prompt by default when re-uploading an existing certificate. Added --show-prompt to show prompts on re-upload.
* Added parameter --environment to 'az containerapp list'
* Added 'az containerapp revision label swap' to swap traffic labels
* Fixed bug with 'az containerapp up' where custom domains would be removed when updating existing containerapp
* Fixed bug with 'az containerapp auth update' when using --unauthenticated-client-action
* Fixed bug with 'az containerapp env certificate upload' where it shows a misleading message for invalid certificate name
* 'az containerapp registry set': allow authenticating with managed identity (MSI) instead of ACR username & password

0.3.5
++++++
* Add parameter --zone-redundant to 'az containerapp env create'
* Added 'az containerapp env certificate' to manage certificates in a container app environment
* Added 'az containerapp hostname' to manage hostnames in a container app
* Added 'az containerapp ssl upload' to upload a certificate, add a hostname and the binding to a container app
* Added 'az containerapp auth' to manage AuthConfigs for a containerapp
* Require Azure CLI version of at least 2.37.0

0.3.4
++++++
* BREAKING CHANGE: 'az containerapp up' and 'az containerapp github-action add' now use the github repo's default branch instead of "main"
* 'az containerapp up' now caches Github credentials so the user won't be prompted to sign in if using the same repo
* Fixed bug with 'az containerapp up --repo' where it hangs after creating github action
* Added 'az containerapp env storage' to manage Container App environment file shares

0.3.3
++++++
* Improved 'az containerapp up' handling of environment locations

0.3.2
++++++
* Added 'az containerapp up' to create or update a container app and all associated resources (container app environment, ACR, Github Actions, resource group, etc.)
* Open an ssh-like shell in a Container App with 'az containerapp exec'
* Support for log streaming with 'az containerapp logs show'
* Replica show and list commands

0.3.1
++++++
* Update "az containerapp github-action add" parameters: replace --docker-file-path with --context-path, add --image.

0.3.0
++++++
* Subgroup commands for managed identities: az containerapp identity

0.1.0
++++++
* Initial release for Container App support with Microsoft.App RP.
* Subgroup commands for dapr, github-action, ingress, registry, revision & secrets
* Various bugfixes for create & update commands
