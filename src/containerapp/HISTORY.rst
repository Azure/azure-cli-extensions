.. :changelog:

Release History
===============

Upcoming
++++++
* 'az containerapp job start': update start execution payload format to exlude template property from API version 2023-05-01 onwards
* 'az containerapp service': add support for creation and deletion of MariaDB
* 'az containerapp create/list': support --environment-type parameter

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
