# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['containerapp'] = """
    type: group
    short-summary: Commands to manage Containerapps.
"""

helps['containerapp create'] = """
    type: command
    short-summary: Create a Containerapp.
    examples:
    - name: Create a Containerapp
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --image MyContainerImage -e MyContainerappEnv \\
              --query properties.configuration.ingress.fqdn
    - name: Create a Containerapp with secrets and environment variables
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --image MyContainerImage -e MyContainerappEnv \\
              --secrets mysecret=escapefromtarkov,anothersecret=isadifficultgame \\
              --environment-variables myenvvar=foo,anotherenvvar=bar \\
              --query properties.configuration.ingress.fqdn
    - name: Create a Containerapp that only accepts internal traffic
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --image MyContainerImage -e MyContainerappEnv \\
              --ingress internal \\
              --query properties.configuration.ingress.fqdn
    - name: Create a Containerapp using an image from a private registry
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --image MyContainerImage -e MyContainerappEnv \\
              --secrets mypassword=verysecurepassword \\
              --registry-login-server MyRegistryServerAddress \\
              --registry-username MyUser \\
              --registry-password mypassword \\
              --query properties.configuration.ingress.fqdn
    - name: Create a Containerapp with a specified startup command and arguments
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --image MyContainerImage  -e MyContainerappEnv \\
              --command "/bin/sh" \\
              --args "-c", "while true; do echo hello; sleep 10;done" \\
              --query properties.configuration.ingress.fqdn
    - name: Create a Containerapp with a minimum resource and replica requirements
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --image MyContainerImage -e MyContainerappEnv \\
              --cpu 0.5 --memory 1.0Gi \\
              --min-replicas 4 --max-replicas 8 \\
              --query properties.configuration.ingress.fqdn
    - name: Create a Containerapp using a YAML configuration. Example YAML configuration - https://docs.microsoft.com/azure/container-apps/azure-resource-manager-api-spec#examples
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --yaml "C:/path/to/yaml/file.yml"
"""

helps['containerapp update'] = """
    type: command
    short-summary: Update a Containerapp.
    examples:
    - name: Update a Containerapp's container image
      text: |
          az containerapp update -n MyContainerapp -g MyResourceGroup \\
              --image MyNewContainerImage
    - name: Update a Containerapp with secrets and environment variables
      text: |
          az containerapp update -n MyContainerapp -g MyResourceGroup \\
              --secrets mysecret=secretfoo,anothersecret=secretbar
              --environment-variables myenvvar=foo,anotherenvvar=secretref:mysecretname
    - name: Update a Containerapp's ingress setting to internal
      text: |
          az containerapp update -n MyContainerapp -g MyResourceGroup \\
              --ingress internal
    - name: Update a Containerapp using an image from a private registry
      text: |
          az containerapp update -n MyContainerapp -g MyResourceGroup \\
              --image MyNewContainerImage \\
              --secrets mypassword=verysecurepassword \\
              --registry-login-server MyRegistryServerAddress \\
              --registry-username MyUser \\
              --registry-password mypassword
    - name: Update a Containerapp using a specified startup command and arguments
      text: |
          az containerapp update -n MyContainerapp -g MyResourceGroup \\
              --image MyContainerImage \\
              --command "/bin/sh"
              --args "-c", "while true; do echo hello; sleep 10;done"
    - name: Update a Containerapp with a minimum resource and replica requirements
      text: |
          az containerapp update -n MyContainerapp -g MyResourceGroup \\
              --cpu 0.5 --memory 1.0Gi \\
              --min-replicas 4 --max-replicas 8
"""

helps['containerapp delete'] = """
    type: command
    short-summary: Delete a Containerapp.
    examples:
    - name: Delete a Containerapp.
      text: az containerapp delete -g MyResourceGroup -n MyContainerapp
