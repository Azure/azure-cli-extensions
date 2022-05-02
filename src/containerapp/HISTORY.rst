.. :changelog:

Release History
===============

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
