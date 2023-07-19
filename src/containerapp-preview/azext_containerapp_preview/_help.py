# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['containerapp create'] = """
    type: command
    short-summary: Create a container app.
    examples:
    - name: Create a container app and retrieve its fully qualified domain name.
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --image myregistry.azurecr.io/my-app:v1.0 --environment MyContainerappEnv \\
              --ingress external --target-port 80 \\
              --registry-server myregistry.azurecr.io --registry-username myregistry --registry-password $REGISTRY_PASSWORD \\
              --query properties.configuration.ingress.fqdn
    - name: Create a container app with resource requirements and replica count limits.
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --image nginx --environment MyContainerappEnv \\
              --cpu 0.5 --memory 1.0Gi \\
              --min-replicas 4 --max-replicas 8
    - name: Create a container app with secrets and environment variables.
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --image my-app:v1.0 --environment MyContainerappEnv \\
              --secrets mysecret=secretvalue1 anothersecret="secret value 2" \\
              --env-vars GREETING="Hello, world" SECRETENV=secretref:anothersecret
    - name: Create a container app using a YAML configuration. Example YAML configuration - https://aka.ms/azure-container-apps-yaml
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --environment MyContainerappEnv \\
              --yaml "path/to/yaml/file.yml"
    - name: Create a container app with an http scale rule
      text: |
          az containerapp create -n myapp -g mygroup --environment myenv --image nginx \\
              --scale-rule-name my-http-rule \\
              --scale-rule-http-concurrency 50
    - name: Create a container app with a custom scale rule
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --image my-queue-processor --environment MyContainerappEnv \\
              --min-replicas 4 --max-replicas 8 \\
              --scale-rule-name queue-based-autoscaling \\
              --scale-rule-type azure-queue \\
              --scale-rule-metadata "accountName=mystorageaccountname" \\
                                    "cloud=AzurePublicCloud" \\
                                    "queueLength": "5" "queueName": "foo" \\
              --scale-rule-auth "connection=my-connection-string-secret-name"
    - name: Create a container app with secrets and mounts them in a volume.
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --image my-app:v1.0 --environment MyContainerappEnv \\
              --secrets mysecret=secretvalue1 anothersecret="secret value 2" \\
              --secret-volume-mount "mnt/secrets"
    - name: Create a container app hosted on a Connected Environment.
      text: |
          az containerapp create -n MyContainerapp -g MyResourceGroup \\
              --image my-app:v1.0 --environment MyContainerappConnectedEnv \\
              --environment-type connected
"""

# Connected Environment Commands
helps['containerapp connected-env'] = """
    type: group
    short-summary: Commands to manage Container Apps Connected environments for use with Arc enabled Container Apps.
"""

helps['containerapp connected-env create'] = """
    type: command
    short-summary: Create a Container Apps connected environment.
    long-summary: Create a Container Apps Connected environment for use with Arc enabled Container Apps.  Environments are an isolation boundary around a collection of container apps.
    examples:
    - name: Create a connected environment
      text: |
          az containerapp connected-env create -n MyContainerappConnectedEnv -g MyResourceGroup \\
              --location northcentralusstage --custom-location MyCustomLocationResourceID
"""


helps['containerapp connected-env delete'] = """
    type: command
    short-summary: Delete a Container Apps connected environment.
    examples:
    - name: Delete a connected environment.
      text: az containerapp connected-env delete -n MyContainerappConnectedEnv -g MyResourceGroup
"""

helps['containerapp connected-env show'] = """
    type: command
    short-summary: Show details of a Container Apps connected environment.
    examples:
    - name: Show the details of a connected environment.
      text: |
          az containerapp connected-env show -n MyContainerappConnectedEnv -g MyResourceGroup
"""

helps['containerapp connected-env list'] = """
    type: command
    short-summary: List Container Apps connected environments by subscription or resource group.
    examples:
    - name: List connected environments in the current subscription.
      text: |
          az containerapp connected-env list
    - name: List connected environments by resource group.
      text: |
          az containerapp connected-env list -g MyResourceGroup
"""