"""

helps['containerapp scale'] = """
    type: command
    short-summary: Set the min and max replicas for a Containerapp.
    examples:
    - name: Scale a Containerapp.
      text: az containerapp scale -g MyResourceGroup -n MyContainerapp --min-replicas 1 --max-replicas 2
"""

helps['containerapp show'] = """
    type: command
    short-summary: Show details of a Containerapp.
    examples:
    - name: Show the details of a Containerapp.
      text: |
          az containerapp show -n MyContainerapp -g MyResourceGroup
"""

helps['containerapp list'] = """
    type: command
    short-summary: List Containerapps.
    examples:
    - name: List Containerapps by subscription.
      text: |
          az containerapp list
    - name: List Containerapps by resource group.
      text: |
          az containerapp list -g MyResourceGroup
"""

# Revision Commands
helps['containerapp revision'] = """
    type: group
    short-summary: Commands to manage a Containerapp's revisions.
"""

helps['containerapp revision show'] = """
    type: command
    short-summary: Show details of a Containerapp's revision.
    examples:
    - name: Show details of a Containerapp's revision.
      text: |
          az containerapp revision show --revision-name MyContainerappRevision -g MyResourceGroup
"""

helps['containerapp revision list'] = """
    type: command
    short-summary: List details of a Containerapp's revisions.
    examples:
    - name: List a Containerapp's revisions.
      text: |
          az containerapp revision list --revision-name MyContainerapp -g MyResourceGroup
"""

helps['containerapp revision restart'] = """
    type: command
    short-summary: Restart a Containerapps's revision.
    examples:
    - name: Restart a Containerapp's revision.
      text: |
          az containerapp revision restart --revision-name MyContainerappRevision -g MyResourceGroup
"""

helps['containerapp revision activate'] = """
    type: command
    short-summary: Activates Containerapp's revision.
    examples:
    - name: Activate a Containerapp's revision.
      text: |
          az containerapp revision activate --revision-name MyContainerappRevision -g MyResourceGroup
"""

helps['containerapp revision deactivate'] = """
    type: command
    short-summary: Deactivates Containerapp's revision.
    examples:
    - name: Deactivate a Containerapp's revision.
      text: |
          az containerapp revision deactivate --revision-name MyContainerappRevision -g MyResourceGroup
"""

helps['containerapp revision mode set'] = """
    type: command
    short-summary: Set the revision mode of a Containerapp.
    examples:
    - name: Set the revision mode of a Containerapp.
      text: |
          az containerapp revision set --mode Single -n MyContainerapp -g MyResourceGroup
"""

helps['containerapp revision copy'] = """
    type: command
    short-summary: Create a revision based on a previous revision.
    examples:
    - name: Create a revision based on a previous revision.
      text: |
          az containerapp revision copy -n MyContainerapp -g MyResourceGroup --cpu 0.75 --memory 1.5Gi
"""

# Environment Commands
helps['containerapp env'] = """
    type: group
    short-summary: Commands to manage Containerapp environments.
"""

helps['containerapp env create'] = """
    type: command
    short-summary: Create a Containerapp environment.
    examples:
    - name: Create a Containerapp Environment with an autogenerated Log Analytics
      text: |
          az containerapp env create -n MyContainerappEnvironment -g MyResourceGroup \\
              -- location Canada Central
    - name: Create a Containerapp Environment with Log Analytics
      text: |
          az containerapp env create -n MyContainerappEnvironment -g MyResourceGroup \\
              --logs-workspace-id myLogsWorkspaceID \\
              --logs-workspace-key myLogsWorkspaceKey \\
              --location Canada Central
"""

helps['containerapp env update'] = """
    type: command
    short-summary: Update a Containerapp environment. Currently Unsupported.
"""

helps['containerapp env delete'] = """
    type: command
    short-summary: Delete a Containerapp Environment.
    examples:
    - name: Delete Containerapp Environment.
      text: az containerapp env delete -g MyResourceGroup -n MyContainerappEnvironment
