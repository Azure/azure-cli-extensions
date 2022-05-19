.. :changelog:

Release History
===============

0.3.5
++++++
* Add parameter --zone-redundant to 'az containerapp env create'
* Added 'az containerapp env certificate' to manage certificates in a container app environment
* Added 'az containerapp hostname' to manage hostnames in a container app
* Added 'az containerapp ssl upload' to upload a certificate, add a hostname and the binding to a container app

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
