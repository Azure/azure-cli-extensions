.. :changelog:

Release History
===============
0.3.21
++++++
* Fix the PermissionError caused for the Temporary files while running `az containerapp up` command on Windows

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