"""

helps['containerapp env show'] = """
    type: command
    short-summary: Show details of a Containerapp environment.
    examples:
    - name: Show the details of a Containerapp Environment.
      text: |
          az containerapp env show -n MyContainerappEnvironment -g MyResourceGroup
"""

helps['containerapp env list'] = """
    type: command
    short-summary: List Containerapp environments by subscription or resource group.
    examples:
    - name: List Containerapp Environments by subscription.
      text: |
          az containerapp env list
    - name: List Containerapp Environments by resource group.
      text: |
          az containerapp env list -g MyResourceGroup
"""

# Ingress Commands
helps['containerapp ingress'] = """
    type: group
    short-summary: Commands to manage Containerapp ingress.
"""

helps['containerapp ingress traffic'] = """
    type: subgroup
    short-summary: Commands to manage Containerapp ingress traffic.
"""

helps['containerapp ingress show'] = """
    type: command
    short-summary: Show details of a Containerapp ingress.
    examples:
    - name: Show the details of a Containerapp ingress.
      text: |
          az containerapp ingress show -n MyContainerapp -g MyResourceGroup
"""

helps['containerapp ingress enable'] = """
    type: command
    short-summary: Enable Containerapp ingress.
    examples:
    - name: Enable Containerapp ingress.
      text: |
          az containerapp ingress enable -n MyContainerapp -g MyResourceGroup --type external --allow-insecure --target-port 80 --transport auto
"""

helps['containerapp ingress disable'] = """
    type: command
    short-summary: Disable Containerapp ingress.
    examples:
    - name: Disable Containerapp ingress.
      text: |
          az containerapp ingress disable -n MyContainerapp -g MyResourceGroup
"""

helps['containerapp ingress traffic'] = """
    type: group
    short-summary: Commands to manage Containerapp ingress traffic.
"""

helps['containerapp ingress traffic set'] = """
    type: command
    short-summary: Set Containerapp ingress traffic.
    examples:
    - name: Set Containerapp ingress traffic.
      text: |
          az containerapp ingress traffic set -n MyContainerapp -g MyResourceGroup --traffic-weight latest=100
"""

helps['containerapp ingress traffic show'] = """
    type: command
    short-summary: Show Containerapp ingress traffic.
    examples:
    - name: Show Containerapp ingress traffic.
      text: |
          az containerapp ingress traffic show -n MyContainerapp -g MyResourceGroup 
"""

# Registry Commands
helps['containerapp registry'] = """
    type: group
    short-summary: Commands to manage Containerapp registries.
"""

helps['containerapp registry show'] = """
    type: command
    short-summary: Show details of a Containerapp registry.
    examples:
    - name: Show the details of a Containerapp registry.
      text: |
          az containerapp registry show -n MyContainerapp -g MyResourceGroup --server MyContainerappRegistry.azurecr.io
"""

helps['containerapp registry list'] = """
    type: command
    short-summary: List registries assigned to a Containerapp.
    examples:
    - name: Show the details of a Containerapp registry.
      text: |
          az containerapp registry list -n MyContainerapp -g MyResourceGroup 
"""

helps['containerapp registry set'] = """
    type: command
    short-summary: Add or update a Containerapp registry.
    examples:
    - name: Add a registry to a Containerapp.
      text: |
          az containerapp registry set -n MyContainerapp -g MyResourceGroup --server MyContainerappRegistry.azurecr.io
    - name: Update a Containerapp registry.
      text: |
          az containerapp registry set -n MyContainerapp -g MyResourceGroup --server MyExistingContainerappRegistry.azurecr.io --username MyRegistryUsername --password MyRegistryPassword
  
"""

helps['containerapp registry delete'] = """
    type: command
    short-summary: Delete a registry from a Containerapp.
    examples:
    - name: Delete a registry from a Containerapp.
      text: |
          az containerapp registry delete -n MyContainerapp -g MyResourceGroup --server MyContainerappRegistry.azurecr.io
"""

# Secret Commands
helps['containerapp secret'] = """
    type: group
    short-summary: Commands to manage Containerapp secrets.
"""

helps['containerapp secret show'] = """
    type: command
    short-summary: Show details of a Containerapp secret.
    examples:
    - name: Show the details of a Containerapp secret.
      text: |
          az containerapp secret show -n MyContainerapp -g MyResourceGroup --secret-name MySecret
"""

helps['containerapp secret list'] = """
    type: command
    short-summary: List the secrets of a Containerapp.
    examples:
    - name: List the secrets of a Containerapp.
      text: |
          az containerapp secret list -n MyContainerapp -g MyResourceGroup
"""

helps['containerapp secret delete'] = """
    type: command
    short-summary: Delete secrets from a Containerapp.
    examples:
    - name: Delete secrets from a Containerapp.
      text: |
          az containerapp secret delete -n MyContainerapp -g MyResourceGroup --secret-names MySecret MySecret2
"""

helps['containerapp secret set'] = """
    type: command
    short-summary: Create/update Containerapp secrets.
    examples:
    - name: Add a secret to a Containerapp.
      text: |
          az containerapp secret set -n MyContainerapp -g MyResourceGroup --secrets MySecretName=MySecretValue 
    - name: Update a Containerapp secret.
      text: |
          az containerapp secret set -n MyContainerapp -g MyResourceGroup --secrets MyExistingSecretName=MyNewSecretValue 
"""

helps['containerapp github-action add'] = """
    type: command
    short-summary: Adds GitHub Actions to the Containerapp
    examples:
    - name: Add GitHub Actions, using Azure Container Registry and personal access token.
      text: az containerapp github-action add -g MyResourceGroup -n MyContainerapp --repo-url https://github.com/userid/repo --branch main
          --registry-url myregistryurl.azurecr.io
          --service-principal-client-id 00000000-0000-0000-0000-00000000
          --service-principal-tenant-id 00000000-0000-0000-0000-00000000
          --service-principal-client-secret ClientSecret
          --token MyAccessToken
    - name: Add GitHub Actions, using Azure Container Registry and log in to GitHub flow to retrieve personal access token.
      text: az containerapp github-action add -g MyResourceGroup -n MyContainerapp --repo-url https://github.com/userid/repo --branch main
          --registry-url myregistryurl.azurecr.io
          --service-principal-client-id 00000000-0000-0000-0000-00000000
          --service-principal-tenant-id 00000000-0000-0000-0000-00000000
          --service-principal-client-secret ClientSecret
          --login-with-github
    - name: Add GitHub Actions, using Dockerhub and log in to GitHub flow to retrieve personal access token.
      text: az containerapp github-action add -g MyResourceGroup -n MyContainerapp --repo-url https://github.com/userid/repo --branch main
          --registry-username MyUsername
          --registry-password MyPassword
          --service-principal-client-id 00000000-0000-0000-0000-00000000
          --service-principal-tenant-id 00000000-0000-0000-0000-00000000
          --service-principal-client-secret ClientSecret
          --login-with-github
"""

helps['containerapp github-action delete'] = """
    type: command
    short-summary: Removes GitHub Actions from the Containerapp
    examples:
    - name: Removes GitHub Actions, personal access token.
      text: az containerapp github-action delete -g MyResourceGroup -n MyContainerapp
          --token MyAccessToken
    - name: Removes GitHub Actions, using log in to GitHub flow to retrieve personal access token.
      text: az containerapp github-action delete -g MyResourceGroup -n MyContainerapp
          --login-with-github
"""

helps['containerapp github-action show'] = """
    type: command
    short-summary: Show the GitHub Actions configuration on a Containerapp
    examples:
    - name: Show the GitHub Actions configuration on a Containerapp
      text: az containerapp github-action show -g MyResourceGroup -n MyContainerapp
"""